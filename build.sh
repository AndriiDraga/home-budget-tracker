#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install -r requirements.txt

# Collect static assets into STATIC_ROOT so WhiteNoise can serve them
python manage.py collectstatic --no-input

# Apply migrations, including 0002_add_default_categories so the
# Postgres instance ends up with the same 10 default categories
python manage.py migrate