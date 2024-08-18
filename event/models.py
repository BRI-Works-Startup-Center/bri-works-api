from django.db import models
from authentication.models import CustomUser

import uuid

class Event(models.Model):
  TYPE_CHOICES = [
    ('WORKSHOP', 'WORKSHOP'),
    ('SEMINAR', 'SEMINAR')
  ]
  id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
  title = models.CharField(max_length=100)
  company = models.CharField(max_length=100, null=True, blank=True)
  location = models.CharField(max_length=100)
  price = models.IntegerField()
  start_time = models.DateTimeField()
  end_time = models.DateTimeField()
  picture = models.CharField(null=True, blank=True)
  description = models.TextField()
  type = models.CharField(choices=TYPE_CHOICES, default='WORKSHOP')
  capacity = models.IntegerField()
  
  def __str__(self):
    return self.title

class EventRegistration(models.Model):
  STATUS_CHOICES = [
    ('REGISTERED', 'REGISTERED'),
    ('ATTENDED', 'ATTENDED')
  ]
  id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
  event = models.ForeignKey(Event, related_name="registrations", on_delete=models.CASCADE)
  user = models.ForeignKey(CustomUser, to_field="email", related_name="registrant", on_delete=models.CASCADE)
  registration_date = models.DateTimeField(auto_now_add=True)
  status = models.CharField(choices=STATUS_CHOICES, default='REGISTERED')
    
  
  def __str__(self):
    return str(self.user) + str(self.event)

class EventReview(models.Model):
  id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
  event = models.ForeignKey(Event, related_name="reviews", on_delete=models.CASCADE)
  star = models.IntegerField()
  comment = models.TextField()
  
  def __str__(self):
    return self.comment
# Create your models here.