from __future__ import annotations

from .base import *  # noqa: F403
from .base import SECRET_KEY  # noqa: F401, F403

DEBUG = False

if SECRET_KEY == "django-insecure-change-me":  # noqa: F405
    raise RuntimeError(
        "SECRET_KEY must be set to a secure value in production. "
        "Set the SECRET_KEY environment variable."
    )

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
