from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


# Create your models here.
from django.db.models import CharField, EmailField


class IrisUser(AbstractUser):
    email = EmailField(unique=True)

    REQUIRED_FIELDS = [
        'email'
    ]
    pass


