"""
Settings for running the test suite (`python manage.py test finance`).

Not wired up as a default anywhere - activate it explicitly:

    set DJANGO_SETTINGS_MODULE=budget_tracker.settings.testing   (PowerShell: $env:DJANGO_SETTINGS_MODULE="budget_tracker.settings.testing")
    python manage.py test finance

Or pass it inline:

    python manage.py test finance --settings=budget_tracker.settings.testing
"""

from .base import *  # noqa: F401,F403

DEBUG = False

ALLOWED_HOSTS = ["testserver", "localhost"]

# In-memory SQLite: fastest option for 54 tests, no file created/torn down.
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
