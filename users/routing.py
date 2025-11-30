from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # 用户访问 ws://yourhost/ws/status/ 时，由 UserStatusConsumer 处理
    re_path(r'ws/status/$', consumers.UserStatusConsumer.as_asgi()), 
]