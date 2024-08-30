from django.db import models
from authentication.models import CustomUser
import uuid

class Space(models.Model):
  id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
  name = models.CharField(max_length=100)
  hourly_price = models.IntegerField()
  daily_price = models.IntegerField()
  picture = models.ImageField(upload_to='space/', blank=True, null=True)
  size = models.IntegerField()
  description = models.TextField(default='')
  tv_facility = models.BooleanField()
  wifi_facility = models.BooleanField()
  sound_system_facility = models.BooleanField()
  location = models.CharField(max_length=100)
  capacity = models.IntegerField()
  rate = models.FloatField(blank=True, null=True)

  
  def __str__(self):
    return self.name
  
  def update_rate(self):
    avg_star = self.space_reviews.aggregate(models.Avg('star'))['star__avg']
    self.rate = avg_star if avg_star else 0.0
    self.save()

class SpaceReservation(models.Model):
  id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
  space_id = models.ForeignKey(Space, related_name="reservations", on_delete=models.CASCADE)
  user = models.ForeignKey(CustomUser, to_field="email", related_name="reserver", on_delete=models.CASCADE, default=None)
  start_time = models.DateTimeField()
  end_time = models.DateTimeField()
  participant_count = models.IntegerField()
  price = models.IntegerField()
  
  def __str__(self):
    return str(self.id)

class SpaceReservationInvitation(models.Model):
  id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
  space_reservation = models.ForeignKey(SpaceReservation, related_name="invitations", on_delete=models.CASCADE)
  user = models.ForeignKey(CustomUser, to_field="email", related_name="invitee", on_delete=models.CASCADE, default=None)
  
  def __str__(self):
    return str(self.id)

class SpaceReview(models.Model):
  id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
  user = models.ForeignKey(CustomUser, to_field="email", related_name="user_space_reviews", on_delete=models.CASCADE, blank=True, null=True)
  space = models.ForeignKey(Space, related_name="space_reviews", on_delete=models.CASCADE) 
  star = models.IntegerField()
  comment = models.TextField()
  
  def __str__(self):
    return str(self.id) + str(self.star) + str(self.comment)

  
# Create your models here.
