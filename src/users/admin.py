from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, UserRole, LoginLog, OperationLog, PasswordResetToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理"""
    list_display = ['username', 'email', 'phone', 'nickname', 'is_active', 'is_locked', 'last_login', 'created_at']
    list_filter = ['is_active', 'is_locked', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'phone', 'nickname']
    ordering = ['-created_at']
    readonly_fields = ['id', 'last_login', 'last_login_ip', 'last_login_device', 'created_at', 'updated_at']
    
    fieldsets = (
        ('基础信息', {
            'fields': ('username', 'password', 'email', 'phone', 'nickname', 'first_name', 'last_name')
        }),
        ('权限设置', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('状态信息', {
            'fields': ('is_locked', 'lock_reason', 'login_failed_count', 'lock_time')
        }),
        ('登录信息', {
            'fields': ('last_login', 'last_login_ip', 'last_login_device', 'last_login_location')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user_roles__role')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """角色管理"""
    list_display = ['name', 'code', 'description', 'is_system', 'created_at']
    list_filter = ['is_system', 'created_at']
    search_fields = ['name', 'code', 'description']
    ordering = ['created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('基础信息', {
            'fields': ('name', 'code', 'description')
        }),
        ('权限设置', {
            'fields': ('permissions', 'is_system')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """用户角色关联管理"""
    list_display = ['user', 'role', 'assigned_by', 'assigned_at', 'is_active']
    list_filter = ['is_active', 'role', 'assigned_at']
    search_fields = ['user__username', 'role__name', 'assigned_by__username']
    ordering = ['-assigned_at']
    readonly_fields = ['id', 'assigned_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'role', 'assigned_by')


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    """登录日志管理"""
    list_display = ['username', 'login_time', 'ip_address', 'device', 'location', 'status']
    list_filter = ['status', 'login_time']
    search_fields = ['username', 'ip_address', 'device']
    ordering = ['-login_time']
    readonly_fields = ['id', 'user', 'username', 'login_time', 'ip_address', 'device', 'location', 'status', 'fail_reason', 'user_agent']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    """操作日志管理"""
    list_display = ['username', 'action', 'module', 'description', 'ip_address', 'status', 'created_at']
    list_filter = ['action', 'module', 'status', 'created_at']
    search_fields = ['username', 'description', 'ip_address']
    ordering = ['-created_at']
    readonly_fields = ['id', 'user', 'username', 'action', 'module', 'description', 'request_data', 'response_data', 'ip_address', 'device', 'status', 'error_message', 'duration', 'created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """密码重置令牌管理"""
    list_display = ['user', 'email', 'created_at', 'expires_at', 'is_used']
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['user__username', 'email']
    ordering = ['-created_at']
    readonly_fields = ['id', 'user', 'token', 'created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
