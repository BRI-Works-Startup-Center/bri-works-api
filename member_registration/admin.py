from django.contrib import admin
from .models import MemberPackage, MemberRegistration

class MemberPackageAdmin(admin.ModelAdmin):
  list_display = ('id', 'name', 'validity_month', 'price', 'accesses', 'facilities')
  search_fields = ('id', 'name')
  ordering = ('name',)

class MemberRegistrationAdmin(admin.ModelAdmin):
  list_display = ('id', 'user', 'package', 'registration_date', 'expiry_date')
  search_fields = ('id', 'user', 'package')
  ordering = ('id', )

admin.site.register(MemberPackage, MemberPackageAdmin)
admin.site.register(MemberRegistration, MemberRegistrationAdmin)
# Register your models here.
