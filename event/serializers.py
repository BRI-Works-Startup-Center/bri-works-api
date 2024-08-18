from .models import Event, EventReview, EventRegistration
from rest_framework import serializers

class EventSerializer(serializers.ModelSerializer):
  class Meta:
    model = Event
    fields = ["id", "title", "location", "price", "start_time", "end_time", "picture", "type", "company"]

class EventDetailSerializer(serializers.ModelSerializer):
  class Meta:
    model = Event
    fields = '__all__'

class EventReviewSerializer(serializers.ModelSerializer):
  class Meta:
    model = EventReview
    fields = '__all__'

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

class CreateEventRegistrationResponse(serializers.Serializer):
    message = serializers.CharField()
    data = EventRegistrationSerializer()
    