import imghdr
import os.path
from os import path, mkdir, rename, remove

from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import render

# Create your views here.
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from .models import Profile
from .serializers import ProfileSerializer, AvatarUpdateSerializer

TEMP_DIR = path.join(os.path.realpath(settings.MEDIA_DIR), 'temp')

if not path.exists(TEMP_DIR):
    mkdir(TEMP_DIR)


class ProfileViewAPI(RetrieveModelMixin, GenericViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class AvatarUpdateAPI(GenericAPIView):
    serializer_class = AvatarUpdateSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)  # type: AvatarUpdateSerializer
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data['avatar']  # type: InMemoryUploadedFile

        temp_path = os.path.join(TEMP_DIR, 'avatar_' + str(request.user.id))

        with open(temp_path, 'wb') as w:
            w.write(file.read())
        # https://www.blog.pythonlibrary.org/2020/02/09/how-to-check-if-a-file-is-a-valid-image-with-python/
        ext = imghdr.what(temp_path)
        # if ext:
        #     rename(p, f'{p}.{ext}')
        if not ext:
            remove(temp_path)
            return Response(status=415)

        relative = path.join('users', str(request.user.id))
        p = path.join(path.realpath(settings.MEDIA_DIR), relative)
        if not path.exists(p):
            mkdir(p)
        p = path.join(p, 'avatar')

        # todo select area
        with Image.open(temp_path) as im:  # type: Image.Image
            im.resize((512, 512)).save(p, 'PNG')
        remove(temp_path)

        profile = Profile.objects.get(user__exact=request.user)
        profile.avatar = path.join('media', relative, 'avatar')
        profile.save()
        return Response(status=204)
