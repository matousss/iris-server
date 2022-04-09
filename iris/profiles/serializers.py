from rest_framework.fields import FileField
from rest_framework.serializers import ModelSerializer, Serializer
from .models import Profile


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class AvatarUpdateSerializer(Serializer):
    avatar = FileField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
