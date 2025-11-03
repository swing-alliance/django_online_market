from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserRegistrationView,UserLoginView,ProtectedTestView,FetchUserInfoView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('test_auth/',ProtectedTestView.as_view(),name='test_auth'),
    path('fetch_user_info/',FetchUserInfoView.as_view(),name='fetch_user_info'),
]