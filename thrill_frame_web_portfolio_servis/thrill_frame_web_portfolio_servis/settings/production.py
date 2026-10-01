"""Production settings."""

from decouple import Csv
from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403
from .base import MIDDLEWARE, config, postgres_config

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEBUG = False

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="",
    cast=Csv(),
)

if not postgres_config("POSTGRES_HOST", default=""):
    raise ImproperlyConfigured("POSTGRES_HOST must be set in production.")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": postgres_config("POSTGRES_DB"),
        "USER": postgres_config("POSTGRES_USER"),
        "PASSWORD": postgres_config("POSTGRES_PASSWORD"),
        "HOST": postgres_config("POSTGRES_HOST"),
        "PORT": postgres_config("POSTGRES_PORT", default="5432"),
        "OPTIONS": {
            "sslmode": postgres_config("POSTGRES_SSLMODE", default="require"),
            "channel_binding": postgres_config(
                "POSTGRES_CHANNEL_BINDING", default="require"
            ),
        },
    }
}

SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=True, cast=bool)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=True, cast=bool)
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=0, cast=int)
