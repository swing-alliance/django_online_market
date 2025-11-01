# users/views.py
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, UserInfoSerializer, UserUpdateSerializer, UserLoginSerializer

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    """用户注册接口：创建 User 和 UserInfo 记录"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class UserLoginView(APIView):
    print('调用登录视图')
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.pop('user')
        tokens = get_tokens_for_user(user)
        serializer.validated_data['access_token'] = tokens['access_token']
        serializer.validated_data['username'] = user.username
        return Response(serializer.validated_data, status=status.HTTP_200_OK)



# --- 2. 用户仪表盘 (RetrieveAPIView) ---
class UserDashboardView(generics.RetrieveAPIView):
    """用户仪表盘/详情接口：返回当前用户的 User 和 UserInfo 数据"""
    # 使用 UserUpdateSerializer 来展示 User 和 UserInfo 的嵌套数据
    serializer_class = UserUpdateSerializer 
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # 确保只返回当前认证用户的数据
        return self.request.user

# --- 3. 用户基础信息更新 (UserInfoUpdateView) ---
class UserInfoUpdateView(generics.UpdateAPIView):
    """更新用户基础信息（如 first_name, last_name, phone_number, 昵称等）注意：头像更新可能需要单独的逻辑或使用 PUT/PATCH"""
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # 确保只能更新自己的信息
        return self.request.user
    
    # 使用 partial_update 来允许 PATCH 请求 (部分更新)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

# --- 4. 用户头像更新 (UserProfileUpdateView) ---
# 这是一个更专业的做法，只处理头像文件上传

    



def get_tokens_for_user(user):
    """一个辅助函数，接收 User 实例，返回 access 和 refresh 令牌。"""
    refresh = RefreshToken.for_user(user)
    return {
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
    }