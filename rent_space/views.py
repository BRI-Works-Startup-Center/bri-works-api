from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from authentication.models import CustomUser
from django.utils import timezone
from .models import Space, SpaceReservation, SpaceReservationInvitation
from  .serializers import SpaceSerializer, SpaceDetailSerializer, SpaceReservationSerializer, SpaceReservationRequest, SpaceReservationInvitationSerializer, RetrieveSpaceReservationInvitationResponse, RetrieveSpaceReservationInvitationDetailResponse

class SpaceAPI(APIView):
  def get(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        'message': 'User not found'
      }, status=status.HTTP_404_NOT_FOUND)
    user = token[0].user
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
        'message': 'User not found'
      }, status=status.HTTP_404_NOT_FOUND)
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
        "message": "User not found"}, status=status.HTTP_401_UNAUTHORIZED)
    user_email = token[0].user
    reservation_data = SpaceReservationSerializer(data=request.data)
    reservation_data.is_valid(raise_exception = True)
    reservation_data = reservation_data.data
    space = Space.objects.get(pk=reservation_data['space_id'])
    if not space:
      return Response({"message": "No related space"}, status=status.HTTP_400_BAD_REQUEST)
    reservation = SpaceReservation.objects.filter(user=user_email, space_id=reservation_data['space_id'], start_time__lt=reservation_data['end_time'], end_time__gt=reservation_data['start_time']).exists()
    if reservation:
      return Response({"message": "Space already booked in given range of time"}, status=status.HTTP_400_BAD_REQUEST)

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
        "message": "User not found"}, status=status.HTTP_401_UNAUTHORIZED)
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
        return Response({"message": "A participant already invited to this reservation"}, status=status.HTTP_400_BAD_REQUEST)
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
      return Response("User not found")
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
      return Response("User not found")
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
      return Response("User not found")
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
# Create your views here.
