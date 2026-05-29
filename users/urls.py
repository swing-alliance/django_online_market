from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from .views import (UserRegistrationView,UserLoginView,
                    FetchUserInfoView,AddFriendRequestView ,FetchUserNotificationView,UserHandleRequestView,UserFetchFriendView
                    ,BoostedFetchUserAvatarView,UserUploadAvatarView,UserLogoutView,GetAvatarByIdView,FetchChatHistoryView,AIChatView
                    ,manager_sensorializer_view,manager_export_chat_his,UserLaunchGroupChatView,user_see_groupchat_view,get_groupchat_his
                    ,UserFetchFriendIdView,delet_group_chat,UserChatInGroupView,DeleteOrExitGroupView,
                    UserCreateForumView,UserJoinForumView,GetForumInfoView,PostLikeView,CreatorDeletePostView,GetTenForumsView
                    ,UserPostInForumView,GetAllPostsView,GetForummemberView,BanUserFromForumView,UserQuitForumView)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('fetch_user_info/',FetchUserInfoView.as_view(),name='fetch_user_info'),
    path('add_friend_request/',AddFriendRequestView.as_view(),name='add_friend_request'),
    path('fetch_user_notifications/', FetchUserNotificationView.as_view(),name='fetch_user_notifications'),
    path('user_handle_request/',UserHandleRequestView.as_view(),name='user_handle_request'),
    path('user_fetch_friends/',UserFetchFriendView.as_view(),name='user_fetch_friend'),
    path('boosted_fetch_user_avatar/',BoostedFetchUserAvatarView.as_view(),name='boosted_fetch_user_avatar'),
    path('user_upload_avatar/',UserUploadAvatarView.as_view(),name='user_upload_avatar'),
    path('get_avatar_by_id/',GetAvatarByIdView.as_view(),name='get_avatar_by_id'),
    path("get_chat_history/",FetchChatHistoryView.as_view(),name="get_chat_history"),
    path("ai_chat/",AIChatView.as_view(),name="ai_chat"),
    path("manager_sensorializer/",manager_sensorializer_view.as_view(),name="manager_sensorializer"),
    path("manager_export_chat_his/",manager_export_chat_his.as_view(),name="manager_export_chat_his"),
    path("user_launch_groupchat/",UserLaunchGroupChatView.as_view(),name="user_launch_groupchat"),#用户发起群聊，输入群聊名称和成员ID列表，返回群聊信息
    path("user_see_groupchat/",user_see_groupchat_view.as_view(),name="user_see_groupchat"),#用户查看自己加入的群聊列表，返回群聊信息和成员列表
    path("get_groupchat_his/",get_groupchat_his.as_view(),name="get_groupchat_his"),#用户查看群聊历史消息，输入群聊名称，返回消息列表
    path("user_fetch_friend_ids/",UserFetchFriendIdView.as_view(),name="user_fetch_friend_ids"),#用户获取好友ID列表
    path("delete_group_chat/",delet_group_chat.as_view(),name="delete_group_chat"),#用户删除群聊（仅限群主，依靠底层多对多中间表自增主键排序判定）
    path("user_chat_in_group/",UserChatInGroupView.as_view(),name="user_chat_in_group"),#用户在群聊中发消息，输入群聊名称和消息内容，返回是否成功
    path("delete_or_exit_group/",DeleteOrExitGroupView.as_view(),name="delete_or_exit_group"),#用户退出群聊（非群主）或解散群聊（群主），输入群聊名称，返回是否成功
    path("get_forum_info/<int:forum_id>/", GetForumInfoView.as_view(), name="get_forum_info"),#用户获取论坛信息，输入论坛ID，返回论坛名称、简介、成员列表和帖子列表
    path("create_forum/",UserCreateForumView.as_view(),name="create_forum"),#用户创建论坛，输入论坛名称和简介，返回论坛信息
    path("join_forum/",UserJoinForumView.as_view(),name="join_forum"),#用户加入论坛，输入论坛ID，返回是否成功
    path("post_like/",PostLikeView.as_view(),name="post_like"),#用户点赞帖子
    path("delete_post/<int:post_id>/", CreatorDeletePostView.as_view(), name="delete_post"),#用户删除自己创建的帖子，输入帖子ID，返回是否成功
    path("get_ten_forums/",GetTenForumsView.as_view(),name="get_ten_forums"),#用户获取最新的10个论坛
    path("user_post_in_forum/",UserPostInForumView.as_view(),name="user_post_in_forum"),#用户在论坛发帖，输入论坛ID、帖子标题和内容，返回帖子信息
    path("get_all_posts/",GetAllPostsView.as_view(),name="get_all_posts"),#获取指定论坛下的所有帖子
    path("forumsmembers/<int:forum_id>/", GetForummemberView.as_view(), name='get_forum_members'),
    path("ban_user_from_forum/", BanUserFromForumView.as_view(), name='ban_user_from_forum'),
    path('forum/quit/', UserQuitForumView.as_view(), name='user-quit-forum'),
]   

