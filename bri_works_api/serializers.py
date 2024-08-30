from rest_framework import serializers
from event.serializers import EventSerializer
from food.serializers import TenantSerializer
from rent_space.models import Space
from authentication.models import CustomUser

class SpaceHomeSerializer(serializers.ModelSerializer):
  picture = serializers.ImageField(use_url=True, allow_null=True, required=False)
  class Meta:
    model = Space
    fields = ['id', 'name', 'picture']

class HomeSerializer(serializers.Serializer):
    events = serializers.ListField(
      child = EventSerializer()
    )
    spaces = serializers.ListField(
      child = SpaceHomeSerializer()
    )
    tenants = serializers.ListField(
      child = TenantSerializer()
    )

class HomeResponse(serializers.Serializer):
  message = serializers.CharField()
  data = HomeSerializer()

class ChangeAvatarRequest(serializers.Serializer):
  avatar = serializers.ImageField()

class ChangeAvatarResponse(serializers.ModelSerializer):
  class Meta:
    model = CustomUser
    fields = ['email', 'avatar']
class ProfileSerializer(serializers.ModelSerializer):
  avatar = serializers.ImageField(use_url=True, allow_null=True, required=False)
  class Meta:
    model = CustomUser
    fields = ['id', 'email', 'phone_number', 'avatar']

class ProfileResponse(serializers.Serializer):
  id = serializers.IntegerField()
  email = serializers.CharField()
  phone_number = serializers.CharField()
  avatar = serializers.ImageField()
  current_package_name = serializers.CharField()
  current_package_expiry_date = serializers.DateTimeField()

class UpdateProfileRequest(serializers.Serializer):
  phone_number = serializers.CharField()

class UpdateProfileResponse(serializers.Serializer):
  id = serializers.IntegerField()
  email = serializers.CharField()
  phone_number = serializers.CharField()
  avatar = serializers.ImageField()
  
  