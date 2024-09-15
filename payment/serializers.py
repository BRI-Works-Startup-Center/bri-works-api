from rest_framework import serializers

class CreateSnapPaymentResponse(serializers.Serializer):
  token = serializers.CharField()
  redirect_url = serializers.CharField() 

class MidtransCallbackRequest(serializers.Serializer):
  transaction_id = serializers.CharField()
  transaction_status = serializers.CharField()
  fraud_status = serializers.CharField()
  status_code = serializers.CharField()
  order_id = serializers.CharField()
  gross_amount = serializers.CharField()
  signature_key = serializers.CharField()

class GetPaymentStatusResponse(serializers.Serializer):
  order_id = serializers.CharField()
  payment_status = serializers.CharField()