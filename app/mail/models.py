from django.utils.translation import gettext_lazy as _
from django.db import models
from uuid import uuid4


class Mail(models.Model):
    uid = models.UUIDField(unique=True, default=uuid4, editable=False)
    user = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        related_name="mail_user",
        blank=True,
        null=True,
    )
    email = models.CharField(max_length=255)
    is_send = models.BooleanField(default=False)
    subject = models.CharField(max_length=500, verbose_name=_("Subject"))
    code = models.CharField(max_length=50, blank=True, null=True)
    body = models.TextField()
    error = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(
        verbose_name=_("Created at"), auto_now=True, editable=False
    )

    def __str__(self) -> str:
        return f"{self.email}"
    

class MailLogo(models.Model):
    logo = models.ImageField(upload_to="mail_logo")
    is_default = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.logo.url}"


