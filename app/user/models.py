from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from uuid import uuid4

from core import exception
from core.models import safe_file_path
from core.validators import validate_file_size, email_validator, phone_validator



class UserManager(BaseUserManager):
    """User manager class for creating users and superusers"""

    def create_user(
        self, email: str, password: str = None, **extra_fields: dict
    ) -> "User":
        """
        Creates and saves new user
        :param email: user email
        :param password: user password
        :param extra_fields: additional parameters
        :return: created user model
        """
        if not email:
            raise exception.get(ValueError, "User must have email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email: str, password: str) -> "User":
        """
        Creates and saves new super user
        :param email: user email
        :param password: user password
        :return: created user model
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    uid = models.UUIDField(unique=True, default=uuid4, editable=False)
    send_push_notifications = models.BooleanField(
        default=True,
        verbose_name=_("Send push notifications"),
    )
    notification_settings = models.OneToOneField(
        "user.UserNotificationSettings",
        on_delete=models.CASCADE,
        verbose_name=_("Notification settings"),
        null=True,
        blank=True,
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        error_messages={"unique": "email_already_used"},
        verbose_name=_("Email"),
        validators=[email_validator],
    )
    name = models.CharField(default="", max_length=64, verbose_name=_("Name"))
    phone = models.CharField(
        max_length=255,
        verbose_name=_("Phone"),
        null=True,
        blank=True,
        validators=[phone_validator],
        unique=True,
        error_messages={"unique": "phone_already_used"},
    )
    is_phone_verified = models.BooleanField(
        default=False,
        verbose_name=_("Is phone verified?"),
    )
    name = models.CharField(default="", max_length=64, verbose_name=_("Name"))
    surname = models.CharField(default="", max_length=64, verbose_name=_("Surname"))
    avatar = models.ImageField(
        upload_to=safe_file_path,
        null=True,
        default=None,
        blank=True,
        validators=[validate_file_size],
        verbose_name=_("Avatar"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name=_("Created at")
    )
    is_email_verified = models.BooleanField(
        default=False, verbose_name=_("Is email verified?")
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_("Is staff?"),
        help_text=_("Use this option for create Staff"),
    )
    current_location = models.PointField(
        verbose_name=_("Current location"),
        blank=True,
        null=True,
    )
    objects = UserManager()
    USERNAME_FIELD = "email"
    
    @property
    def get_firebase_token(self) -> str:
        return None
    
    @property
    def get_social_info(self) -> dict:
        return {}

    def __str__(self) -> str:
        return f"{self.email}"
    
    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        if not self.notification_settings:
            self.notification_settings = UserNotificationSettings.objects.create()
        super(User, self).save(*args, **kwargs)
    

class UserNotificationSettings(models.Model):
    pass


class UserPushToken(models.Model):
    user = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        related_name="push_tokens",
    )
    push_id = models.CharField(
        max_length=255,
        unique=True,
        blank=False,
        null=False,
        verbose_name=_("Push notification id"),
    )

    def __new__(cls, *args, **kwargs):
        """
        Use like this:
        UserPushToken(user=User(1), push_id='Some string')
        """
        instance = super().__new__(cls)
        for item in kwargs.keys():
            if hasattr(instance, item):
                setattr(instance, item, kwargs.get(item))
        return instance
