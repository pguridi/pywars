"""
Django settings for battleground project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from os.path import expanduser

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'efd+65=+8_sbguv%*bvi$y)cdeq#=6bbv22uwlpy=j$0j(ruvx'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

ACCOUNT_ACTIVATION_DAYS = 3

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'registration',
    'django_ace',
    'game',
    'compressor',
    'djangobower',
    'mailer',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'battleground.urls'

WSGI_APPLICATION = 'battleground.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(expanduser("~"), 'pywars.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_URL = '/static/'

CELERY_TASK_SERIALIZER = "json"

#STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_ROOT = "/var/www/static"
BOWER_COMPONENTS_ROOT = os.path.join(PROJECT_ROOT, 'components')


STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'djangobower.finders.BowerFinder',
    'compressor.finders.CompressorFinder',
)

# Default:  the opposite of DEBUG
# Disable this for testing the compressor
#COMPRESS_ENABLED = True

BOWER_INSTALLED_APPS = (
    'jquery',
    'bootstrap',
    'phaser',
)
