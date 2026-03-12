from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, Role, UserRole, LoginLog, OperationLog
import uuid
from datetime import timedelta
from django.utils import timezone


class UserRegistrationSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password', 'confirm_password', 'nickname']
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('该邮箱已被注册')
        return value
    
    def validate_phone(self, value):
        if value and User.objects.filter(phone=value).exists():
            raise serializers.ValidationError('该手机号已被注册')
        return value
    
    def validate_password(self, value):
        validate_password(value)
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError('两次密码输入不一致')
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    remember = serializers.BooleanField(default=False)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        # 检查用户是否被锁定
        try:
            user = User.objects.get(username=username)
            if user.is_locked and user.lock_time and timezone.now() < user.lock_time:
                raise serializers.ValidationError('账号已被锁定，请稍后再试')
        except User.DoesNotExist:
            pass
        
        # 验证用户名和密码
        user = authenticate(username=username, password=password)
        if not user:
            # 记录登录失败
            self._record_login_failure(username)
            raise serializers.ValidationError('用户名或密码错误')
        
        # 检查用户状态
        if not user.is_active:
            raise serializers.ValidationError('账号已被禁用')
        
        # 重置登录失败次数
        user.login_failed_count = 0
        user.is_locked = False
        user.lock_time = None
        user.save(update_fields=['login_failed_count', 'is_locked', 'lock_time'])
        
        attrs['user'] = user
        return attrs
    
    def _record_login_failure(self, username):
        """记录登录失败"""
        try:
            user = User.objects.get(username=username)
            user.login_failed_count += 1
            
            # 连续失败5次锁定15分钟
            if user.login_failed_count >= 5:
                user.is_locked = True
                user.lock_time = timezone.now() + timedelta(minutes=15)
                user.lock_reason = '连续登录失败次数过多'
            
            user.save(update_fields=['login_failed_count', 'is_locked', 'lock_time', 'lock_reason'])
        except User.DoesNotExist:
            pass


class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器"""
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'nickname', 'avatar',
            'first_name', 'last_name', 'is_active', 'date_joined',
            'last_login', 'last_login_ip', 'last_login_device', 'last_login_location',
            'created_at', 'updated_at', 'roles'
        ]
        read_only_fields = [
            'id', 'username', 'date_joined', 'last_login', 
            'last_login_ip', 'last_login_device', 'last_login_location',
            'created_at', 'updated_at'
        ]
    
    def get_roles(self, obj):
        user_roles = UserRole.objects.filter(user=obj, is_active=True).select_related('role')
        return [
            {
                'id': str(ur.role.id),
                'name': ur.role.name,
                'code': ur.role.code,
                'description': ur.role.description
            }
            for ur in user_roles
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户信息更新序列化器"""
    
    class Meta:
        model = User
        fields = ['nickname', 'email', 'phone', 'first_name', 'last_name']
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError('该邮箱已被使用')
        return value
    
    def validate_phone(self, value):
        if value and User.objects.filter(phone=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError('该手机号已被使用')
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """修改密码序列化器"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError('原密码错误')
        return value
    
    def validate_new_password(self, value):
        validate_password(value, user=self.instance)
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError('两次密码输入不一致')
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    """密码重置序列化器"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('该邮箱未注册')
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """密码重置确认序列化器"""
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate_new_password(self, value):
        validate_password(value)
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError('两次密码输入不一致')
        return attrs


class RoleSerializer(serializers.ModelSerializer):
    """角色序列化器"""
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'code', 'description', 'permissions', 'is_system', 'created_at', 'user_count']
    
    def get_user_count(self, obj):
        return UserRole.objects.filter(role=obj, is_active=True).count()


class UserRoleSerializer(serializers.ModelSerializer):
    """用户角色分配序列化器"""
    role_name = serializers.CharField(source='role.name', read_only=True)
    role_code = serializers.CharField(source='role.code', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True)
    
    class Meta:
        model = UserRole
        fields = ['id', 'user', 'role', 'role_name', 'role_code', 'assigned_by', 'assigned_by_name', 'assigned_at', 'is_active']


class UserManagementSerializer(serializers.ModelSerializer):
    """用户管理序列化器"""
    roles = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'nickname', 'avatar',
            'first_name', 'last_name', 'is_active', 'is_locked',
            'date_joined', 'last_login', 'last_login_ip',
            'created_at', 'updated_at', 'roles', 'status'
        ]
    
    def get_roles(self, obj):
        user_roles = UserRole.objects.filter(user=obj, is_active=True).select_related('role')
        return [ur.role.name for ur in user_roles]
    
    def get_status(self, obj):
        if obj.is_locked:
            return 'locked'
        elif obj.is_active:
            return 'active'
        else:
            return 'inactive'


class LoginLogSerializer(serializers.ModelSerializer):
    """登录日志序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = LoginLog
        fields = [
            'id', 'user', 'user_name', 'username', 'login_time', 'ip_address',
            'device', 'location', 'status', 'fail_reason', 'user_agent'
        ]


class OperationLogSerializer(serializers.ModelSerializer):
    """操作日志序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = OperationLog
        fields = [
            'id', 'user', 'user_name', 'username', 'action', 'module',
            'description', 'request_data', 'response_data', 'ip_address',
            'device', 'status', 'error_message', 'duration', 'created_at'
        ]
