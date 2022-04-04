from datetime import timedelta
from os import getenv
from typing import Optional

import pytz
import random
import string

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.datetime_safe import datetime
from knox.models import AuthToken
from rest_framework.exceptions import ErrorDetail, APIException
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from .models import AccountActivation, IrisUser
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer, ActivationSerializer
from ..exceptions import NoContentException


# def validation_error_response(serializer: Serializer) -> Optional[Response]:
#     # noinspection PyBroadException
#     try:
#         serializer.is_valid(raise_exception=True)
#
#     except Exception:
#         error_dict = {}
#         for error in serializer.errors.keys():
#             error_detail: ErrorDetail
#             error_detail = serializer.errors[error][0]
#             error_dict[error] = error_detail.code
#         return Response({
#             'result': 'error',
#             'details': error_dict,
#         })
#     return None



def send_activation_email(user: IrisUser, activation: AccountActivation = None):
    if not activation:
        activation = AccountActivation.objects.get(user=user)
    context = {'activation_code': activation.activation_code}
    confirmation_mail = EmailMultiAlternatives(
        'Activate your account',
        # f'Your activation code is: {activation.activation_code}'
        get_template('email_code.txt').render(context),
        settings.EMAIL_HOST_USER,
        [user.email],
    )
    confirmation_mail.attach_alternative(get_template('email_code.html').render(context), 'text/html')
    confirmation_mail.send()





class RegisterAPI(GenericAPIView):
    serializer_class = RegisterSerializer

    authentication_classes = ()
    permission_classes = (AllowAny,)

    def post(self, request: Request, *args, **kwargs):
        serializer: RegisterSerializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.create(serializer.validated_data)

        activation_code = ''.join(random.choice(string.digits) for _ in range(6))
        expiration = datetime.now(tz=pytz.UTC) + timedelta(hours=12)
        activation, get = AccountActivation.objects.get_or_create(
            user=user,
            defaults={
                'activation_code': activation_code,
                'expiration': expiration,
            }
        )
        if get:
            activation.activation_code = activation_code
            activation.expiration = expiration

        user.save()

        activation.save()
        send_activation_email(user)
        # token = AuthToken.objects.create(user)

        return Response(
            {
                'user': UserSerializer(user, context=self.get_serializer_context()).data,
                # 'token': token[1]
            }
        )


class LoginAPI(GenericAPIView):
    serializer_class = LoginSerializer
    authentication_classes = ()
    permission_classes = (AllowAny,)

    ###
    # request: {username, password}
    # response:
    #   200: {user, token}
    #   204: User not found
    #   401: Invalid password
    # ###
    def post(self, request, *args, **kwargs):
        serializer: LoginSerializer
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except IrisUser.DoesNotExist:
            raise NoContentException(detail='User not found', code='user_not_found')

        success, user = serializer.validated_data
        response_data = {
            'user': UserSerializer(user, context=self.get_serializer_context()).data,
            'token': AuthToken.objects.create(user)[1],
        }

        return Response(response_data)


class UserAPIView(RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


# todo user from token mby?
class AccountActivationAPI(GenericAPIView):
    serializer_class = ActivationSerializer
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)  # type: ActivationSerializer
        serializer.is_valid(raise_exception=True)

        success, user = serializer.validated_data  # type: bool, IrisUser

        user.is_active = True
        user.save()

        AccountActivation.objects.get(user=user).delete()

        response_data = {
            'user': UserSerializer(user, context=self.get_serializer_context()).data,
            'token': AuthToken.objects.create(user)[1],
        }
        return Response(response_data)
