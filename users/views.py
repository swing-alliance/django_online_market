from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.contrib.auth import get_user_model
from .serializers import (UserRegistrationSerializer, UserLoginSerializer, fetch_user_info,
                          user_add_friend,fetch_user_notification,user_handle_request,user_fetch_friends,user_del_friend,
                          BoostedFetchUserAvatarSerializer,UserUploadAvatarSerializer,GetAvatarByIdSerializer)
from .models import UserInfo
from django.conf import settings
from django.contrib.auth import login, logout
import datetime

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    """用户注册接口：创建 User 和 UserInfo 记录"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class UserLoginView(APIView):
    """
    用户登录端点：
    1. 生成 JWT Token 并返回到响应体。
    2. 执行 django.contrib.auth.login() 设置 SessionID Cookie (适配 Channels)。
    """
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        login(request, user) 
        tokens = get_tokens_for_user(user)
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
        response_data = {
            'username': user.username,
            'user_id': user.id,
            'message': '登录成功',
            'access_token': access_token,
            'refresh_token': refresh_token,
        }
        response = Response(response_data, status=status.HTTP_200_OK)

        session_key = request.session.session_key
        response.set_cookie(
        key='sessionid',
        value=session_key,
        httponly=True,  # 防止 JavaScript 访问
        secure=False,    # 开发时禁用 HTTPS
        samesite='Lax',  # 限制跨站点请求时发送
        path='/',        # 在整个网站有效
        max_age=60*60*24*7
        )
        return response


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated] 
    def post(self, request):
        logout(request)
        response = Response({"message": "Logout successful."}, status=status.HTTP_200_OK)
        response.delete_cookie('sessionid')
        return response

class FetchUserInfoView(APIView):
    "用户获取自己的信息"
    permission_classes = [IsAuthenticated] 
    def get(self, request):
        sessionid = request.COOKIES.get('sessionid')
        try:
            user_info_instance = request.user.user_info 
        except UserInfo.DoesNotExist:
            return Response(
                {"detail": "用户资料记录不存在。"}, 
                status=404
            )
        serializer = fetch_user_info(instance=user_info_instance)
        return Response(serializer.data, status=200)


    


def get_tokens_for_user(user):
    """一个辅助函数，接收 User 实例，返回 access 和 refresh 令牌。"""
    refresh = RefreshToken.for_user(user)
    return {
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
    }




class AddFriendRequestView(APIView):
    "用户添加好友"
    permission_classes = [IsAuthenticated] 
    def post(self, request, *args, **kwargs):
        serializer = user_add_friend(data=request.data,context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": "ok"})
    


class FetchUserNotificationView(APIView):
    "用户获取自己的通知"
    permission_classes = [IsAuthenticated] 
    notification_queue = []
    def get(self, request):
        try:
            request_instance = request.user.received_requests.filter(status=1) 
        except UserInfo.DoesNotExist:
            return Response(
                {"detail": "用户资料记录不存在。"}, 
                status=404
            )
        serializer = fetch_user_notification(instance=request_instance,many=True)
        return Response(serializer.data, status=200)

class UserHandleRequestView(APIView):
    "用户处理好友请求"
    permission_classes = [IsAuthenticated] 
    def post(self, request, *args, **kwargs):
        try:
            request_instance = request.user.received_requests
        except:
            return Response(
                {"错误": "处理失败。"}, 
                status=404
            )
        serializer = user_handle_request(instance=request_instance,data=request.data,context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": "ok"})
    


class UserFetchFriendView(APIView):
    "用户获取好友列表"
    permission_classes = [IsAuthenticated] 
    def get(self, request):
        try:
            request_instance = request.user
        except UserInfo.DoesNotExist:
            return Response(
                {"detail": "用户资料记录不存在。"}, 
                status=404
            )
        serializer = user_fetch_friends(instance=request_instance,context={'request': request})
        return Response(serializer.data, status=200)


class BoostedFetchUserAvatarView(APIView):
    permission_classes = [IsAuthenticated] 
    def get(self, request, *args, **kwargs):
        try:
            user_info = UserInfo.objects.get(profile=request.user)
        except UserInfo.DoesNotExist:
            return Response({"detail": "User info not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = BoostedFetchUserAvatarSerializer(user_info)
        return Response(serializer.data, status=status.HTTP_200_OK)





class UserUploadAvatarView(generics.UpdateAPIView):
    """处理用户头像上传和更新的通用视图，使用 try/except 手动查找实例。"""
    serializer_class = UserUploadAvatarSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        try:
            instance = UserInfo.objects.get(profile=self.request.user)
            return instance
        except UserInfo.DoesNotExist:
            raise Http404("用户没有对应的 UserInfo 记录。")
    


class GetAvatarByIdView(APIView):
    permission_classes = [permissions.AllowAny] 
    def get(self, request):
        account_id=request.query_params.get('account_id')
        try:
            user_info = UserInfo.objects.get(profile=account_id)
        except UserInfo.DoesNotExist:
            return Response({"detail": "User info not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = GetAvatarByIdSerializer(user_info)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FetchChatHistoryView(APIView):
    "用户获取与某好友的聊天记录"
    permission_classes = [IsAuthenticated] 
    def get(self, request):
        from .models import GenericMessage
        friend_id=request.query_params.get('friend_id')
        user_id=request.user.id
        search_id=GenericMessage.get_thread_id(user_id,friend_id)
        chat_history = GenericMessage.objects.filter(thread_id=search_id).order_by('created_at')
        history_data = []
        for msg in chat_history:
            if msg.sender_id == user_id:
                # 我发的消息
                history_data.append({
                    "myword": msg.content,
                    "timestamp": msg.created_at.timestamp()
                })
            else:
                # 好友发的消息
                history_data.append({
                    "friendword": msg.content,
                    "timestamp": msg.created_at.timestamp()
                })
        return Response(history_data, status=200)














