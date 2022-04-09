import os

from django.http import FileResponse, HttpResponseNotFound
from django.urls import path, include
from knox import settings
from rest_framework.routers import DefaultRouter

from .models import Profile
from .views import ProfileViewAPI, AvatarUpdateAPI

router = DefaultRouter()
router.register(r'profile', ProfileViewAPI, basename='profile')


# def get_media(request, fpath):
#     p = os.path.join(os.path.realpath(settings.MEDIA_DIR), fpath)
#     if os.path.exists(p):
#         return FileResponse(open(p, 'rb'), content_type='image/' + fpath.split('.')[-1])
#
#     return HttpResponseNotFound()
# re_path('media/(?P<fpath>.*)', get_media),


def get_avatar(request, user_id):
    try:
        profile = Profile.objects.get(user_id__exact=user_id)
    except Profile.DoesNotExist:
        return HttpResponseNotFound()
    if profile.avatar:
        try:
            return FileResponse(profile.avatar.open('rb'), content_type='image/png')
        except FileNotFoundError:
            pass
    return HttpResponseNotFound()


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/avatar', AvatarUpdateAPI.as_view()),
    path('media/users/<uuid:user_id>/avatar', get_avatar)
]
