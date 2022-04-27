# direct channel can have only 2 persons
# in case it gets changed from inside or user is being deleted
# delete also direct channel
from uuid import UUID
import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Channel, DirectChannel, Message
from .serializers import MessageSerializer


@receiver(post_save, sender=Message)
def message_update(_, instance: Message, **kwargs):
    channel_layer = get_channel_layer()
    data = MessageSerializer(instance).data
    for k in data.keys():
        if isinstance(data[k], UUID):
            data[k] = str(data[k])

    async_to_sync(channel_layer.group_send)(
        str(instance.channel_id),
        {
            'type': 'updated.message',  # 'type': 'updated.message',
            'message': json.dumps(data),
        }
    )
