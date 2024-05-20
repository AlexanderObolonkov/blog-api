import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from chat.consumers import ChatConsumer
from django.core.asgi import get_asgi_application
from django.urls import path

from api.middleware import JWTAuthMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_channels_chat.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            JWTAuthMiddleware(
                URLRouter(
                    [
                        path("", ChatConsumer.as_asgi()),
                    ]
                ),
            ),
        ),
    }
)
