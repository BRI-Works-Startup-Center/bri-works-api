from rest_framework import serializers

from .models import MemberRegistration, MemberPackage
from authentication.models import CustomUser

class MemberRegistrationRequest(serializers.Serializer):
  package = serializers.UUIDField()

class MemberPackageSerializer(serializers.ModelSerializer):
  class Meta:
    model = MemberPackage
    fields = '__all__'

class MemberRegistrationSerializer(serializers.ModelSerializer):
  package = MemberPackageSerializer()
  class Meta:
    model = MemberRegistration
    fields = '__all__'

class UserMemberFormSerializer(serializers.ModelSerializer):
  class Meta:
    model = CustomUser
    fields = ['id', 'name', 'birthdate', 'job', 'address', 'institution']