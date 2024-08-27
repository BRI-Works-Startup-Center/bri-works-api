from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from django.utils import timezone

from .models import Tenant, Order, OrderItem, FoodBeverage
from .serializers import TenantSerializer, TenantCatalogSerializer, OrderSerializer, OrderResponse, OrderHistoryItemResponse

class TenantAPI(APIView):
  def get(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
    tenants = Tenant.objects.all().order_by('-rate')
    serializer = TenantSerializer(tenants, many=True)
    response_data = {
      'message': 'Succesfully retrieved',
      'data': serializer.data
    }
    return Response(response_data)

class TenantCatalogAPI(APIView):
  def get(self, request, tenant_id):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
    tenant = Tenant.objects.filter(pk=tenant_id)[0]
    serializer = TenantCatalogSerializer(tenant)
    response_data = {
      'message': 'Succesfully retrieved',
      'data': serializer.data
    }
    return Response(response_data)

class OrderAPI(APIView):
  def post(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
    user_email = token[0].user
    order_data = OrderSerializer(data=request.data)
    order_data.is_valid(raise_exception = True)
    order_data = order_data.data
    tenant = Tenant.objects.get(pk=order_data['tenant'])
    if not tenant:
      return Response({"message": "No related event"}, status=status.HTTP_400_BAD_REQUEST)

    new_order = Order.objects.create(
      tenant=tenant,
      user=user_email,
    )
    
    new_order.save()
    new_order.total_price = 0
    for order_item_data in order_data['order_items']:
      foodbeverage = FoodBeverage.objects.get(pk=order_item_data['item'])
      order_item = OrderItem.objects.create(
        order=new_order,
        item=foodbeverage,
        quantity=order_item_data['quantity'],
        total_price=foodbeverage.price * order_item_data['quantity']
      )
      new_order.total_price = new_order.total_price + order_item.total_price 
      order_item.save()
    new_order.save()
    
    
    
    serializer = OrderSerializer(new_order)
    
    response_data = {
      'message': 'Order succesfully created.',
      'data': serializer.data
    }
    return Response(response_data, status=status.HTTP_201_CREATED)

class OrderDetailAPI(APIView):
  def get(self, request, order_id):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
    order_exist = Order.objects.filter(pk=order_id).exists()
    if not order_exist:
      return Response({
        'message': 'No matching order with given id',
        'status': status.HTTP_404_NOT_FOUND
      })
    order = Order.objects.get(pk=order_id)
    serializer = OrderResponse(order)
    
    response_data = {
      'message': 'Succesfully retrieved',
      'data': serializer.data
    }
    return Response(response_data)

class OrderHistoryAPI(APIView):
  def get(self, request):
    auth_header = request.headers.get('Authorization', '')
    token = Token.objects.filter(key=auth_header[6:])
    if not len(token):
      return Response({
        'message': 'User has not been authenticated'
      }, status=status.HTTP_401_UNAUTHORIZED)
    user_email = token[0].user
    now = timezone.now()
    orders = Order.objects.filter(user=user_email, created_at__lt=now).order_by('-created_at')
    response_data = {
      'message': 'Succesfully retrieved',
      'data': []
    }
    for order in orders:
      tenant = Tenant.objects.get(pk=order.tenant.id)
      items = OrderItem.objects.filter(order=order)
      data = {
        'id': order.id,
        'tenant_name': tenant.name,
        'total_price': order.total_price,
        # 'food_picture': items[0].item.picture,
        'tenant_picture': tenant.picture,
        # 'food_name': items[0].item.name,
        'items': items,
        'status': order.status,
        'menu_count': items.count()
      }
      serializer = OrderHistoryItemResponse(data)
      # serializer.is_valid(raise_exception=True)
      response_data['data'].append(serializer.data)
    return Response(response_data)
  

# Create your views here.
