"""
Django settings for canvas_lti project.

Generated by 'django-admin startproject' using Django 2.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import json

# with open('/etc/config.json') as config_file:
# 	config = json.load(config_file)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_DIR = os.path.join(BASE_DIR,'api/')
FILES_DIR = os.path.join(BASE_DIR, 'files/')




# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0v-n_tq)-s8f$8%2=nw+f41do*1wg6d*ja=+m2dm56n=fl&trt'
# SECRET_KEY = config['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['https://learn-lti.herokuapp.com/', 'localhost', '127.0.0.1', 'agile007.science.uva.nl']


# Application definition

INSTALLED_APPS = [
    'iki',
    'iki_lti',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django_extensions',
    'django.contrib.staticfiles',
    'background_task',
    'reversion',
    'rest_framework',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'simple_history.middleware.HistoryRequestMiddleware',
    'reversion.middleware.RevisionMiddleware',
]

ROOT_URLCONF = 'canvas_lti.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

REST_FRAMEWORK = {
'DEFAULT_AUTHENTICATION_CLASSES': (
'rest_framework.authentication.BasicAuthentication',
)
}

WSGI_APPLICATION = 'canvas_lti.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Add LTI configuration settings (for django-app-lti)
LTI_SETUP = {
    "TOOL_TITLE": "Coach3",
    "TOOL_DESCRIPTION": "Learning Analytics Dashboard",
    "LAUNCH_URL": "lti:launch",
    "LAUNCH_REDIRECT_URL": "iki:index",
    "INITIALIZE_MODELS": "resource_and_course_users", # Options: False|resource_only|resource_and_course|resource_and_course_users
    "EXTENSION_PARAMETERS": {
        "canvas.instructure.com": {
            "privacy_level": "public",
            "course_navigation": {
                "enabled": "true",
                "default": "enabled",
                "text": "Coach (localhost)",
                "visibility": "public",
                "url": "https://agile007.science.uva.nl/lti/launch",
            },
            "course_home_sub_navigation": {
                "enabled": "true",
                "default": "enabled",
                "text": "Coach (localhost)",
                "visibility": "public",
                "url": "https://agile007.science.uva.nl/lti/launch",
            }
        }
    }
}

LTI_SECRET = '4339900ae5861f3086861ea492772864'
LTI_KEY = '0cd500938a8e7414ccd31899710c98ce'

#LTI_SECRET = config['LTI_SECRET']
#LTI_KEY = config['LTI_KEY']


BASELINK = 'http://localhost:8080'
# BASELINK = 'https://agile007.science.uva.nl'

#AUTH_USER_MODEL = "iki_lti.User"




# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Amsterdam'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
#LOGIN_REDIRECT_URL = 'index'

#Background processes
BACKGROUND_TASK_RUN_ASYNC = False
MAX_ATTEMPTS = 5

X_FRAME_OPTIONS = 'ALLOW'

