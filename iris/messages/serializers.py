from rest_framework.serializers import ModelSerializer, Serializer

from .models import Channel, DirectChannel, GroupChannel, Message


class ChannelSerializer(ModelSerializer):
    class Meta:
        model = Channel
        fields = ('id', 'users')


class DirectChannelSerializer(ModelSerializer):
    class Meta:
        model = DirectChannel
        fields = ('id', 'users')


class GroupChannelSerializer(ModelSerializer):
    class Meta:
        model = GroupChannel
        fields = ('id', 'name', 'users', 'owner', 'admins')


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'text')
