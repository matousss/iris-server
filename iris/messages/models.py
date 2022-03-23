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
    name = TextField(max_length=256, blank=False, null=True)
    owner = ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=False, on_delete=CASCADE, related_name='owner')
    admins = ManyToManyField(settings.AUTH_USER_MODEL, related_name='admins')


class Message(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    author = ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=SET_NULL)
    creation = DateTimeField(blank=False, null=False, auto_now_add=True)
    channel = ForeignKey('iris_messages.Channel', blank=False, null=False, on_delete=CASCADE)


class TextMessage(Message):
    text = TextField(null=True, blank=False)


def media_file_path(instance, file):
    return f'{settings.MEDIA_DIR}/messages/{instance.channel.id}/{instance.id}/{file}'


class MediaMessage(TextMessage):
    media = FileField(upload_to=media_file_path)
