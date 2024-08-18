from rest_framework import serializers
from .models import CustomUser

class RegisterSerializer(serializers.Serializer):
    email = serializers.CharField()
    phone_number = serializers.CharField()
    password = serializers.CharField()
    
class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

class ResponseError(serializers.Serializer):
    message = serializers.CharField()
    status = serializers.IntegerField()

class TokenResponse(serializers.Serializer):
    token = serializers.CharField()