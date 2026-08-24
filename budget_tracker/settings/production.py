"""
Production settings, used on Render.

Activated explicitly via the DJANGO_SETTINGS_MODULE environment variable
set in the Render Dashboard -> Environment tab:

    DJANGO_SETTINGS_MODULE=budget_tracker.settings.production

wsgi.py also defaults to this module as a safety net, in case that
environment variable is ever missing.
"""

import os

from .base import *  # noqa: F401,F403

DEBUG = False

# Render provides the external hostname at runtime; it isn't known
# ahead of time (see RENDER_EXTERNAL_HOSTNAME step in the deploy guide).
ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Without this, POST requests (login, register, any form) return
# 403 CSRF verification failed, because Django checks the Origin
# header against an https:// scheme, not just the host.
CSRF_TRUSTED_ORIGINS = []
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['POSTGRES_DB'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': os.environ['POSTGRES_HOST'],
        'PORT': int(os.environ['POSTGRES_DB_PORT']),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# WhiteNoise must sit right after SecurityMiddleware so it can serve
# static files before any other middleware touches the request.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    *MIDDLEWARE[1:],
]

STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Basic HTTPS hardening - safe to enable since Render terminates
# TLS for you and always serves the app over https.
# SECURE_PROXY_SSL_HEADER is required here: Render's proxy talks to
# gunicorn over plain HTTP internally, so without this Django can't
# tell the original request was HTTPS and SECURE_SSL_REDIRECT would
# redirect forever.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
