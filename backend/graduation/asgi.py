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
from channels.sessions import SessionMiddlewareStack
import chat.routing
import notification.routing

# HTTP应用
http_application = get_asgi_application()

# WebSocket应用
websocket_application = AuthMiddlewareStack(
    URLRouter(
        chat.routing.websocket_urlpatterns + 
        notification.routing.websocket_urlpatterns
    )
)

# 添加Session middleware到WebSocket
websocket_application = SessionMiddlewareStack(websocket_application)

application = ProtocolTypeRouter({
    "http": http_application,
    "websocket": websocket_application,
})