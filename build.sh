#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate

# Create superuser from environment variables (if provided)
python << END
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staffly.settings.production')
django.setup()

from accounts.models import User

admin_email = os.environ.get('ADMIN_EMAIL')
admin_password = os.environ.get('ADMIN_PASSWORD')

if admin_email and admin_password:
    if not User.objects.filter(email=admin_email).exists():
        user = User.objects.create_superuser(
            email=admin_email,
            password=admin_password,
            first_name='Admin',
            last_name='User'
        )
        print(f'Superuser {admin_email} created successfully!')
    else:
        print(f'User {admin_email} already exists.')
else:
    print('ADMIN_EMAIL and ADMIN_PASSWORD not set. Skipping superuser creation.')
END
