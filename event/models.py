from django.db import models
import uuid

class Event(models.Model):
  TYPE_CHOICES = [
    ('WORKSHOP', 'WORKSHOP'),
    ('SEMINAR', 'SEMINAR')
  ]
  id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
  title = models.CharField(max_length=100)
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

class EventReview(models.Model):
  event = models.ForeignKey(Event, related_name="reviews", on_delete=models.CASCADE)
  star = models.IntegerField()
  comment = models.TextField()
  
  def __str__(self):
    return self.comment
# Create your models here.