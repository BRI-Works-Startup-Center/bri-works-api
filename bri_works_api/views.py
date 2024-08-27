from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from event.models import Event, EventRegistration
from food.models import Tenant
from rent_space.models import Space
from member_registration.models import MemberRegistration
from .serializers import SpaceHomeSerializer, ProfileSerializer, ChangeAvatarResponse, ProfileResponse
from event.serializers import EventSerializer, EventRegistrationSerializer
from food.serializers import TenantSerializer
from authentication.models import CustomUser

from django.utils import timezone

class HomeAPI(APIView):
  def get(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
    user = token[0].user
    now = timezone.now()
    events = Event.objects.filter(end_time__gte=now).order_by('start_time')[:5]
    events_data = []
    for event in events:
      registrations = EventRegistration.objects.filter(user=user, event=event)
      registered = registrations.exists()
      if not registered:
        event_data = EventSerializer(event).data
      else:
        event_data = EventSerializer(event).data
        registration_data = EventRegistrationSerializer(registrations[0]).data
        event_data['registration_date'] = registration_data['registration_date']
      events_data.append(event_data)
    tenants = Tenant.objects.order_by('-rate')[:5]
    tenants_serializer = TenantSerializer(tenants, many=True)
    spaces = Space.objects.order_by('name')[:5]
    spaces_serializer = SpaceHomeSerializer(spaces, many=True)
       
    response_data = {
      'message': 'Successfully retrieved',
      'data': {
          'events': events_data,
          'tenants': tenants_serializer.data,
          'spaces': spaces_serializer.data
      }
    }
    return Response(response_data)

class AvatarAPI(APIView):
  def put(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
    user_email = token[0].user
    user = CustomUser.objects.get(email=user_email)
    user.avatar = request.data['avatar']
    user.save()
    serializer = ChangeAvatarResponse(user)
    response_data = {
      'message': 'Succesfully change the avatar',
      'data': serializer.data
    }
    return Response(response_data)

class ProfileAPI(APIView):
  def get(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
    user = token[0].user
    # user = CustomUser.objects.filter(email=user_email)[0]
    package = MemberRegistration.objects.filter(user=user, expiry_date__gt = timezone.now())
    serializer = ProfileResponse({
      'id': user.id,
      'email': user.email,
      'phone_number': user.phone_number,
      'avatar': user.avatar,
      'current_package_name': package[0].package.name if package.exists() else None,
      'current_package_expiry_date': package[0].expiry_date if package.exists() else None
    }
    )
    response_data = {
      'message': 'Succesfully retrieved profile',
      'data': serializer.data
    }
    return Response(response_data)

class EmailAPI(APIView):
  def get(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
    user = token[0].user    
    response_data = {
      'message': 'Succesfully retrieved profile',
      'data': {
        'email': user.email
      }
    }
    return Response(response_data)