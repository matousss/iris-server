from typing import Type
from uuid import UUID

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Model
from django.db.models.signals import post_save, m2m_changed, post_delete
from django.dispatch import receiver

from .models import Channel, DirectChannel, Message, GroupChannel
from .serializers import MessageSerializer, DirectChannelSerializer, GroupChannelSerializer, AllChannelSerializer


def object_update(sender, instance, *args, serializer_class, get_listeners, created, **kwargs):
    channel_layer = get_channel_layer()
    try:
        data = serializer_class(instance).data
    except TypeError:
        return
    for k in data.keys():
        if isinstance(data[k], UUID):
            data[k] = str(data[k])
        if isinstance(data[k], list):
            for i in range(len(data[k])):
                if isinstance(data[k][i], UUID):
                    data[k][i] = str(data[k][i])

    listeners = get_listeners(instance)
    for channel in listeners:
        async_to_sync(channel_layer.group_send)(
            channel,
            {
                'type': 'object.update',
                'data': data,
                'object': sender.__name__,
                'created': created,
            }
        )


def object_deleted(sender, instance, *args, get_listeners, **kwargs):
    channel_layer = get_channel_layer()
    listeners = get_listeners(instance)
    for channel in listeners:
        async_to_sync(channel_layer.group_send)(
            channel,
            {
                'type': 'object.delete',
                'id': str(instance.pk),
                'object': sender.__name__,
            }
        )


def register_tracked_obj(sender: Type[Model], serializer_class, get_listeners):
    post_save.connect(lambda *args, **kwargs: object_update(*args, serializer_class=serializer_class,
                                                            get_listeners=get_listeners, **kwargs), sender=sender)
    post_delete.connect(lambda *args, **kwargs: object_deleted(*args, get_listeners=get_listeners, **kwargs),
                        sender=sender)


def instance_pk(instance):
    return [str(instance.pk)]


# also for deletion
register_tracked_obj(Message, MessageSerializer, lambda instance: [str(instance.channel_id)])
register_tracked_obj(Channel, AllChannelSerializer, instance_pk)
register_tracked_obj(DirectChannel, DirectChannelSerializer, instance_pk)
register_tracked_obj(GroupChannel, GroupChannelSerializer, instance_pk)


@receiver(m2m_changed, sender=Channel.users.through)
def user_relation_changed(*args, action, instance, pk_set, **kwargs):
    channel_layer = get_channel_layer()
    channel_id = str(instance.pk)
    if action == 'post_add':
        for pk in pk_set:
            async_to_sync(channel_layer.group_send)(
                str(pk),
                {
                    'type': 'add.channel',
                    'channel': channel_id,
                }
            )
        print(pk_set)
        object_update(instance.__class__, instance, serializer_class=AllChannelSerializer, get_listeners=lambda _: [str(pk) for pk in pk_set], created=True)

    elif action == 'post_remove':
        for pk in pk_set:
            async_to_sync(channel_layer.group_send)(
                str(pk),
                {
                    'type': 'remove.channel',
                    'channel': channel_id,
                }
            )
        pass
    else:
        return
