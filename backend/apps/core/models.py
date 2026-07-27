"""
Core abstract models providing shared fields across all apps.
These models are never directly instantiated — they serve as
base classes that other models inherit from.
"""
import uuid
from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides:
    - UUID primary key (more secure than auto-increment integers for public APIs)
    - created_at timestamp (set once on creation)
    - updated_at timestamp (updated on every save)

    All models in this project inherit from this class.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this record."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this record was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when this record was last updated."
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.__class__.__name__} ({self.id})"