from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器
router = DefaultRouter()
# router.register(r'users', views.UserManagementListView)
# router.register(r'roles', views.RoleListCreateView)

app_name = 'users'

urlpatterns = [
    # 认证相关
    path('auth/', views.AuthView.as_view(), name='auth'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/change-password/', views.PasswordView.as_view(), name='change-password'),
    path('auth/forgot-password/', views.forgot_password, name='forgot-password'),
    path('auth/reset-password/', views.reset_password, name='reset-password'),
    
    # 用户资料相关
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/avatar/', views.AvatarUploadView.as_view(), name='avatar-upload'),
    
    # 用户管理（管理员）
    path('users/', views.UserManagementListView.as_view(), name='user-list'),
    path('users/<uuid:pk>/', views.UserManagementDetailView.as_view(), name='user-detail'),
    path('users/<uuid:user_id>/role/', views.assign_user_role, name='assign-user-role'),
    path('users/<uuid:user_id>/status/', views.update_user_status, name='update-user-status'),
    
    # 角色管理（管理员）
    path('roles/', views.RoleListCreateView.as_view(), name='role-list'),
    path('roles/<uuid:pk>/', views.RoleDetailView.as_view(), name='role-detail'),
    path('permissions/', views.get_permissions, name='permissions'),
    
    # 日志管理（管理员）
    path('logs/login/', views.LoginLogListView.as_view(), name='login-logs'),
    path('logs/operation/', views.OperationLogListView.as_view(), name='operation-logs'),
    path('logs/user/<uuid:user_id>/', views.OperationLogListView.as_view(), name='user-operation-logs'),
]
