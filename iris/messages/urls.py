import glob
import imghdr
import os
from mimetypes import guess_type

from django.conf import settings
from django.contrib.auth import authenticate
from django.http import FileResponse, HttpResponseNotFound, HttpResponseForbidden, Http404
from django.urls import re_path, path, include
from rest_framework.generics import RetrieveAPIView, GenericAPIView
from rest_framework.routers import DefaultRouter

from .consumers import MessageConsumer

from .api import ChannelViewSet, MessageViewSet, ViewedChannelAPI

router = DefaultRouter()
router.register(r'channel', ChannelViewSet, basename='channel')
router.register(r'message', MessageViewSet, basename='message')
router.register(r'message', MessageViewSet, basename='message')


urlpatterns = [
    # path('media/<str:channel_id>/<str:message_id>/<str:file>', GetMedia.as_view()),
    # path('api/channel/<uuid:channel_id>', ChannelAPIView.as_view()),
    # path('api/channel', GetChannelsAPI.as_view()),
    path('api/', include(router.urls)),
    path(r'api/viewed-channel/<uuid:channel_id>', ViewedChannelAPI.as_view(), name='viewed-channel'),
]

ws_urlpatterns = [
    # re_path(r'^ws/client/(?P<room_id>[^/]+)/$', ClientConsumer.as_asgi()),
    re_path(r'ws/messages', MessageConsumer.as_asgi())
]
