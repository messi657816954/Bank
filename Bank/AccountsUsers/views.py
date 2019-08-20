
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, generics
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from AccountsUsers.mixins import  MaPaginationMixin
from AccountsUsers.permissions import *
from AccountsUsers.pagination import WsPagination
from django.contrib.auth import authenticate, login
from rest_framework.authentication import TokenAuthentication, BasicAuthentication

from AccountsUsers.serializer.ChangePasswordSerializer import ChangePasswordSerializer
from AccountsUsers.serializer.LoginSerializer import LoginSerializer
from AccountsUsers.serializer.RegistrationSerializer import RegistrationSerializer
from AccountsUsers.serializer.UserDetailSerializer import UserDetailSerializer
from AccountsUsers.serializer.UserListSerializer import UserListSerializer
from AccountsUsers.serializer.UserSerializer import UserSerializer
from AppelFond.models import User, Tbanque

import json
from django.http import HttpResponse
from django.contrib.sessions.models import Session
from django.utils import timezone


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        print(request.data) 
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        RESPONSE_MSG = {
            'msg_code': 'MG001',
            'success': 1,
            'results': serializer.data,
            'errors': "[{'error_code':'', 'error_msg':''}]"
        }
        return Response(RESPONSE_MSG, status=status.HTTP_201_CREATED)

class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = (BasicAuthentication, TokenAuthentication)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(username=request.data['email'], password=request.data['password'])
        if not user:
            RESPONSE_MSG = {
                'msg_code': 'MG000',
                'success': 0,
                'results': "[]",
                'errors': [{'error_code':'', 'error_msg':'Enter a good password or a good email'}]
            }
            return Response(RESPONSE_MSG)
        login(request, user)
        token, create = request.user.token
        user_info = get_object_or_404(User, email=serializer.data['email'])
        user_json = {'id': user_info.id,
                     'email': user_info.email,
                     'role': user_info.role,
                     'phone': user_info.phone,
                     'username': user_info.username,
                     'banque': user_info.banque.id if user_info.banque else user_info.banque
                     }
        res = {'content': user_json, 'token': token.key}
        RESPONSE_MSG = {
            'msg_code': 'MG001',
            'success': 1,
            'results': res,
            'errors': [{'error_code':'', 'error_msg':''}]
        }
        return Response(RESPONSE_MSG)


class Logout(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def post(self,request):
        return self.logout(request)

    def logout(self, request,format=None):
        try:
            #print("request.session .flush()",request.session.flush())
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            RESPONSE_MSG = {
                'msg_code': 'MG000',
                'success': 0,
                'results': "[]",
                'errors': [{'error_code':'', 'error_msg':'Une erreur est survenue pendant la suppression du token'}]
            }
            return Response(RESPONSE_MSG)
        logout(request)
        RESPONSE_MSG = {
            'msg_code': 'MG001',
            'success': 1,
            'results': "Successfully logged out.",
            'errors': [{'error_code':'', 'error_msg':''}]
        }
        #res={"success": "Successfully logged out."},status=status.HTTP_200_OK
        return Response(RESPONSE_MSG)

class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                RESPONSE_MSG = {
                    'msg_code': 'MG000',
                    'success': 0,
                    'results': "[]",
                    'errors': [{'error_code':'', 'error_msg':'password wrong! Enter a good password'}]
                }
                #res = {"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST
                return Response(RESPONSE_MSG)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            RESPONSE_MSG = {
                'msg_code': 'MG001',
                'success': 1,
                'results': "Password change Successfully",
                'errors': "[{'error_code':'', 'error_msg':''}]"
            }
            #res="Success.", status=status.HTTP_200_OK
            return Response(RESPONSE_MSG)
        RESPONSE_MSG = {
            'msg_code': 'MG000',
            'success': 0,
            'results': serializer.errors,
            'errors':status.HTTP_400_BAD_REQUEST
        }
        #res=serializer.errors, status=status.HTTP_400_BAD_REQUEST
        return Response(RESPONSE_MSG)

class CheckPassword(APIView):
    def post(self, request,*args, **kwargs):
        user = request.user
        print("user.password", user.password)
        if user.check_password(request.data['password']):
            #res = {"status": True,"message": "password check succefully!"}
            RESPONSE_MSG = {
                'msg_code': 'MG001',
                'success': 1,
                'results': "password check succefully!",
                'errors': ""
            }
            return Response(RESPONSE_MSG)
        #res = {"status": False, "message": "password wrong! try again"}
        RESPONSE_MSG = {
            'msg_code': 'MG000',
            'success': 0,
            'results': "[]",
            'errors': [{'error_code':'', 'error_msg':'password wrong! try again'}]
        }
        return Response(RESPONSE_MSG)


class  UserlistClientView(generics.ListAPIView):
    permission_classes = [IsAuthenticated & IsGestionnaireOnly]
    authentication_classes = [TokenAuthentication]
    pagination_class = WsPagination
    search_fields = ['username', 'email', 'phone', 'last_login']
    ordering_fields = ['username', 'created_at', 'last_login']
    serializer_class = UserListSerializer

    # def list(self, request, *args, **kwargs):
    #     RESPONSE_MSG = {
    #         'msg_code': 'MG001',
    #         'success': 0,
    #         'results': self.serializer.data,
    #         'errors': [{'error_code': '', 'error_msg': ''}]
    #     }
    #     response = super(UserlistClientView, self).list(request, *args, **kwargs)
    #     return Response(RESPONSE_MSG)


    def get_queryset(self):
        banque_obj_manager = self.request.user.banque
        banque_obj = Tbanque.objects.get(pk=self.request.query_params['pk'])
        if banque_obj.pk == banque_obj_manager.pk:
            qs = User.objects.filter(role='CLIENT', banque=banque_obj)
            return qs
        return User.objects.none()

#@perms.apply(IsMyOwnerProfile)
class UserDetailClientView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated & IsMyOwnerOrManagerSeeProfile]
    authentication_classes = [TokenAuthentication]
    #queryset = User.objects.filter(role='CLIENT')
    serializer_class = UserDetailSerializer
    #lookup_field = 'id'

    def get_queryset(self):
        banq_obj_user_connect = self.request.user.banque
        banq_obj = Tbanque.objects.get(pk=self.request.query_params['pk'])
        if banq_obj_user_connect.pk == banq_obj.pk:
            user_qs = User.objects.filter(role='CLIENT') #,pk=self.kwargs['pk']
            return user_qs
        return User.objects.none()

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(),pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

class UserUpdateClientView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    #queryset = User.objects.all()
    #serializer_class = UserSerializer

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def put(self, request, *args, **kwargs):
        if request.user:
            if 'pk' in request.query_params:
                item = self.get_object(request.query_params['pk'])

                output_serializer = UserSerializer(instance=item, data=request.query_params, partial=True)
                output_serializer.is_valid(raise_exception=True)
                if output_serializer.is_valid(raise_exception=True):
                    output_serializer.save()
                else:
                    print(output_serializer.errors)
                    return Response(output_serializer.errors)
            return Response(output_serializer.data)
        
        return Response([{'error_code': 2, 'content': {'msg': 'vous devez vous authentifier'}}],
                        status=status.HTTP_400_BAD_REQUEST)
    #lookup_field = 'id'

    # def perform_update(self, serializer):
    #     rm_pawd = serializer.validate_data.pop('password', None)
    #     serializer.save()

class UserDeleteClientView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    #http://localhost:8000/%5Ebanques/?pk=1
    def delete(self, request, *args, **kwargs):
        #item = models.TPlafond.objects.get(pk=request.query_params['pk'])
        item = self.get_object(request.query_params['pk'])
        item.delete()
        return Response(status= status.HTTP_204_NO_CONTENT)

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    # def get_object(self, pk):
    #     try:
    #         return User.objects.get(pk=pk)
    #     except User.DoesNotExist:
    #         raise Http404

    # def delete(self, request, pk, format=None):
    #     user = self.get_object(pk)
    #     user.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)





    # class UserDeleteClientView(generics.DestroyAPIView):
#     permission_classes = []
#     authentication_classes = []
#     queryset = User.objects.all()
#     serializer_class = UserDetailSerializer







# class Logged_users_views(APIView):
#
#     def get_current_users(self):
#         active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
#         user_id_list = []
#         for session in active_sessions:
#             data = session.get_decoded()
#             user_id_list.append(data.get('_auth_user_id', None))
#         return User.objects.filter(id__in=user_id_list).values()
#
#     def get(self, request, *args, **kwargs):
#         from django.core import serializers
#         data = serializers.serialize('json', self.get_current_users())
#         print("data", data)
#         return HttpResponse({
#             'data': data,
#             'count': len(data)},
#             content_type='application/json')
#

class MyView(APIView,MaPaginationMixin):
    from rest_framework.settings import api_settings
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    # Nous devons overrider la methode get pour activer la pagination
    def get(self, request):

        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)


