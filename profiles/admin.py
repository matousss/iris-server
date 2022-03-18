from django.contrib.admin import site

from .models import Profile

register = site.register

# Register your models here.
register(Profile)