from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers, status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, LoginSerializer, ResponseError, TokenResponse
from .models import CustomUser

class RegisterAPI(APIView):
    def post(self, request):
        register_data = RegisterSerializer(data=request.data)
        register_data.is_valid(raise_exception=True)
        register_data = register_data.data
        user_exist = CustomUser.objects.filter(email=register_data['email']).exists()
        if user_exist:
            serializer = ResponseError(
                data = {
                    'message': 'Email already registered',
                    'status': status.HTTP_409_CONFLICT
                }
            )
            serializer.is_valid()
            return Response(serializer.data, status=status.HTTP_409_CONFLICT)

        
        new_user = CustomUser.objects.create_user(
            email=register_data['email'],
            phone_number=register_data['phone_number'],
            password=register_data['password']
            )
        
        new_user.save()

        token = Token.objects.create(user=new_user)

        serializer = TokenResponse(
            data = {
                'token': token.key
            }
        )
        serializer.is_valid()

        return Response(serializer.data)
    
class LoginAPI(APIView):
    def post(self, request):
        login_data = LoginSerializer(data=request.data)
        login_data.is_valid(raise_exception=True)
        login_data = login_data.data

        user = authenticate(
            request,
            username=login_data['email'],
            password=login_data['password']
            )
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            serializer = TokenResponse(
                data={
                    'token': token.key
                }
            )
            serializer.is_valid()

            return Response(serializer.data)
        else:
            serializer = ResponseError(
                data={
                    'message': 'Invalid credentials',
                    'status': status.HTTP_401_UNAUTHORIZED
                }
            )
            serializer.is_valid()
            return Response(serializer.data, status=status.HTTP_401_UNAUTHORIZED)
