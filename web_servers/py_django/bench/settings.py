import os
from enum import Enum

import sentry_sdk

DEBUG = False


class Databases(str, Enum):
    MYSQL_ORM = "mysql_orm"
    POSTGRES_ORM = "postgres_orm"


sentry_sdk.init(dsn="")


"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-=8k%+on4qwxm&f2#3icqu2(_ivvss_of34bams*h(omgdfyr-8"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "bench",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "bench.views.DisableCSRFMiddleware",
]

ROOT_URLCONF = "bench.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ASGI_APPLICATION = "src.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
CHOSEN_DB = os.environ["DATABASE"]

match CHOSEN_DB:
    case Databases.MYSQL_ORM:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.mysql",
                "NAME": "webservers_bench",
                "USER": "user",
                "PASSWORD": "pass",
                "HOST": "localhost",
                "PORT": "13306",
            }
        }
    case Databases.POSTGRES_ORM:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": "webservers_bench",
                "USER": "postgres",
                "PASSWORD": "pass",
                "HOST": "localhost",
                "PORT": "15432",
            }
        }
    case _:
        raise NotImplementedError(f"Database not implemented: {CHOSEN_DB}")


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
