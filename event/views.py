from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Event, EventReview
from .serializers import EventSerializer, EventDetailSerializer, EventReviewSerializer, CreateEventReviewResponse

class EventAPI(APIView):
  def get(self, request):
    events = Event.objects.all()
    serializer = EventSerializer(events, many=True)
    serialized_data = serializer.data
    return Response(serialized_data )

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
# Create your views here.
