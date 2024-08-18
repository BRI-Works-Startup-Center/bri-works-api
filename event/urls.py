from django.urls import path, re_path
from .views import EventAPI, EventDetailAPI, EventReviewAPI, EventRegistrationAPI, UpcomingEventAPI, EventRegistrationDetailAPI

urlpatterns = [
  path("", EventAPI.as_view()),
  path("<uuid:event_id>", EventDetailAPI.as_view()),
  path("review", EventReviewAPI.as_view()),
  path("register", EventRegistrationAPI.as_view()),
  path("upcoming", UpcomingEventAPI.as_view()),
  path("registered/<uuid:registration_id>", EventRegistrationDetailAPI.as_view())
]
