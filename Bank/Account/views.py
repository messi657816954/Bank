import json
from rest_framework import serializers
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, generics
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from Account.Permissions import *
from AppelFond.models import User
from Account.pagination import WsPagination
from Account.serializers import (RegistrationSerializer,
                          LoginSerializer,
                          ChangePasswordSerializer,
                          UserListSerializer,
                          UserDetailSerializer)


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return Response({'doc-type': "MG000", 'content':{'error_code':1,'error_msg': '\n'.join(e.detail['non_field_errors'])}})
        except :
            return Response({'doc-type': "MG000",
                             'content': {'error_code': 1,
                                         'error_msg': 'une erreur est survenue pendant la requète'}})


class Logout(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        return self.logout(request)

    def logout(self, request,format=None):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass
        logout(request)
        return Response({"success": "Successfully logged out."},
                        status=status.HTTP_200_OK)

class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    #permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response("Success.", status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class  UserlistClientView(generics.ListAPIView):
    #permission_classes = [IsMyClient]
    authentication_classes = []
    pagination_class = WsPagination
    search_fields = ['username', 'email', 'phone', 'last_login']
    ordering_fields = ['username', 'created_at', 'last_login']
    serializer_class = UserListSerializer

    def get_queryset(self):
        qs = User.objects.all()
        #qs = User.objects.filter(role='CLIENT')
        return qs

class UserDetailClientView(generics.RetrieveAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = User.objects.filter(role='CLIENT')
    serializer_class = UserDetailSerializer
    lookup_field = 'id'

    def get_object(self, *args, **kwargs):
        kwargs = self.kwargs
        kw_id = kwargs.get('id')
        return User.objects.get(id=kw_id)

class UserUpdateClientView(generics.RetrieveUpdateAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    #lookup_field = 'id'

    # def perform_update(self, serializer):
    #     rm_pawd = serializer.validate_data.pop('password', None)
    #     serializer.save()

class UserDeleteClientView(generics.DestroyAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer