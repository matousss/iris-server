from typing import Type
from uuid import UUID

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Model
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from .models import Channel, DirectChannel, Message, GroupChannel
from .serializers import MessageSerializer, DirectChannelSerializer, GroupChannelSerializer, AllChannelSerializer


def object_update(sender, instance, serializer_class, get_listeners, created, *args, **kwargs):
    channel_layer = get_channel_layer()
    data = serializer_class(instance).data
    for k in data.keys():
        if isinstance(data[k], UUID):
            data[k] = str(data[k])
        if isinstance(data[k], list):
            for i in range(len(data[k])):
                if isinstance(data[k][i], UUID):
                    data[k][i] = str(data[k][i])

    print(args)
    print(kwargs)

    channel = str(get_listeners(instance))
    async_to_sync(channel_layer.group_send)(
        channel,
        {
            'type': 'object.' + ('created' if created else 'update'),
            'data': data,
            'object': sender.__name__,
        }
    )


def register_tracked_obj(sender: Type[Model], serializer_class, get_listeners):
    post_save.connect(lambda *args, **kwargs: object_update(*args, serializer_class=serializer_class,
                                                            get_listeners=get_listeners, **kwargs),
                      sender=sender)


def instance_pk(instance):
    print(instance)
    return instance.pk


# also for deletion
register_tracked_obj(Message, MessageSerializer, lambda instance: instance.channel_id)
register_tracked_obj(Channel, AllChannelSerializer, instance_pk)
register_tracked_obj(DirectChannel, DirectChannelSerializer, instance_pk)
register_tracked_obj(GroupChannel, GroupChannelSerializer, instance_pk)



@receiver(m2m_changed, sender=Channel.users.through)
def user_relation_changed(*args, action, **kwargs):
    if action == 'post_add':
        # print('added')
        pass
    elif action == 'post_remove':
        # print('post_remove')
        pass
    else:
        return

