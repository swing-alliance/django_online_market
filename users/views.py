from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from adrf.views import APIView as AdrfAPIView
from django.http import Http404
from .confuse import is_validation_field_valid
from django.db.models import Count
import traceback
from datetime import timedelta
from channels.db import database_sync_to_async
from .models import GenericMessage, GroupChatRoom,UserFriendRelationship,Forum,Post,Comment,PostLike,ForumBanList
import io
import csv
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from llm_service.AI_Engine import ai_engine
from rest_framework.permissions import IsAuthenticated
from asgiref.sync import sync_to_async
from django.http import StreamingHttpResponse, JsonResponse
import json
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
        # 打印所有请求头，方便调试查看字段是否正确传入
        validation_field = request.headers.get('ValidationField')
        if not validation_field:
            return Response({"detail": "缺少验证字段。"}, status=400)
        success, message = is_validation_field_valid(validation_field)
        if not success:
            return Response({"detail": "时间校验失败"}, status=403)
        print(f"--- 接收到的 ValidationField: {validation_field} ---")
        print(f"--- 验证结果: {message} ---")

        # 如果你想查看完整的头部信息，可以取消下面这行的注释
        # print("All Request Headers:", request.headers)

        sessionid = request.COOKIES.get('sessionid')
        try:
            print("调用了 FetchUserInfoView")
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
    




class UserFetchFriendIdView(AdrfAPIView):
    """返回好友的 id 和 username 列表"""
    permission_classes = [IsAuthenticated]
    
    async def get(self, request, *args, **kwargs):
        try:
            current_user = request.user
            def query_db():
                sent_ids = list(UserFriendRelationship.objects.filter(
                    user=current_user, relationship='好友'
                ).values_list('friend_id', flat=True))
                received_ids = list(UserFriendRelationship.objects.filter(
                    friend=current_user, relationship='好友'
                ).values_list('user_id', flat=True))
                friend_ids_set = set(sent_ids) | set(received_ids)
                friend_ids_set.discard(current_user.id)
                
                # 4. 批量查出对应的用户信息
                friends_data = list(User.objects.filter(
                    id__in=friend_ids_set
                ).values('id', 'username'))
                
                return friends_data
            friend_list = await database_sync_to_async(query_db)()
            return JsonResponse({"friends": friend_list}, status=200)
            
        except Exception as e:
            traceback.print_exc() 
            return JsonResponse({"error": "服务器内部错误", "detail": str(e)}, status=500)



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




@method_decorator(csrf_exempt, name='dispatch')
class AIChatView(View):
    """
    原生异步视图，完美适配 QwenStateMachine 的异步锁和流式推理
    """

    async def get(self, request, *args, **kwargs):
        """状态查询：Vue 轮询调用"""
        return JsonResponse({
            "model_status": ai_engine.status,
            "device": ai_engine.device,
            "initialized": ai_engine.initialized
        })

    async def post(self, request, *args, **kwargs):
        """流式对话：处理 AI 推理"""
        try:
            # 1. 解析数据
            body_data = json.loads(request.body)
            query = body_data.get("query")
            history = body_data.get("history", [])
            if not query:
                return JsonResponse({"error": "提问内容不能为空"}, status=400)
            # 2. 关键：必须 await 异步启动方法
            # QwenStateMachine.startup 内部有状态判断，多次调用不会重复加载
            await ai_engine.startup()
            if ai_engine.status == "OFFLINE":
                return JsonResponse({"error": "模型未能成功加载"}, status=500)
            # 3. 异步生成器适配 TextIteratorStreamer
            async def sse_generator():
                try:
                    # 调用 ai_engine 的异步流式方法
                    async for token in ai_engine.stream_chat(query, history):
                        if token:
                            # 构造符合 SSE 协议的消息
                            payload = json.dumps({"token": token}, ensure_ascii=False)
                            yield f"data: {payload}\n\n"
                    
                    yield "data: [DONE]\n\n"
                except Exception as stream_e:
                    print(f"Streaming Error: {traceback.format_exc()}")
                    yield f"data: {json.dumps({'error': str(stream_e)})}\n\n"
            # 4. 返回流式响应
            response = StreamingHttpResponse(
                sse_generator(),
                content_type="text/event-stream"
            )
            response['Cache-Control'] = 'no-cache'
            response['X-Accel-Buffering'] = 'no'
            return response
        except Exception as e:
            print("!!! AIChatView POST 崩溃 !!!")
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)



class manager_sensorializer_view(AdrfAPIView):
    permission_classes = [IsAuthenticated]
    async def post(self, request, *args, **kwargs):
        try:
            word = request.data.get("word", "")
            if not word:
                return JsonResponse({"error": "输入不能为空"}, status=400)
            is_legal = await ai_engine.is_word_legal(word)
            return JsonResponse({"is_legal": is_legal})
        except Exception as e:
            print(f"Manager Sensor Error: {traceback.format_exc()}")
            return JsonResponse({"error": str(e)}, status=500)
        
def generate_csv_data():
    """
    同步函数：负责安全地从数据库中提取数据并转换为 CSV 字节流
    """
    buffer = io.StringIO()
    buffer.write('\ufeff') 
    writer = csv.writer(buffer)
    writer.writerow([
        '消息ID', '会话ID', '发送方ID', '发送方用户名', 
        '接收方ID', '接收方用户名', '内容类型', '消息内容', 
        '是否已读', '是否有效', '创建时间', '扩展数据'
    ])
    queryset = GenericMessage.objects.all().select_related('sender', 'receiver').order_by('-created_at')
    for msg in queryset.iterator(chunk_size=2000):
        writer.writerow([
            msg.id,
            msg.thread_id,
            msg.sender_id,
            msg.sender.username if msg.sender else '',
            msg.receiver_id,
            msg.receiver.username if msg.receiver else '',
            msg.content_type,
            msg.content,
            1 if msg.is_read else 0,
            1 if msg.is_valid else 0,
            msg.created_at.strftime('%Y-%m-%d %H:%M:%S') if msg.created_at else '',
            msg.extensions
        ])
    
    # 返回整段二进制数据
    return buffer.getvalue().encode('utf-8')


class manager_export_chat_his(AdrfAPIView):
    permission_classes = [IsAuthenticated]

    async def get(self, request, *args, **kwargs):
        """
        异步 GET 请求：导出所有聊天记录为 CSV 格式
        """
        # 使用 sync_to_async 将同步的数据库 IO 和 CSV 拼装放到独立线程池执行，防止阻塞异步事件循环
        csv_bytes = await sync_to_async(generate_csv_data, thread_sensitive=False)()
        
        # 封装为文件下载响应
        response = StreamingHttpResponse(
            iter([csv_bytes]), 
            content_type='text/csv; charset=utf-8'
        )
        response['Content-Disposition'] = 'attachment; filename="chat_history_export.csv"'
        
        return response


class UserLaunchGroupChatView(AdrfAPIView):
    """用户发起拉群请求，创建房间并同步添加成员"""
    permission_classes = [IsAuthenticated]
    async def post(self, request, *args, **kwargs):
        try:
            current_user = request.user
            group_id = request.data.get("group_id")       
            user_ids = request.data.get("user_ids", [])   
            if not group_id:
                return JsonResponse({"error": "group_id 不能为空"}, status=400)
            if not isinstance(user_ids, list):
                user_ids = [user_ids] if user_ids else []
            user_ids = [int(uid) for uid in user_ids if uid]
            if current_user.id in user_ids:
                user_ids.remove(current_user.id)
            user_ids.insert(0, current_user.id)
            def get_or_create_room():
                try:
                    return GroupChatRoom.objects.get(name=group_id), False
                except GroupChatRoom.DoesNotExist:
                    return GroupChatRoom.objects.create(name=group_id, leader=current_user), True

            room, is_created = await database_sync_to_async(get_or_create_room)()

            # 调用经过清洗强化的 add_members 模型方法
            await database_sync_to_async(room.add_members)(user_ids)

            msg = f"成功创建群聊 '{group_id}'，您已成为群主" if is_created else f"已成功向群聊 '{group_id}' 邀请/同步新成员"

            return JsonResponse({
                "status": "success", 
                "message": msg,
                "data": {
                    "group_id": group_id,
                    "leader_id": current_user.id,
                    "current_members": user_ids
                }
            }, status=200)

        except ValueError:
            return JsonResponse({"error": "传入的 user_ids 格式不正确"}, status=400)
        except Exception as e:
            print(f"Launch Group Chat Error: {traceback.format_exc()}")
            return JsonResponse({"error": "服务器内部错误，请检查日志"}, status=500)



class user_see_groupchat_view(AdrfAPIView):  # 确保继承自 AdrfAPIView
    """查看当前用户已加入的群聊列表"""
    permission_classes = [IsAuthenticated]

    async def get(self, request, *args, **kwargs):
        try:
            current_user = request.user
            def get_user_groups():
                try:
                    return list(current_user.group_chats.all().values_list('name', flat=True))
                except AttributeError:
                    return list(current_user.groupchatroom_set.all().values_list('name', flat=True))
            group_chats_list = await database_sync_to_async(get_user_groups)()
            return JsonResponse({"group_chats": group_chats_list}, status=200)
        except Exception as e:
            print(f"See Group Chat Error:\n{traceback.format_exc()}")
            return JsonResponse({"error": "服务器内部错误", "detail": str(e)}, status=500)
        
class get_groupchat_his(AdrfAPIView):
    """用户获取某个群聊的聊天记录"""
    permission_classes = [IsAuthenticated]
    async def get(self, request, *args, **kwargs):
        try:
            group_id = request.query_params.get("group_id")
            if not group_id:
                return JsonResponse({"error": "group_id 不能为空"}, status=400)
            # 1. 异步获取群聊对象
            room = await database_sync_to_async(GroupChatRoom.objects.get)(name=group_id)
            # 2. 异步获取该群聊的所有消息记录
            messages = await database_sync_to_async(list)(
                room.messages.all().order_by('created_at').values(
                    'sender__username', 'content_type', 'content', 'created_at'
                )
            )
            return JsonResponse({
                "status": "success",
                "messages": messages
            }, status=200)
        except GroupChatRoom.DoesNotExist:
            return JsonResponse({"error": "指定的群聊不存在"}, status=404)
        except Exception as e:
            print(f"Get Group Chat History Error: {traceback.format_exc()}")
            return JsonResponse({"error": "服务器内部错误，请检查日志"}, status=500)



class delet_group_chat(AdrfAPIView):
    """用户删除群聊（仅限群主，依靠底层多对多中间表自增主键排序判定）"""
    permission_classes = [IsAuthenticated]
    async def post(self, request, *args, **kwargs):
        try:
            group_id = request.data.get("group_id")
            if not group_id:
                return JsonResponse({"error": "group_id 不能为空"}, status=400)
                
            # 1. 异步获取群聊对象
            room = await database_sync_to_async(GroupChatRoom.objects.get)(name=group_id)
            def get_creator_id(room):
                return room.leader_id
            creator_id = await database_sync_to_async(get_creator_id)(room)
            # 2. 严格核对权限
            if creator_id and creator_id != request.user.id:
                return JsonResponse({"error": "只有群创作者（群主）可以解散该群聊"}, status=403)
            # 3. 异步删除群聊对象（会级联删除相关消息）
            await database_sync_to_async(room.delete)()
            return JsonResponse({"status": "success", "message": f"群聊 '{group_id}' 已被成功解散并删除"}, status=200)
            
        except GroupChatRoom.DoesNotExist:
            return JsonResponse({"error": "指定的群聊不存在"}, status=404)
        except Exception as e:
            print(f"Delete Group Chat Error: {traceback.format_exc()}")
            return JsonResponse({"error": "服务器内部错误，请检查日志"}, status=500)
        


class get_group_info(AdrfAPIView):
    """查看群成员"""
    permission_classes = [IsAuthenticated]
    async def get(self, request, *args, **kwargs):
        try:
            group_id = request.query_params.get("group_id")
            if not group_id:
                return JsonResponse({"error": "group_id 不能为空"}, status=400)
            room = await database_sync_to_async(GroupChatRoom.objects.get)(name=group_id)
            members = await database_sync_to_async(list)(
                room.members.all().values('id', 'username')
            )
            return JsonResponse({
                "status": "success",
                "members": members
            }, status=200)
        except GroupChatRoom.DoesNotExist:
            return JsonResponse({"error": "指定的群聊不存在"}, status=404)
        except Exception as e:
            print(f"Get Group Info Error: {traceback.format_exc()}")
            return JsonResponse({"error": "服务器内部错误，请检查日志"}, status=500)


class UserChatInGroupView(AdrfAPIView):
    """安全强化版：用户在群聊中发送消息"""
    permission_classes = [IsAuthenticated]
    async def post(self, request, *args, **kwargs):
        try:
            current_user = request.user
            group_id = request.data.get("group_id")
            content = request.data.get("content")
            if not group_id or not content:
                return JsonResponse({"error": "group_id 和 content 不能为空"}, status=400)
            def get_group_room():
                return GroupChatRoom.objects.filter(name=group_id).order_by().first()
            room = await database_sync_to_async(get_group_room)()

            if not room:
                return JsonResponse({"error": "指定的群聊不存在"}, status=404)
            def check_membership():
                return room.members.order_by().filter(pk=current_user.pk).exists()
                
            is_member = await database_sync_to_async(check_membership)()
            if not is_member:
                return JsonResponse({"error": "您不是该群聊的成员，无法发送消息"}, status=403)
            message = await database_sync_to_async(room.messages.create)(
                sender=current_user,
                content_type="text",
                content=content
            )
            return JsonResponse({
                "status": "success",
                "message": f"消息已成功发送到群聊 '{group_id}'"
            }, status=200)

        except Exception as e:
            print(f"User Chat in Group Error: {traceback.format_exc()}")
            return JsonResponse({"error": "服务器内部错误，请检查日志"}, status=500)
        



class DeleteOrExitGroupView(AdrfAPIView):
    """创建者（leader）解散删除群聊，非创建者安全退出群聊"""
    permission_classes = [IsAuthenticated]
    
    async def post(self, request, *args, **kwargs):
        try:
            current_user = request.user
            group_id = request.data.get("group_id") 
            
            if not group_id:
                return JsonResponse({"error": "group_id 不能为空"}, status=400)
            def get_group_room():
                return GroupChatRoom.objects.filter(name=group_id).order_by().first()
            room = await database_sync_to_async(get_group_room)()
            if not room:
                return JsonResponse({"error": "指定的群聊不存在"}, status=404)
            def handle_group_action():
                if room.leader_id == current_user.id:
                    GroupChatRoom.objects.filter(name=group_id).delete()
                    return "dismissed", f"您是群主，已成功解散并删除了群聊 '{group_id}'"
                else:
                    # 非群主 -> 退出群组
                    if room.members.order_by().filter(pk=current_user.pk).exists():
                        room.members.remove(current_user)
                        return "exited", f"已成功退出群聊 '{group_id}'"
                    else:
                        return "not_in", "你本身就不在这个群聊中"

            action_type, message = await database_sync_to_async(handle_group_action)()
            return JsonResponse({
                "status": "success",
                "action": action_type,
                "message": message
            }, status=200)
            
        except Exception as e:
            print(f"Delete/Exit Group Error: {traceback.format_exc()}")
            return JsonResponse({"error": "服务器内部错误，请检查后端日志"}, status=500)





class UserCreateForumView(AdrfAPIView):
    permission_classes = [IsAuthenticated]
    async def post(self, request, *args, **kwargs):
        data = request.data
        user = request.user 
        forum_name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        icon_base64 = data.get('icon_base64', '') # 接收 Base64 字符串
        if not forum_name:
            return Response({"detail": "论坛名称不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        if await Forum.objects.filter(name=forum_name).aexists():
            return Response({"detail": "该论坛名称已被占用"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            forum = await Forum.objects.acreate(
                name=forum_name,
                description=description,
                icon_base64=icon_base64, # 存入 Base64
                creator=user
            )
            @sync_to_async
            def initialize_forum_relations(forum_obj, user_obj):
                forum_obj.admins.add(user_obj)
                forum_obj.members.add(user_obj)
                forum_obj.save()
            await initialize_forum_relations(forum, user)
            return Response({
                "message": "论坛创建成功！",
                "forum_info": {
                    "id": forum.id,
                    "name": forum.name,
                    "description": forum.description,
                    "creator": user.username,
                    "created_at": forum.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    # 注意：如果 Base64 特别大，建议不要在列表页返回此字段，这里仅返回成功确认
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": f"创建失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PostLikeView(AdrfAPIView):
    permission_classes = [IsAuthenticated]
    async def post(self, request, post_id, *args, **kwargs):
        """点赞/取消点赞接口"""
        user = request.user
        like_obj, created = await PostLike.objects.aget_or_create(post_id=post_id, user=user)
        if not created:
            await like_obj.adelete()
            return Response({"message": "取消点赞成功", "status": "unliked"})
        return Response({"message": "点赞成功", "status": "liked"}, status=status.HTTP_201_CREATED)



class UserJoinForumView(AdrfAPIView):
    permission_classes = [IsAuthenticated]
    async def post(self, request, *args, **kwargs):
        """玩家申请加入指定的 Forum（带黑名单拦截机制）前端请求 Body 需包含: {"forum_id": 1}"""
        forum_id = request.data.get('forum_id')
        if not forum_id:
            return Response({"detail": "缺少 forum_id"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        now = timezone.now()

        # 1. 黑名单检查
        is_banned = await ForumBanList.objects.filter(
            forum_id=forum_id,
            user_id=user.id,
            ban_until__gt=now
        ).aexists()

        if is_banned:
            ban_record = await ForumBanList.objects.aget(
                forum_id=forum_id,
                user_id=user.id,
                ban_until__gt=now
            )
            remaining_time = ban_record.ban_until - now
            days = remaining_time.days
            hours = remaining_time.seconds // 3600
            return Response({
                "detail": f"加入失败！你已被该论坛封禁。剩余封禁时间：{days}天 {hours}小时。"
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            # 2. 获取论坛并检查成员资格
            forum = await Forum.objects.aget(id=forum_id)
            is_member = await forum.members.filter(id=user.id).aexists()

            if is_member:
                return Response({
                    "detail": "你已经是该论坛的成员啦，无需重复加入 🕹️"
                }, status=status.HTTP_400_BAD_REQUEST)

            # 3. 异步执行加入操作 (使用 aadd 和 acount)
            await forum.members.aadd(user)
            total_members = await forum.members.acount()

            return Response({
                "message": f"🎉 欢迎加入【{forum.name}】游戏社区！",
                "forum_id": forum.id,
                "current_members_count": total_members
            }, status=status.HTTP_200_OK)

        except Forum.DoesNotExist:
            return Response({
                "detail": "你要加入的论坛不存在，可能已被管理员拔线 🔍"
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "detail": f"服务器开小差了: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class GetForumInfoView(AdrfAPIView):
    permission_classes = [IsAuthenticated]

    async def get(self, request, forum_id, *args, **kwargs):
        """
        获取论坛详细信息，包含：
        1. 基础信息
        2. 成员/管理员列表
        3. 带有封面图和点赞数的帖子预览（前10条）
        """
        try:
            forum = await Forum.objects.prefetch_related('members', 'admins').aget(id=forum_id)
            
            # 2. 异步查询最新的帖子（只取封面、点赞数、标题）
            posts_queryset = forum.posts.only('id', 'title', 'cover_image', 'like_count') \
                .order_by('-created_at')[:10]
            
            posts = []
            async for post in posts_queryset:
                posts.append({
                    "id": post.id,
                    "title": post.title,
                    "cover_image": post.cover_image, # 这是我们新增的封面字段
                    "like_count": post.like_count      # 这是我们新增的点赞计数
                })

            # 3. 整理成员和管理员数据
            members = [user async for user in forum.members.all().values('id', 'username')]
            admins = [user async for user in forum.admins.all().values('id', 'username')]
            
            return Response({
                "forum_info": {
                    "id": forum.id,
                    "name": forum.name,
                    "description": forum.description,
                    "icon_url": forum.icon_url,
                    "creator": forum.creator.username if forum.creator else "已注销",
                    "member_count": len(members) # 明确返回人数
                },
                "members": members,
                "admins": admins,
                "latest_posts": posts # 这里把帖子数据带上
            }, status=status.HTTP_200_OK)

        except Forum.DoesNotExist:
            return Response({"detail": "论坛不存在"}, status=status.HTTP_404_NOT_FOUND)




class CreatorDeletePostView(AdrfAPIView):
    permission_classes = [IsAuthenticated]
    
    async def delete(self, request, post_id, *args, **kwargs):
        try:
            # 使用 id 直接查询
            post = await Post.objects.select_related('forum').aget(id=post_id)
            forum = post.forum
            user = request.user
            
            # 使用 _id 字段比对，效率高且不易报错
            is_author = (post.author_id == user.id)
            is_creator = (forum.creator_id == user.id)
            is_admin = await sync_to_async(forum.admins.filter(id=user.id).exists)()

            if not (is_author or is_admin or is_creator):
                return Response({"detail": "无权限删除"}, status=status.HTTP_403_FORBIDDEN)
            
            await post.adelete()
            return Response({"message": "删除成功"}, status=status.HTTP_204_NO_CONTENT)
            
        except Post.DoesNotExist:
            return Response({"detail": "帖子不存在"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # 控制台输出报错详情，方便调试
            print(f"Error: {e}") 
            return Response({"detail": "服务器开小差了"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetTenForumsView(AdrfAPIView):
    permission_classes = [IsAuthenticated]
    async def get(self, request, *args, **kwargs):
        """获取最新的10个论坛，包含基础信息和成员数量"""
        try:
            # 优化：使用 annotate 直接在数据库层面计算 member_count，减少循环查询的压力
            forums_queryset = Forum.objects.annotate(
                member_count=Count('members')
            ).select_related('creator').order_by('-created_at')[:10]
            forums = []
            async for forum in forums_queryset:
                forums.append({
                    "id": forum.id,
                    "name": forum.name,
                    "description": forum.description,
                    # 如果 Base64 太长，列表页只返回前 100 个字符进行测试，或者根据实际需要返回
                    "icon_base64": forum.icon_base64, 
                    "creator": forum.creator.username if forum.creator else "已注销",
                    "member_count": forum.member_count # 直接使用上面 annotate 计算好的结果
                })
            return Response({"forums": forums}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": f"服务器开小差了: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserPostInForumView(AdrfAPIView):
    permission_classes = [IsAuthenticated]
    async def post(self, request, *args, **kwargs):
        """用户在论坛中发帖，前端请求 Body 需包含: {"forum_id": 1, "title": "帖子标题", "content": "帖子内容", "cover_image_base64": "数据..."}"""
        forum_id = request.data.get('forum_id')
        title = request.data.get('title', '').strip()
        content = request.data.get('content', '').strip()
        cover_image_base64 = request.data.get('cover_image_base64', '') # 新增封面字段

        if not forum_id or not title or not content:
            return Response(
                {"detail": "forum_id、title 和 content 都不能为空"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            forum = await Forum.objects.aget(id=forum_id)
            is_member = await forum.members.filter(id=request.user.id).aexists()
            if not is_member:
                return Response(
                    {"detail": "你不是该论坛的成员，无法发帖 "}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            post = await Post.objects.acreate(
                forum=forum,
                author=request.user,
                title=title,
                content=content,
                cover_image=cover_image_base64 # 存入封面数据
            )
            return Response({
                "message": "帖子发布成功！",
                "post_info": {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content,
                    "cover_image": post.cover_image, # 返回封面数据
                    "created_at": post.created_at.strftime("%Y-%m-%d %H:%M:%S")
                }
            }, status=status.HTTP_201_CREATED)
        except Forum.DoesNotExist:
            return Response(
                {"detail": "你要发布帖子的论坛不存在，可能已被管理员拔线 🔍"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": f"服务器开小差了: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetAllPostsView(AdrfAPIView):
    """获取指定论坛下的所有帖子"""
    async def get(self, request, *args, **kwargs):
        forum_id = request.query_params.get('forum_id')
        if not forum_id:
            return Response({"detail": "缺少 forum_id 参数"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            posts_queryset = Post.objects.filter(forum_id=forum_id).select_related('author').order_by('-created_at')  
            posts = []
            async for post in posts_queryset:
                posts.append({
                    "id": post.id,
                    "title": post.title,
                    "content": post.content,
                    "cover_image": post.cover_image,
                    "like_count": post.like_count,
                    "view_count": post.view_count,
                    "author": post.author.username,
                    "created_at": post.created_at.strftime("%Y-%m-%d %H:%M:%S")
                })
            return Response({"posts": posts}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": f"服务器查询出错: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class GetForummemberView(AdrfAPIView):
    async def get(self, request, forum_id):
        try:
            # 1. 异步获取 forum 对象
            forum = await Forum.objects.aget(id=forum_id)
            def get_members():
                return list(forum.members.all().values('id', 'username', 'email'))
            
            members = await sync_to_async(get_members)()

            return Response({
                "members": members,
                "count": len(members)
            }, status=status.HTTP_200_OK)

        except Forum.DoesNotExist:
            return Response({"detail": "论坛不存在"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # 打印错误到控制台以便排查
            print(f"DEBUG ERROR: {str(e)}") 
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class BanUserFromForumView(AdrfAPIView):
    permission_classes = [IsAuthenticated]

    async def post(self, request, *args, **kwargs):
        # 1. 接收并清理参数
        forum_id = request.data.get('forum_id')
        user_id = request.data.get('user_id')
        
        try:
            duration_hours = int(request.data.get('duration_hours', 24))
        except (ValueError, TypeError):
            return Response({"detail": "封禁时长必须为数字"}, status=status.HTTP_400_BAD_REQUEST)

        if not forum_id or not user_id:
            return Response({"detail": "参数缺失：需要 forum_id 和 user_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            forum = await Forum.objects.aget(id=forum_id)
            is_creator = (forum.creator_id == request.user.id)
            is_admin = await forum.admins.filter(id=request.user.id).aexists()
            
            if not (is_creator or is_admin):
                return Response({"detail": "权限不足：仅管理员或创建者可执行封禁"}, status=status.HTTP_403_FORBIDDEN)
            ban_until = timezone.now() + timedelta(hours=duration_hours)
            obj, created = await ForumBanList.objects.aupdate_or_create(
                forum=forum,
                user_id=user_id,
                defaults={
                    'reason': "管理员手动封禁",
                    'ban_until': ban_until
                }
            )

            return Response({
                "message": "封禁操作成功",
                "status": "created" if created else "updated"
            }, status=status.HTTP_200_OK)

        except Forum.DoesNotExist:
            return Response({"detail": "该版块不存在"}, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            traceback.print_exc() 
            return Response({"detail": f"服务器内部错误: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UserQuitForumView(AdrfAPIView):
    permission_classes = [IsAuthenticated]

    async def post(self, request, *args, **kwargs):
        forum_id = request.data.get('forum_id')
        if not forum_id:
            return Response({"detail": "缺少 forum_id"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            forum = await Forum.objects.aget(id=forum_id)
            is_member = await forum.members.filter(id=request.user.id).aexists()
            if not is_member:
                return Response({"detail": "你不是该论坛的成员"}, status=status.HTTP_403_FORBIDDEN)
            await forum.members.aremove(request.user)
            return Response({"message": f"已成功退出论坛 '{forum.name}'"}, status=status.HTTP_200_OK)
        except Forum.DoesNotExist:
            return Response({"detail": "论坛不存在"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            traceback.print_exc() 
            return Response({"detail": f"服务器内部错误: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)








