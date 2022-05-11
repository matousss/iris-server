from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Message, GroupChannel, DirectChannel

register = admin.site.register


# Register your models here.

class GroupChannelAdmin(ModelAdmin):
    list_display = ['id', 'name']
    readonly_fields = ['last_open_by']


class DirectChannelAdmin(ModelAdmin):
    list_display = ['id']
    readonly_fields = ['last_open_by']


class MessageAdmin(ModelAdmin):
    list_display = ['id', 'text', 'media', 'creation']
    readonly_fields = ['creation']


register(Message, MessageAdmin)
register(GroupChannel, GroupChannelAdmin)
register(DirectChannel, DirectChannelAdmin)
