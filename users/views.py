from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from adrf.views import APIView as AdrfAPIView
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from asgiref.sync import sync_to_async
from .redis_service import redis_client
from django.utils import timezone
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


# class FetchChatHistoryView(APIView):
#     "用户获取与某好友的聊天记录"
#     permission_classes = [IsAuthenticated] 
#     def get(self, request):
#         from .models import GenericMessage
#         friend_id=request.query_params.get('friend_id')
#         user_id=request.user.id
#         search_id=GenericMessage.get_thread_id(user_id,friend_id)
#         chat_history = GenericMessage.objects.filter(thread_id=search_id).order_by('created_at')
#         history_data = []
#         for msg in chat_history:
#             if msg.sender_id == user_id:
#                 # 我发的消息
#                 history_data.append({
#                     "myword": msg.content,
#                     "timestamp": msg.created_at.timestamp()
#                 })
#             else:
#                 # 好友发的消息
#                 history_data.append({
#                     "friendword": msg.content,
#                     "timestamp": msg.created_at.timestamp()
#                 })
#         return Response(history_data, status=200)




class FetchChatHistoryView(AdrfAPIView):
    """返回对话记录，同步redis和数据库保证完整性"""
    permission_classes = [IsAuthenticated]

    async def get(self, request):
        from .models import GenericMessage
        friend_id = request.query_params.get('friend_id')
        user_id = request.user.id
        
        # 1. 包装静态方法或类方法 (包装数据库计算逻辑)
        # 假设 get_thread_id 涉及数据库查询或计算
        search_id = GenericMessage.get_thread_id(user_id, friend_id)

        # 2. 包装 QuerySet 查询并立即转为 list
        # QuerySet 本身不能在异步环境中直接遍历，必须先转成列表
        def get_db_history():
            return list(GenericMessage.objects.filter(thread_id=search_id).order_by('created_at'))

        chat_history = await sync_to_async(get_db_history)()

        history_data = []
        for msg in chat_history:
            history_data.append(self.serialize_msg(msg, user_id))

        # 2. 从 Redis 队列中获取还没入库的消息（解决刷新消失问题的关键）
        # 读取队列中所有的消息 (0-0 表示从头开始读)
        pending_entries = await redis_client.xrange("msg_write_queue")
        
        for m_id, content in pending_entries:
            s_id = str(content.get(b'sender_id', b'')).decode()
            r_id = str(content.get(b'receiver_id', b'')).decode()
            
            # 判断这条待入库消息是否属于当前聊天对话
            if (s_id == str(user_id) and r_id == str(friend_id)) or \
               (s_id == str(friend_id) and r_id == str(user_id)):
                msg_content = content.get(b'content', b'').decode()
                # 构造与数据库一致的格式
                item = {
                    "timestamp": timezone.now().timestamp(), # 临时时间戳
                    "is_pending": True # 标识这是还没存盘的消息
                }
                if s_id == str(user_id):
                    item["myword"] = msg_content
                else:
                    item["friendword"] = msg_content
                history_data.append(item)
        # 3. 按时间戳简单排序（防止 Redis 和 DB 数据交织）
        history_data.sort(key=lambda x: x['timestamp'])
        return Response(history_data, status=200)

    def serialize_msg(self, msg, user_id):
        if msg.sender_id == user_id:
            return {"myword": msg.content, "timestamp": msg.created_at.timestamp()}
        else:
            return {"friendword": msg.content, "timestamp": msg.created_at.timestamp()}









