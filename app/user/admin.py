from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from leaflet.admin import LeafletGeoAdmin

from user import models

# unregister unnecessary models
from django.contrib.auth.admin import GroupAdmin
from rest_framework_simplejwt.token_blacklist.admin import OutstandingTokenAdmin, BlacklistedTokenAdmin
OutstandingTokenAdmin.has_module_permission = lambda self, request: False
BlacklistedTokenAdmin.has_module_permission = lambda self, request: False
GroupAdmin.has_module_permission = lambda self, request: False


@admin.register(models.User)
class UserAdmin(UnfoldModelAdmin, LeafletGeoAdmin):
    readonly_fields = [
        "uid",
        "created_at",
        "last_login",

        "longitude",
        "latitude",
        "has_paid",
    ]
    search_fields = [
        "email",
        "name",
        "surname",
        "uid",
    ]
    list_display = (
        "uid",
        "name",
        "surname",
        "email",
        "is_email_verified",
        "is_phone_verified",
        "created_at",
        "has_paid",
    )
    fields = [
        "uid",
        "notification_settings",
        "email",
        "name",
        "phone",
        "is_staff",
        "is_email_verified",
        "is_phone_verified",
        "password",
        "is_active",
        "avatar",
        "current_location",
        "created_at",
        "last_login",

        "longitude",
        "latitude",

        "has_paid",
    ]

    def has_paid(self, obj):
        return obj.has_paid

    def has_delete_permission(self, request, obj=None):
        return obj != request.user
    
    def longitude(self, obj):
        return obj.current_location.x
    
    def latitude(self, obj):
        return obj.current_location.y

    # on save if password is not encrypted encrypt it
    def save_model(self, request, obj, form, change):
        if not obj.password:
            obj.save()
        if obj.password and not obj.password.startswith("pbkdf2_sha256"):
            obj.set_password(obj.password)
        obj.save()
