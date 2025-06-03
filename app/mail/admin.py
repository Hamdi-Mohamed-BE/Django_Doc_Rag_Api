from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from django.utils.safestring import mark_safe
from mail import models


@admin.register(models.Mail)
class MailAdmin(UnfoldModelAdmin):
    search_fields = ['user__email']
    list_display = ['user', 'email', 'is_send', 'created_at',]
    list_filter = ['is_send']

    # make all field read-only
    def get_readonly_fields(self, request, obj=None):
        fields = [f.name for f in self.model._meta.fields]
        preview_body = 'preview_body'
        if preview_body not in fields:
            fields.append(preview_body)
        return fields
    
    def preview_body(self, obj):
        if obj.body:
            return mark_safe(
                f'<div style="border: 1px solid #ccc; padding: 10px; '
                f'width: 600px; height: 400px; overflow: auto;">{obj.body}</div>'
            )
        return "-"
    
    preview_body.short_description = "Email Body Preview"


@admin.register(models.MailLogo)
class MailLogoAdmin(UnfoldModelAdmin):
    list_display = ['id', 'logo', 'is_default']
    list_filter = ['is_default']
    search_fields = ['logo']
