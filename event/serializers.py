from .models import Event, EventReview, EventRegistration
from rest_framework import serializers
from payment.serializers import CreateSnapPaymentResponse

class EventSerializer(serializers.ModelSerializer):
  registration_date = serializers.DateTimeField(allow_null=True)
  class Meta:
    model = Event
    fields = ["id", "title", "location", "price", "start_time", "end_time", "picture", "type", "company", "registration_date"]
  
  def get_registration_date(self, obj):
    return None
  
class EventDetailSerializer(serializers.ModelSerializer):
  registration_date = serializers.DateTimeField(allow_null=True)
  class Meta:
    model = Event
    fields = '__all__'
  def get_registration_date(self, obj):
    return None

class EventReviewSerializer(serializers.ModelSerializer):
  class Meta:
    model = EventReview
    fields = ['id', 'event', 'star', 'comment']

class EventRegistrationSerializer(serializers.ModelSerializer):
  class Meta:
    model = EventRegistration
    fields = ['id', 'event', 'registration_date', 'status']

class RetrieveEventRegistrationResponse(serializers.ModelSerializer):
  event = EventSerializer()
  class Meta:
    model = EventRegistration
    fields = ['id', 'event', 'registration_date', 'status',]
class RetrieveEventRegistrationDetailResponse(serializers.ModelSerializer):
  event = EventDetailSerializer()
  class Meta:
    model = EventRegistration
    fields = ['id', 'event', 'registration_date', 'status',]
class CreateEventReviewResponse(serializers.Serializer):
    message = serializers.CharField()
    data = EventReviewSerializer()
    

class CreateEventRegistrationResponseData(serializers.Serializer):
  transaction_detail = CreateSnapPaymentResponse()
  event_registration = EventRegistrationSerializer()

class CreateEventRegistrationResponse(serializers.Serializer):
  message = serializers.CharField()
  data = CreateEventRegistrationResponseData()
    