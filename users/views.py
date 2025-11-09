from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, UserLoginSerializer, fetch_user_info,user_add_friend,fetch_user_notification
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
    permission_classes = [IsAuthenticated] 
    def post(self, request, *args, **kwargs):
        serializer = user_add_friend(data=request.data,context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": "ok"})
    


class FetchUserNotification(APIView):
    permission_classes = [IsAuthenticated] 
    notification_queue = []
    def get(self, request):
        try:
            request_instance = request.user.received_requests 
        except UserInfo.DoesNotExist:
            return Response(
                {"detail": "用户资料记录不存在。"}, 
                status=404
            )
        serializer = fetch_user_notification(instance=request_instance,many=True)
        print(serializer.data)
        return Response(serializer.data, status=200)

