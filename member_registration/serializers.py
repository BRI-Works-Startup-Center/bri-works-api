from rest_framework import serializers

from .models import MemberRegistration, MemberPackage
from authentication.models import CustomUser
from payment.serializers import CreateSnapPaymentResponse

class MemberRegistrationRequest(serializers.Serializer):
  package = serializers.UUIDField()

class MemberPackageSerializer(serializers.ModelSerializer):
  class Meta:
    model = MemberPackage
    fields = '__all__'

class MemberRegistrationSerializer(serializers.ModelSerializer):
  id = serializers.CharField(required=False)
  package = MemberPackageSerializer()
  class Meta:
    model = MemberRegistration
    fields = '__all__'

class CreateMemberRegistrationResponse(serializers.Serializer):
  transaction_details = CreateSnapPaymentResponse()
  member_registration = MemberRegistrationSerializer()

class UserMemberFormSerializer(serializers.ModelSerializer):
  class Meta:
    model = CustomUser
    fields = ['id', 'name', 'birthdate', 'job', 'address', 'institution']