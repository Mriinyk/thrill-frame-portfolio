"""
ASGI config for thrill_frame_web_portfolio_servis project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "thrill_frame_web_portfolio_servis.settings"
)

application = get_asgi_application()
