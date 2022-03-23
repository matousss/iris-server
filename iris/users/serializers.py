import pytz
from django.contrib.auth import authenticate
from django.utils.datetime_safe import datetime
from rest_framework.exceptions import ValidationError, APIException, NotAcceptable, AuthenticationFailed
from rest_framework.serializers import Serializer, CharField, ModelSerializer
from rest_framework.status import HTTP_204_NO_CONTENT

from .models import IrisUser, AccountActivation
from ..exceptions import NoContentException


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
        if not user:
            entry = IrisUser.objects.get(username=data['username'])
            if entry and not entry.is_active:
                raise APIException(detail='User not found', code='user_not_found')
            raise AuthenticationFailed(detail={'details': 'invalid_user'})

        return (True, user)
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
            raise NotAcceptable(detail={'user': 'not_found'})
        success = False
        ###
        # Test pozornosti:
        #   otevřete: https://docs.google.com/forms/d/1yRFpxVO_MCHfLbWnaoeWMDehMHMvRQc3dok562nNT8M
        #   a do odpovědi dejte "Ne"
        # ###
        try:
            activation = AccountActivation.objects.get(user=user)
        except AccountActivation.DoesNotExist:
            raise NotAcceptable(detail={'details': 'no_pending_activation'})

        if activation.expiration and activation.expiration < datetime.now(tz=pytz.UTC):
            raise NoContentException(detail={'details': 'expired_code'}, code='expired_code')

        if data['activation_code'] == activation.activation_code:
            return True, user

        raise ValidationError(detail='Invalid activation code', code='invalid_code')
