from rest_framework import serializers
from .models import Space, SpaceReservation, SpaceReservationInvitation

class SpaceSerializer(serializers.ModelSerializer):
  class Meta:
    model = Space
    fields = ["id", "name", "capacity", "hourly_price", "daily_price", "picture"]

class SpaceDetailSerializer(serializers.ModelSerializer):
  class Meta:
    model = Space
    fields = ["id", "location", "size", "name", "capacity", "hourly_price", "daily_price", "picture", "description", "tv_facility", "wifi_facility", "sound_system_facility"]

class SpaceReservationSerializer(serializers.ModelSerializer):
  class Meta:
    model = SpaceReservation
    fields = '__all__'
    
class SpaceReservationInvitationSerializer(serializers.ModelSerializer):
  class Meta:
    model = SpaceReservationInvitation
    fields = '__all__'
    
class SpaceReservationRequest(serializers.Serializer):
  space_reservation = serializers.CharField()
  list_email = serializers.ListField(child = serializers.CharField())

class RetrieveSpaceReservationResponse(serializers.ModelSerializer):
  space_id = SpaceSerializer()
  class Meta:
    model = SpaceReservation
    fields = ['id', 'space_id']
class RetrieveSpaceReservationDetailResponse(serializers.ModelSerializer):
  space_id = SpaceDetailSerializer()
  class Meta:
    model = SpaceReservation
    fields = ['id', 'space_id', 'start_time', 'end_time']
    
class RetrieveSpaceReservationInvitationResponse(serializers.ModelSerializer):
  space_reservation = RetrieveSpaceReservationResponse()
  class Meta:
    model = SpaceReservationInvitation
    fields = ['id', 'space_reservation', 'user']
    
class RetrieveSpaceReservationInvitationDetailResponse(serializers.ModelSerializer):
  space_reservation = RetrieveSpaceReservationDetailResponse()
  class Meta:
    model = SpaceReservationInvitation
    fields = ['id', 'space_reservation', 'user']
  