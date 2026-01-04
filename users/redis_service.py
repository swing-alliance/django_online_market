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
        key = f"{ONLINE_STATUS_KEY_PREFIX}{user_id}"
        await redis_client.set(key, "online", ex=STATUS_TTL)

    @staticmethod
    async def set_offline(user_id):
        key = f"{ONLINE_STATUS_KEY_PREFIX}{user_id}"
        await redis_client.delete(key)

    @staticmethod
    async def enqueue_message(sender_id, receiver_id, content):
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
        while True:
            try:
                # 批量读取 100 条，阻塞 1 秒
                entries = await redis_client.xread({"msg_write_queue": "0-0"}, count=100, block=1000)
                if entries:
                    stream, msgs = entries[0]
                    to_save = []
                    msg_ids = []
                    for m_id, content in msgs:
                        if content['sender_id'] >= content['receiver_id']:
                            thread_id = GenericMessage.get_thread_id(content['receiver_id'], content['sender_id'])
                        to_save.append(GenericMessage(
                            thread_id=thread_id,
                            sender_id=content['sender_id'],
                            receiver_id=content['receiver_id'],
                            content=content['content']
                        ))
                        msg_ids.append(m_id)
                    
                    # 批量写入数据库 (Bulk Create)
                    if to_save:
                        await sync_to_async(GenericMessage.objects.bulk_create)(to_save)
                        # 处理完后删除内存中的消息
                        await redis_client.xdel("msg_write_queue", *msg_ids)
            except Exception as e:
                print(f"Worker Error: {e}")
                await asyncio.sleep(5)