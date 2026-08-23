"""
Custom middleware.
"""
import time
import logging

logger = logging.getLogger('apps.requests')


class RequestLoggingMiddleware:
    """
    Logs every HTTP request with method, path, status code,
    and response time.

    Format:
        GET /api/projects/ 200 45ms
        POST /api/contact/ 201 120ms

    Only active when the logger level is set to INFO or lower.
    In production, set root logger to WARNING to suppress this.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        duration_ms = round((time.monotonic() - start) * 1000)

        # Skip logging for static files and health checks
        path = request.path
        if not any(path.startswith(p) for p in ['/static/', '/media/', '/favicon']):
            logger.info(
                '%s %s %s %dms',
                request.method,
                path,
                response.status_code,
                duration_ms
            )

        return response