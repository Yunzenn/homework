from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import login, logout
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import uuid
import json

from .models import User, Role, UserRole, LoginLog, OperationLog, PasswordResetToken
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserUpdateSerializer, PasswordChangeSerializer, PasswordResetSerializer,
    PasswordResetConfirmSerializer, RoleSerializer, UserRoleSerializer,
    UserManagementSerializer, LoginLogSerializer, OperationLogSerializer
)
from .utils import send_password_reset_email, get_client_info, log_operation
from .permissions import IsAdminUser, IsOwnerOrAdmin


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class LoginView(APIView):
    """专门处理登录的视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """用户登录"""
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            remember = serializer.validated_data.get('remember', False)
            
            # 检查是否为测试账号
            is_test_account = (user.username == 'admin' and 
                             user.email == 'admin@example.com')
            
            # 记录登录信息
            from .utils import log_login, get_client_info
            log_login(
                user=user,
                username=user.username,
                ip_address=get_client_info(request)['ip'],
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                success=True
            )
            
            # 生成token
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            
            # 获取用户权限和角色
            user_data = UserProfileSerializer(user).data
            
            return Response({
                'user': user_data,
                'token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'is_test_account': is_test_account
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    """专门处理注册的视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        return AuthView().register(request)


class LogoutView(APIView):
    """专门处理登出的视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        return AuthView().logout_user(request)


class AuthView(APIView):
    """认证视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, action):
        if action == 'register':
            return self.register(request)
        elif action == 'login':
            return self.login_user(request)
        elif action == 'logout':
            return self.logout_user(request)
        elif action == 'refresh':
            return self.refresh_token(request)
        else:
            return Response({'error': '无效的操作'}, status=status.HTTP_400_BAD_REQUEST)
    
    def register(self, request):
        """用户注册"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # 记录操作日志
            log_operation(
                user=user,
                action='CREATE',
                module='user',
                description='用户注册',
                request_data=request.data,
                ip_address=get_client_info(request)['ip']
            )
            
            return Response({
                'message': '注册成功',
                'user': UserProfileSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def login_user(self, request):
        """用户登录"""
        from django.conf import settings
        
        # 开发环境测试账号检查
        if settings.DEBUG:
            username = request.data.get('username')
            password = request.data.get('password')
            
            # 硬编码测试账号
            if username == 'admin' and password == 'admin123':
                # 创建测试用户信息（不存数据库）
                test_user_data = {
                    'id': 'test-admin-id',
                    'username': 'admin',
                    'email': 'admin@waterquality.com',
                    'nickname': '系统管理员（测试）',
                    'is_active': True,
                    'roles': [{'name': '超级管理员', 'code': 'admin'}],
                    'permissions': [
                        'user.create', 'user.read', 'user.update', 'user.delete',
                        'user.assign_role', 'user.lock_user',
                        'role.create', 'role.read', 'role.update', 'role.delete',
                        'role.assign_permission',
                        'log.read', 'log.export',
                        'system.manage', 'data.export'
                    ]
                }
                
                # 生成测试token
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken.for_user(User(
                    id='test-admin-id',
                    username='admin'
                ))
                
                # 记录登录日志
                log_login(
                    user=None,
                    username=username,
                    ip_address=get_client_info(request)['ip'],
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    success=True
                )
                
                return Response({
                    'user': test_user_data,
                    'token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                    'is_test_account': True
                }, status=status.HTTP_200_OK)
        
        # 生产环境正常登录流程
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            remember = serializer.validated_data.get('remember', False)
            
            # 记录登录信息
            client_info = get_client_info(request)
            user.last_login = timezone.now()
            user.last_login_ip = client_info['ip']
            user.last_login_device = client_info['device']
            user.last_login_location = client_info['location']
            user.save(update_fields=['last_login', 'last_login_ip', 'last_login_device', 'last_login_location'])
            
            # 记录登录日志
            LoginLog.objects.create(
                user=user,
                username=user.username,
                ip_address=client_info['ip'],
                device=client_info['device'],
                location=client_info['location'],
                status=True,
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # 记录操作日志
            log_operation(
                user=user,
                action='LOGIN',
                module='auth',
                description='用户登录',
                request_data=request.data,
                ip_address=client_info['ip']
            )
            
            # 生成token（这里简化处理，实际应该使用JWT）
            from rest_framework.authtoken.models import Token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'message': '登录成功',
                'token': token.key,
                'user': UserProfileSerializer(user).data,
                'expires_in': 7 * 24 * 60 * 60 if remember else 2 * 60 * 60  # 7天或2小时
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def logout_user(self, request):
        """用户退出"""
        if request.user.is_authenticated:
            # 记录操作日志（可选，如果出错可以注释掉）
            try:
                log_operation(
                    user=request.user,
                    action='LOGOUT',
                    module='auth',
                    description='用户退出',
                    ip_address=get_client_info(request)['ip']
                )
            except Exception as e:
                print(f"记录退出日志失败: {e}")
            
            # 删除token
            try:
                from rest_framework.authtoken.models import Token
                Token.objects.filter(user=request.user).delete()
            except:
                pass
            
            logout(request)
            return Response({'message': '退出成功'})
        return Response({'error': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)
    
    def refresh_token(self, request):
        """刷新token"""
        if request.user.is_authenticated:
            from rest_framework.authtoken.models import Token
            token, created = Token.objects.get_or_create(user=request.user)
            return Response({
                'token': token.key,
                'expires_in': 2 * 60 * 60  # 2小时
            })
        return Response({'error': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)


class PasswordView(APIView):
    """密码管理视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, action):
        if action == 'change':
            return self.change_password(request)
        else:
            return Response({'error': '无效的操作'}, status=status.HTTP_400_BAD_REQUEST)
    
    def change_password(self, request):
        """修改密码"""
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # 记录操作日志
            log_operation(
                user=user,
                action='UPDATE',
                module='user',
                description='修改密码',
                ip_address=get_client_info(request)['ip']
            )
            
            return Response({'message': '密码修改成功'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def forgot_password(request):
    """忘记密码"""
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # 生成重置令牌
        token = str(uuid.uuid4())
        expires_at = timezone.now() + timedelta(hours=24)  # 24小时有效
        
        PasswordResetToken.objects.create(
            user=user,
            token=token,
            email=email,
            expires_at=expires_at
        )
        
        # 发送重置邮件
        send_password_reset_email(email, token)
        
        return Response({'message': '重置链接已发送到您的邮箱'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def reset_password(request):
    """重置密码"""
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
            if reset_token.is_expired():
                return Response({'error': '重置链接已过期'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 重置密码
            user = reset_token.user
            user.set_password(new_password)
            user.save()
            
            # 标记令牌已使用
            reset_token.is_used = True
            reset_token.save()
            
            # 记录操作日志
            log_operation(
                user=user,
                action='UPDATE',
                module='user',
                description='重置密码',
                ip_address=get_client_info(request)['ip']
            )
            
            return Response({'message': '密码重置成功'})
        except PasswordResetToken.DoesNotExist:
            return Response({'error': '无效的重置链接'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """用户资料视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """获取个人资料"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """更新个人资料"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            
            # 记录操作日志
            log_operation(
                user=user,
                action='UPDATE',
                module='user',
                description='更新个人资料',
                request_data=request.data,
                ip_address=get_client_info(request)['ip']
            )
            
            return Response({
                'message': '资料更新成功',
                'user': UserProfileSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AvatarUploadView(APIView):
    """头像上传视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """上传头像"""
        if 'avatar' not in request.FILES:
            return Response({'error': '请选择头像文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        avatar_file = request.FILES['avatar']
        
        # 验证文件类型和大小
        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        if avatar_file.content_type not in allowed_types:
            return Response({'error': '只支持JPG、PNG、GIF格式的图片'}, status=status.HTTP_400_BAD_REQUEST)
        
        if avatar_file.size > 2 * 1024 * 1024:  # 2MB
            return Response({'error': '图片大小不能超过2MB'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 删除旧头像
        if request.user.avatar:
            request.user.avatar.delete()
        
        # 保存新头像
        request.user.avatar = avatar_file
        request.user.save()
        
        # 记录操作日志
        log_operation(
            user=request.user,
            action='UPDATE',
            module='user',
            description='上传头像',
            ip_address=get_client_info(request)['ip']
        )
        
        return Response({
            'message': '头像上传成功',
            'avatar': request.user.avatar.url if request.user.avatar else None
        })


class RoleListCreateView(ListCreateAPIView):
    """角色列表和创建视图"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination
    
    def perform_create(self, serializer):
        role = serializer.save()
        
        # 记录操作日志
        log_operation(
            user=self.request.user,
            action='CREATE',
            module='role',
            description=f'创建角色: {role.name}',
            request_data=self.request.data,
            ip_address=get_client_info(self.request)['ip']
        )


class RoleDetailView(RetrieveUpdateDestroyAPIView):
    """角色详情视图"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]
    
    def perform_update(self, serializer):
        role = serializer.save()
        
        # 记录操作日志
        log_operation(
            user=self.request.user,
            action='UPDATE',
            module='role',
            description=f'更新角色: {role.name}',
            request_data=self.request.data,
            ip_address=get_client_info(self.request)['ip']
        )
    
    def perform_destroy(self, instance):
        # 记录操作日志
        log_operation(
            user=self.request.user,
            action='DELETE',
            module='role',
            description=f'删除角色: {instance.name}',
            ip_address=get_client_info(self.request)['ip']
        )
        instance.delete()


class UserManagementListView(ListCreateAPIView):
    """用户管理列表视图"""
    queryset = User.objects.all()
    serializer_class = UserManagementSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['username', 'email', 'phone', 'is_active', 'is_locked']
    search_fields = ['username', 'email', 'phone', 'nickname']
    
    def perform_create(self, serializer):
        user = serializer.save()
        
        # 记录操作日志
        log_operation(
            user=self.request.user,
            action='CREATE',
            module='user',
            description=f'创建用户: {user.username}',
            request_data=self.request.data,
            ip_address=get_client_info(self.request)['ip']
        )


class UserManagementDetailView(RetrieveUpdateDestroyAPIView):
    """用户管理详情视图"""
    queryset = User.objects.all()
    serializer_class = UserManagementSerializer
    permission_classes = [IsAdminUser]
    
    def perform_update(self, serializer):
        user = serializer.save()
        
        # 记录操作日志
        log_operation(
            user=self.request.user,
            action='UPDATE',
            module='user',
            description=f'更新用户: {user.username}',
            request_data=self.request.data,
            ip_address=get_client_info(self.request)['ip']
        )
    
    def perform_destroy(self, instance):
        # 记录操作日志
        log_operation(
            user=self.request.user,
            action='DELETE',
            module='user',
            description=f'删除用户: {instance.username}',
            ip_address=get_client_info(self.request)['ip']
        )
        instance.delete()


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def assign_user_role(request, user_id):
    """分配用户角色"""
    try:
        user = User.objects.get(id=user_id)
        role_id = request.data.get('role_id')
        
        if not role_id:
            return Response({'error': '角色ID不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        role = Role.objects.get(id=role_id)
        
        # 创建或更新用户角色关联
        user_role, created = UserRole.objects.update_or_create(
            user=user,
            role=role,
            defaults={
                'assigned_by': request.user,
                'is_active': True
            }
        )
        
        if not created:
            user_role.assigned_by = request.user
            user_role.is_active = True
            user_role.save()
        
        # 记录操作日志
        log_operation(
            user=request.user,
            action='UPDATE',
            module='user',
            description=f'为用户 {user.username} 分配角色 {role.name}',
            request_data=request.data,
            ip_address=get_client_info(request)['ip']
        )
        
        return Response({'message': '角色分配成功'})
    
    except User.DoesNotExist:
        return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Role.DoesNotExist:
        return Response({'error': '角色不存在'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_user_status(request, user_id):
    """更新用户状态"""
    try:
        user = User.objects.get(id=user_id)
        new_status = request.data.get('is_active')
        lock_reason = request.data.get('lock_reason', '')
        
        if new_status is None:
            return Response({'error': '状态不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_active = new_status
        
        if not new_status:
            user.is_locked = True
            user.lock_reason = lock_reason or '管理员禁用'
            user.lock_time = timezone.now()
        else:
            user.is_locked = False
            user.lock_reason = ''
            user.lock_time = None
            user.login_failed_count = 0
        
        user.save()
        
        # 记录操作日志
        action = 'ENABLE' if new_status else 'DISABLE'
        log_operation(
            user=request.user,
            action=action,
            module='user',
            description=f'{"启用" if new_status else "禁用"}用户 {user.username}',
            request_data=request.data,
            ip_address=get_client_info(request)['ip']
        )
        
        return Response({'message': '状态更新成功'})
    
    except User.DoesNotExist:
        return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)


class LoginLogListView(ListCreateAPIView):
    """登录日志列表视图"""
    queryset = LoginLog.objects.all()
    serializer_class = LoginLogSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['user', 'status', 'ip_address']
    search_fields = ['username', 'ip_address', 'device']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # 按时间范围过滤
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(login_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(login_time__lte=end_date)
        
        return queryset


class OperationLogListView(ListCreateAPIView):
    """操作日志列表视图"""
    queryset = OperationLog.objects.all()
    serializer_class = OperationLogSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['user', 'action', 'module', 'status']
    search_fields = ['username', 'description', 'ip_address']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # 按时间范围过滤
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_permissions(request):
    """获取所有权限列表"""
    permissions = [
        # 页面权限
        {'code': 'dashboard:view', 'name': '查看仪表盘', 'module': 'dashboard'},
        {'code': 'data:view', 'name': '查看数据', 'module': 'data'},
        {'code': 'data:create', 'name': '新增数据', 'module': 'data'},
        {'code': 'data:update', 'name': '修改数据', 'module': 'data'},
        {'code': 'data:delete', 'name': '删除数据', 'module': 'data'},
        {'code': 'data:import', 'name': '导入数据', 'module': 'data'},
        {'code': 'data:export', 'name': '导出数据', 'module': 'data'},
        {'code': 'alert:view', 'name': '查看报警', 'module': 'alert'},
        {'code': 'alert:confirm', 'name': '确认报警', 'module': 'alert'},
        {'code': 'alert:config', 'name': '配置阈值', 'module': 'alert'},
        {'code': 'user:view', 'name': '查看用户', 'module': 'user'},
        {'code': 'user:create', 'name': '新增用户', 'module': 'user'},
        {'code': 'user:update', 'name': '修改用户', 'module': 'user'},
        {'code': 'user:delete', 'name': '删除用户', 'module': 'user'},
        {'code': 'user:role', 'name': '分配角色', 'module': 'user'},
        {'code': 'role:view', 'name': '查看角色', 'module': 'role'},
        {'code': 'role:create', 'name': '创建角色', 'module': 'role'},
        {'code': 'role:update', 'name': '修改角色', 'module': 'role'},
        {'code': 'role:delete', 'name': '删除角色', 'module': 'role'},
        {'code': 'log:view', 'name': '查看日志', 'module': 'log'},
        {'code': 'analysis:view', 'name': '查看分析', 'module': 'analysis'},
    ]
    
    return Response({'permissions': permissions})
