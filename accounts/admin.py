from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'is_staff', 'is_active', 'role', 'profile_image')
    list_filter = ('is_staff', 'is_active', 'role')

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ( 'role', 'profile_image')}),
    )# type: ignore , it will work at runtime

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ( 'role', 'profile_image')}),
    )
