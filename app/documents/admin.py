from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from django.utils.safestring import mark_safe

from documents import models as document_models


@admin.register(document_models.Document)
class DocumentAdmin(UnfoldModelAdmin):
    readonly_fields = [
        "uid",
        "user",
        "created_at",
        "updated_at",
        "file_preview",
    ]
    search_fields = [
        "title",
        "description",
        "uid",
    ]
    list_filter = (
        "status",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
    list_display = (
        "uid",
        "user",
        "title",
        "status",
        "description",
        "created_at",
        "updated_at",
    )
    fields = [
        "uid",
        "user",
        "title",
        "description",
        "document_file",
        "file_preview",
        "status",
        "created_at",
        "updated_at",
    ]

    def file_preview(self, obj):
        if obj.document_file:
            return mark_safe(f'<a href="{obj.document_file.url}" target="_blank">View File</a>')
        return "No file uploaded"