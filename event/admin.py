from django.contrib import admin
from .models import Event

# Register your models here.
class EventAdmin(admin.ModelAdmin):
  list_display = ("title", "location", "price", "start_time", "end_time", "picture", "description", "type", "capacity")
  search_fields = ("title",)
  ordering = ("-start_time",)
  
admin.site.register(Event, EventAdmin)