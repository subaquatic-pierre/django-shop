from .base import *
import os
from .config import Config

# Ititialize settings from config.json file
settings = Config()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

SECRET_KEY = settings.SECRET_KEY
ROOT_URLCONF = 'scubadivedubai.urls'
STRIPE_PUBLIC_KEY = settings.STRIPE_LIVE_PUBLIC_KEY
STRIPE_SECRET_KEY = settings.STRIPE_LIVE_SECRET_KEY
# SET LOGOUT BUTTONG TO POST REQUEST ON EVENT LISTEN
ACCOUNT_LOGOUT_ON_GET = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_extensions',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'crispy_forms',
    'django_countries',
    'core'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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


# Check if development or production environment
if settings.DEVELOPMENT:
    ALLOWED_HOSTS = ['*']
    DEBUG = True
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static_root")]

    # Set no email server for allauth
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    # Set shop to allow for notes to work, have to manualy create user profile
    INSTALLED_APPS += ['shop', 'debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

    # DEBUG TOOLBAR SETTINGS

    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ]

    def show_toolbar(request):
        return True

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        'SHOW_TOOLBAR_CALLBACK': show_toolbar
    }

# Production environment
else:
    ALLOWED_HOSTS = ['*']
    STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')
    DEBUG = settings.DEBUG

    # Email settings

    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = settings.EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD
    # Set to ChopConfig to allow for shop signals to work
    INSTALLED_APPS += ['shop.apps.ShopConfig']

    # AUTH_PASSWORD_VALIDATORS = [
    #     {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    #     {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    #     {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    #     {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}
    # ]


WSGI_APPLICATION = 'scubadivedubai.wsgi.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dubai'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_root')

# Auth

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
)

# Site settings

SITE_ID = 1
CRISPY_TEMPLATE_PACK = 'bootstrap4'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'

# TODO: Add custom form for UserSignUp in settings/base.py

# ACCOUNT_SIGNUP_FORM_CLASS = 'yourapp.forms.SignupForm'

# TODO: Change database seetings when app is ready for publication

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': config('DB_NAME'),
#         'USER': config('DB_USER'),
#         'PASSWORD': config('DB_PASSWORD'),
#         'HOST': config('DB_HOST'),
#         'PORT': ''
#     }
# }
