from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core import exception
from core.helpers import convert_size
import re


def validate_file_size(value):
    filesize = value.size

    if filesize > settings.MAX_UPLOAD_SIZE:
        error_msg = _("File is bigger than max file size (%(file_size)s)") % {
            "file_size": convert_size(settings.MAX_UPLOAD_SIZE)
        }
        raise exception.get_list_error(ValidationError, error_msg)
    else:
        return value


def email_validator(value):
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", value):
        raise exception.get_list_error(ValidationError, _("Invalid email format"))
    return value


def phone_validator(value):
    if not re.match(r"^\+?1?\d{9,15}$", value):
        raise exception.get_list_error(
            ValidationError, _("Invalid phone number format")
        )
    return value
