from django.contrib import admin
from .models import Space, SpaceReservation, SpaceReservationInvitation, SpaceReview

class SpaceAdmin(admin.ModelAdmin):
  list_display = ("id", "name", "hourly_price", "daily_price", "picture", "size", "location", "capacity", "tv_facility", "wifi_facility", "sound_system_facility", "description", "rate")
  search_fields = ("id", "name")
  ordering = ("-name",)

class SpaceReservationAdmin(admin.ModelAdmin):
  list_display = ("id", "space_id", "start_time", "end_time", "participant_count", "price")
  search_fields = ("id", "space_id")
  ordering = ("id",)

class SpaceReservationInvitationAdmin(admin.ModelAdmin):
  list_display = ("id", "space_reservation", "user")
  search_fields = ("id", "space_reservation",)
  ordering = ("id",)

class SpaceReviewAdmin(admin.ModelAdmin):
  list_display = ("id", "space", "star", "comment")
  search_fields = ("id", "space")
  ordering = ("id", "space")

admin.site.register(Space, SpaceAdmin)
admin.site.register(SpaceReservation, SpaceReservationAdmin)
admin.site.register(SpaceReservationInvitation, SpaceReservationInvitationAdmin)
admin.site.register(SpaceReview, SpaceReviewAdmin)


# Register your models here.
