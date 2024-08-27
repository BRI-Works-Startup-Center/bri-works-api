from rest_framework import serializers

from .models import MemberRegistration, MemberPackage
from authentication.models import CustomUser

class MemberRegistrationRequest(serializers.Serializer):
  package = serializers.UUIDField()
  name = serializers.CharField()
  birthdate = serializers.DateField()
  address = serializers.CharField()
  job = serializers.CharField()
  institution = serializers.CharField(allow_null=True, required=False)

class MemberRegistrationSerializer(serializers.ModelSerializer):
  class Meta:
    model = MemberRegistration
    fields = '__all__'

class MemberPackageSerializer(serializers.ModelSerializer):
  class Meta:
    model = MemberPackage
    fields = '__all__'

class UserMemberFormSerializer(serializers.ModelSerializer):
  class Meta:
    model = CustomUser
    fields = ['id', 'name', 'birthdate', 'job', 'address', 'institution']