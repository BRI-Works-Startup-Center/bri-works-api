from django.urls import path
from .views import PaymentFailedPageView, PaymentNotificationCallbackAPI, EventRegistrationPaymentStatusAPI, SpaceReservationPaymentStatusAPI, FoodOrderPaymentStatusAPI, MemberRegistrationPaymentStatusAPI, PaymentSuccessPageView

urlpatterns = [
    path('notification', PaymentNotificationCallbackAPI.as_view()),
    path('status/event', EventRegistrationPaymentStatusAPI.as_view()),
    path('status/space', SpaceReservationPaymentStatusAPI.as_view()),
    path('status/food', FoodOrderPaymentStatusAPI.as_view()), 
    path('status/member', MemberRegistrationPaymentStatusAPI.as_view()),
    path('success-page', PaymentSuccessPageView.as_view()),
    path('fail-page', PaymentFailedPageView.as_view()),
]
