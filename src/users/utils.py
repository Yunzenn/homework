import json
import requests
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from .models import OperationLog


def get_client_info(request):
    """获取客户端信息"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # 简单的设备检测
    device = 'Unknown'
    if 'Mobile' in user_agent:
        device = 'Mobile'
    elif 'Tablet' in user_agent:
        device = 'Tablet'
    elif 'Windows' in user_agent:
        device = 'Windows'
    elif 'Mac' in user_agent:
        device = 'Mac'
    elif 'Linux' in user_agent:
        device = 'Linux'
    
    # 获取地理位置（这里简化处理，实际可以使用IP地理位置API）
    location = get_location_by_ip(ip)
    
    return {
        'ip': ip,
        'device': device,
        'user_agent': user_agent,
        'location': location
    }


def get_location_by_ip(ip):
    """根据IP获取地理位置"""
    try:
        # 这里可以使用免费的IP地理位置API，如ip-api.com
        response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return f"{data['country']}-{data['city']}"
    except:
        pass
    
    return 'Unknown'


def send_password_reset_email(email, token):
    """发送密码重置邮件"""
    try:
        subject = '水质监控系统 - 密码重置'
        
        # 构建重置链接
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        
        # 渲染邮件模板
        html_message = render_to_string('users/password_reset_email.html', {
            'reset_url': reset_url,
            'token': token,
            'expiry_hours': 24
        })
        
        text_message = render_to_string('users/password_reset_email.txt', {
            'reset_url': reset_url,
            'token': token,
            'expiry_hours': 24
        })
        
        # 发送邮件
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False
        )
        
        return True
    except Exception as e:
        print(f"发送邮件失败: {e}")
        return False


def log_operation(user, action, module, description, request_data=None, 
                 response_data=None, ip_address=None, device=None, 
                 status=True, error_message=None, duration=0):
    """记录操作日志"""
    try:
        OperationLog.objects.create(
            user=user,
            username=user.username if user else 'Anonymous',
            action=action,
            module=module,
            description=description,
            request_data=request_data,
            response_data=response_data,
            ip_address=ip_address,
            device=device,
            status=status,
            error_message=error_message,
            duration=duration
        )
    except Exception as e:
        print(f"记录操作日志失败: {e}")


def operation_logger(action=None, module=None):
    """操作日志装饰器"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            start_time = timezone.now()
            
            try:
                response = view_func(request, *args, **kwargs)
                end_time = timezone.now()
                duration = int((end_time - start_time).total_seconds() * 1000)
                
                # 记录成功日志
                if hasattr(request, 'user') and request.user.is_authenticated:
                    client_info = get_client_info(request)
                    log_operation(
                        user=request.user,
                        action=action or 'VIEW',
                        module=module or 'unknown',
                        description=f"{action} {module}",
                        request_data=request.data if request.method in ['POST', 'PUT', 'PATCH'] else None,
                        response_data=response.data if hasattr(response, 'data') else None,
                        ip_address=client_info['ip'],
                        device=client_info['device'],
                        status=True,
                        duration=duration
                    )
                
                return response
                
            except Exception as e:
                end_time = timezone.now()
                duration = int((end_time - start_time).total_seconds() * 1000)
                
                # 记录错误日志
                if hasattr(request, 'user') and request.user.is_authenticated:
                    client_info = get_client_info(request)
                    log_operation(
                        user=request.user,
                        action=action or 'ERROR',
                        module=module or 'unknown',
                        description=f"{action} {module} - {str(e)}",
                        request_data=request.data if request.method in ['POST', 'PUT', 'PATCH'] else None,
                        ip_address=client_info['ip'],
                        device=client_info['device'],
                        status=False,
                        error_message=str(e),
                        duration=duration
                    )
                
                raise
        
        return wrapper
    return decorator


def validate_password_strength(password):
    """验证密码强度"""
    errors = []
    
    if len(password) < 8:
        errors.append('密码长度至少8位')
    
    if not any(c.isupper() for c in password):
        errors.append('密码必须包含大写字母')
    
    if not any(c.islower() for c in password):
        errors.append('密码必须包含小写字母')
    
    if not any(c.isdigit() for c in password):
        errors.append('密码必须包含数字')
    
    special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
    if not any(c in special_chars for c in password):
        errors.append('密码必须包含特殊字符')
    
    return errors


def generate_random_password(length=12):
    """生成随机密码"""
    import random
    import string
    
    # 确保密码包含各种字符类型
    characters = string.ascii_letters + string.digits + '!@#$%^&*'
    password = ''.join(random.choice(characters) for _ in range(length))
    
    # 确保至少包含一个大写字母、小写字母、数字和特殊字符
    password = list(password)
    password[0] = random.choice(string.ascii_uppercase)
    password[1] = random.choice(string.ascii_lowercase)
    password[2] = random.choice(string.digits)
    password[3] = random.choice('!@#$%^&*')
    random.shuffle(password)
    
    return ''.join(password)


def format_file_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f}{size_names[i]}"


def create_default_roles():
    """创建默认角色"""
    from .models import Role
    
    default_roles = [
        {
            'name': '管理员',
            'code': 'admin',
            'description': '系统管理员，拥有所有权限',
            'permissions': ['*'],
            'is_system': True
        },
        {
            'name': '主管',
            'code': 'supervisor',
            'description': '部门主管，可以管理数据和用户',
            'permissions': [
                'dashboard:view', 'data:view', 'data:create', 'data:update', 'data:delete',
                'data:import', 'data:export', 'alert:view', 'alert:confirm',
                'user:view', 'user:create', 'user:update', 'user:role',
                'log:view', 'analysis:view'
            ],
            'is_system': True
        },
        {
            'name': '操作员',
            'code': 'operator',
            'description': '数据操作员，可以管理数据',
            'permissions': [
                'dashboard:view', 'data:view', 'data:create', 'data:update',
                'data:import', 'data:export', 'alert:view', 'alert:confirm',
                'analysis:view'
            ],
            'is_system': True
        },
        {
            'name': '只读用户',
            'code': 'viewer',
            'description': '只读用户，只能查看数据',
            'permissions': [
                'dashboard:view', 'data:view', 'data:export', 'alert:view',
                'analysis:view'
            ],
            'is_system': True
        }
    ]
    
    for role_data in default_roles:
        Role.objects.get_or_create(
            code=role_data['code'],
            defaults=role_data
        )


def create_admin_user():
    """创建默认管理员用户"""
    from django.contrib.auth import get_user_model
    from .models import Role, UserRole
    
    User = get_user_model()
    
    # 检查是否已存在管理员
    if User.objects.filter(username='admin').exists():
        return
    
    # 创建管理员用户
    admin_user = User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='admin123456',  # 生产环境中应该使用强密码
    )
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()


def log_login(user, username, ip_address, user_agent, success=True):
    """记录登录日志"""
    from .models import LoginLog
    
    LoginLog.objects.create(
        user=user,
        username=username,
        ip_address=ip_address,
        user_agent=user_agent,
        status=success,  # 使用status字段而不是success
        login_time=timezone.now()
    )
