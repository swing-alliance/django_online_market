import json
import time
import asyncio
import redis.asyncio as aioredis
from asgiref.sync import sync_to_async

# 配置
REDIS_URL = "redis://localhost:6379/0"
ONLINE_STATUS_KEY_PREFIX = "online_user:"
STATUS_TTL = 3600 

# 全局异步连接池
redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)

class RedisService:
    @staticmethod
    async def set_online(user_id):
        """设置用户在线状态，带过期时间"""
        key = f"{ONLINE_STATUS_KEY_PREFIX}{user_id}"
        await redis_client.set(key, "online", ex=STATUS_TTL)

    @staticmethod
    async def set_offline(user_id):
        """删除用户在线状态"""
        key = f"{ONLINE_STATUS_KEY_PREFIX}{user_id}"
        await redis_client.delete(key)

    @staticmethod
    async def refresh_online_status(user_id):
        """刷新用户在线状态的过期时间"""
        # 假设你的在线状态 Key 格式是 user:online:{user_id}
        key = f"{ONLINE_STATUS_KEY_PREFIX}{user_id}"
        # 重新设置过期时间，比如 300 秒（5分钟）
        # expire 方法只更新时间，不会改动数据内容
        await redis_client.expire(key, 300)


    @staticmethod
    async def is_online(user_id):
        """检查用户是否在线"""
        key = f"{ONLINE_STATUS_KEY_PREFIX}{user_id}"
        status = await redis_client.get(key)
        if status == "online":
            return True
        return False

    @staticmethod
    async def enqueue_send_message(sender_id, receiver_id, content):
        """核心：消息入内存队列，不准碰硬盘"""
        payload = {
            "sender_id": str(sender_id),
            "receiver_id": str(receiver_id),
            "content": content,
            "timestamp": str(time.time())
        }
        # 使用 Redis Stream 存储，maxlen 保证内存不爆
        await redis_client.xadd("msg_write_queue", payload, maxlen=100000)
        return payload

    @staticmethod
    async def start_db_worker():
        """
        后台持久化协程：批量写硬盘
        可以在 Django 启动时异步挂载，或者单独运行
        """
        from .models import GenericMessage # 局部导入，避开启动报错
        from django.utils import timezone
        now = timezone.now()
        while True:
            try:
                # 批量读取 100 条，阻塞 1 秒
                entries = await redis_client.xread({"msg_write_queue": "0-0"}, count=100, block=1000)
                if entries:
                    stream, msgs = entries[0]
                    to_save = []
                    msg_ids = []
                    for m_id, content in msgs:
                        # 清洗数据：如果是字符串 "None"，转为真正的 None 对象
                        s_id = None if content['sender_id'] == 'None' else content['sender_id']
                        r_id = None if content['receiver_id'] == 'None' else content['receiver_id']

                        if s_id and r_id:
                            thread_id = GenericMessage.get_thread_id(r_id, s_id)
                            to_save.append(GenericMessage(
                                thread_id=thread_id,
                                sender_id=s_id,
                                receiver_id=r_id,
                                created_at=now,
                                content=content['content']
                            ))
                        msg_ids.append(m_id)
                    
                    # 批量写入数据库 (Bulk Create)
                    if to_save:
                        await sync_to_async(GenericMessage.objects.bulk_create)(to_save)
                        await redis_client.xdel("msg_write_queue", *msg_ids)
            except Exception as e:
                print(f"持久化协程错误: {e}")
                await asyncio.sleep(5)