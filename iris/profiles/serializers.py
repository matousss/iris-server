from rest_framework.fields import FileField, CharField, UUIDField, ImageField
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer, Serializer
from .models import Profile


class ProfileSerializer(ModelSerializer):
    id = UUIDField(source='user.pk')
    username = CharField(source='user.username')
    email = CharField(source='user.email')

    class Meta:
        model = Profile
        exclude = ['user']


class AvatarUpdateSerializer(Serializer):
    avatar = ImageField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class ProfileMiniatureSerializer(ModelSerializer):
    id = UUIDField(source='user.pk')
    username = CharField(source='user.username')

    class Meta:
        model = Profile
        fields = ('id', 'username', 'avatar')
