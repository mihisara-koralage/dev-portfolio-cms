"""
Core utility views.
"""
from django.http import JsonResponse
from django.db import connection


def health_check(request):
    """
    Health check endpoint used by:
    - Docker HEALTHCHECK instruction
    - AWS load balancer target group checks
    - CloudWatch synthetic monitoring

    Returns 200 if the app and database are reachable.
    Returns 503 if the database connection fails.
    """
    try:
        connection.ensure_connection()
        db_status = 'ok'
    except Exception:
        db_status = 'error'

    status_code = 200 if db_status == 'ok' else 503

    return JsonResponse({
        'status': 'ok' if db_status == 'ok' else 'degraded',
        'database': db_status,
    }, status=status_code)