import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import OneToOneField, Model, ManyToManyField, FileField, CASCADE


def avatar_file_path(instance, file):
    s = file.split(".")
    return fr'{settings.MEDIA_DIR}\users\{instance.user.id}\avatar' + (('.' + s[-1]) if len(s) > 1 else "")


class Profile(Model):
    user = OneToOneField(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='user', primary_key=True)
    friends = ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='friends', validators=[])
    avatar = FileField(default=None, blank=True, null=True, upload_to=avatar_file_path)

    def __str__(self):
        return self.user.username

    # todo make this work
    def validate_friends(self, value):
        if self.user in value:
            raise ValidationError('Sorry you can\'t add yourself to friends. You\'re not alone. '
                                  'Just go outside and find some friends. I beleive in you.')
