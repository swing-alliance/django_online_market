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
    return os.path.join('avatars', str(instance.user.id), new_filename)

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
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages',verbose_name="发送方")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages',verbose_name="接收方",db_index=True)
    content_type = models.CharField(max_length=50, verbose_name="内容类型",default="text")
    content = models.TextField(verbose_name="消息内容",null=False,blank=False)
    is_read = models.BooleanField(default=False, verbose_name="是否已读")
    is_valid = models.BooleanField(default=True, verbose_name="是否有效")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    extensions = models.JSONField(default=dict, verbose_name="扩展数据")

    class Meta:
        verbose_name = "消息"
        verbose_name_plural = "消息"
        ordering = ['created_at'] 
        indexes = [models.Index(fields=['sender', 'receiver','created_at'], name='sender_receiver_thread_idx'),]
    