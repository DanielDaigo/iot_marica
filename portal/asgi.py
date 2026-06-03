"""
ASGI config for portal project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# In production the ASGI entrypoint should use production settings by default.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings_production')

application = get_asgi_application()
