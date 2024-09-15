from django.urls import path
from .views import PaymentNotificationCallbackAPI, EventRegistrationPaymentStatusAPI, SpaceReservationPaymentStatusAPI, FoodOrderPaymentStatusAPI, MemberRegistrationPaymentStatusAPI

urlpatterns = [
    path('notification', PaymentNotificationCallbackAPI.as_view()),
    path('status/event', EventRegistrationPaymentStatusAPI.as_view()),
    path('status/space', SpaceReservationPaymentStatusAPI.as_view()),
    path('status/food', FoodOrderPaymentStatusAPI.as_view()), 
    path('status/member', MemberRegistrationPaymentStatusAPI.as_view()), 
]
