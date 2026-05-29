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

class GroupChatRoom(models.Model):
    # 使用 name 作为 primary_key，杜绝了默认自增 id
    name = models.CharField(max_length=100, primary_key=True, verbose_name="群聊名称")
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_groups', verbose_name="群主")
    members = models.ManyToManyField(User, related_name='group_chats', verbose_name="群聊成员")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "群聊"
        verbose_name_plural = "群聊"

    def __str__(self):
        return self.name

    def add_members(self, users):
        if not users:
            return
        if not isinstance(users, (list, tuple, models.QuerySet)):
            users = [users]
        else:
            users = list(users)
            
        cleaned_users = []
        for u in users:
            if isinstance(u, (int, models.Model)):
                cleaned_users.append(u)
            elif isinstance(u, str) and u.isdigit():
                cleaned_users.append(int(u))  # 强转前端传来的字符串 ID   
        if cleaned_users:
            self.members.add(*cleaned_users)


class GroupMessage(models.Model):
    group = models.ForeignKey(GroupChatRoom, on_delete=models.CASCADE, related_name='messages', verbose_name="所属群聊")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_messages', verbose_name="发送者")
    content_type = models.CharField(max_length=20, default="text", verbose_name="内容类型")
    content = models.TextField(verbose_name="消息内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "群消息"
        verbose_name_plural = "群消息"

    def __str__(self):
        return f"{self.sender.username} in {self.group.name}: {self.content[:20]}"


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
    


class Forum(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Forum版块名称")
    description = models.TextField(blank=True, verbose_name="版块简介/公告")
    icon_base64 = models.TextField(blank=True, verbose_name="版块图标Base64")
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_forums', verbose_name="Forum创始人")
    admins = models.ManyToManyField(User, related_name='managed_forums', blank=True, verbose_name="Forum管理员列表")
    members = models.ManyToManyField(User, related_name='joined_forums', blank=True, verbose_name="Forum成员列表")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="帖子标题")
    content = models.TextField(verbose_name="帖子正文")
    # 封面图与点赞统计（冗余字段以提升查询性能）
    cover_image = models.TextField(blank=True, null=True, verbose_name="封面图Base64")
    like_count = models.PositiveIntegerField(default=0, verbose_name="点赞总数")
    
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='posts', verbose_name="所属Forum")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name="发帖人")
    view_count = models.PositiveIntegerField(default=0, verbose_name="浏览量")
    is_pinned = models.BooleanField(default=False, verbose_name="是否置顶")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")

class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', verbose_name="所属帖子")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_posts', verbose_name="点赞用户")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="点赞时间")

    class Meta:
        unique_together = ('post', 'user')

class PostMedia(models.Model):
    MEDIA_TYPE_CHOICES = [('image', '图片'), ('video', '视频')]
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='medias', verbose_name="所属帖子")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, verbose_name="媒体类型")
    file_url = models.URLField(max_length=500, verbose_name="文件CDN直链")
    sort_order = models.IntegerField(default=0, verbose_name="排序")

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name="所属帖子")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="评论人")
    content = models.TextField(verbose_name="回复内容")
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")

class ForumBanList(models.Model):
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='ban_records', verbose_name="所属Forum")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_bans', verbose_name="被封禁玩家")
    reason = models.CharField(max_length=255, blank=True, verbose_name="封禁原因")
    banned_at = models.DateTimeField(auto_now_add=True, verbose_name="封禁开始时间")
    ban_until = models.DateTimeField(verbose_name="解封时间")

    class Meta:
        unique_together = ('forum', 'user')

    @classmethod
    def check_user_ban_status(cls, user_id, forum_id):
        now = timezone.now()
        try:
            ban_record = cls.objects.get(user_id=user_id, forum_id=forum_id, ban_until__gt=now)
            remaining_time = ban_record.ban_until - now
            return {
                "is_banned": True,
                "reason": ban_record.reason,
                "remaining_str": f"{remaining_time.days}天 {remaining_time.seconds // 3600}小时"
            }
        except cls.DoesNotExist:
            return {"is_banned": False}