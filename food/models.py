from django.db import models
import uuid

class Tenant(models.Model):
  id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
  name = models.CharField(max_length=100)
  rate = models.FloatField()
  picture = models.CharField(null=True, blank=True)
  location = models.CharField(max_length=100)
  
  def __str__(self):
    return self.name
  
class FoodBeverage(models.Model):
  tenant = models.ForeignKey(Tenant, related_name="foodbeverages", on_delete=models.CASCADE)
  picture = models.CharField(null=True, blank=True)
  name = models.CharField()
  price = models.IntegerField()
  def __str__(self):
    return self.name

# Create your models here.
