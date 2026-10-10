"""
Settings for running the test suite (`python manage.py test finance`).

Not wired up as a default anywhere - activate it explicitly:

    set DJANGO_SETTINGS_MODULE=budget_tracker.settings.testing   (PowerShell: $env:DJANGO_SETTINGS_MODULE="budget_tracker.settings.testing")
    python manage.py test finance

Or pass it inline:

    python manage.py test finance --settings=budget_tracker.settings.testing
"""

import os

from .base import *  # noqa: F401,F403

DEBUG = False

ALLOWED_HOSTS = ["testserver", "localhost"]

if os.environ.get("USE_POSTGRES_FOR_TESTS") == "1":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["POSTGRES_DB"],
            "USER": os.environ["POSTGRES_USER"],
            "PASSWORD": os.environ["POSTGRES_PASSWORD"],
            "HOST": os.environ["POSTGRES_HOST"],
            "PORT": int(os.environ["POSTGRES_DB_PORT"]),
        }
    }
else:
    # In-memory SQLite: fastest option for local tests, no file created/torn down.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }

# MD5 is drastically faster than the default PBKDF2 hasher - password
# hashing security doesn't matter for test-only data.
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
