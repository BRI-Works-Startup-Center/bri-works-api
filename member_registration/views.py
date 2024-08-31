from django.shortcuts import render
from rest_framework.views import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import status
from django.utils import timezone
from rest_framework.views import APIView
from dateutil import parser
 
from .serializers import MemberRegistrationRequest, MemberRegistrationSerializer, MemberPackageSerializer, UserMemberFormSerializer
from .models import MemberRegistration, MemberPackage

class MemberRegistrationAPI(APIView):
  def post(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
    user = token[0].user
    request_data = MemberRegistrationRequest(data=request.data)
    request_data.is_valid(raise_exception=True)
    request_data = request_data.data
    package = MemberPackage.objects.get(pk=request_data['package'])
    current_membership = MemberRegistration.objects.filter(user = user, expiry_date__gt = timezone.now())
    if current_membership.exists():
      return Response({
        'message': 'User already has its own membership',
        'status': status.HTTP_409_CONFLICT
      })
    new_membership = MemberRegistration.objects.create(user = user, package = package)
    new_membership.save()
    serializer = MemberRegistrationSerializer(new_membership)
    response_data = {
      'message': 'Succesfully created the membership',
      'data': serializer.data
    }
    return Response(response_data, status=status.HTTP_201_CREATED)
  
  def get(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
    user = token[0].user
    subscription = MemberRegistration.objects.filter(user=user, expiry_date__gt=timezone.now())
    if not subscription.exists():
      return Response({
        'message': 'User has no active subscription'
      }, status=status.HTTP_404_NOT_FOUND)
    serializer = MemberRegistrationSerializer(subscription[0])
    response_data = {
      'message': 'Succesfully retrieved',
      'data': serializer.data
    }
    return Response(response_data)
  


class MemberRegistrationFormAPI(APIView):
  def get(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
    user = token[0].user
    serializer = UserMemberFormSerializer(user)
    response_data = {
      'message': 'Succesfully retrieved',
      'data': serializer.data
    }
    return Response(response_data)
      
    
    

class MemberPackageAPI(APIView):
  def get(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
    packages = MemberPackage.objects.all().order_by('-price')
    serializer = MemberPackageSerializer(packages, many=True)
    response_data = {
      'message': 'Successfully retrieved',
      'data': serializer.data
    }
    return Response(response_data)
# Create your views here.
