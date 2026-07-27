"""
Accounts admin configuration.

We inline the UserProfile into the User admin so both
can be edited from a single page — a clean UX pattern.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """
    Displays UserProfile fields directly inside the User admin page.
    This means admins never need to navigate to a separate profile page.
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        'title',
        'bio',
        'location',
        'years_of_experience',
        'profile_picture',
        'resume',
        'github_url',
        'linkedin_url',
        'email',
        'website_url',
        'twitter_url',
        'meta_description',
    )


class UserAdmin(BaseUserAdmin):
    """Extended User admin with profile inline."""
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']


# Unregister the default User admin and register our extended version
admin.site.unregister(User)
admin.site.register(User, UserAdmin)