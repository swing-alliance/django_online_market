from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import (UserRegistrationSerializer, UserLoginSerializer, fetch_user_info,
                          user_add_friend,fetch_user_notification,user_handle_request,user_fetch_friends,user_del_friend,BoostedFetchUserAvatarSerializer)
from .models import UserInfo

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    """用户注册接口：创建 User 和 UserInfo 记录"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class UserLoginView(APIView):
    """用户登录接口：返回 access 和 refresh 令牌"""
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.pop('user')
        serializer.validated_data.pop('password')
        tokens = get_tokens_for_user(user)
        serializer.validated_data['access_token'] = tokens['access_token']
        serializer.validated_data['refresh_token'] = tokens['refresh_token']
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class FetchUserInfoView(APIView):
    permission_classes = [IsAuthenticated] 
    def get(self, request):
        try:
            user_info_instance = request.user.user_info 
        except UserInfo.DoesNotExist:
            return Response(
                {"detail": "用户资料记录不存在。"}, 
                status=404
            )
        serializer = fetch_user_info(instance=user_info_instance)
        return Response(serializer.data, status=200)


    
class ProtectedTestView(APIView):
    """这是一个需要 JWT 认证才能访问的测试 API。"""
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"message": "已认证！Access Token 有效。"})


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


























