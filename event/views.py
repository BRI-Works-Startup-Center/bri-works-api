from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Event, EventReview, EventRegistration
from authentication.models import CustomUser
from .serializers import EventSerializer, EventDetailSerializer, EventReviewSerializer, CreateEventReviewResponse, EventRegistrationSerializer, CreateEventRegistrationResponse

class EventAPI(APIView):
  def get(self, request):
    events = Event.objects.all()
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
    review_data = EventReviewSerializer(data=request.data)
    review_data.is_valid(raise_exception = True)
    review_data = review_data.data
    event = Event.objects.get(pk=review_data['event'])
    if not event:
      return Response("No related event", status=status.HTTP_400_BAD_REQUEST)
    
    new_review = EventReview.objects.create(
      event=event,
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
    
  
# Create your views here.
