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
  
  def __str__(self):
    return self.name

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
# Create your models here.
