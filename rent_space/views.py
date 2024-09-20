from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from zoneinfo import ZoneInfo

from authentication.models import CustomUser
from django.utils import timezone
from django.core.mail import send_mail
from django.db.transaction import atomic, set_rollback
from datetime import datetime
from dateutil import parser
from .models import Space, SpaceReservation, SpaceReservationInvitation, SpaceReview
from .serializers import SpaceSerializer, SpaceDetailSerializer, SpaceReservationSerializer, SpaceReservationRequest, SpaceReservationInvitationSerializer, RetrieveSpaceReservationInvitationResponse, RetrieveSpaceReservationInvitationDetailResponse, SpaceReviewSerializer, CreateSpaceReservationResponse
from payment.models import PaymentTransaction
from .utils import send_invitation_email, generate_time_string

import midtransclient
import os
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
    reservations = SpaceReservation.objects.filter(space_id=reservation_data['space_id'], start_time__lt=reservation_data['end_time'], end_time__gt=reservation_data['start_time'], status='REGISTERED')
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
    with atomic():
      new_reservation = SpaceReservation.objects.create(
        space_id=space,
        user=user_email,
        participant_count=reservation_data['participant_count'],
        price=reservation_data['price'],
        start_time=reservation_data['start_time'],
        end_time=reservation_data['end_time']
      )
    
      new_reservation.save()
      snap = midtransclient.Snap(
        is_production = True if os.getenv('MIDTRANS_IS_PRODUCTION') == 'True' else False,
        server_key = str(os.getenv('MIDTRANS_SERVER_KEY')),
        client_key= str(os.getenv('MIDTRANS_CLIENT_KEY'))
      )
      order_id = f'space_{new_reservation.id}'
      reservation_price = new_reservation.price
      snap_transaction = snap.create_transaction({
        "transaction_details": {
          "order_id": order_id,
          "gross_amount": reservation_price
        },
        "item_details": {
          "price": reservation_price,
          "quantity": 1,
          "name": f'{space.name} Reservation'
        }
      })
      snap_token = snap_transaction['token']
      snap_redirect_url = snap_transaction['redirect_url']
      new_payment = PaymentTransaction.objects.create(
        order_id = f'space_{new_reservation.id}',
        type = 'SPACE',
        gross_amount = reservation_price,
        midtrans_token = snap_token,
        redirect_url = snap_redirect_url,
      )
      new_payment.save()
    
    serializer =  CreateSpaceReservationResponse(data={
      'transaction_details': {
        'token': snap_token,
        'redirect_url': snap_redirect_url
      },
      'space_reservation': SpaceReservationSerializer(new_reservation).data
    })
    serializer.is_valid(raise_exception=True)
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
    reserver = token[0].user
    invitation_data = SpaceReservationRequest(data=request.data)
    invitation_data.is_valid(raise_exception=True)
    invitation_data = invitation_data.data
    reservation = SpaceReservation.objects.filter(pk=invitation_data['space_reservation'], user=reserver)
    if not reservation.exists():
      return Response({
        "message": "This user is not the reserver or the reservation isn't exist"}, status=status.HTTP_400_BAD_REQUEST)
    reservation = reservation.first()
    response_data = {
      'message': 'Succesfully invite all the participant',
      'data': []
    }
    qr_code_list = []
    with atomic():
      for email in invitation_data['list_email']:
        invitation_exist = SpaceReservationInvitation.objects.filter(user=email, space_reservation=invitation_data['space_reservation']).exists()
        if invitation_exist:
          set_rollback(True)
          return Response({"message": "A participant already invited to this reservation"}, status=status.HTTP_409_CONFLICT)
        
        user = CustomUser.objects.filter(email=email)
        
        if not user.exists():
          set_rollback(True)
          return Response({"message": "A participant is not registered in this app"}, status=status.HTTP_400_BAD_REQUEST)
        user = user.first()
        invitation = SpaceReservationInvitation.objects.create(
          space_reservation = reservation,
          user = user
        )
        invitation.save()
        qr_code_list.append(invitation.id)
        response_data['data'].append(SpaceReservationInvitationSerializer(invitation).data)
        print(email)
      reserver_invitation = SpaceReservationInvitation.objects.create(
          space_reservation = reservation,
          user = reserver
        )
      reserver_invitation.save()  
    invitation_data['list_email'].append(reserver.email)
    qr_code_list.append(reserver_invitation.id)
    
    send_invitation_email(
      subject='[UI BRI Works] Invitation for co-working space reservation',
      recipient_list=invitation_data['list_email'],
      location=reservation.space_id.location,
      time=generate_time_string(reservation.start_time, reservation.end_time),
      qr_code_data_list=qr_code_list)
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
    # space_review_exist = SpaceReview.objects.filter(user=user, space=space)
    
    # if space_review_exist.exists():
    #   return Response({
    #     'message': 'User already reviewed this space',
    #   }, status=status.HTTP_409_CONFLICT)
    
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
    reservations = SpaceReservation.objects.filter(status='REGISTERED', start_time__lt=end_time, end_time__gt=start_time)
    reservation_exist = reservations.exists()
    return Response({
      'message': 'Succesfully retrieved availability',
      'data': {
        'exist': reservation_exist
      }
    })
    
    
# Create your views here.
