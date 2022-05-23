import random
import string
from datetime import timedelta
import pytz
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate, user_logged_out
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.datetime_safe import datetime
from django.utils.translation import gettext_lazy as _
from knox.models import AuthToken
from knox.views import LoginView, LogoutAllView as KnoxLogoutAllView
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_202_ACCEPTED

from .models import AccountActivation, IrisUser
from .serializers import RegisterSerializer, UserSerializer, ActivationSerializer, PasswordChangeSerializer


def init_activation(user, *, save=False):
    activation_code = ''.join(random.choice(string.digits) for _ in range(6))
    expiration = datetime.now(tz=pytz.UTC) + timedelta(hours=12)
    encoded = make_password(activation_code)
    activation, created = AccountActivation.objects.get_or_create(
        user=user,
        defaults={
            'activation_code': encoded,
            'expiration': expiration,
        }
    )
    if not created:
        activation.activation_code = encoded
        activation.expiration = expiration
    if save is True:
        activation.save()
    return activation, activation_code


def send_activation_email(email, activation_code):
    context = {'activation_code': activation_code}
    confirmation_mail = EmailMultiAlternatives(
        'Activate your account',
        # f'Your activation code is: {activation.activation_code}'
        get_template('email_code.txt').render(context),
        settings.EMAIL_HOST_USER,
        [email],
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
        activation, activation_code = init_activation(user)

        user.save()

        activation.save()
        send_activation_email(user.email, activation_code)
        # token = AuthToken.objects.create(user)[1]

        return Response(
            {
                'user': UserSerializer(user, context=self.get_serializer_context()).data,
                # 'token': token
            }
        )


class PasswordAuthentication(BasicAuthentication):
    def authenticate_credentials(self, userid, password, request=None):
        credentials = {
            get_user_model().USERNAME_FIELD: userid,
            'password': password
        }
        user = authenticate(request=request, **credentials)
        if user is None:
            try:
                user = get_user_model().objects.all().get(**{get_user_model().USERNAME_FIELD: userid})

                if not user.is_active:
                    send_activation_email(user.email, init_activation(user, save=True)[1])
                    e = AuthenticationFailed(_('User inactive.'))
                    e.status_code = 406
                    raise e

            except get_user_model().DoesNotExist:
                pass

            raise AuthenticationFailed(_('Invalid username/password.'))

        return user, None


class LoginAPI(LoginView):
    authentication_classes = (PasswordAuthentication,)


class UserAPIView(RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class AccountActivationAPI(GenericAPIView):
    serializer_class = ActivationSerializer
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)  # type: ActivationSerializer
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data  # type: IrisUser

        user.is_active = True
        user.save()

        AccountActivation.objects.get(user=user).delete()

        response_data = {
            # 'user': UserSerializer(user, context=self.get_serializer_context()).data,
            'token': AuthToken.objects.create(user)[1],
        }
        return Response(response_data)


class TokenCheckAPI(GenericAPIView):
    def get(self, request):
        IrisUser.objects.get(username__exact='user').password = make_password('password')
        return Response(request.auth.expiry)


class PasswordChangeAPI(GenericAPIView):
    serializer_class = PasswordChangeSerializer
    authentication_classes = (PasswordAuthentication, )

    def post(self, request):
        serializer = self.get_serializer(data=request.data) # type: PasswordChangeSerializer
        serializer.is_valid(raise_exception=True)

        serializer.update(request.user, serializer.validated_data)
        # ?todo invalidate tokens
        return Response()


class LogoutAllView(KnoxLogoutAllView):
    def delete(self, *args, **kwargs):
        return super(LogoutAllView, self).post(*args, **kwargs)

    def post(self, request, format=None):
        request.user.auth_token_set.all().exclude(pk__exact=request.auth.pk).delete()
        user_logged_out.send(sender=request.user.__class__,
                             request=request, user=request.user)
        return Response(None, status=HTTP_202_ACCEPTED)
