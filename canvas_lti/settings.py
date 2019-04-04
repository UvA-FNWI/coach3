"""
Django settings for canvas_lti project.

Generated by 'django-admin startproject' using Django 2.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0v-n_tq)-s8f$8%2=nw+f41do*1wg6d*ja=+m2dm56n=fl&trt'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['https://learn-lti.herokuapp.com/', 'localhost', '127.0.0.1']


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
    #'django_auth_lti',
    #'django_app_lti',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django_auth_lti.middleware.LTIAuthMiddleware',
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

WSGI_APPLICATION = 'canvas_lti.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# # Password validation
# # https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators
#
# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]

# # Add to authentication backends (for django-auth-lti)
# AUTHENTICATION_BACKENDS = [
#     'django.contrib.auth.backends.ModelBackend',
#     'django_auth_lti.backends.LTIAuthBackend',
# ]

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
                "url": "http://localhost:8000/lti/launch",
            },
            "course_home_sub_navigation": {
                "enabled": "true",
                "default": "enabled",
                "text": "Coach (localhost)",
                "visibility": "public",
                "url": "http://localhost:8000/lti/launch",
            }
        }
    }
}

# LTI_SECRET = "69dc913725629f46f9a4324490a61ca82cdb360f354a7c2ca5d6b21994f5ddc0"
# LTI_KEY = "9bd2b1cfd3857f5274e8fd7ec428857e"

LTI_SECRET = '4339900ae5861f3086861ea492772864'
LTI_KEY = '0cd500938a8e7414ccd31899710c98ce'


BASELINK = 'http://localhost:8080'

#AUTH_USER_MODEL = "iki_lti.User"

# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'rest_framework_simplejwt.authentication.JWTAuthentication',
#     ),
# }


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
#LOGIN_REDIRECT_URL = 'index'
