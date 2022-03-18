from django.conf import settings
from django.db.models import OneToOneField, Model, ManyToManyField, FileField, CASCADE


def avatar_file_path(instance, file):
    return f'{settings.MEDIA_DIR}/users/{instance.id}/avatar.{file.split(".")[-1]}'


class Profile(Model):
    user = OneToOneField(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='user')
    friends = ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='friends')
    avatar = FileField(default=None, blank=False, null=True, upload_to=avatar_file_path)

