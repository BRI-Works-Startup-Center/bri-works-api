from django.urls import path
from .views import LoginAPI, RegisterAPI

urlpatterns = [
  path('login', LoginAPI.as_view()),
  path('register', RegisterAPI.as_view())
]