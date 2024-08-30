from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from zoneinfo import ZoneInfo

from authentication.models import CustomUser
from django.utils import timezone
from datetime import datetime
from dateutil import parser
from .models import Space, SpaceReservation, SpaceReservationInvitation, SpaceReview
from .serializers import SpaceSerializer, SpaceDetailSerializer, SpaceReservationSerializer, SpaceReservationRequest, SpaceReservationInvitationSerializer, RetrieveSpaceReservationInvitationResponse, RetrieveSpaceReservationInvitationDetailResponse, SpaceReviewSerializer

class SpaceAPI(APIView):
  def get(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
    spaces = Space.objects.all()
    serializer = SpaceSerializer(spaces, many=True)
    response_data = {
      'message': 'Succesfully retrieved',
      'data': serializer.data
    }
    return Response(response_data)

class SpaceDetailAPI(APIView):
  def get(self, request, space_id):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
    space = Space.objects.filter(pk=space_id)[0]
    serializer = SpaceDetailSerializer(space)
    response_data = {
      'message': 'Succesfully retrieved',
      'data': serializer.data
    }
    return Response(response_data)

class SpaceReservationAPI(APIView):
  def post(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      
      return Response({
        "message": "User has not been authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    user_email = token[0].user
    reservation_data = SpaceReservationSerializer(data=request.data)
    reservation_data.is_valid(raise_exception = True)
    reservation_data = reservation_data.data
    space = Space.objects.get(pk=reservation_data['space_id'])
    if not space:
      return Response({"message": "No related space"}, status=status.HTTP_400_BAD_REQUEST)
    reservations = SpaceReservation.objects.filter(space_id=reservation_data['space_id'], start_time__lt=reservation_data['end_time'], end_time__gt=reservation_data['start_time'])
    reservation_exist = reservations.exists()
    if reservation_exist:
      unavailable_times = []
      for reservation in reservations:
        unavailable_times.append({
          'start_time' : max(reservation.start_time, parser.parse(reservation_data['start_time'])),
          'end_time' : min(reservation.end_time, parser.parse(reservation_data['end_time'])) 
        })
      return Response({
        "message": "Space already booked in given range of time",
        "data": {
          'unavailable_times': unavailable_times
          }
      }, status=status.HTTP_409_CONFLICT)

    new_reservation = SpaceReservation.objects.create(
      space_id=space,
      user=user_email,
      participant_count=reservation_data['participant_count'],
      price=reservation_data['price'],
      start_time=reservation_data['start_time'],
      end_time=reservation_data['end_time']
    )
    
    new_reservation.save()
    
    new_invitation = SpaceReservationInvitation.objects.create(
        space_reservation = new_reservation,
        user = user_email
    )
    
    new_invitation.save()
    
    serializer = SpaceReservationSerializer(new_reservation)
    response_data = {
      'message': 'Succesfully created the reservation',
      'data': serializer.data
    }
    
    return Response(response_data, status=status.HTTP_201_CREATED)

class SpaceReservationInvitationAPI(APIView):
  def post(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        "message": "User has not been authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    invitation_data = SpaceReservationRequest(data=request.data)
    invitation_data.is_valid(raise_exception=True)
    invitation_data = invitation_data.data
    reservation = SpaceReservation.objects.get(pk=invitation_data['space_reservation'])
    response_data = {
      'message': 'Succesfully invite all the participant',
      'data': []
    }
    for email in invitation_data['list_email']:
      invitation_exist = SpaceReservationInvitation.objects.filter(user=email, space_reservation=invitation_data['space_reservation']).exists()
      if invitation_exist:
        return Response({"message": "A Participant already invited to this reservation"}, status=status.HTTP_409_CONFLICT)
      user = CustomUser.objects.get(email=email)
      invitation = SpaceReservationInvitation.objects.create(
        space_reservation = reservation,
        user = user
      )
      invitation.save()
      response_data['data'].append(SpaceReservationInvitationSerializer(invitation).data)
    return Response(response_data, status=status.HTTP_201_CREATED)

class UpcomingReservationAPI(APIView):
  def get(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        "message": "User has not been authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    user_email = token[0].user
    now = timezone.now()
    reservation_invitations = SpaceReservationInvitation.objects.filter(user=user_email, space_reservation__end_time__gte=now).select_related('space_reservation').select_related('space_reservation__space_id').order_by('space_reservation__start_time')
    serializer = RetrieveSpaceReservationInvitationResponse(reservation_invitations, many=True)
    response_data = {
      'message': 'Succesfully retrieved',
      'data': serializer.data
    }
    # serializer.is_valid(raise_exception=True)
    return Response(response_data)

class AttendedReservationAPI(APIView):
  def get(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        "message": "User has not been authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    user_email = token[0].user
    now = timezone.now()
    reservation_invitations = SpaceReservationInvitation.objects.filter(user=user_email, space_reservation__end_time__lt=now).select_related('space_reservation').select_related('space_reservation__space_id').order_by('space_reservation__start_time')
    serializer = RetrieveSpaceReservationInvitationResponse(reservation_invitations, many=True)
    response_data = {
      'message': 'Succesfully retrieved',
      'data': serializer.data
    }
    # serializer.is_valid(raise_exception=True)
    return Response(response_data)

class SpaceReservationInvitationDetailAPI(APIView):
  def get(self, request, invitation_id):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        "message": "User has not been authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    user_email = token[0].user
    invitation_exist = SpaceReservationInvitation.objects.filter(pk=invitation_id).exists
    if not invitation_exist:
      return Response({
        'message': 'Reservation not found'
      }, status=status.HTTP_404_NOT_FOUND)
    invitation = SpaceReservationInvitation.objects.get(pk=invitation_id)
    if invitation.user != user_email:
      return Response({
        'message': 'User not invited to the reservation'
      }, status=status.HTTP_400_BAD_REQUEST)
    serializer = RetrieveSpaceReservationInvitationDetailResponse(invitation)
    response_data = {
      'message': 'Succesfully retrieved',
      'data': serializer.data
    }
    return Response(response_data)

class SpaceReviewAPI(APIView):
  def post(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        "message": "User has not been authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    user = token[0].user
    space_review_data = SpaceReviewSerializer(data=request.data)
    space_review_data.is_valid(raise_exception=True)
    space_review_data = space_review_data.data
    space = Space.objects.filter(id=space_review_data['space'])
    
    if not space.exists():
      return Response({
        'message': 'There is no related space',
      }, status=status.HTTP_400_BAD_REQUEST)
    space = space[0]
    space_review_exist = SpaceReview.objects.filter(user=user, space=space)
    
    if space_review_exist.exists():
      return Response({
        'message': 'User already reviewed this space',
      }, status=status.HTTP_409_CONFLICT)
    
    space_review = SpaceReview.objects.create(space=space, user=user, star=space_review_data['star'], comment=space_review_data['comment'])
    space_review.save()
    space.update_rate()
    response_data = SpaceReviewSerializer(space_review).data
    return Response({
      'message': 'Review succesfully created',
      'data': response_data
    }, status=status.HTTP_201_CREATED)

class SpaceAvailabilityAPI(APIView):
  def get(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        "message": "User has not been authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    start_time_param = request.GET.get("start_time", None)
    end_time_param = request.GET.get("end_time", None)
    space_param = request.GET.get("space", None)
    if not start_time_param or not end_time_param or not space_param:
      return Response({
        'message': 'start_time, end_time, and space in the request params is not provided'
      }, status=status.HTTP_400_BAD_REQUEST)
    
    start_time = datetime.strptime(start_time_param, "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(end_time_param, "%Y-%m-%d %H:%M:%S")
    space = Space.objects.filter(id=request.GET.get("space", None))
    if not space.exists():
      return Response({
        'message': 'No Space found'
      }, status=status.HTTP_400_BAD_REQUEST)
    reservations = SpaceReservation.objects.filter(start_time__lt=end_time, end_time__gt=start_time)
    reservation_exist = reservations.exists()
    return Response({
      'message': 'Succesfully retrieved availability',
      'data': {
        'exist': reservation_exist
      }
    })
    
    
# Create your views here.
