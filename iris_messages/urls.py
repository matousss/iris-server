from django.http import FileResponse
from django.urls import re_path, path

from .views import GetMedia
from .api import ChannelAPIView

websockets_patterns = [
    # re_path(r'^ws/client/(?P<room_id>[^/]+)/$', ClientConsumer.as_asgi()),
]



urlpatterns = [
     path('media/<str:channel_id>/<str:message_id>/<str:file>', GetMedia.as_view()),
     path('api/channel/', ChannelAPIView.as_view()),
]

