from rest_framework import serializers
from event.serializers import EventSerializer
from food.serializers import TenantSerializer
from rent_space.models import Space

class SpaceHomeSerializer(serializers.ModelSerializer):
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