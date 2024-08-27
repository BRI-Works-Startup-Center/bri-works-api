from django.urls import path
from .views import MemberRegistrationAPI, MemberPackageAPI

urlpatterns = [
    path('', MemberPackageAPI.as_view()),
    path('register', MemberRegistrationAPI.as_view()),
]
