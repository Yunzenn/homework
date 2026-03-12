from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import User, Role, UserRole
# from .utils import create_default_roles, create_admin_user  # 暂时注释


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """用户创建时的信号处理"""
    if created:
        # 为新用户分配默认角色（只读用户）
        try:
            default_role = Role.objects.get(code='viewer')
            UserRole.objects.create(
                user=instance,
                role=default_role,
                is_active=True
            )
        except Role.DoesNotExist:
            pass


@receiver(post_migrate)
def create_initial_data(sender, **kwargs):
    """数据库迁移后创建初始数据"""
    # 暂时禁用，避免迁移时冲突
    pass
    # if sender.name == 'users':
    #     create_default_roles()
    #     # admin用户通过迁移创建，不需要在这里创建


@receiver(post_save, sender=UserRole)
def log_role_assignment(sender, instance, created, **kwargs):
    """角色分配时的日志记录"""
    if created:
        from .utils import log_operation, get_client_info
        
        # 这里需要获取request对象，但在信号中无法直接获取
        # 可以考虑使用中间件来记录
        pass
