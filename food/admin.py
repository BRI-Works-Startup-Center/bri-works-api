from django.contrib import admin
from .models import Tenant

class TenantAdmin(admin.ModelAdmin):
  list_display = ("id", "name", "rate", "picture", "location")
  search_fields = ("name", "id")
  ordering = ("-name",)
  
admin.site.register(Tenant, TenantAdmin)

# Register your models here.
