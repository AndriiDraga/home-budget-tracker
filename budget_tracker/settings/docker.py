"""
Local Docker Compose settings.

Activated by docker-compose.yml via
    DJANGO_SETTINGS_MODULE=budget_tracker.settings.docker

Uses the PostgreSQL container (no SSL, no HTTPS redirect), so the
Render production settings stay untouched.
"""

import os

from .base import *  # noqa: F401,F403

DEBUG = os.getenv('DJANGO_DEBUG', '0') == '1'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'web', 'nginx']
CSRF_TRUSTED_ORIGINS = ['http://localhost:8080', 'http://127.0.0.1:8080']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['POSTGRES_DB'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': os.environ.get('POSTGRES_HOST', 'db'),
        'PORT': os.environ.get('POSTGRES_DB_PORT', '5432'),
    }
}

# WhiteNoise serves collected static files from Gunicorn.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    *MIDDLEWARE[1:],  # noqa: F405
]

STATIC_ROOT = BASE_DIR / 'staticfiles'  # noqa: F405

STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}
