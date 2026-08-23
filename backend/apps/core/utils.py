"""
Shared utility functions.
"""
import re
import logging

logger = logging.getLogger(__name__)


def sanitize_html(content):
    """
    Basic HTML sanitizer for blog post content.

    Strips script tags and event handler attributes
    (onclick, onload, onerror, etc.) to prevent XSS.

    This is a defence-in-depth measure. The primary
    protection is Django's template auto-escaping.
    Only call this if you're rendering content with |safe.
    """
    if not content:
        return content

    # Remove script tags and their content
    content = re.sub(
        r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>',
        '',
        content,
        flags=re.IGNORECASE
    )

    # Remove event handler attributes
    content = re.sub(
        r'\s+on\w+\s*=\s*["\'][^"\']*["\']',
        '',
        content,
        flags=re.IGNORECASE
    )

    # Remove javascript: protocol in href/src attributes
    content = re.sub(
        r'(href|src)\s*=\s*["\']javascript:[^"\']*["\']',
        '',
        content,
        flags=re.IGNORECASE
    )

    return content


def get_client_ip(request):
    """
    Extracts the real client IP from a Django request.
    Checks X-Forwarded-For first (set by Nginx/load balancer).
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')