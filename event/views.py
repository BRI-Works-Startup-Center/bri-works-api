from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Event, EventReview, EventRegistration
from authentication.models import CustomUser
from .serializers import EventSerializer, EventDetailSerializer, EventReviewSerializer, CreateEventReviewResponse, EventRegistrationSerializer, CreateEventRegistrationResponse, RetrieveEventRegistrationResponse, RetrieveEventRegistrationDetailResponse
from django.utils import timezone

class EventAPI(APIView):
  def get(self, request):
    now = timezone.now()
    events = Event.objects.filter(start_time__gte = now).order_by('start_time')
    serializer = EventSerializer(events, many=True)
    serialized_data = serializer.data
    return Response(serialized_data)

class EventDetailAPI(APIView):
  def get(self, request, event_id):
    event = Event.objects.filter(pk=event_id)[0]
    serializer = EventDetailSerializer(event)
    serialized_data = serializer.data
    return Response(serialized_data)

class EventReviewAPI(APIView):
  def post(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        "message": "User not found"
      }, status=status.HTTP_404_NOT_FOUND)
    user_email = token[0].user
    review_data = EventReviewSerializer(data=request.data)
    review_data.is_valid(raise_exception = True)
    review_data = review_data.data
    event = Event.objects.get(pk=review_data['event'])
    if not event:
      return Response({
        "message" : "No related event"}, status=status.HTTP_400_BAD_REQUEST)
    review_exist = EventReview.objects.filter(user=user_email, event=review_data['event']).exists()
    if review_exist:
      return Response({"message": "User already reviewed this event"}, status=status.HTTP_400_BAD_REQUEST)
    new_review = EventReview.objects.create(
      event=event,
      user=user_email,
      star=review_data['star'],
      comment=review_data['comment']
    )
    
    new_review.save()
    
    serializer = CreateEventReviewResponse(
      data={
        'message': 'Review succesfully created.',
        'data': review_data
      }
    )
    
    serializer.is_valid(raise_exception=True)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

class EventRegistrationAPI(APIView):
  def post(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response("User not found")
    user_email = token[0].user
    registration_data = EventRegistrationSerializer(data=request.data)
    registration_data.is_valid(raise_exception = True)
    registration_data = registration_data.data
    event = Event.objects.get(pk=registration_data['event'])
    print(event)
    if not event:
      return Response({"message": "No related event"}, status=status.HTTP_400_BAD_REQUEST)
    registration = EventRegistration.objects.filter(user=user_email, event=registration_data['event']).exists()
    if registration:
      return Response({"message": "User already registered to the event"}, status=status.HTTP_400_BAD_REQUEST)

    new_registration = EventRegistration.objects.create(
      event=event,
      user=user_email
    )
    
    new_registration.save()
    
    serializer = CreateEventRegistrationResponse(
      data={
        'message': 'Registration succesfully created.',
        'data': registration_data
      }
    )
    
    serializer.is_valid(raise_exception=True)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

class EventRegistrationDetailAPI(APIView):
  def get(self, request, registration_id):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response("User not found")
    user_email = token[0].user
    registration_exist = EventRegistration.objects.filter(pk=registration_id).exists
    if not registration_exist:
      return Response({
        'message': 'Event not found'
      }, status=status.HTTP_404_NOT_FOUND)
    registration = EventRegistration.objects.get(pk=registration_id)
    if registration.user != user_email:
      return Response({
        'message': 'User not registered to this event'
      }, status=status.HTTP_400_BAD_REQUEST)
    serializer = RetrieveEventRegistrationDetailResponse(registration)
    response_data = {
      'message': 'Succesfully retrieved',
      'data': serializer.data
    }
    return Response(response_data)

class UpcomingEventAPI(APIView):
  def get(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response("User not found")
    user_email = token[0].user
    now = timezone.now()
    event_registrations = EventRegistration.objects.filter(user=user_email, event__end_time__gte=now).select_related('event').order_by('event__start_time')
    serializer = RetrieveEventRegistrationResponse(event_registrations, many=True)
    response_data = {
      'message': 'Succesfully retrieved',
      'data': serializer.data
    }
    # serializer.is_valid(raise_exception=True)
    return Response(response_data)

class AttendedEventAPI(APIView):
  def get(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response("User not found")
    user_email = token[0].user
    now = timezone.now()
    event_registrations = EventRegistration.objects.filter(user=user_email, event__end_time__lt=now).select_related('event').order_by('event__start_time')
    serializer = RetrieveEventRegistrationResponse(event_registrations, many=True)
    response_data = {
      'message': 'Succesfully retrieved',
      'data': serializer.data
    }
    # serializer.is_valid(raise_exception=True)
    return Response(response_data)

