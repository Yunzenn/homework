from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = '创建测试水质数据'

    def handle(self, *args, **options):
        from api.models import WaterQualityRecord
        
        # 清除现有数据
        WaterQualityRecord.objects.all().delete()
        
        # 生成测试数据
        points = ['ST001', 'ST002', 'ST003', 'ST004', 'ST005']
        
        for i in range(100):
            # 随机生成30天内的数据
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            
            created_at = timezone.now() - timedelta(
                days=days_ago, 
                hours=hours_ago, 
                minutes=minutes_ago
            )
            
            # 生成随机水质数据
            record = WaterQualityRecord.objects.create(
                point_id=random.choice(points),
                date=created_at.date(),
                time=created_at.time(),
                chlorine=round(random.uniform(0.1, 2.0), 2),
                conductivity=round(random.uniform(100, 500), 2),
                ph=round(random.uniform(6.0, 8.5), 2),
                orp=round(random.uniform(100, 300), 2),
                turbidity=round(random.uniform(0.1, 5.0), 2),
                created_at=created_at
            )
            
            # 随机生成一些报警数据
            if random.random() < 0.15:  # 15% 概率产生报警
                alert_items = []
                
                if record.ph < 6.5:
                    alert_items.append('pH偏低')
                elif record.ph > 8.0:
                    alert_items.append('pH偏高')
                
                if record.turbidity > 3.0:
                    alert_items.append('浊度偏高')
                
                if record.chlorine < 0.3:
                    alert_items.append('余氯偏低')
                elif record.chlorine > 1.5:
                    alert_items.append('余氯偏高')
                
                if alert_items:
                    record.alert_level = '警告' if random.random() < 0.7 else '严重'
                    record.alert_items = alert_items
                    record.save()
        
        self.stdout.write(self.style.SUCCESS(f'成功创建100条测试水质记录'))
        self.stdout.write(self.style.SUCCESS(f'监测点: {", ".join(points)}'))
        self.stdout.write(self.style.SUCCESS(f'数据时间范围: 最近30天'))
