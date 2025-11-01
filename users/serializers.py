from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from .models import UserInfo  # 确保导入了您定义的 UserInfo 模型
import re

User = get_user_model()



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
        print('调用我')
        username = data.get('username')
        password = data.get('password')
        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            print(user)
            if not user:
                msg = _('账户或密码错误。') 
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('必须提供用户名和密码。')
            raise serializers.ValidationError(msg, code='authorization')
        data['user'] = user
        return data
    




# --- 2. 详细信息序列化器 (用于仪表盘展示) ---
class UserInfoSerializer(serializers.ModelSerializer):
    # account_id 是只读的，由 default=generate_user_id 自动生成
    account_id = serializers.CharField(read_only=True) 
    # 获取头像的绝对 URL
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserInfo
        # 列出所有需要展示或更新的字段
        fields = ('phone_number', 'account_id', 'account_avatar', 'avatar_url', 'created_at')
        read_only_fields = ('account_id', 'created_at') # 账户ID和创建时间只读
    
    def get_avatar_url(self, obj):
        # 调用模型上的辅助方法
        return obj.get_avatar_url()

# --- 3. 用户信息更新序列化器 (UserInfoUpdateView 使用) ---
class UserUpdateSerializer(serializers.ModelSerializer):
    # 将 UserInfo 嵌套进来，用于展示和更新 UserInfo 字段
    user_info = UserInfoSerializer() 
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'user_info')
        read_only_fields = ('username',) # 假设 username 不允许修改

    # 重写 update 方法以处理嵌套模型
    def update(self, instance, validated_data):
        user_info_data = validated_data.pop('user_info', {})
        
        # 1. 更新 User 模型字段
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        
        # 2. 更新 UserInfo 模型字段
        user_info = instance.user_info # 通过 related_name 访问
        if user_info_data:
            # 假设只允许更新 phone_number
            user_info.phone_number = user_info_data.get('phone_number', user_info.phone_number)
            # 处理头像文件上传（如果需要）
            if 'account_avatar' in user_info_data:
                user_info.account_avatar = user_info_data['account_avatar']
            
            user_info.save()

        return instance