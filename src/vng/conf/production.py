import raven
import os

from .base import *

#
# Standard Django settings.
#

DEBUG = False

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

DEFAULT_FROM_EMAIL = 'info@api-test.nl'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'vngatvprod',
        'USER': 'vngatv',
        'PASSWORD': os.getenv('DB_PASS'),
        'HOST': '',  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',  # Set to empty string for default.
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.getenv('SECRET_KEY')

ALLOWED_HOSTS = ['.api-test.nl']

# Redis cache backend
# NOTE: If you do not use a cache backend, do not use a session backend or
# cached template loaders that rely on a backend.
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/4", # NOTE: watch out for multiple projects using the same cache!
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        }
    }
}

CELERY_BROKER_URL = "redis://127.0.0.1:6379/5"
# EMAIL_HOST = 'smtp.sendgrid.net'
# EMAIL_HOST_USER = 'apikey'
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Caching sessions.
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = "default"

# Caching templates.
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', RAW_TEMPLATE_LOADERS),
]

# The file storage engine to use when collecting static files with the
# collectstatic management command.
# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Production logging facility.
LOGGING['loggers'].update({
    '': {
        'handlers': ['sentry'],
        'level': 'ERROR',
        'propagate': False,
    },
    'django': {
        'handlers': ['django'],
        'level': 'WARNING',
        'propagate': True,
    },
    'django.security.DisallowedHost': {
        'handlers': ['django'],
        'level': 'CRITICAL',
        'propagate': False,
    },
})

#
# Custom settings
#

# Show active environment in admin.
ENVIRONMENT = 'production'
SHOW_ALERT = False

# We will assume we're running under https
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
# Only set this when we're behind Nginx as configured in our example-deployment
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_CONTENT_TYPE_NOSNIFF = True # Sets X-Content-Type-Options: nosniff
SECURE_BROWSER_XSS_FILTER = True # Sets X-XSS-Protection: 1; mode=block

#
# Library settings
#

ELASTIC_APM['SERVICE_NAME'] += ' ' + ENVIRONMENT

# Raven
INSTALLED_APPS = INSTALLED_APPS + [
    'raven.contrib.django.raven_compat',
]
RAVEN_CONFIG = {
    'dsn': 'https://c0af4517252242e7a8db00470b488517@sentry.maykinmedia.nl/124',
    'release': raven.fetch_git_sha(BASE_DIR),
}
LOGGING['handlers'].update({
    'sentry': {
        'level': 'WARNING',
        'class': 'raven.handlers.logging.SentryHandler',
        'dsn': RAVEN_CONFIG['dsn']
    },
})

RUN_KUBERNETES_CMD = True

SUBDOMAIN_SEPARATOR = '.'
