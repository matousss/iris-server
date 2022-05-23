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
# todo logout user on token deletion
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

        self.user = self.scope['user']
        for channel in self.get_user_channels():
            async_to_sync(self.channel_layer.group_add)(str(channel.id), self.channel_name)
        async_to_sync(self.channel_layer.group_add)(str(self.user.id), self.channel_name)

        self.accept()

    def error_to_front(self, detail):
        self.send(
            text_data=json.dumps({
                'object': 'error',
                'data': {'detail': detail},
            })
        )

    def receive(self, text_data=None, bytes_data=None):
        if text_data:
            try:
                data = json.loads(text_data)
            except Exception as e:
                self.error_to_front({'detail': _('JSON has invalid format'), 'type': str(type(e))})
                return

            if data['type'] != 'message':
                self.error_to_front({'detail': _('Invalid type %s').format(data['type']), 'type': 'BadRequest'})
                return
            serializer = MessageSerializer(data=data['data'], context={'user': self.user})
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

    def object_update(self, event):
        self.send(text_data=json.dumps({'object': event['object'], 'data': event['data']}))
