from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


# Create your models here.
from django.db.models import CharField, EmailField, Model, OneToOneField, IntegerField, DateTimeField


class IrisUser(AbstractUser):
    email = EmailField(unique=True)

    REQUIRED_FIELDS = [
        'email'
    ]
    pass


class AccountActivation(Model):
    user = OneToOneField(IrisUser, on_delete=models.CASCADE, parent_link=False, unique=True)
    activation_code = CharField(max_length=8, blank=False)
    expiration = DateTimeField(default=None)

