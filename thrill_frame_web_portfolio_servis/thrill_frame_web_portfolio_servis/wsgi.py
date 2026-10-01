"""
WSGI config for thrill_frame_web_portfolio_servis project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application

from thrill_frame_web_portfolio_servis.settings_loader import (
    configure_settings_module,
)

configure_settings_module()

application = get_wsgi_application()
