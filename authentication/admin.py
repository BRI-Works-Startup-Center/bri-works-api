from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('email', 'phone_number', 'is_staff', 'is_active')
    search_fields = ('email', 'phone_number')
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)
