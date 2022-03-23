from django.core.exceptions import BadRequest
from django.http import HttpResponse
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Channel, Message, TextMessage
from .serializers import ChannelSerializer, MessageSerializer


class ChannelViewSet(ModelViewSet):
    serializer_class = ChannelSerializer
    queryset = Channel.objects.all()

    # get channel
    # def get(self, request, *args, channel_id, **kwargs):
    #     if not channel_id:
    #         raise ValidationError(detail={'channel_id': 'required'})
    #     channel = Channel.objects.get(id=channel_id)
    #     serializer = self.get_serializer(channel)
    #     return Response(serializer.data)

    def filter_queryset(self, queryset):
        return queryset.filter(users__exact=self.request.user)

    # channel creation
    def post(self, request, *args, **kwargs):
        pass

    # add user or leave channel
    # check perms for adding
    def patch(self, request, *args, **kwargs):
        pass


#
# class GetChannelsAPI(ListAPIView):
#     # return all channels user can view
#     serializer_class = ChannelSerializer
#     queryset = Channel.objects.all()


class MessageViewSet(ModelViewSet):
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(channel__in=Channel.objects.filter(users__exact=self.request.user))

    def filter_queryset(self, queryset):
        return queryset.filter(channel__exect=self.kwargs['channel_id'])
