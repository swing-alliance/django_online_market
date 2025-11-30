from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import redis # 用于直接操作 Redis
import json


r = redis.Redis(host='localhost', port=6379, db=0)

# 定义在线状态 Key 的前缀和过期时间
ONLINE_STATUS_KEY_PREFIX = "online_user:"
STATUS_TTL = 3600  # 状态保持 1 小时，会被心跳包刷新

class UserStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('self.scope',self.scope)
        self.user_id = None
        self.group_name = None
        self.user = self.scope.get("user")
        print(f"WebSocket 连接来自用户：{self.user}")
        if not self.user or not self.user.is_authenticated:
            print("WebSocket 拒绝未认证的用户连接")
            await self.close()
            return
        self.user_id = str(self.user.id)  # 确保是字符串，方便 Redis Key
        self.group_name = f'user_{self.user_id}'

        # 4. 接受连接
        await self.accept()

        # 5. 更新 Redis 实时在线表
        await self.set_user_online_status()

        # 6. 加入 Channels 的 Group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        print(f"用户 {self.user_id} 已上线，状态已更新到 Redis。")


    async def disconnect(self, close_code):
        if self.user_id:
            # 1. 移除 Channels 的 Group
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

            # 2. 从 Redis 实时在线表移除
            await self.remove_user_online_status()
            
            print(f"用户 {self.user_id} 已离线，状态已从 Redis 移除。")

    # -------------------
    # Redis 操作（使用 database_sync_to_async 确保操作运行在安全线程中）
    # -------------------

    @database_sync_to_async
    def set_user_online_status(self):
        """设置用户在线状态，并设置 TTL"""
        key = f"{ONLINE_STATUS_KEY_PREFIX}{self.user_id}"
        # Value 可以是当前连接的时间戳、设备 ID 等信息
        r.set(key, json.dumps({"status": "online", "device": "web"}), ex=STATUS_TTL)

    @database_sync_to_async
    def remove_user_online_status(self):
        """删除用户在线状态"""
        key = f"{ONLINE_STATUS_KEY_PREFIX}{self.user_id}"
        r.delete(key)

    # -------------------
    # 接收消息（目前暂时忽略）
    # -------------------
    async def receive(self, text_data):
        # 暂时不做任何操作，只保持连接
        pass