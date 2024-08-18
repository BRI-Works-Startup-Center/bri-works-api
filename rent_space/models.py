from django.db import models
import uuid

class Space(models.Model):
  id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
  name = models.CharField(max_length=100)
  hourly_price = models.IntegerField()
  daily_price = models.IntegerField()
  picture = models.CharField(null=True, blank=True)
  size = models.IntegerField()
  description = models.TextField(default='')
  tv_facility = models.BooleanField()
  wifi_facility = models.BooleanField()
  sound_system_facility = models.BooleanField()
  location = models.CharField(max_length=100)
  capacity = models.IntegerField()
  
  def __str__(self):
    return self.name

# Create your models here.
