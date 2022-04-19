from rest_framework.fields import FileField, CharField
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer, Serializer
from .models import Profile


class ProfileSerializer(ModelSerializer):
    username = CharField(source='user.username')
    class Meta:
        model = Profile
        fields = '__all__'


class AvatarUpdateSerializer(Serializer):
    avatar = FileField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class ProfileMiniatureSerializer(ModelSerializer):
    username = CharField(source='user.username')

    class Meta:
        model = Profile
        fields = ('user', 'username', 'avatar')
