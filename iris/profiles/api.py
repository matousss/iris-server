import imghdr
import os.path
from os import path, makedirs, remove

from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.filters import SearchFilter
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from .models import Profile
from .serializers import ProfileSerializer, AvatarUpdateSerializer, ProfileMiniatureSerializer

TEMP_DIR = path.join(os.path.realpath(settings.MEDIA_DIR), 'temp')

if not path.exists(TEMP_DIR):
    makedirs(TEMP_DIR)


class AbstractProfileViewAPI(RetrieveModelMixin, GenericViewSet, ListModelMixin):
    queryset = Profile.objects.all()
    filter_backends = [SearchFilter]
    search_fields = ['user__username', 'user__email']

    def get_object(self):
        if (self.kwargs['pk'] == 'current') and self.request.user:
            return self.get_queryset().get(user=self.request.user)
        return super(AbstractProfileViewAPI, self).get_object()


class ProfileViewAPI(AbstractProfileViewAPI):
    serializer_class = ProfileSerializer


class MiniProfileViewAPI(AbstractProfileViewAPI):
    serializer_class = ProfileMiniatureSerializer


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
            makedirs(p)
        p = path.join(p, 'avatar')

        # todo select area
        with Image.open(temp_path) as im:  # type: Image.Image
            im.resize((512, 512)).save(p + '.png', 'PNG')
        remove(temp_path)

        profile = Profile.objects.get(user__exact=request.user)
        profile.avatar = path.join('media', relative, 'avatar.png')
        profile.save()
        return Response(status=200)
