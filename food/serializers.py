from rest_framework import serializers
from .models import Tenant, FoodBeverage, Order, OrderItem

class TenantSerializer(serializers.ModelSerializer):
  class Meta:
    model = Tenant
    fields = ["id", "name", "location", "rate", "picture"]


class FoodBeverageSerializer(serializers.ModelSerializer):
  class Meta:
    model = FoodBeverage
    fields = ["id", "picture", "name", "price", "type"]
    
class TenantCatalogSerializer(serializers.ModelSerializer):
  foodbeverages = serializers.SerializerMethodField()
  
  class Meta:
    model = Tenant
    fields = ["id", "name", "foodbeverages"]
    
  def get_foodbeverages(self, obj):
    foodbeverages = obj.foodbeverages.all()
    categorized_foods = {
      'food': [],
      'beverage': [],
      'other': []
    }
    for food in foodbeverages:
      type = food.type
      if type not in categorized_foods:
        categorized_foods[type] = []
      categorized_foods[type].append(FoodBeverageSerializer(food).data)
    return categorized_foods

class OrderItemSerializer(serializers.ModelSerializer):
  item = serializers.PrimaryKeyRelatedField(queryset=FoodBeverage.objects.all())
  total_price=serializers.IntegerField(required=False)
  class Meta:
    model = OrderItem
    fields = ['item', 'quantity', 'total_price']

class OrderItemResponse(serializers.ModelSerializer):
  item = FoodBeverageSerializer()
  total_price=serializers.IntegerField(required=False)
  class Meta:
    model = OrderItem
    fields = ['item', 'quantity', 'total_price']
    
class OrderSerializer(serializers.ModelSerializer):
  order_items = OrderItemSerializer(many=True)
  class Meta:
    model = Order
    fields = ['id', 'tenant', 'order_items', 'status', 'total_price']
    
class OrderResponse(serializers.ModelSerializer):
  order_items = OrderItemResponse(many=True)
  class Meta:
    model = Order
    fields = ['id', 'tenant', 'order_items', 'status', 'total_price']

class OrderHistoryItemResponse(serializers.Serializer):
  id = serializers.UUIDField()
  tenant_name = serializers.CharField()
  total_price = serializers.IntegerField()
  food_picture = serializers.CharField(allow_null=True)
  food_name = serializers.CharField()
  status = serializers.CharField()
  menu_count = serializers.CharField()
  
