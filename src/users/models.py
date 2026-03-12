from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    """扩展用户模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # 基础信息
    phone = models.CharField('手机号', max_length=11, unique=True, null=True, blank=True)
    avatar = models.ImageField('头像', upload_to='avatars/', null=True, blank=True)
    nickname = models.CharField('昵称', max_length=50, null=True, blank=True)
    
    # 状态控制
    is_active = models.BooleanField('是否激活', default=True)
    is_locked = models.BooleanField('是否锁定', default=False)
    lock_reason = models.CharField('锁定原因', max_length=255, null=True, blank=True)
    login_failed_count = models.IntegerField('登录失败次数', default=0)
    lock_time = models.DateTimeField('锁定时间', null=True, blank=True)
    
    # 时间记录
    last_login_ip = models.GenericIPAddressField('最后登录IP', null=True, blank=True)
    last_login_device = models.CharField('最后登录设备', max_length=255, null=True, blank=True)
    last_login_location = models.CharField('最后登录地点', max_length=100, null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    # 元数据
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username or self.email or self.phone


class Role(models.Model):
    """角色模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('角色名称', max_length=50, unique=True)
    code = models.CharField('角色编码', max_length=50, unique=True)  # admin, supervisor, operator, viewer
    description = models.TextField('描述', null=True, blank=True)
    permissions = models.JSONField('权限列表', default=list)  # 存储权限code列表
    is_system = models.BooleanField('系统角色', default=False)  # 系统内置不可删除
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'roles'
        verbose_name = '角色'
        verbose_name_plural = '角色'
        ordering = ['created_at']
    
    def __str__(self):
        return self.name


class UserRole(models.Model):
    """用户角色关联模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_users')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_roles')
    assigned_at = models.DateTimeField('分配时间', auto_now_add=True)
    is_active = models.BooleanField('是否激活', default=True)
    
    class Meta:
        db_table = 'user_roles'
        verbose_name = '用户角色'
        verbose_name_plural = '用户角色'
        unique_together = ['user', 'role']
    
    def __str__(self):
        return f"{self.user.username} - {self.role.name}"


class LoginLog(models.Model):
    """登录日志模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_logs', null=True, blank=True)
    username = models.CharField('用户名', max_length=150)  # 冗余字段，登录失败时记录
    login_time = models.DateTimeField('登录时间', auto_now_add=True)
    ip_address = models.GenericIPAddressField('IP地址')
    device = models.CharField('设备信息', max_length=255)
    location = models.CharField('登录地点', max_length=100, null=True, blank=True)
    status = models.BooleanField('登录成功', default=True)
    fail_reason = models.CharField('失败原因', max_length=255, null=True, blank=True)
    user_agent = models.TextField('User Agent', null=True, blank=True)
    
    class Meta:
        db_table = 'login_logs'
        verbose_name = '登录日志'
        verbose_name_plural = '登录日志'
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['user', 'login_time']),
            models.Index(fields=['login_time']),
        ]
    
    def __str__(self):
        return f"{self.username} - {self.login_time}"


class OperationLog(models.Model):
    """操作日志模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='operation_logs')
    username = models.CharField('用户名', max_length=150)  # 冗余字段，用户删除后保留
    action = models.CharField('操作类型', max_length=50)  # CREATE, UPDATE, DELETE, QUERY, LOGIN, LOGOUT
    module = models.CharField('操作模块', max_length=50)  # user, role, data, alert
    description = models.TextField('操作描述')
    request_data = models.JSONField('请求数据', null=True, blank=True)
    response_data = models.JSONField('响应数据', null=True, blank=True)
    ip_address = models.GenericIPAddressField('IP地址')
    device = models.CharField('设备信息', max_length=255)
    status = models.BooleanField('操作成功', default=True)
    error_message = models.TextField('错误信息', null=True, blank=True)
    duration = models.IntegerField('耗时(ms)', default=0)
    created_at = models.DateTimeField('操作时间', auto_now_add=True)
    
    class Meta:
        db_table = 'operation_logs'
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['module', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.username} - {self.action} - {self.created_at}"


class PasswordResetToken(models.Model):
    """密码重置令牌模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField('令牌', max_length=255, unique=True)
    email = models.EmailField('邮箱')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    expires_at = models.DateTimeField('过期时间')
    is_used = models.BooleanField('是否已使用', default=False)
    
    class Meta:
        db_table = 'password_reset_tokens'
        verbose_name = '密码重置令牌'
        verbose_name_plural = '密码重置令牌'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.token[:8]}"
    
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at
