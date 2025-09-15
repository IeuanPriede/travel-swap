import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

# Minimal Django configuration
settings.configure(
    DEBUG=True,
    INSTALLED_APPS=[
        'django.contrib.staticfiles',
    ],
    STATIC_URL='/static/',
    STATIC_ROOT=r'C:\Users\pried\Travel-Swap\travel-swap\test_staticfiles',
    STATICFILES_DIRS=[
        r'C:\Users\pried\Travel-Swap\travel-swap\static',
    ],
    SECRET_KEY='test-key',
)

django.setup()

execute_from_command_line([
    'manage.py',
    'collectstatic',
    '--noinput',
    '--verbosity=2'
    ])
