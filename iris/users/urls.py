import knox.urls
import knox.views
from django.urls import path, include

from .api import RegisterAPI, UserAPIView, AccountActivationAPI, LoginAPI, TokenCheckAPI, PasswordChangeAPI, LogoutAllView

api_urls = [
    path('', include('knox.urls')),
    path('register', RegisterAPI.as_view()),
    path('login', LoginAPI.as_view()),
    path('user', UserAPIView.as_view()),
    path('activate', AccountActivationAPI.as_view()),
    path('check', TokenCheckAPI.as_view()),
    path('changepassword', PasswordChangeAPI.as_view()),
    path('logoutall', LogoutAllView.as_view()),

]

urlpatterns = [
    path('api/auth/', include(api_urls))
]
