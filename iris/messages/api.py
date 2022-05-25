from uuid import UUID

from django.http import Http404
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import mixins
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .models import Channel, Message
from .serializers import MessageSerializer, AllChannelSerializer, DateTimeSerializer


class ChannelViewSet(ModelViewSet):
    serializer_class = AllChannelSerializer
    queryset = Channel.objects.all()

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
            raise ValidationError('Invalid channel type')
        data = request.data.copy()

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
    # def patch(self, request, *args, **kwargs):
    #     return MethodNotAllowed(method='PATCH')
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if hasattr(instance, 'groupchannel'):
            user = request.user
            if not user == instance.groupchannel.owner and user not in instance.groupchannel.admins.all():
                raise PermissionDenied()
        self.perform_destroy(instance)
        return Response(status=HTTP_204_NO_CONTENT)


class MessageViewSet(mixins.CreateModelMixin,
                     # mixins.RetrieveModelMixin, # asi není potřeba
                     # mixins.UpdateModelMixin, #todo editování zpráv
                     # mixins.DestroyModelMixin, #todo mazání zpráv
                     mixins.ListModelMixin,
                     GenericViewSet):
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(
            channel__in=Channel.objects.filter(users__exact=self.request.user)
        ).order_by('-creation')

    def filter_queryset(self, queryset):
        try:
            channel_id = UUID(self.request.GET['channel_id'])
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


class ViewedChannelAPI(GenericAPIView):
    def patch(self, request, *, channel_id):
        try:
            channel = Channel.objects.get(id__exact=channel_id)  # type: Channel
        except Channel.DoesNotExist:
            raise Http404()

        # just to make sure it's possible to safely retrieve back datetime form
        dt_serializer = DateTimeSerializer(data={'datetime': timezone.now()})
        dt_serializer.is_valid(True)
        channel.last_open_by[str(request.user.id)] = dt_serializer.data['datetime']
        channel.save()

        return Response()
