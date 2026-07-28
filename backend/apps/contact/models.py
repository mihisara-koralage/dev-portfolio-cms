"""
Contact models: stores messages submitted through the contact form.
"""
from django.db import models
from apps.core.models import TimeStampedModel


class ContactMessage(TimeStampedModel):
    """
    A message submitted through the public contact form.

    Messages are stored and can be marked as read or deleted
    through the admin dashboard.
    """
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    is_read = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Mark as read once you have reviewed the message."
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Stored for spam detection purposes."
    )

    class Meta:
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.subject}"