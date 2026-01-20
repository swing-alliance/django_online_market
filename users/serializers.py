from rest_framework import serializers
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from django.db import transaction,models
from .models import UserInfo  ,UserFriendRelationship,FriendRequest
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.conf import settings
import os,base64
import datetime
from django.utils import timezone
from datetime import timedelta
from pathlib import Path
import re

User = get_user_model()
DEFAULT_AVATAR_PATH = r'media/avatar/default_avatar.png'


class UserRegistrationSerializer(serializers.ModelSerializer):
    """用户注册"""
    phone_number = serializers.CharField(required=True, max_length=15, label='手机号',write_only=True ) 
    password_confirm = serializers.CharField(style={'input_type': 'password'}, write_only=True, label='确认密码')
    class Meta:
        model = User
        fields = ('username', 'phone_number', 'password', 'password_confirm')
        extra_kwargs = {
            'password': {'write_only': True},
            'phone_number': {'write_only': True}, 
            'password_confirm': {'write_only': True}
        }
    def validate(self, data):
        username=data['username']
        if username.strip() == '':
            raise serializers.ValidationError({"用户名不能为空。"})
        if len(username) > 7:
            raise serializers.ValidationError({"用户名最多 7 个字符。"})
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "两次输入的密码不匹配。"})
        phone_number = data.get('phone_number')
        if phone_number and str(phone_number).strip():
            phone_number_str = str(phone_number).strip()
            if not re.match(r'^\d{11}$', phone_number_str):
                raise serializers.ValidationError({"错误": "电话号码格式不正确，必须是 11 位数字。"})
            if UserInfo.objects.filter(phone_number=phone_number).exists():
                 raise serializers.ValidationError({"错误": "该手机号已被注册。"})
        return data

    @transaction.atomic
    def create(self, validated_data):
        phone_number = validated_data.pop('phone_number')
        validated_data.pop('password_confirm')
        user = User.objects.create_user( username=validated_data['username'], password=validated_data['password'])
        UserInfo.objects.create(profile=user, phone_number=phone_number)
        return user



class UserLoginSerializer(serializers.Serializer):
    """用户登录"""
    username = serializers.CharField(label='用户名', write_only=True)
    password = serializers.CharField(label='密码', style={'input_type': 'password'}, write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        request = self.context.get('request')
        
        if username and password:
            user = authenticate(request=request, username=username, password=password)
            if not user:
                msg = _('账户或密码错误。') 
                raise serializers.ValidationError(msg, code='authorization')
            if not user.is_active:
                msg = _('用户账户未激活。')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('必须提供用户名和密码。')
            raise serializers.ValidationError(msg, code='authorization')
        data['user'] = user
        return data
    


class fetch_user_info(serializers.Serializer):
    """获取用户信息"""
    username = serializers.CharField(source='profile.username', read_only=True)
    account_id = serializers.CharField(read_only=True)
    account_avatar = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = UserInfo
        fields = ('username', 'account_id', 'account_avatar')
    def get_account_avatar(self, obj):
        avatar_field = getattr(obj, 'account_avatar', None)
        if avatar_field and avatar_field.name:
            absolute_file_path = avatar_field.path
        else:
            absolute_file_path = os.path.join(settings.BASE_DIR,DEFAULT_AVATAR_PATH)
        if not os.path.exists(absolute_file_path):
            return None  # 文件不存在时返回空
        try:
            with open(absolute_file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return f"data:image/png;base64,{encoded_string}" 
        except Exception as e:
            print(f"Error reading or encoding image: {e}")
            return None
        
class user_add_friend(serializers.Serializer):
    """添加好友"""
    account_id=serializers.CharField(label="用户id",allow_blank=True)
    account_name=serializers.CharField(label="用户名称",allow_blank=True)
    def validate(self, data):
        request = self.context.get('request')
        from_account_instance = request.user
        from_account_id_index = from_account_instance.pk
        to_account_id = data.get('account_id')
        to_accout_name = data.get('account_name')
        has_id = bool(to_account_id)
        has_name = bool(to_accout_name)
        def get_db_to_user_id_index():
            if has_id:
                try:
                    to_user_info_record = UserInfo.objects.get(account_id=to_account_id.strip())
                    return to_user_info_record.pk
                except UserInfo.DoesNotExist:
                    raise serializers.ValidationError("用户ID不存在。")
            elif has_name:
                try:
                    to_user_info_record = User.objects.get(username=to_accout_name.strip())
                    return to_user_info_record.pk
                except User.DoesNotExist:
                    raise serializers.ValidationError("用户名称不存在。")
        if has_id and has_name:
            raise serializers.ValidationError("只能传入 'account_id' 或 'account_name' 中的一个，不能同时传入两者。")
        if not has_id and not has_name:
            raise serializers.ValidationError("请至少传入 'account_id' 或 'account_name' 中的一个。")
        try:
            db_to_user_id_index=get_db_to_user_id_index()
            if db_to_user_id_index==from_account_id_index:
                raise serializers.ValidationError("不能添加自己为好友。")
            is_friend_already = UserFriendRelationship.objects.filter(user_id=from_account_id_index,friend_id=db_to_user_id_index).exists()
            reverse_is_friend_already = UserFriendRelationship.objects.filter(user_id=db_to_user_id_index,friend_id=from_account_id_index).exists()
            if is_friend_already or reverse_is_friend_already:
                raise serializers.ValidationError("已经是好友关系。")
            requested_history = FriendRequest.objects.filter(from_user_id=from_account_id_index,to_user_id=db_to_user_id_index)
            if requested_history:
                for every_request in requested_history:
                    if every_request.status==1:
                        raise serializers.ValidationError("已经发送过好友请求。")
                    elif every_request.status==2:
                        raise serializers.ValidationError("已经是好友关系。")
                    elif every_request.status==3:
                        timenow=timezone.now()
                        punish_days = timedelta(days=0)
                        allowday=every_request.rejected_at+punish_days
                        timeleft=allowday-timenow
                        if timeleft > timedelta(0):
                            hours_left = timeleft.total_seconds() / 3600
                            raise serializers.ValidationError(f"已经拒绝过好友请求，约 {hours_left} 小时可后再试。")
                        every_request.delete()
            data['from_account_id_index'] = from_account_id_index
            data['db_to_user_id_index'] = db_to_user_id_index
        except UserInfo.DoesNotExist:
            raise serializers.ValidationError("传入的 accout_id 不存在。")
        return data
    @transaction.atomic
    def create(self, validated_data):
        from_account_id_index = validated_data.pop('from_account_id_index')
        db_to_user_id_index = validated_data.pop('db_to_user_id_index')
        FriendRequest.objects.create(from_user_id=from_account_id_index,to_user_id=db_to_user_id_index)
        return validated_data
    




class fetch_user_notification(serializers.Serializer):
    "好友请求通知"
    notify_name = serializers.ReadOnlyField(default='好友请求')
    notify_content = serializers.SerializerMethodField(read_only=True)
    request_id = serializers.IntegerField(source='id', read_only=True) # 方便前端操作这条请求
    from_user_id = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    def get_notify_content(self, obj):
        try:
            request_from_name = obj.from_user.username
            return f"您收到了来自 {request_from_name} 的好友请求，请及时处理。"
        except User.DoesNotExist:
            return "您收到了来自未知用户的请求。"



class user_handle_request(serializers.Serializer):
    "用户处理好友请求"
    request_id = serializers.IntegerField(required=True) 
    action = serializers.ChoiceField(choices=['approve', 'reject', 'ignore'], required=True)
    def validate(self, data):
        request_id = data.get('request_id')
        action = data.get('action')
        try:
            request_instance = FriendRequest.objects.get(id=request_id,status=1,to_user=self.context['request'].user)
        except FriendRequest.DoesNotExist:
            raise serializers.ValidationError({"错误": "请求不存在或者此请求与你无关。"})
        if request_instance.status==2:
            raise serializers.ValidationError({"错误": "已经是好友关系。"})
        if request_instance.status==3:
            raise serializers.ValidationError({"错误": "已经拒绝过好友请求。"})
        if action not in ['approve', 'reject', 'ignore']:
            raise serializers.ValidationError({"错误": "无效的操作。"})
        return data
    @transaction.atomic
    def update(self, instance, validated_data):
        request_id = validated_data.get('request_id')
        action = validated_data.get('action')
        try:
            request_instance = FriendRequest.objects.get(id=request_id)
        except FriendRequest.DoesNotExist:
            raise serializers.ValidationError({"错误": "请求不存在。"})
        if action == 'approve':
            UserFriendRelationship.objects.create(user=request_instance.to_user,friend=request_instance.from_user,relationship='好友')
            UserFriendRelationship.objects.create(user=request_instance.from_user,friend=request_instance.to_user,relationship='好友')
            reverse_request = FriendRequest.objects.filter(from_user=request_instance.to_user,to_user=request_instance.from_user).first()
            if reverse_request:
                reverse_request.delete()
            request_instance.delete()
        elif action == 'reject':
            request_instance.status = 3
            request_instance.rejected_at = datetime.datetime.now()
            request_instance.save()
        elif action == 'ignore':
            request_instance.delete()
        return request_instance

class user_fetch_friends(serializers.Serializer):
    """获取好友列表"""
    friend_id = serializers.SerializerMethodField(read_only=True)
    friend_account_name = serializers.SerializerMethodField(read_only=True)
    friend_account_id = serializers.SerializerMethodField(read_only=True)
    avatar_url = serializers.SerializerMethodField(read_only=True)
    @cached_property
    def get_relationship_instances(self):
        """获取好友关系实例"""
        user = self.context['request'].user
        instances = UserFriendRelationship.objects.filter(user=user, relationship='好友').select_related('friend', 'friend__user_info')
        return instances

    def get_friend_id(self, obj):
        try:
            instances = self.get_relationship_instances
            friend_ids = [instance.friend.id for instance in instances]
            return friend_ids
        except Exception:
            return [] 
        
    def get_friend_account_name(self, obj):
        try:
            instances = self.get_relationship_instances
            friend_accout_names = [instance.friend.username for instance in instances]
            return friend_accout_names
        except Exception:
            return []

    def get_friend_account_id(self, obj):
        try:
            instances = self.get_relationship_instances
            friend_accout_ids = [instance.friend.user_info.account_id 
                                 for instance in instances 
                                 if hasattr(instance.friend, 'user_info')] 
            return friend_accout_ids
        except Exception as e:
            return []
    
    def get_avatar_url(self, obj):
        try:
            instances = self.get_relationship_instances
            avatar_urls = [
            instance.friend.user_info.account_avatar.url 
            if instance.friend.user_info and instance.friend.user_info.account_avatar 
            else None 
            for instance in instances
        ]
            return avatar_urls
        except Exception:
            return []


class user_del_friend(serializers.Serializer):
    "用户删除好友"
    friend_id = serializers.IntegerField(required=True)
    def validate(self, data):
        friend_id = data.get('friend_id')
        try:
            friend_instance = UserFriendRelationship.objects.get(user=self.context['request'].user,friend_id=friend_id,relationship='好友')
            friend_instance.delete()
        except User.DoesNotExist:
            raise serializers.ValidationError({"错误": "好友不存在。"})
        return data
    
class UserUploadAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ['account_avatar']
    def validate_account_avatar(self, value):
        """验证上传的头像文件大小不超过 4MB"""
        max_size = 4 * 1024 * 1024  # 4MB in bytes
        if value and value.size > max_size:
            raise serializers.ValidationError("文件大小不能超过 4MB。")
        return value



class BoostedFetchUserAvatarSerializer(serializers.ModelSerializer):
    """序列化器：返回带修改时间戳版本号的头像 URL，实现高效浏览器缓存。"""
    # 使用 SerializerMethodField 自定义 avatar_url 的返回逻辑
    avatar_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserInfo 
        fields = ('avatar_url',)

    def get_avatar_url(self, obj):
        """核心逻辑：生成带有文件修改时间戳（mtime）查询参数的 URL。"""
        avatar_file = obj.account_avatar
        if not avatar_file or not hasattr(avatar_file, 'url'):
            return f'{settings.BASE_DOMAIN}{DEFAULT_AVATAR_PATH}'
        try:
            file_path = avatar_file.path
        except NotImplementedError:
             return avatar_file.url
        except Exception:
            return f'{settings.BASE_DOMAIN}{DEFAULT_AVATAR_PATH}'
        try:
            mtime = int(os.path.getmtime(file_path))
        except FileNotFoundError:
            return f'{settings.BASE_DOMAIN}{DEFAULT_AVATAR_PATH}'
        return f"{avatar_file.url}?v={mtime}"


class GetAvatarByIdSerializer(serializers.Serializer):
    avatar_url = serializers.SerializerMethodField(read_only=True)
    def get_avatar_url(self, obj):
        avatar_file = obj.account_avatar
        if not avatar_file or not hasattr(avatar_file, 'url'):
            return f'{settings.BASE_DOMAIN}{DEFAULT_AVATAR_PATH}'
        return avatar_file.url




