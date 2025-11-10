import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class NotificationSender:
    """一个通用的消息通知发送器，通过 Django Channels 发送实时消息。"""
    def __init__(self):
        # 获取 Channels Layer 实例
        self.channel_layer = get_channel_layer()

    def send_notification(self, user_id, message_type, payload):
        """
        向指定用户发送通知。
        
        :param user_id: 接收消息的用户的ID。
        :param message_type: 消息类型，用于前端Consumer路由。
        :param payload: 消息体数据。
        """
        # Channels 的 Group Name 约定：'notification_<user_id>'
        group_name = f'notification_{user_id}'

        # 构建要发送的消息字典
        message = {
            'type': message_type, # 例如 'notification.friend_request_approved'
            'text': json.dumps(payload)
        }

        # 异步发送消息到同步函数包装器
        async_to_sync(self.channel_layer.group_send)(
            group_name,
            message
        )
        
    def send_friend_status(self, user_id, status, request_id):
        """发送好友请求状态更新的快捷方法。"""
        payload = {
            'status': status,
            'request_id': request_id,
            'detail': f'好友请求已{status}'
        }
        self.send_notification(
            user_id=user_id,
            message_type='friend_status_update',
            payload=payload
        )

notification_sender = NotificationSender()