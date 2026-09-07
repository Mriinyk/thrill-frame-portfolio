"""
WSGI config for thrill_frame_web_portfolio_servis project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "thrill_frame_web_portfolio_servis.settings"
)

application = get_wsgi_application()
