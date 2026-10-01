"""
ASGI config for thrill_frame_web_portfolio_servis project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/asgi/
"""

from django.core.asgi import get_asgi_application

from thrill_frame_web_portfolio_servis.settings_loader import (
    configure_settings_module,
)

configure_settings_module()

application = get_asgi_application()
