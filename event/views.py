from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Event, EventReview, EventRegistration
from authentication.models import CustomUser
from .serializers import EventSerializer, EventDetailSerializer, EventReviewSerializer, CreateEventReviewResponse, EventRegistrationSerializer, CreateEventRegistrationResponse, RetrieveEventRegistrationResponse, RetrieveEventRegistrationDetailResponse
from django.utils import timezone
from django.db.transaction import atomic
from django.db.models import Q
from payment.models import PaymentTransaction
from .utils import send_invitation_email, generate_time_string

import midtransclient
import os

class EventAPI(APIView):
  def get(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
    user = token[0].user
    now = timezone.now()
    events = Event.objects.filter(start_time__gte = now).order_by('start_time')
    data = []
    for event in events:
      registrations = EventRegistration.objects.filter(user=user, event=event)
      registered = registrations.exists()
      if not registered:
        event_data = EventSerializer(event).data
      else:
        event_data = EventSerializer(event).data
        registration_data = EventRegistrationSerializer(registrations[0]).data
        event_data['registration_date'] = registration_data['registration_date']
      data.append(event_data)
    return Response(data)

class EventDetailAPI(APIView):
  def get(self, request, event_id):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
    user = token[0].user
    event = Event.objects.filter(pk=event_id)[0]
    event_data = EventDetailSerializer(event).data
    registration = EventRegistration.objects.filter(user=user, event=event)
    registered = registration.exists()
    if registered:
      registration_data = EventRegistrationSerializer(registration[0]).data
      event_data['registration_date'] = registration_data['registration_date']
    return Response(event_data)

class EventReviewAPI(APIView):
  def post(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
    user_email = token[0].user
    review_data = EventReviewSerializer(data=request.data)
    review_data.is_valid(raise_exception = True)
    review_data = review_data.data
    event = Event.objects.get(pk=review_data['event'])
    if not event:
      return Response({
        "message" : "No related event"}, status=status.HTTP_400_BAD_REQUEST)
    registration_exist = EventRegistration.objects.filter(Q(status='REGISTERED') | Q(status='ATTENDED'),user=user_email, event=review_data['event']).exists()
    if not registration_exist:
      return Response({"message": "User is not registered to the event"}, status=status.HTTP_400_BAD_REQUEST)
    review_exist = EventReview.objects.filter(user=user_email, event=review_data['event']).exists()
    if review_exist:
      return Response({"message": "User already reviewed this event"}, status=status.HTTP_409_CONFLICT)
    new_review = EventReview.objects.create(
      event=event,
      user=user_email,
      star=review_data['star'],
      comment=review_data['comment']
    )
    
    new_review.save()
    event.update_rate()
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
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
    user = token[0].user
    registration_data = EventRegistrationSerializer(data=request.data)
    registration_data.is_valid(raise_exception = True)
    registration_data = registration_data.data
    event = Event.objects.get(pk=registration_data['event'])
    if not event:
      return Response({"message": "No related event"}, status=status.HTTP_400_BAD_REQUEST)
    registration = EventRegistration.objects.filter(Q(status='REGISTERED') | Q(status='ATTENDED'), user=user, event=registration_data['event']).exists()
    if registration:
      return Response({"message": "User already registered to the event"}, status=status.HTTP_409_CONFLICT)
    with atomic():
      new_registration = EventRegistration.objects.create(
        event=event,
        user=user
      )
      new_registration.save()
      snap = midtransclient.Snap(
        is_production = True if os.getenv('MIDTRANS_IS_PRODUCTION') == 'True' else False,
        server_key = str(os.getenv('MIDTRANS_SERVER_KEY')),
        client_key= str(os.getenv('MIDTRANS_CLIENT_KEY'))
      )
      order_id = f'event_{new_registration.id}'
      event_price = event.price
      event_name = event.title
      snap_transaction = snap.create_transaction({
        "transaction_details": {
          "order_id": order_id,
          "gross_amount": event_price
        },
        "item_details": {
          "price": event_price,
          "quantity": 1,
          "name": event_name
        }
      })
      snap_token = snap_transaction['token']
      snap_redirect_url = snap_transaction['redirect_url']
      new_payment = PaymentTransaction.objects.create(
        order_id = f'event_{new_registration.id}',
        type = 'EVENT',
        gross_amount = event_price,
        midtrans_token = snap_token,
        redirect_url = snap_redirect_url,
      )
      new_payment.save()
    
    serializer = CreateEventRegistrationResponse(
      data={
        'message': 'Registration succesfully created.',
        'data': {
          'transaction_detail': {
            'token': snap_token,
            'redirect_url': snap_redirect_url
          }, 
          'event_registration': registration_data
        }
      }
    )
    serializer.is_valid(raise_exception=True)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

class EventRegistrationDetailAPI(APIView):
  def get(self, request, registration_id):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
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
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
    user_email = token[0].user
    now = timezone.now()
    event_registrations = EventRegistration.objects.filter(user=user_email, event__end_time__gte=now, status='REGISTERED').select_related('event').order_by('event__start_time')
    serializer = RetrieveEventRegistrationResponse(event_registrations, many=True)
    response_data = {
      'message': 'Succesfully retrieved',
      'data': serializer.data
    }
    return Response(response_data)

class AttendedEventAPI(APIView):
  def get(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
    user_email = token[0].user
    now = timezone.now()
    event_registrations = EventRegistration.objects.filter(
      Q(status = 'REGISTERED') | Q(status='ATTENDED'),
      user=user_email,
      event__end_time__lt=now).select_related('event').order_by('event__start_time')
    serializer = RetrieveEventRegistrationResponse(event_registrations, many=True)
    response_data = {
      'message': 'Succesfully retrieved',
      'data': serializer.data
    }
    # serializer.is_valid(raise_exception=True)
    return Response(response_data)

