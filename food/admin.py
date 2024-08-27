from django.contrib import admin
from .models import Tenant, FoodBeverage, Order, OrderItem, TenantReview

class TenantAdmin(admin.ModelAdmin):
  list_display = ("id", "name", "rate", "picture", "location")
  search_fields = ("name", "id")
  ordering = ("name",)

class FoodBeverageAdmin(admin.ModelAdmin):
  list_display = ("id", "tenant", "name", "picture", "price", "type")
  search_fields = ("name", "tenant", "id")
  ordering = ("id",)

class OrderAdmin(admin.ModelAdmin):
  list_display = ("id", "user", "tenant", "created_at", "status", "total_price")
  search_fields = ("id", "user", "tenant", "status")
  ordering = ("id",)
  
class OrderItemAdmin(admin.ModelAdmin):
  list_display = ("id", "order", "item", "quantity", "total_price")
  search_fields = ("id", "order", "item", "status")
  ordering = ("id",)

class TenantReviewAdmin(admin.ModelAdmin):
  list_display = ("id", "star", "comment", "tenant", "user")
  search_fields = ("id",)
  ordering = ("tenant",)
  
admin.site.register(Tenant, TenantAdmin)
admin.site.register(FoodBeverage, FoodBeverageAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(TenantReview, TenantReviewAdmin)

# Register your models here.
