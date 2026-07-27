"""
Accounts models.

UserProfile extends Django's built-in User model via a OneToOneField.
This keeps authentication concerns in Django's hands while allowing
us to add portfolio-specific fields like bio and social links.
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.models import TimeStampedModel


class UserProfile(TimeStampedModel):
    """
    Extended profile for the site owner (admin user).

    Linked 1:1 with Django's User model. Created automatically
    when a User is created via the post_save signal below.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text="The Django user this profile belongs to."
    )

    # Professional info
    title = models.CharField(
        max_length=100,
        blank=True,
        help_text="Professional title, e.g. 'Full Stack Developer & DevOps Engineer'."
    )
    bio = models.TextField(
        blank=True,
        help_text="Short biography displayed on the About section."
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g. 'Colombo, Sri Lanka'."
    )
    years_of_experience = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Years of professional experience."
    )

    # Profile picture
    profile_picture = models.ImageField(
        upload_to='profile/',
        null=True,
        blank=True,
        help_text="Profile photo displayed on the homepage."
    )
    resume = models.FileField(
        upload_to='resume/',
        null=True,
        blank=True,
        help_text="Latest resume PDF. Visitors will always download this version."
    )

    # Social links
    github_url = models.URLField(
        blank=True,
        help_text="Full GitHub profile URL."
    )
    linkedin_url = models.URLField(
        blank=True,
        help_text="Full LinkedIn profile URL."
    )
    email = models.EmailField(
        blank=True,
        help_text="Public contact email displayed on the website."
    )
    website_url = models.URLField(
        blank=True,
        help_text="Personal website URL if different from this portfolio."
    )
    twitter_url = models.URLField(
        blank=True,
        help_text="Twitter/X profile URL."
    )

    # SEO
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="SEO meta description for the homepage (max 160 chars)."
    )

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"Profile — {self.user.get_full_name() or self.user.username}"

    @property
    def full_name(self):
        """Returns the user's full name from the linked User model."""
        return self.user.get_full_name() or self.user.username

    @property
    def has_resume(self):
        """Returns True if a resume file has been uploaded."""
        return bool(self.resume)


# ----------------------------------------------------------------
# Signals
# ----------------------------------------------------------------

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a UserProfile when a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Automatically save the UserProfile when the User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()