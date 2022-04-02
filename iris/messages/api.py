from uuid import UUID

from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import ModelViewSet

from .models import Channel, Message
from .serializers import MessageSerializer, AllChannelSerializer


class ChannelViewSet(ModelViewSet):
    serializer_class = AllChannelSerializer
    queryset = Channel.objects.all()

    # get channel
    # def get(self, request, *args, channel_id, **kwargs):
    #     if not channel_id:
    #         raise ValidationError(detail={'channel_id': 'required'})
    #     channel = Channel.objects.get(id=channel_id)
    #     serializer = self.get_serializer(channel)
    #     return Response(serializer.data)

    @staticmethod
    def select_serializer(name):
        if name not in AllChannelSerializer.CHANNEL_TYPES.keys():
            raise ValidationError(detail='Invalid channel type', code='invalid_channel_type')
        return AllChannelSerializer.CHANNEL_TYPES[name]

    def filter_queryset(self, queryset):
        return queryset.filter(users__exact=self.request.user)

    # channel creation
    def create(self, request, *args, **kwargs):
        try:
            serializer_type = self.select_serializer(request.data['type'])  # type: ModelSerializer.__class__
        except KeyError:
            raise ValidationError()
        data = request.data.copy()
        # if data['type'] == 'directchannel':
        #     if str(request.user.id) not in data.getlist('users'):
        #         users_list = data.getlist('users')
        #         users_list.append(str(request.user.id))
        #         data.setlist('users', users_list)

        serializer = serializer_type(data=data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        channel = serializer.create(serializer.validated_data)
        channel.save()
        return Response(
            serializer_type(channel).data,
            status=HTTP_201_CREATED,
            headers=self.get_success_headers(serializer_type(channel, context=self.get_serializer_context()))
        )

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
    permission_classes = [HasChannelPermission]

    def get_queryset(self):
        return Message.objects.filter(channel__in=Channel.objects.filter(users__exact=self.request.user))

    def filter_queryset(self, queryset):
        try:
            channel_id = UUID(self.request.GET['channel'])
        except MultiValueDictKeyError:
            # raise ValidationError(detail={'channel_id': 'required'})
            return queryset
        except ValueError:
            raise ValidationError(detail={'channel': 'invalid'})
        return queryset.filter(channel__exact=channel_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)
