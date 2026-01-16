"""
ASGI config for graduation project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

# 设置环境变量
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "graduation.settings")

# 先初始化Django
django.setup()

# 现在可以安全地导入其他模块
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing
import notification.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns + 
            notification.routing.websocket_urlpatterns
        )
    ),
})