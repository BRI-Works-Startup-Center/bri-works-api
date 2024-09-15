from django.db import models

import uuid

class PaymentTransaction(models.Model):
  TYPE_CHOICES = [
    ('EVENT', 'EVENT'),
    ('SPACE', 'SPACE'),
    ('FOOD', 'FOOD'),
    ('MEMBER', 'MEMBER')
  ]
  id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
  order_id = models.CharField(max_length=100, unique=True)
  midtrans_token = models.CharField(max_length=100, unique=True)
  redirect_url = models.CharField(null=True, blank=True)
  gross_amount = models.IntegerField()
  type = models.CharField(choices=TYPE_CHOICES, default='EVENT')
  payment_status = models.CharField(max_length=100, default='pending')
  fraud_status = models.CharField(max_length=100, null=True, blank=True)
  payment_time = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return f'{self.id} Payment'

# Create your models here.
