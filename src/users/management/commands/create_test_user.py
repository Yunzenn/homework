"""
创建测试用户的Django管理命令
"""

from django.core.management.base import BaseCommand
from users.models import User, Role, UserRole

class Command(BaseCommand):
    help = '创建测试用户admin'

    def handle(self, *args, **options):
        try:
            # 检查用户是否已存在
            if User.objects.filter(username='admin').exists():
                self.stdout.write(
                    self.style.WARNING('测试用户admin已存在')
                )
                return

            # 创建或获取管理员角色
            admin_role, created = Role.objects.get_or_create(
                code='admin',
                defaults={
                    'name': '系统管理员',
                    'description': '系统管理员角色，拥有所有权限',
                    'permissions': ['all'],
                    'is_system': True
                }
            )

            # 创建测试用户
            user = User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='管理员',
                last_name='系统',
                is_staff=True,
                is_superuser=True,
                phone='13800138000'
            )

            # 分配管理员角色
            UserRole.objects.create(
                user=user,
                role=admin_role
            )

            self.stdout.write(
                self.style.SUCCESS('测试用户admin创建成功')
            )
            self.stdout.write('用户名: admin')
            self.stdout.write('密码: admin123')
            self.stdout.write('手机号: 13800138000')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'创建测试用户失败: {str(e)}')
            )
