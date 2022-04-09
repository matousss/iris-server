from django.shortcuts import render

# Create your views here.
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from .models import Profile
from .serializers import ProfileSerializer


class ProfileViewAPI(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def update(self, request, *args, **kwargs):
        print(request)
        super(ProfileViewAPI, self).update(request, *args, **kwargs)

    pass
