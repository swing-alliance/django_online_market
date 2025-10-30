from rest_framework import generics
from rest_framework.permissions import AllowAny # 导入 AllowAny 权限
from django.contrib.auth.models import User
from .serializers import RegisterSerializer

class RegisterView(generics.CreateAPIView):
    """
    处理用户注册的 API 视图。
    接受 POST 请求，如果数据有效，则创建新用户。
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    # 允许任何人 (包括未认证用户) 访问此视图
    permission_classes = [AllowAny] 

# 注意: 你还需要在你的 Django 应用中配置 urls.py 来指向这个 RegisterView
# 例如: path('register/', RegisterView.as_view(), name='register'),
