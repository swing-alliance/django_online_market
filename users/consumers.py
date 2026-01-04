import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .redis_service import RedisService # 只导入 Service

class UserStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return  
        self.user_id = str(self.user.id)
        self.group_name = f'user_{self.user_id}'
        await self.accept()
        await RedisService.set_online(self.user_id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        count = await self.get_pending_requests()
        await self.send(text_data=json.dumps({"type": "pending_requests", "count": count}))# 发送未读消息数,初次连接时发送

    async def disconnect(self, close_code):
        if hasattr(self, 'user_id'):
            await RedisService.set_offline(self.user_id)
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except: return

        if data.get('type') == "sendmessage":
            # 3. 极速响应：写入 Redis 队列
            msg_payload = await RedisService.enqueue_message(
                sender_id=self.user_id,
                receiver_id=data.get('friend_id'), # 建议前端直接传 ID
                content=data.get('content')
            )
            
            # 4. 实时广播：通过内存转发给接收者
            await self.channel_layer.group_send(
                f"user_{data.get('friend_id')}",
                {
                    "type": "chat.message",
                    "data": msg_payload
                }
            )

    async def chat_message(self, event):
        """接收并下发来自 group_send 的消息"""
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_pending_requests(self):
        # 局部导入，防止 ImproperlyConfigured
        from .models import FriendRequest
        return FriendRequest.objects.filter(to_user=self.user, status=1).count()