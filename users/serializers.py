from rest_framework import serializers
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from django.db import transaction,models
from .models import UserInfo  ,UserFriendRelationship,FriendRequest
from django.conf import settings
import os,base64
import datetime
from datetime import timedelta
from pathlib import Path
import re

User = get_user_model()
DEFAULT_AVATAR_PATH = r'media\avatar\default_avatar.png'


class UserRegistrationSerializer(serializers.ModelSerializer):
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
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        UserInfo.objects.create(
            profile=user, 
            phone_number=phone_number
        )
        return user



class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(label='用户名', write_only=True)
    password = serializers.CharField(label='密码', style={'input_type': 'password'}, write_only=True)
    token = serializers.CharField(label=_("Token"), read_only=True) 

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                msg = _('账户或密码错误。') 
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('必须提供用户名和密码。')
            raise serializers.ValidationError(msg, code='authorization')
        data['user'] = user
        return data
    


class fetch_user_info(serializers.Serializer):
    username = serializers.CharField(source='profile.username', read_only=True)
    account_id = serializers.CharField(read_only=True)
    account_avatar = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = UserInfo
        fields = ('username', 'account_id', 'account_avatar')
    def get_account_avatar(self, obj):
        avatar_field = getattr(obj, 'account_avatar', None)
        if avatar_field and avatar_field.name:
            print('直接找到关联头像文件')
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
        print('执行到这')
        if has_id and has_name:
            raise serializers.ValidationError("只能传入 'account_id' 或 'account_name' 中的一个，不能同时传入两者。")
        if not has_id and not has_name:
            raise serializers.ValidationError("请至少传入 'account_id' 或 'account_name' 中的一个。")
        try:
            db_to_user_id_index=get_db_to_user_id_index()
            if db_to_user_id_index==from_account_id_index:
                raise serializers.ValidationError("不能添加自己为好友。")
            is_friend_already = UserFriendRelationship.objects.filter(user_id=from_account_id_index,friend_id=db_to_user_id_index).exists()
            if is_friend_already:
                raise serializers.ValidationError("已经是好友关系。")
            requested_history = FriendRequest.objects.filter(from_user_id=from_account_id_index,to_user_id=db_to_user_id_index)
            if requested_history:
                for every_request in requested_history:
                    if every_request.status==1:
                        raise serializers.ValidationError("已经发送过好友请求。")
                    elif every_request.status==2:
                        raise serializers.ValidationError("已经是好友关系。")
                    elif every_request.status==3:
                        timenow=datetime.datetime.now()
                        three_days = timedelta(days=3)
                        time_difference = timenow - every_request.rejected_at
                        allowday=every_request.rejected_at+three_days
                        hours_left=(allowday-timenow)*24
                        if time_difference < three_days:
                            error_message = f"已经拒绝过好友请求，约 {hours_left} 小时可后再试。" 
                            raise serializers.ValidationError(error_message)
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
    notify_name = serializers.CharField(default='好友请求')
    notify_content = serializers.SerializerMethodField(default='你收到好友请求', read_only=True)

    def has_notification(self,request):
        friendrequest_instance=request.user.received_requests
        for every_request in friendrequest_instance:
            if every_request.status==1:
                return True
        return False


class fetch_user_notification(serializers.Serializer):
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

