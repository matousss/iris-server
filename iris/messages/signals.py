from typing import Type
from uuid import UUID

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import Settings
from django.conf.global_settings import AUTH_USER_MODEL
from django.db.models import Model
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from rest_framework.serializers import Serializer

from .models import Channel, DirectChannel, Message, GroupChannel
from .serializers import MessageSerializer, DirectChannelSerializer, GroupChannelSerializer


# @receiver(post_save, sender=Message)
# def message_update(sender, instance: Message, **kwargs):
#     channel_layer = get_channel_layer()
#     data = MessageSerializer(instance).data
#     print('sedm')
#     for k in data.keys():
#         if isinstance(data[k], UUID):
#             data[k] = str(data[k])
#     print(data)
#     async_to_sync(channel_layer.group_send)(
#         str(instance.channel_id),
#         {
#             'type': 'updated.message',  # 'type': 'updated.message',
#             'message': data,
#         }
#     )

def object_update(sender, instance, serializer_class, get_listeners, **kwargs):
    channel_layer = get_channel_layer()
    data = serializer_class(instance).data
    for k in data.keys():
        if isinstance(data[k], UUID):
            data[k] = str(data[k])
    print(data),
    channel = str(get_listeners(instance))
    print(channel)
    async_to_sync(channel_layer.group_send)(
        channel,
        {
            'type': 'object.update',
            'data': data,
            'object': sender.__name__,
        }
    )


def register_tracked_obj(sender: Type[Model], serializer_class, get_listeners):
    post_save.connect(lambda *args, **kwargs: object_update(*args, serializer_class=serializer_class,
                                                            get_listeners=get_listeners, **kwargs),
                      sender=sender)


def instance_pk(instance):
    return instance.pk


# also for deletion
register_tracked_obj(Message, MessageSerializer, lambda instance: instance.channel_id)
register_tracked_obj(DirectChannel, DirectChannelSerializer, instance_pk)
register_tracked_obj(GroupChannel, GroupChannelSerializer, instance_pk)


@receiver(m2m_changed, sender=Channel.users.through)
def user_relation_changed(*args, action, **kwargs):
    if action == 'post_add':
        print('added')
    elif action == 'post_remove':
        print('post_remove')
    else:
        return
    print(args)
    print(kwargs)
