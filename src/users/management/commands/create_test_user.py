"""
创建测试用户的Django管理命令
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

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

            # 创建测试用户
            user = User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='管理员',
                last_name='系统',
                is_staff=True,
                is_superuser=True
            )

            # 创建用户档案
            UserProfile.objects.create(
                user=user,
                phone='13800138000',
                department='系统管理',
                position='系统管理员'
            )

            self.stdout.write(
                self.style.SUCCESS('测试用户admin创建成功')
            )
            self.stdout.write('用户名: admin')
            self.stdout.write('密码: admin123')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'创建测试用户失败: {str(e)}')
            )
