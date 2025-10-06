from django.contrib import admin
from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "user_type", "is_approved")
    list_filter = ("user_type", "is_approved")
    actions = ["approve_users"]

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)
    approve_users.short_description = "Approve selected employers"

admin.site.register(CustomUser, CustomUserAdmin)
from django.apps import AppConfig


