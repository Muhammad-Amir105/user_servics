from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'pending_vendor')}),
    )

    actions = ['approve_vendors']

    def approve_vendors(self, request, queryset):
        queryset.update(role='vendor', pending_vendor=False)
        self.message_user(request, "Selected users have been approved as vendors.")

    approve_vendors.short_description = "Approve selected vendors"

admin.site.register(CustomUser, CustomUserAdmin)