from django.db import models
import uuid
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from authentication.models import CustomUser

class MemberPackage(models.Model):
  id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
  name = models.CharField(max_length=100)
  validity_month = models.IntegerField()
  accesses = models.JSONField(default=list)
  facilities = models.JSONField(default=list)
  price = models.IntegerField()
  def __str__(self):
    return self.name

class MemberRegistration(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user = models.ForeignKey(CustomUser, to_field="email", related_name="member", on_delete=models.CASCADE)
    package = models.ForeignKey(MemberPackage, related_name='registrations', on_delete=models.CASCADE, blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.expiry_date:
            self.expiry_date = timezone.now() + relativedelta(months=self.package.validity_month)
        super().save(*args, **kwargs)

    def is_active(self):
        return timezone.now() < self.end_date
    
    def __str__(self):
        return str(self.id)
  
  
# Create your models here.
