import os
from pathlib import Path
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

LOGS_DIR = BASE_DIR / 'logs'

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost 127.0.0.1').split()

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',
]

LOCAL_APPS = [
    'apps.workforce',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'common.middleware.APIRequestLoggerMiddleware',
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
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

# NeonDB Connection
DATABASES = {
    'default': dj_database_url.parse(
        config('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'workforce.User'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),   
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# DRF Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'common.pagination.StandardPagination',
    'EXCEPTION_HANDLER': 'common.exceptions.custom_exception_handler',
}

# CORS Settings — allow React frontend
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://localhost:3000',
    config('FRONTEND_URL', default='http://localhost:5173'),
]

CORS_ALLOW_CREDENTIALS = True

# Spectacular Settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Workforce Analytics API',
    'DESCRIPTION': 'HR Workforce Performance Dashboard API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Media files (uploaded documents)
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ─── LOGGING ──────────────────────────────────────────────────────────────────
if LOGS_DIR.exists():
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '[{asctime}] {levelname} {name} {module}:{lineno} — {message}',
                'style': '{',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'simple': {
                'format': '[{asctime}] {levelname} — {message}',
                'style': '{',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'api': {
                'format': '[{asctime}] {levelname} {message}',
                'style': '{',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'level': 'DEBUG',
            },
            'file_general': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': BASE_DIR / 'logs' / 'workpulse.log',
                'maxBytes': 5 * 1024 * 1024,
                'backupCount': 5,
                'formatter': 'verbose',
                'level': 'DEBUG',
                'encoding': 'utf-8',
            },
            'file_errors': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': BASE_DIR / 'logs' / 'errors.log',
                'maxBytes': 5 * 1024 * 1024,
                'backupCount': 5,
                'formatter': 'verbose',
                'level': 'ERROR',
                'encoding': 'utf-8',
            },
            'file_api': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': BASE_DIR / 'logs' / 'api_requests.log',
                'maxBytes': 5 * 1024 * 1024,
                'backupCount': 5,
                'formatter': 'api',
                'level': 'INFO',
                'encoding': 'utf-8',
            },
        },
        'loggers': {
            'apps': {
                'handlers': ['console', 'file_general', 'file_errors'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'api_requests': {
                'handlers': ['file_api', 'console'],
                'level': 'INFO',
                'propagate': False,
            },
            'django': {
                'handlers': ['console', 'file_general'],
                'level': 'WARNING',
                'propagate': False,
            },
            'django.request': {
                'handlers': ['file_errors', 'console'],
                'level': 'ERROR',
                'propagate': False,
            },
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False,
            },
        },
    }
else:
    # Production — console only (no logs/ directory on server)
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'WARNING',
            },
        },
        'loggers': {
            'django': {'handlers': ['console'], 'level': 'WARNING', 'propagate': False},
            'django.request': {'handlers': ['console'], 'level': 'ERROR', 'propagate': False},
        },
    }

FRONTEND_URL      = config('FRONTEND_URL',      default='http://localhost:5173')
EMAIL_WEBHOOK_URL = config('EMAIL_WEBHOOK_URL',  default='http://localhost:3001')

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'