from django.contrib import admin
from .models import PaymentTransaction

class PaymentTransactionAdmin(admin.ModelAdmin):
  list_display = ('id', 'order_id', 'midtrans_token', 'redirect_url', 'gross_amount', 'type', 'payment_status', 'fraud_status', 'payment_time')
  search_fields = ('id', 'order_id', 'midtrans_token', 'type')
  ordering = ('id',)

admin.site.register(PaymentTransaction, PaymentTransactionAdmin)

# Register your models here.
