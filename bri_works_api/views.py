from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from event.models import Event, EventReview
from food.models import Tenant
from rent_space.models import Space
from .serializers import HomeResponse, SpaceHomeSerializer
from event.serializers import EventSerializer
from food.serializers import TenantSerializer

class HomeAPI(APIView):
  def get(self, request):
    events = Event.objects.order_by('start_time')[:5]
    events_serializer = EventSerializer(events, many=True)
    tenants = Tenant.objects.order_by('-rate')[:5]
    tenants_serializer = TenantSerializer(tenants, many=True)
    spaces = Space.objects.order_by('name')[:5]
    spaces_serializer = SpaceHomeSerializer(spaces, many=True)
    
    response_data = {
      'message': 'Successfully retrieved',
      'data': {
          'events': events_serializer.data,
          'tenants': tenants_serializer.data,
          'spaces': spaces_serializer.data
      }
    }
    return Response(response_data)