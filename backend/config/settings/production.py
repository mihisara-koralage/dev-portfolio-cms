"""
Production settings — hardened for deployment.
Completed in Phase 6.
"""
from .base import *

DEBUG = False

# Security headers (completed in Phase 6)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'