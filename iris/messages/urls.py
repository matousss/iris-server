from django.http import FileResponse
from django.urls import re_path, path, include
from rest_framework.routers import DefaultRouter

from .views import GetMedia
from .api import ChannelViewSet, MessageViewSet

websockets_patterns = [
    # re_path(r'^ws/client/(?P<room_id>[^/]+)/$', ClientConsumer.as_asgi()),
]

router = DefaultRouter()
router.register(r'channel', ChannelViewSet, basename='channel')
router.register(r'message', MessageViewSet, basename='message')
router.register(r'message', MessageViewSet, basename='message')

urlpatterns = [
     path('media/<str:channel_id>/<str:message_id>/<str:file>', GetMedia.as_view()),
     # path('api/channel/<uuid:channel_id>', ChannelAPIView.as_view()),
     # path('api/channel', GetChannelsAPI.as_view()),
     path('api/', include(router.urls))
]

