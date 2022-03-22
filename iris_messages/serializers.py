from rest_framework.serializers import ModelSerializer, Serializer

from .models import Channel, DirectChannel, GroupChannel


class ChannelSerializer(ModelSerializer):
    class Meta:
        model = DirectChannel
        fields = ('id', 'users')


class DirectChannelSerializer(ModelSerializer):
    class Meta:
        model = DirectChannel
        fields = ('id', 'users')


class GroupChannelSerializer(ModelSerializer):
    class Meta:
        model = GroupChannel
        fields = ('id', 'users', 'owner', 'admins')


class GetChannelsSerializer(Serializer):

    # we don't need to mass update all channels
    def update(self, instance, validated_data):
        # return [Channel.objects.create(**e) for e in validated_data]
        pass

    def create(self, validated_data):
        pass

