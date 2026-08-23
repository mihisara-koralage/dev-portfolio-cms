"""
Development settings.
Never use these in production.
"""
from .base import *
import sys

TESTING = "test" in sys.argv

DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Allow all CORS origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Show emails in console instead of sending them
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Django Debug Toolbar
if DEBUG and not TESTING:
    INSTALLED_APPS += [
        "debug_toolbar",
    ]
if DEBUG and not TESTING:
    MIDDLEWARE.insert(
        0,
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    )
INTERNAL_IPS = ['127.0.0.1']

# Relaxed security for local development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Development cache — no caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Detailed logging in development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'dev': {
            'format': '{levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'dev',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',  # set to DEBUG to see all SQL queries
            'propagate': False,
        },
    },
}