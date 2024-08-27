from django.urls import path
from .views import MemberRegistrationAPI, MemberPackageAPI, MemberRegistrationFormAPI

urlpatterns = [
    path('', MemberPackageAPI.as_view()),
    path('register', MemberRegistrationAPI.as_view()),
    path('form', MemberRegistrationFormAPI.as_view()),
]
