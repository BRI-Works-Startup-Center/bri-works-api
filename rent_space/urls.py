from django.urls import path, re_path
from .views import SpaceAPI, SpaceDetailAPI, SpaceReservationAPI, SpaceReservationInvitationAPI, UpcomingReservationAPI, AttendedReservationAPI, SpaceReservationInvitationDetailAPI

urlpatterns = [
  path("", SpaceAPI.as_view()),
  path("reserve", SpaceReservationAPI.as_view()),
  path("reserve/invite", SpaceReservationInvitationAPI.as_view()),
  path("upcoming", UpcomingReservationAPI.as_view()),
  path("attended", AttendedReservationAPI.as_view()),
  path("reserved/<uuid:invitation_id>", SpaceReservationInvitationDetailAPI.as_view()),
  path("<uuid:space_id>", SpaceDetailAPI.as_view()),
]