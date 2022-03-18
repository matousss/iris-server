import mimetypes
import os.path

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponseNotFound, HttpResponseForbidden
from django.contrib.auth import authenticate
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from users.models import IrisUser

from .models import Channel


class GetMedia(GenericAPIView):
    # authentication_classes = ()
    # permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        user: IrisUser
        user = authenticate(request)
        try:
            channel = Channel.objects.get(id=kwargs['channel_id'])
        except Channel.DoesNotExist:
            raise Http404(request)
        if not channel.users.contains(user):
            return HttpResponseForbidden()

        p = settings.BASE_DIR.joinpath(f'{settings.MEDIA_DIR}/' + '/'.join(kwargs.values()))
        if os.path.exists(p):
            return FileResponse(open(p, 'rb'), content_type=mimetypes.guess_type(kwargs['file'])[0])

        return HttpResponseNotFound()
