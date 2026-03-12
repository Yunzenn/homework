from django.core.management.base import BaseCommand
from django.db import transaction
import uuid


class Command(BaseCommand):
    help = '创建管理员用户'

    def handle(self, *args, **options):
        from users.models import User, Role, UserRole
        
        # 检查是否已存在
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING('Admin用户已存在'))
            return
        
        try:
            with transaction.atomic():
                # 创建角色
                admin_role, created = Role.objects.get_or_create(
                    code='admin',
                    defaults={
                        'name': '系统管理员',
                        'description': '系统内置管理员角色，拥有所有权限',
                        'permissions': [
                            'user.create', 'user.read', 'user.update', 'user.delete',
                            'user.assign_role', 'user.lock_user',
                            'role.create', 'role.read', 'role.update', 'role.delete',
                            'role.assign_permission',
                            'log.read', 'log.export',
                            'system.manage', 'data.export'
                        ],
                        'is_system': True
                    }
                )
                
                # 创建用户
                user = User.objects.create_user(
                    username='admin',
                    email='admin@waterquality.com',
                    phone='13800138000',
                    nickname='系统管理员',
                    password='admin',
                    is_active=True,
                    is_locked=False
                )
                
                # 分配角色
                UserRole.objects.create(
                    user=user,
                    role=admin_role,
                    assigned_by=None,
                    is_active=True
                )
                
                self.stdout.write(self.style.SUCCESS('成功创建admin用户'))
                self.stdout.write(self.style.SUCCESS(f'用户名: admin'))
                self.stdout.write(self.style.SUCCESS(f'密码: admin'))
                self.stdout.write(self.style.SUCCESS(f'邮箱: admin@waterquality.com'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'创建失败: {str(e)}'))
