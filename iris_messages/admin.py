from django.contrib import admin
from .models import TextMessage, MediaMessage, GroupChannel, DirectChannel

register = admin.site.register
# Register your models here.
register(TextMessage)
register(MediaMessage)
register(GroupChannel)
register(DirectChannel)
