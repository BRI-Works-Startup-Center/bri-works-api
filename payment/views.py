from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import MidtransCallbackRequest, GetPaymentStatusResponse
from .utils import verify_notification
from django.db.transaction import atomic, set_rollback
from .models import PaymentTransaction
from rent_space.models import SpaceReservation
from event.models import EventRegistration
from food.models import Order
from member_registration.models import MemberRegistration
from event.utils import send_invitation_email, generate_time_string
from rest_framework.authtoken.models import Token
from django.views.generic import TemplateView

import os

class PaymentNotificationCallbackAPI(APIView):
  def post(self, request):
    request_data = MidtransCallbackRequest(data=request.data)
    request_data.is_valid(raise_exception=True)
    request_data = request_data.data
    notification_verification = verify_notification(
      order_id=request_data['order_id'],
      status_code=request_data['status_code'],
      gross_amount=request_data['gross_amount'],
      signature_key=request_data['signature_key'])
    
    if not notification_verification:
      return Response({
        'message': 'Request is not authentic'
      }, status=status.HTTP_403_FORBIDDEN)

    with atomic():
      payment_transaction = PaymentTransaction.objects.filter(order_id=request_data['order_id']).first()
      if not payment_transaction:
        return Response({
        'message': 'Payment transaction not found'
      }, status=status.HTTP_404_NOT_FOUND)
      success_status_set = {'capture', 'settlement'}
      failed_status_set = {'deny', 'cancel', 'expire', 'failure'} 
      # Handle setting the status for space reservation 
      if payment_transaction.type == 'SPACE':
        reservation_id = payment_transaction.order_id.split('_')[1]
        space_reservation = SpaceReservation.objects.filter(id=reservation_id)
        if not space_reservation.exists():
          return Response({
            'message': 'No space reservation of this payment'
          }, status=status.HTTP_400_BAD_REQUEST)
        space_reservation = space_reservation.first()
        if request_data['transaction_status'] in success_status_set:
          space_reservation.status = 'REGISTERED'
        elif request_data['transaction_status'] in failed_status_set:
          space_reservation.status = 'CANCELLED'
        else:
          space_reservation.status = 'CANCELLED'
        space_reservation.save()
      # Handle setting the status for event registration
      elif payment_transaction.type == 'EVENT':
        registration_id = payment_transaction.order_id.split('_')[1]
        event_registration = EventRegistration.objects.filter(id=registration_id)
        if not event_registration.exists():
          return Response({
            'message': 'No event registration of this payment'
          }, status=status.HTTP_400_BAD_REQUEST)
        event_registration = event_registration.first()
        if request_data['transaction_status'] in success_status_set:
          event_registration.status = 'REGISTERED'
          event = event_registration.event
          send_invitation_email(
            subject='[UI BRI Works] Invitation for co-working space reservation',
            recipient_list=[event_registration.user.email],
            event=event.title,
            location=event.location,
            time=generate_time_string(event.start_time, event.end_time),
            qr_code_data_list=[event_registration.id])
        elif request_data['transaction_status'] in failed_status_set:
          event_registration.status = 'CANCELLED'
        else:
          event_registration.status = 'CANCELLED'
        event_registration.save()
      # Handle setting the status for food order
      elif payment_transaction.type == 'FOOD':
        order_id = payment_transaction.order_id.split('_')[1]
        order = Order.objects.filter(id=order_id)
        if not order.exists():
          return Response({
            'message': 'No food order of this payment'
          }, status=status.HTTP_400_BAD_REQUEST)
        order = order.first()
        if request_data['transaction_status'] in success_status_set:
          order.status = 'REGISTERED'
        elif request_data['transaction_status'] in failed_status_set:
          order.status = 'CANCELLED'
        else:
          order.status = 'CANCELLED'
        order.save()
      # Handle setting the status for member registration
      elif payment_transaction.type == 'MEMBER':
        registration_id = payment_transaction.order_id.split('_')[1]
        member_registration = MemberRegistration.objects.filter(id=registration_id)
        if not member_registration.exists():
          return Response({
            'message': 'No member registration of this payment'
          }, status=status.HTTP_400_BAD_REQUEST)
        member_registration = member_registration.first()
        if request_data['transaction_status'] in success_status_set:
          member_registration.status = 'REGISTERED'
        elif request_data['transaction_status'] in failed_status_set:
          member_registration.status = 'CANCELLED'
        else:
          member_registration.status = 'CANCELLED'
        member_registration.save()
      else:
        set_rollback(True)
        return Response({
          'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
      payment_transaction.payment_status = request_data['transaction_status']
      payment_transaction.fraud_status = request_data['fraud_status']
      payment_transaction.save()
    return Response({
      'message': 'Notification succesfully received',
      'data': request_data
    })
    
class EventRegistrationPaymentStatusAPI(APIView):
  def get(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        "message": "User has not been authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    event_registration_id = request.GET.get("event_registration", None)
    order_id = f'event_{event_registration_id}'
    payment_transaction = PaymentTransaction.objects.filter(type = 'EVENT', order_id = order_id)
    if not payment_transaction.exists():
      return Response({
        'message': 'No payment transaction for the event',
      }, status=status.HTTP_400_BAD_REQUEST)
    payment_transaction = payment_transaction.first()
    serializer = GetPaymentStatusResponse(data={
      'order_id': order_id,
      'payment_status': payment_transaction.payment_status
    })
    serializer.is_valid(raise_exception=True)
    return Response({
      'message': 'Succesfully retrieved',
      'data': serializer.data
    })

class SpaceReservationPaymentStatusAPI(APIView):
  def get(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        "message": "User has not been authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    space_reservation_id = request.GET.get("space_reservation", None)
    order_id = f'space_{space_reservation_id}'
    payment_transaction = PaymentTransaction.objects.filter(type = 'SPACE', order_id = order_id)
    if not payment_transaction.exists():
      return Response({
        'message': 'No payment transaction for the space reservation',
      }, status=status.HTTP_400_BAD_REQUEST)
    payment_transaction = payment_transaction.first()
    serializer = GetPaymentStatusResponse(data={
      'order_id': order_id,
      'payment_status': payment_transaction.payment_status
    })
    serializer.is_valid(raise_exception=True)
    return Response({
      'message': 'Succesfully retrieved',
      'data': serializer.data
    })

class FoodOrderPaymentStatusAPI(APIView):
  def get(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        "message": "User has not been authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    food_order_id = request.GET.get("food_order", None)
    order_id = f'food_{food_order_id}'
    payment_transaction = PaymentTransaction.objects.filter(type = 'FOOD', order_id = order_id)
    if not payment_transaction.exists():
      return Response({
        'message': 'No payment transaction for the order',
      }, status=status.HTTP_400_BAD_REQUEST)
    payment_transaction = payment_transaction.first()
    serializer = GetPaymentStatusResponse(data={
      'order_id': order_id,
      'payment_status': payment_transaction.payment_status
    })
    serializer.is_valid(raise_exception=True)
    return Response({
      'message': 'Succesfully retrieved',
      'data': serializer.data
    })

class MemberRegistrationPaymentStatusAPI(APIView):
  def get(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        "message": "User has not been authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    member_registration_id = request.GET.get("member_registration", None)
    order_id = f'member_{member_registration_id}'
    payment_transaction = PaymentTransaction.objects.filter(type = 'MEMBER', order_id = order_id)
    if not payment_transaction.exists():
      return Response({
        'message': 'No payment transaction for the member registration',
      }, status=status.HTTP_400_BAD_REQUEST)
    payment_transaction = payment_transaction.first()
    serializer = GetPaymentStatusResponse(data={
      'order_id': order_id,
      'payment_status': payment_transaction.payment_status
    })
    serializer.is_valid(raise_exception=True)
    return Response({
      'message': 'Succesfully retrieved',
      'data': serializer.data
    })


class PaymentFinishPageView(TemplateView):
  template_name = 'payment-finish.html'
  def get_context_data(self, **kwargs):
      context = super().get_context_data()
      transaction_status = self.request.GET.get('transaction_status', 'pending')
      success_statuses = {'capture', 'settlement'}
      context_status = 'fail'
      if transaction_status in success_statuses:
         context_status = 'success'
      context['status'] = context_status
      return context

class PaymentPageView(TemplateView):
  template_name = 'payment-page.html'
  def get_context_data(self, **kwargs):
      context = super().get_context_data()
      midtrans_client_key = os.getenv('MIDTRANS_CLIENT_KEY')
      context['client_key'] = midtrans_client_key
      context['is_prod'] = os.getenv('MIDTRANS_IS_PRODUCTION')
      return context
    

# Create your views here.
