from django.contrib import admin

from .models import IrisUser, AccountActivation
# Register your models here.
admin.site.register(IrisUser)
admin.site.register(AccountActivation)