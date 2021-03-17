"""
Django settings for production build of FiveGuysPowerTesting project.

Be sure to set environment variable DJANGO_SETTINGS_MODULE as such:
    DJANGO_SETTINGS_MODULE=FiveGuysPowerTesting.prod_settings
"""

from FiveGuysPowerTesting.settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Hostname
ALLOWED_HOSTS = ['group-six-prod.colab.duke.edu', 'localhost']

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'fiveguyspowertesting',
        'USER': 'jjc70',
        'PASSWORD': 'DukeECE458',
        'HOST': 'localhost',
        'PORT': '',
    }
}