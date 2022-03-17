from django.db.models import Model, UUIDField, ForeignKey, TextField, FileField, DateTimeField, \
    ManyToManyField, SET_NULL, CASCADE
from django.conf import settings


class Message(Model):
    id = UUIDField(primary_key=True)
    author = ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=SET_NULL)
    creation = DateTimeField(blank=False, null=False, auto_now_add=True)

    class Meta:
        abstract = True


class TextMessage(Message):
    text = TextField(null=False, blank=False)


def file_path(instance, file):
    return f'media/{instance.id}/{file}'


class MediaMessage(Message):
    author = ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=SET_NULL, related_name='media_message_author')
    text = TextField(null=True, blank=False)
    media = FileField(upload_to=file_path)


class Channel(Model):
    id = UUIDField(primary_key=True)
    users = ManyToManyField(settings.AUTH_USER_MODEL, blank=False, related_name='channel_users')

    class Meta:
        abstract = True


class DirectChannel(Channel):
    users = ManyToManyField(settings.AUTH_USER_MODEL, blank=False, max_length=2, related_name='user2user')
    pass


class GroupChannel(Channel):
    owner = ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=False, on_delete=CASCADE, related_name='owner')
    admins = ManyToManyField(settings.AUTH_USER_MODEL, related_name='admins')
