from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, Serializer

from .models import Channel, DirectChannel, GroupChannel, Message


class DirectChannelSerializer(ModelSerializer):
    class Meta:
        model = DirectChannel
        fields = ('id', 'users')

    def validate(self, attrs):
        if len(DirectChannel.objects.filter(users__in=attrs['users'])) > 0:
            raise ValidationError(detail='Channel already exist', code='duplicate_request')

        return super().validate(attrs)
class GroupChannelSerializer(ModelSerializer):
    class Meta:
        model = GroupChannel
        fields = ('id', 'name', 'users', 'owner', 'admins')


class ChannelSerializer(ModelSerializer):
    class Meta:
        model = Channel
        fields = ('id', 'users')


class AllChannelSerializer(ModelSerializer):
    CHANNEL_TYPES = {'directchannel': DirectChannelSerializer,
                     'groupchannel': GroupChannelSerializer}

    def to_representation(self,
                          instance  # type: Channel
                          ):
        data = None

        for t in AllChannelSerializer.CHANNEL_TYPES.keys():
            if hasattr(instance, t):
                o = instance.__getattribute__(t)
                data = AllChannelSerializer.CHANNEL_TYPES[t](o).data
                try:
                    last_message = \
                        MessageSerializer(Message.objects.filter(channel__exact=instance).latest('creation')).data
                except Message.DoesNotExist:
                    last_message = None
                data['last_message'] = last_message
                data['type'] = t
                return data

        raise Exception("Invalid object type " + str(type(instance)))

    class Meta:
        fields = '__all__'


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'text', 'creation')
