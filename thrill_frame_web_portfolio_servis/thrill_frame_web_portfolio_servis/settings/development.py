"""Local development settings."""

from decouple import Csv

from .base import *  # noqa: F401,F403
from .base import BASE_DIR, config

DEBUG = True

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost",
    cast=Csv(),
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
