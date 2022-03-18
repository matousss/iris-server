from uuid import uuid4
from django.db.models import Model, UUIDField, ForeignKey, TextField, FileField, DateTimeField, \
    ManyToManyField, SET_NULL, CASCADE, OneToOneField
from django.conf import settings


class Channel(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    users = ManyToManyField(settings.AUTH_USER_MODEL, blank=False, related_name='channel_users')


class DirectChannel(Channel):
    pass


class GroupChannel(Channel):
    owner = ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=False, on_delete=CASCADE, related_name='owner')
    admins = ManyToManyField(settings.AUTH_USER_MODEL, related_name='admins')


class Message(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    author = ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=SET_NULL)
    creation = DateTimeField(blank=False, null=False, auto_now_add=True)
    channel = ForeignKey('iris_messages.Channel', blank=False, null=False, on_delete=CASCADE)

    class Meta:
        abstract = True


class TextMessage(Message):
    text = TextField(null=False, blank=False)


def file_path(instance, file):
    return f'media/{instance.channel.id}/{instance.id}/{file}'


class MediaMessage(Message):
    author = ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=SET_NULL, related_name='media_message_author')
    text = TextField(null=True, blank=False)
    media = FileField(upload_to=file_path)


class FriendShip(Model):
    id = OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, on_delete=CASCADE, related_name='user')
    friends = ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='friends')
