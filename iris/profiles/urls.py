from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProfileViewAPI

router = DefaultRouter()
router.register(r'profile', ProfileViewAPI, basename='profile')

urlpatterns = [
    path('api/', include(router.urls))
]
