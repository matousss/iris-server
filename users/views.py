from django.shortcuts import render
from knox.views import LoginView as KnoxLoginView


# Create your views here.
class LoginView(KnoxLoginView):
    permission_classes = ()
