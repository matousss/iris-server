from django.urls import re_path, path, include
from rest_framework.routers import DefaultRouter

from .consumers import MessageConsumer

from .api import ChannelViewSet, MessageViewSet, ViewedChannelAPI

router = DefaultRouter()
router.register(r'channel', ChannelViewSet, basename='channel')
router.register(r'message', MessageViewSet, basename='message')
router.register(r'message', MessageViewSet, basename='message')


urlpatterns = [
    path('api/', include(router.urls)),
    path(r'api/viewed-channel/<uuid:channel_id>', ViewedChannelAPI.as_view(), name='viewed-channel'),
]

ws_urlpatterns = [
    re_path(r'ws/messages', MessageConsumer.as_asgi())
]
