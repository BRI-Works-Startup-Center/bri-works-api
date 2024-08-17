from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers, status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, LoginSerializer
from .models import CustomUser

class RegisterResponse(serializers.Serializer):
    token = serializers.CharField()

class RegisterAPI(APIView):
    def post(self, request):
        register_data = RegisterSerializer(data=request.data)
        register_data.is_valid(raise_exception=True)
        register_data = register_data.data
        new_user = CustomUser.objects.create_user(
            email=register_data['email'],
            phone_number=register_data['phone_number'],
            password=register_data['password']
            )
        
        new_user.save()

        token = Token.objects.create(user=new_user)

        serializer = RegisterResponse(
            data = {
                'token': token.key
            }
        )
        serializer.is_valid()

        return Response(serializer.data)
    

    
class LoginResponse(serializers.Serializer):
    message = serializers.CharField()
    
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
            token, created = Token.objects.get_or_create(user=user)
            serializer = RegisterResponse(
                data={
                    'token': token.key
                }
            )
            serializer.is_valid()

            return Response(serializer.data)
        else:
            serializer = LoginResponse(
                data={
                    'message': 'Invalid credentials'
                }
            )
            serializer.is_valid()

            return Response(serializer.data, status=status.HTTP_401_UNAUTHORIZED)
