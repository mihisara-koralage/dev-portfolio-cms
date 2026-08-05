"""
Public context processors.

Injected into every template rendered by the public app.
Provides profile data globally so nav and footer always
have access to social links and the owner's name.
"""
from apps.accounts.models import UserProfile


def profile(request):
    """
    Injects the site owner's profile into every template context.
    Uses select_related to avoid an extra query for the User model.
    Result is cached on the request object to avoid repeated DB hits
    on the same request.
    """
    if not hasattr(request, '_cached_profile'):
        try:
            request._cached_profile = UserProfile.objects.select_related(
                'user'
            ).first()
        except Exception:
            request._cached_profile = None
    return {'site_profile': request._cached_profile}