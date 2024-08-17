from .models import Event, EventReview
from rest_framework import serializers

class EventSerializer(serializers.ModelSerializer):
  class Meta:
    model = Event
    fields = ["id", "title", "location", "price", "start_time", "end_time", "picture", "type"]

class EventDetailSerializer(serializers.ModelSerializer):
  class Meta:
    model = Event
    fields = '__all__'

class EventReviewSerializer(serializers.ModelSerializer):
  class Meta:
    model = EventReview
    fields = '__all__'
    
class CreateEventReviewResponse(serializers.Serializer):
    message = serializers.CharField()
    data = EventReviewSerializer()
    