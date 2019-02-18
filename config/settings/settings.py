from os.path import abspath, dirname, join
from os import getenv
import datetime


DEV_DB_HOST = getenv('HASKER_DB_HOST', 'localhost')
DEV_DB_PORT = getenv('HASKER_DB_PORT', '5432')
DEV_DB_NAME = getenv('HASKER_DB_NAME', 'hasker_db')
DEV_DB_USER = getenv('HASKER_DB_USER', 'hasker_db_user')
DEV_DB_PASSWORD = getenv('HASKER_DB_PASSWORD', 'hasker_db_user_pass')


def root(*dirs):
    base_dir = join(dirname(__file__), '..', '..', 'hasker')
    return abspath(join(base_dir, *dirs))

BASE_DIR = root()
MEDIA_URL = '/media/'
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    root('static'),
]

TRENDING_NUM = 20
QUESTION_PAGINATE = 20
ANSWER_PAGINATE = 30

SECRET_KEY = ''

DEBUG = False

ALLOWED_HOSTS = ["127.0.0.1"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_swagger',

    'hasker.qa.apps.QaConfig',
    'hasker.users.apps.UsersConfig',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

JWT_AUTH = {
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=300)
}

AUTH_USER_MODEL = 'users.Profile'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [root('templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'custom_tags': 'hasker.templatetags.custom_tags',
            },
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

LOGGING = {}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True


try:
    from .local_settings import *
except ImportError:
    pass
