from django.db.models import TextChoices

class DocumentProcessingStatus(TextChoices):
    """Enumeration for document processing statuses."""
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"