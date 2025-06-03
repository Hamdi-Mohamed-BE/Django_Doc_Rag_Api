import uuid
from django.conf import settings


def safe_file_path(instance, filename):
    """Generate file path for new files"""
    ext = filename.split(".")[-1]
    name = uuid.uuid4()
    parts = str(name).split("-")
    path = "/".join(parts)
    filename = f"{uuid.uuid4()}.{ext}"
    return f"{instance.__class__.__name__.lower()}/{path}/{filename}"
