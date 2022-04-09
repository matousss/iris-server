import uuid

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

# Create your models here.
from django.db.models import CharField, EmailField, Model, OneToOneField, IntegerField, DateTimeField, UUIDField


class IrisUser(AbstractUser):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    email = EmailField(unique=True)

    REQUIRED_FIELDS = [
        'email'
    ]


class AccountActivation(Model):
    user = OneToOneField(IrisUser, on_delete=models.CASCADE, parent_link=False, unique=True)
    activation_code = CharField(max_length=256, blank=False)
    expiration = DateTimeField(default=None)

    def save(self, **kwargs):
        if self.activation_code is not None:
            self.activation_code = make_password(self.activation_code)
        super(AccountActivation, self).save(**kwargs)
