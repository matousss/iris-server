import pytz
from django.contrib.auth import authenticate
from django.utils.datetime_safe import datetime
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import Serializer, CharField, ModelSerializer

from .models import IrisUser, AccountActivation


class UserSerializer(ModelSerializer):
    class Meta:
        model = IrisUser
        fields = ('username', 'email')


class RegisterSerializer(ModelSerializer):
    class Meta:
        model = IrisUser
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = IrisUser.objects.create_user(
            validated_data['username'],
            validated_data['email'],
            validated_data['password'],
            is_active=False
        )
        return user


class LoginSerializer(Serializer):

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    username = CharField()
    password = CharField()

    def validate(self, data):
        user = authenticate(**data)

        result = 'unknown_error'
        valid = False
        if not user:
            result = 'invalid_user'
            entry = IrisUser.objects.get(username=data['username'])
            if entry and not entry.is_active:
                result = 'inactive_user'
                user = entry
        else:
            result = 'success'
            valid = True

        return (valid,
                {
                    'result': result,
                    'user': user,
                }
                )
        # raise ValidationError('Password or Username is invalid')

# todo user from token activate
class ActivationSerializer(Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    username = CharField()
    activation_code = CharField()

    def validate(self, data):
        try:
            user = IrisUser.objects.get(username=data['username'])
        except IrisUser.DoesNotExist:
            user = None
        success = False
        if not user:
            result = 'invalid_user'
        else:
            activation = AccountActivation.objects.get(user=user)

            if not activation:
                result = 'no_pending_activation'

            elif not activation.expiration or activation.expiration < datetime.now(tz=pytz.UTC):
                result = 'expired_code'

            elif data['activation_code'] == activation.activation_code:
                result = 'success'
                success = True

            else:
                result = 'invalid_code'
        return (success,
                {
                    'result': result,
                    'user': user,
                }
                )
