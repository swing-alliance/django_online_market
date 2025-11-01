# users/urls.py (最终版本)

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserRegistrationView, UserDashboardView, UserInfoUpdateView, UserProfileUpdateView,UserLoginView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dashboard/', UserDashboardView.as_view(), name='dashboard'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile-update'), 
    path('userinfo/update/', UserInfoUpdateView.as_view(), name='userinfo-update'), 
]