from django.urls import path
from . import views, test_views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('me/', views.get_current_user, name='get_current_user'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('test-register/', test_views.test_register, name='test-register'),  # 测试注册接口
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # JWT token刷新
]