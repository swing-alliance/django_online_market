import uuid
import os
from django.db import models
from django.contrib.auth.models import User

def generate_user_id():
    """生成随机用户ID：8位字母数字"""
    return str(uuid.uuid4())[:8].upper()

def user_avatar_upload_path(instance, filename):
    """生成头像上传路径：avatars/用户ID/文件名"""
    ext = filename.split('.')[-1]
    new_filename = f"avatar_{instance.account_id}.{ext}"
    return os.path.join('avatar', str(instance.profile.id), new_filename)

class UserInfo(models.Model):
    profile = models.OneToOneField(User,on_delete=models.CASCADE,related_name='user_info',primary_key=True)
    phone_number = models.CharField(max_length=15,verbose_name="手机号",db_index=True)
    account_id = models.CharField(max_length=8,default=generate_user_id,unique=True,verbose_name="账户ID")
    account_avatar = models.ImageField(upload_to=user_avatar_upload_path,blank=True,null=True,verbose_name="账户头像",help_text="支持 JPG, PNG 格式，建议尺寸 200x200 像素")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'user_info'
        verbose_name = '用户信息'
        verbose_name_plural = '用户信息'
    def __str__(self):
        return f"{self.profile.username} (ID: {self.account_id})"

    def get_avatar_url(self):
        if self.account_avatar and hasattr(self.account_avatar, 'url'):
            return self.account_avatar.url
        return None

    def delete_avatar(self):
        if self.account_avatar:
            self.account_avatar.delete(save=False)
            self.account_avatar = None
            self.save()

            
class UserFriendRelationship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_friends')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_users')
    relationship=models.CharField(max_length=10,default='好友')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ['user', 'friend']


class FriendRequest(models.Model):
    STATUS_PENDING = 1
    STATUS_ACCEPTED = 2
    STATUS_REJECTED = 3
    
    STATUS_CHOICES = ((STATUS_PENDING, '待处理'),(STATUS_ACCEPTED, '已接受'),(STATUS_REJECTED, '已拒绝'),)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests', verbose_name="发送方")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests', verbose_name="接收方")
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name="请求状态")
    rejected_at = models.DateTimeField(null=True, blank=True, verbose_name="拒绝时间",default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')
        verbose_name = "好友请求"

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.get_status_display()})"
    


class GenericMessage(models.Model):
    # 核心优化：thread_id = f"{min_id}_{max_id}"，用于聚合两个人的双向对话
    thread_id = models.CharField(max_length=64, default="system",db_index=True, verbose_name="会话ID",help_text="格式: 小用户ID_大用户ID")
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages',
        verbose_name="发送方"
    )
    
    receiver = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_messages',
        verbose_name="接收方"
    )
    
    content_type = models.CharField(
        max_length=20, 
        default="text", 
        verbose_name="内容类型"
    )
    
    content = models.TextField(verbose_name="消息内容")
    is_read = models.BooleanField(default=False, verbose_name="是否已读")
    is_valid = models.BooleanField(default=True, verbose_name="是否有效")
    created_at = models.DateTimeField(db_index=True, verbose_name="创建时间")
    extensions = models.JSONField(default=dict, blank=True, verbose_name="扩展数据")
    class Meta:
        verbose_name = "消息"
        verbose_name_plural = "消息"
        indexes = [
            models.Index(fields=['thread_id', '-created_at'], name='idx_thread_time'),
            
            # 2. 场景：查询发送给“我”的所有未读消息
            # 覆盖索引：先找接收人，再找未读状态
            models.Index(fields=['receiver', 'is_read', '-created_at'], name='idx_receiver_unread'),
            
            # 3. 场景：根据发送者查询（用于撤回消息或个人消息审计）
            models.Index(fields=['sender', '-created_at'], name='idx_sender_time'),
        ]

    def __str__(self):
        return f"{self.sender_id} -> {self.receiver_id}: {self.content[:20]}"

    @staticmethod
    def get_thread_id(id1, id2):
        """工具方法：生成一致的会话ID"""
        ids = sorted([int(id1), int(id2)])
        return f"{ids[0]}_{ids[1]}"
    