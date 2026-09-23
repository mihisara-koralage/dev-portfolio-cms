"""
Production settings.

Every setting here is deliberate. Do not weaken these
without understanding the security implication.
"""
from .base import *
from decouple import config

DEBUG = False

# ----------------------------------------------------------------
# Hosts & CORS
# ----------------------------------------------------------------
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default=''
).split(',')

CORS_ALLOW_CREDENTIALS = True

# ----------------------------------------------------------------
# Security headers
# Django sets these headers on every response.
# ----------------------------------------------------------------

# Force HTTPS — browser will refuse HTTP for 1 year
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Only redirect to HTTPS when actually behind HTTPS
# Set SECURE_SSL_REDIRECT=True in .env.production on the real server
SECURE_SSL_REDIRECT   = config('SECURE_SSL_REDIRECT',   default=False, cast=bool)

# Session and CSRF cookies only sent over HTTPS
# These must be False until HTTPS is configured (Phase 10)
# Set to True in .env.production after domain + SSL are active
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_SECURE    = config('CSRF_COOKIE_SECURE',    default=False, cast=bool)

# Prevent session cookie being accessed by JavaScript
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Cookie same-site policy — prevents CSRF from third-party sites
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# Prevent browsers from MIME-sniffing the content type
SECURE_CONTENT_TYPE_NOSNIFF = True

# Enable browser XSS filtering
SECURE_BROWSER_XSS_FILTER = True

# Prevent site from being embedded in iframes (clickjacking)
X_FRAME_OPTIONS = 'DENY'

# Tell browser to use HTTPS for all future requests to this origin
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Nginx handles SSL termination — trust its header
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ----------------------------------------------------------------
# Session
# ----------------------------------------------------------------
SESSION_COOKIE_AGE = 3600          # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# ----------------------------------------------------------------
# Database
# ----------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     config('DB_NAME'),
        'USER':     config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST':     config('DB_HOST'),
        'PORT':     config('DB_PORT', default='5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        },
        'CONN_MAX_AGE': 60,
    }
}

# ----------------------------------------------------------------
# Static & Media
# ----------------------------------------------------------------
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT  = BASE_DIR / 'media'

# AWS S3 for media storage (activated in Phase 8)
# AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# ----------------------------------------------------------------
# Email (production)
# ----------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='')

# ----------------------------------------------------------------
# Logging (production)
# ----------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'production': {
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'production',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ----------------------------------------------------------------
# Cache (production — override in Phase 8 with Redis/ElastiCache)
# ----------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}

# ----------------------------------------------------------------
# CSRF trusted origins
# ----------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default=''
).split(',')