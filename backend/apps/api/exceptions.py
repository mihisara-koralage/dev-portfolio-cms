"""
Custom API exception handlers.
"""
from django.http import JsonResponse
from django_ratelimit.exceptions import Ratelimited


def ratelimited_error(request, exception):
    """
    Called when a rate limit is exceeded.
    Returns JSON instead of Django's default HTML 403 page.
    """
    return JsonResponse(
        {
            'detail': 'Too many requests. Please wait before trying again.',
            'code': 'rate_limited',
        },
        status=429
    )