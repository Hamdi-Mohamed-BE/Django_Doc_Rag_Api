from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.parsers import FileUploadParser
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

import requests

from user import serializers


# TODO: write descriptions for swagger!


class TokenPairRefreshView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = serializers.TokenRefreshSerializer


class DeleteMeView(generics.DestroyAPIView):
    serializer_class = serializers.UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class EmailRegistrationView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = serializers.EmailRegistration


class LoginEmailView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = serializers.LoginEmailSerializer


class DetailView(generics.RetrieveAPIView):
    """
        `social_info.platform` enum: `GOOGLE`, `FACEBOOK`, `APPLE`, `INSTAGRAM`
    """
    serializer_class = serializers.UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    

class UpdateUserView(generics.UpdateAPIView):
    serializer_class = serializers.UserUpdateSerializer
    permission_classes = [IsAuthenticated]
    allowed_methods = {"PATCH"}


    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ChangePasswordSerializer

