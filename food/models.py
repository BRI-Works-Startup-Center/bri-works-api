from django.db import models
import uuid

from authentication.models import CustomUser

class Tenant(models.Model):
  id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
  name = models.CharField(max_length=100)
  rate = models.FloatField()
  picture = models.CharField(null=True, blank=True)
  location = models.CharField(max_length=100)
  def __str__(self):
    return self.name
  def update_rate(self):
    avg_star = self.tenant_reviews.aggregate(models.Avg('star'))['star__avg']
    self.rate = avg_star if avg_star else 0.0
    self.save()
     
  
class FoodBeverage(models.Model):
  TYPE_CHOICES = [
    ('FOOD', 'FOOD'),
    ('BEVERAGE', 'BEVERAGE'),
    ('OTHER', 'OTHER')
  ]
  tenant = models.ForeignKey(Tenant, related_name="foodbeverages", on_delete=models.CASCADE)
  picture = models.CharField(null=True, blank=True)
  name = models.CharField()
  price = models.IntegerField()
  type = models.CharField(choices=TYPE_CHOICES, default='FOOD')
  def __str__(self):
    return self.name
  
class Order(models.Model):
  STATUS_CHOICES = [
    ('ORDERED', 'ORDERED'),
    ('PROCESSING', 'PROCESSING'),
    ('DONE', 'DONE')
  ]
  id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
  user = models.ForeignKey(CustomUser, to_field="email", related_name="orderer", on_delete=models.CASCADE)
  tenant = models.ForeignKey(Tenant, related_name='orders', on_delete=models.CASCADE)
  created_at = models.DateTimeField(auto_now_add=True)
  total_price = models.IntegerField(null=True, blank=True)
  status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='DONE')
  def __str__(self):
    return f"Order {self.id} by {self.user.email}"

class OrderItem(models.Model):
  order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
  item = models.ForeignKey(FoodBeverage, related_name='order_items', on_delete=models.CASCADE)
  quantity = models.IntegerField()
  total_price = models.IntegerField()

  def __str__(self):
    return f"{self.quantity} x {self.item.name} in Order {self.order.id}"

class TenantReview(models.Model):
  id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
  tenant = models.ForeignKey(Tenant, related_name="tenant_reviews", on_delete=models.CASCADE)
  user = models.ForeignKey(CustomUser, to_field="email", related_name="tenant_review", on_delete=models.CASCADE)

  star = models.IntegerField()
  comment = models.TextField()
  
  def __str__(self):
    return self.comment
  
  

# Create your models here.
