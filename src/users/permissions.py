from rest_framework import permissions
from .models import UserRole


class IsAdminUser(permissions.BasePermission):
    """管理员权限"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_staff
        )
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsOwnerOrAdmin(permissions.BasePermission):
    """资源所有者或管理员权限"""
    
    def has_object_permission(self, request, view, obj):
        return (
            request.user and
            request.user.is_authenticated and
            (obj == request.user or request.user.is_staff)
        )


class HasRolePermission(permissions.BasePermission):
    """基于角色的权限检查"""
    
    def __init__(self, required_permission=None):
        self.required_permission = required_permission
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 管理员拥有所有权限
        if request.user.is_staff:
            return True
        
        # 检查用户角色权限
        user_roles = UserRole.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('role')
        
        for user_role in user_roles:
            if self.required_permission in user_role.role.permissions:
                return True
        
        return False


class HasAnyRole(permissions.BasePermission):
    """检查用户是否具有指定角色"""
    
    def __init__(self, allowed_roles=None):
        self.allowed_roles = allowed_roles or []
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 管理员拥有所有权限
        if request.user.is_staff:
            return True
        
        # 检查用户角色
        user_roles = UserRole.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('role')
        
        user_role_codes = [ur.role.code for ur in user_roles]
        
        return any(role_code in user_role_codes for role_code in self.allowed_roles)


def has_permission(user, permission_code):
    """检查用户是否具有指定权限"""
    if not user or not user.is_authenticated:
        return False
    
    # 管理员拥有所有权限
    if user.is_staff:
        return True
    
    # 检查用户角色权限
    user_roles = UserRole.objects.filter(
        user=user,
        is_active=True
    ).select_related('role')
    
    for user_role in user_roles:
        if permission_code in user_role.role.permissions:
            return True
    
    return False


def has_role(user, role_code):
    """检查用户是否具有指定角色"""
    if not user or not user.is_authenticated:
        return False
    
    # 管理员拥有所有权限
    if user.is_staff:
        return True
    
    # 检查用户角色
    user_roles = UserRole.objects.filter(
        user=user,
        is_active=True
    ).select_related('role')
    
    user_role_codes = [ur.role.code for ur in user_roles]
    
    return role_code in user_role_codes


def get_user_permissions(user):
    """获取用户所有权限"""
    if not user or not user.is_authenticated:
        return []
    
    # 管理员拥有所有权限
    if user.is_staff:
        return ['*']
    
    # 获取用户角色权限
    user_roles = UserRole.objects.filter(
        user=user,
        is_active=True
    ).select_related('role')
    
    permissions = set()
    for user_role in user_roles:
        permissions.update(user_role.role.permissions)
    
    return list(permissions)


def get_user_roles(user):
    """获取用户所有角色"""
    if not user or not user.is_authenticated:
        return []
    
    user_roles = UserRole.objects.filter(
        user=user,
        is_active=True
    ).select_related('role')
    
    return [
        {
            'id': str(ur.role.id),
            'name': ur.role.name,
            'code': ur.role.code,
            'description': ur.role.description,
            'permissions': ur.role.permissions
        }
        for ur in user_roles
    ]
