from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import Serializer, CharField, ModelSerializer

from .models import IrisUser


class UserSerializer(ModelSerializer):
    class Meta:
        model = IrisUser
        fields = ('id', 'username', 'email')


class RegisterSerializer(ModelSerializer):
    class Meta:
        model = IrisUser
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        print(validated_data['password'])
        user = IrisUser.objects.create_user(validated_data['username'],
                                            validated_data['email'],
                                            validated_data['password'])
        return user


class LoginSerializer(Serializer):
    username = CharField()
    password = CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise ValidationError('Password or Username is invalid')
