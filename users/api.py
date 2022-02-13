from knox.models import AuthToken
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from .serializers import RegisterSerializer, UserSerializer


class RegisterAPI(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer: ModelSerializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(str(request.data))
        user = serializer.save()
        token = AuthToken.objects.create(user)

        return Response(
            {
                "users": UserSerializer(user, context=self.get_serializer_context()).data,
                "token": token[1]
            }
        )


class UserAPIView(RetrieveAPIView):
    permission_classes = [
        IsAuthenticated
    ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
