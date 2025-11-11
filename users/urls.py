from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (UserRegistrationView,UserLoginView,ProtectedTestView,
                    FetchUserInfoView,AddFriendRequestView ,FetchUserNotificationView,UserHandleRequestView,UserFetchFriendView)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('test_auth/',ProtectedTestView.as_view(),name='test_auth'),
    path('fetch_user_info/',FetchUserInfoView.as_view(),name='fetch_user_info'),
    path('add_friend_request/',AddFriendRequestView.as_view(),name='add_friend_request'),
    path('fetch_user_notifications/', FetchUserNotificationView.as_view(),name='fetch_user_notifications'),
    path('user_handle_request/',UserHandleRequestView.as_view(),name='user_handle_request'),
    path('user_fetch_friends/',UserFetchFriendView.as_view(),name='user_fetch_friend'),
]