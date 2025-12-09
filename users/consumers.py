from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async

import redis 
import json


r = redis.Redis(host='localhost', port=6379, db=0)

ONLINE_STATUS_KEY_PREFIX = "online_user:"
STATUS_TTL = 3600 

class UserStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = None
        self.group_name = None
        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
        self.user_id = str(self.user.id)  # 确保是字符串，方便 Redis Key
        self.group_name = f'user_{self.user_id}'
        await self.accept()
        await self.set_user_online_status()
        await self.channel_layer.group_add(self.group_name,self.channel_name)
        pending_count = await self.get_pending_requests()
        await self.send(text_data=json.dumps({"type": "pending_requests", "count": pending_count}))
        print(f"用户 {self.user_id} 已上线，状态已更新到 Redis。")




    async def disconnect(self, close_code):
        if self.user_id:
            await self.channel_layer.group_discard(self.group_name,self.channel_name)
            await self.remove_user_online_status()
            print(f"用户 {self.user_id} 已离线，状态已从 Redis 移除。")



    @sync_to_async
    def set_user_online_status(self):
        """设置用户在线状态，并设置 TTL"""
        key = f"{ONLINE_STATUS_KEY_PREFIX}{self.user_id}"
        r.set(key, json.dumps({"status": "online"}), ex=STATUS_TTL)

    @sync_to_async
    def remove_user_online_status(self):
        """删除用户在线状态"""
        key = f"{ONLINE_STATUS_KEY_PREFIX}{self.user_id}"
        r.delete(key)

    @database_sync_to_async
    def get_pending_requests(self):
        from .models import FriendRequest
        user_id = self.user.id
        try:
            count = FriendRequest.objects.filter(to_user=user_id,status=1).count()
            return count
        except Exception as e:
            print(f"查询好友请求失败: {e}")
            return 0



    async def receive(self, text_data):
        """先判断在线状态 → 消息持久化到 DB → 若在线则通过 Channel Layer 实时推送 → 若离线则留待 DB 作为队列，下次上线时投递"""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            # 如果不是有效的 JSON，打印错误或忽略
            print(f"Received invalid JSON or plain text: {text_data}")
            return
        if data.get('type') == "ping":
            pong_response = json.dumps({"type": "pong"})
            await self.send(text_data=pong_response)
            return


