from django.contrib import admin
from .models import Space

class SpaceAdmin(admin.ModelAdmin):
  list_display = ("id", "name", "hourly_price", "daily_price", "picture", "size", "location", "capacity", "tv_facility", "wifi_facility", "sound_system_facility", "description")
  search_fields = ("id", "name")
  ordering = ("-name",)
  
admin.site.register(Space, SpaceAdmin)
# Register your models here.
