from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Model, UUIDField, ForeignKey, TextField, DateTimeField, \
    ManyToManyField, SET_NULL, CASCADE, BooleanField


class Channel(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    users = ManyToManyField(settings.AUTH_USER_MODEL, blank=False, related_name='channel_users')


class DirectChannel(Channel):
    pass


class GroupChannel(Channel):
    name = TextField(max_length=256, blank=False, null=True)
    owner = ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=False, on_delete=CASCADE, related_name='owner')
    admins = ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='admins')

    def __str__(self):
        return self.name


def media_file_path(instance, file):
    return f'{settings.MEDIA_DIR}/messages/{instance.channel.id}/{instance.id}/{file}'


class Message(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    author = ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=SET_NULL)
    creation = DateTimeField(blank=False, null=False, auto_now_add=True, editable=False)
    channel = ForeignKey('iris_messages.Channel', blank=False, null=False, on_delete=CASCADE)
    text = TextField(null=True, blank=False)
    media = BooleanField(default=False, null=False, blank=False)

    def clean(self):
        if self.text is None and self.media is False:
            raise ValidationError('text and media can\'t be None and False at same time')
        super().clean()
