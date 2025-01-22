from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin interface for CustomUser.
    """
    model = CustomUser
    list_display = ('username', 'email',  'is_active', 'is_staff')
    search_fields = ('username', 'email' )
    ordering = ('username',)