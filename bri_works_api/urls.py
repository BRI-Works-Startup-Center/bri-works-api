"""
URL configuration for bri_works_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import HomeAPI, AvatarAPI, ProfileAPI, EmailAPI

urlpatterns = [
    path('api/v1/home', HomeAPI.as_view()),
    path('api/v1/avatar', AvatarAPI.as_view()),
    path('api/v1/profile', ProfileAPI.as_view()),
    path('api/v1/email', EmailAPI.as_view()),
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/event/', include('event.urls')),
    path('api/v1/space/', include('rent_space.urls')),
    path('api/v1/food/', include('food.urls')),
    path('api/v1/member/', include('member_registration.urls')),
    path('api/v1/payment/', include('payment.urls')),
]
