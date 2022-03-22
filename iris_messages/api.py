from django.core.exceptions import BadRequest
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.generics import GenericAPIView, ListAPIView


from .serializers import ChannelSerializer


class ChannelAPIView(GenericAPIView):
    serializer_class = ChannelSerializer

    # get channel
    def get(self, request, *args, channel_id=None, **kwargs):
        if not channel_id:
            raise ValidationError(detail={'channel_id': 'required'})
        pass

    # channel creation
    def post(self, request, *args, **kwargs):
        pass

    # add user or leave channel
    # check perms for adding
    def patch(self, request, *args, **kwargs):
        pass


class GetChannelsAPI(ListAPIView):
    # return all channels user can view
    def get(self, request, *args, **kwargs):
        pass
