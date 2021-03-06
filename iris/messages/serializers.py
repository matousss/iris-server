from rest_framework.exceptions import ValidationError, PermissionDenied, APIException
from rest_framework.fields import DateTimeField
from rest_framework.serializers import ModelSerializer, Serializer

from .models import Channel, DirectChannel, GroupChannel, Message


class DirectChannelSerializer(ModelSerializer):
    class Meta:
        model = DirectChannel
        fields = '__all__'
        read_only_fields = ('id',)

    def validate(self, attrs):
        r = super(DirectChannelSerializer, self).validate(attrs)
        user = self.context['request'].user
        if len(attrs['users']) != 1:
            raise ValidationError(detail={'users': 'This field requires one value'}, code='too_many_users')
        if user.id == attrs['users'][0].id:
            raise APIException(detail='Cannot message yourself', code='message_yourself')
        if len(DirectChannel.objects.filter(users__exact=attrs['users'][0].id).filter(users__exact=user.id)) > 0:
            e = APIException(detail='Channel already exist', code='duplicate_request')
            e.status_code = 406
            raise e
        return r

    def create(self, validated_data):
        validated_data['users'].append(self.context['request'].user)
        return super(DirectChannelSerializer, self).create(validated_data)


class GroupChannelSerializer(ModelSerializer):
    class Meta:
        model = GroupChannel
        fields = '__all__'
        read_only_fields = ('id', 'owner')

    def create(self, validated_data):
        user = self.context['request'].user
        admins = validated_data.pop('admins')
        users = validated_data.pop('users')
        o = GroupChannel.objects.create(owner=user, **validated_data)
        o.admins.set(admins)
        o.users.set(users)
        o.users.add(user)
        return o


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

        for t in AllChannelSerializer.CHANNEL_TYPES.keys():
            if hasattr(instance, t):
                o = instance.__getattribute__(t)
                data = AllChannelSerializer.CHANNEL_TYPES[t](o).data
                data['type'] = t
                return data

        raise TypeError("Object is missing supported child model")

    class Meta:
        fields = '__all__'


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'author', 'text', 'creation', 'media', 'channel')

    def create(self, validated_data):
        user = self.get_user()
        channel = validated_data['channel']  # type: Channel
        if user not in channel.users.all():
            raise PermissionDenied()
        return Message.objects.create(author=user, **validated_data)

    def get_user(self):
        try:
            return self.context['user']
        except KeyError:
            try:
                return self.context['request'].user
            except KeyError:
                raise ValidationError(detail='User not provided', code='no_user')

    def validate(self, attrs):
        def get_att(name):
            return attrs[name] if name in attrs.keys() else None

        if not get_att('text') and not get_att('media'):
            raise ValidationError(
                detail={'text': 'Text or media must be provided', 'media': 'Text or media must be provided'},
                code='no_text_or_media')

        r = super(MessageSerializer, self).validate(attrs)
        user = self.get_user()
        if user not in r['channel'].users.all():
            raise PermissionDenied()

        return r


class DateTimeSerializer(Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    datetime = DateTimeField()
