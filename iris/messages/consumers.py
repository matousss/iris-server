import json
from uuid import UUID

from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError

from .models import Channel, Message, DirectChannel
from .serializers import MessageSerializer


# todo fix exceptions

# todo disconnect on token invalidation
# todo updated channels
class MessageConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None

    def get_user_channels(self):
        return Channel.objects.filter(users__exact=self.user).all()

    def connect(self):
        if self.scope['user'].is_anonymous:
            self.close()
            return

        # user, auth_token = knoxAuth.authenticate_credentials()
        # self.scope['user'] = user

        self.user = self.scope['user']
        for channel in self.get_user_channels():
            async_to_sync(self.channel_layer.group_add)(str(channel.id), self.channel_name)

        self.accept()
        print('connected')

    def error_to_front(self, detail):
        self.send(
            text_data=json.dumps({
                'error': detail,
            })
        )

    def receive(self, text_data=None, bytes_data=None):
        if False and text_data:
            try:
                data = json.loads(text_data)
            except Exception as e:
                self.error_to_front({'detail': _('JSON has invalid format'), 'type': str(type(e))})
                return

            serializer = MessageSerializer(data=data, context={'user': self.user})
            try:
                serializer.is_valid(raise_exception=True)
            except ValidationError as e:
                detail = e.detail
                detail['type'] = ValidationError.__name__
                self.error_to_front(detail)
                return
            serializer.save()
        else:
            self.close()

    def updated_message(self, event):
        self.send(text_data=event['message'])
