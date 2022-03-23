from django.contrib import admin

from .models import IrisUser, AccountActivation
register = admin.site.register

register(IrisUser)
register(AccountActivation)
