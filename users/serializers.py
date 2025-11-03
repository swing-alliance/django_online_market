from rest_framework import serializers
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from django.db import transaction,models
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
    class Meta:
        model = UserInfo
        fields = ('username', 'account_id')


