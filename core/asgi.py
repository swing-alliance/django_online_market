import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack  # 这里直接使用 Django 的认证中间件
from channels.routing import ProtocolTypeRouter, URLRouter
from users import routing as users_routing


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


# 创建一个 ProtocolTypeRouter 路由器来处理不同的协议请求
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # 用 Django 处理 HTTP 请求
    "websocket": AuthMiddlewareStack(  # 使用 Django Channels 的认证堆栈，基于 Cookie 和 Session 认证
        URLRouter(
            users_routing.websocket_urlpatterns  # WebSocket 的路由
        )
    ),
})
