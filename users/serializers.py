from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class RegisterSerializer(serializers.ModelSerializer):
    # 确认密码字段，Model中没有，只用于验证
    password_confirm = serializers.CharField(
        style={'input_type': 'password'}, 
        write_only=True
    )

    class Meta:
        model = User
        # 接收前端的这四个字段
        fields = ('username', 'email', 'password', 'password_confirm') 
        extra_kwargs = {
            # 密码必须是写入操作，且不被读取
            'password': {'write_only': True, 'style': {'input_type': 'password'}}, 
            'email': {'required': True}, # 强制要求邮箱
        }

    def validate_email(self, value):
        # 验证邮箱是否已被注册
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("此邮箱已被注册。")
        return value

    def validate(self, data):
        # 检查两次密码是否一致
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "两次输入的密码不一致。"})
        return data

    def create(self, validated_data):
        # 移除确认密码字段，因为它不需要保存到数据库
        validated_data.pop('password_confirm') 
        
        # 使用 create_user 方法安全地创建用户 (自动哈希密码)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
