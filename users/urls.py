import knox.urls
import knox.views
from django.urls import path, include

from .api import RegisterAPI, UserAPIView
from .views import LoginView

api_urls = [
    path('', include('knox.urls')),
    path('register', RegisterAPI.as_view()),
    path('user', UserAPIView.as_view()),
]

urlpatterns = [
    path('api/auth/', include(api_urls))
]
