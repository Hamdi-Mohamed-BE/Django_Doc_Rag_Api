from uuid import uuid4

from django.utils.translation import gettext_lazy as _
from django.contrib.gis.db import models

from core.models import safe_file_path
from core.validators import validate_file_size

from documents import enums as document_enums


class Document(models.Model):
    uid = models.UUIDField(
        unique=True,
        default=uuid4,
        editable=False,
        verbose_name=_("Unique ID"),
    )
    user = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
    )
    document_file = models.FileField(
        upload_to=safe_file_path,
        validators=[validate_file_size],
        verbose_name=_("Document File"),
    )
    status = models.CharField(
        max_length=20,
        choices=document_enums.DocumentProcessingStatus.choices,
        default=document_enums.DocumentProcessingStatus.PENDING,
        verbose_name=_("Processing Status"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
    )


