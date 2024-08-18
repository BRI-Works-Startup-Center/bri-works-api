from django.contrib import admin
from .models import Event, EventReview, EventRegistration

# Register your models here.
class EventAdmin(admin.ModelAdmin):
  list_display = ("id", "title", "location", "price", "start_time", "end_time", "picture", "description", "type", "capacity")
  search_fields = ("title",)
  ordering = ("-start_time",)
  
class EventReviewAdmin(admin.ModelAdmin):
  list_display = ("id", "star", "comment", "event")
  search_fields = ("id",)
  ordering = ("event",)

class EventRegistrationAdmin(admin.ModelAdmin):
  list_display = ("id", "event", "user", "status", "registration_date")
  search_fields = ("status",)
  ordering = ("registration_date",)
  
admin.site.register(Event, EventAdmin)
admin.site.register(EventReview, EventReviewAdmin)
admin.site.register(EventRegistration, EventRegistrationAdmin)