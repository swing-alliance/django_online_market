from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from .views import (UserRegistrationView,UserLoginView,
                    FetchUserInfoView,AddFriendRequestView ,FetchUserNotificationView,UserHandleRequestView,UserFetchFriendView
                    ,BoostedFetchUserAvatarView,UserUploadAvatarView,UserLogoutView,GetAvatarByIdView)

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
]

