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
    phone_number = models.CharField(max_length=15,verbose_name="手机号")
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
