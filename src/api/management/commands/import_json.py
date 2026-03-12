import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count
from api.models import WaterQualityRecord


class Command(BaseCommand):
    help = '从JSON文件导入水质数据到SQLite数据库'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='JSON文件路径 (默认: data/water_quality.json)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清空现有数据'
        )
    
    def handle(self, *args, **options):
        json_file = options.get('json_file', 'data/water_quality.json')
        clear_existing = options.get('clear', False)
        
        # 检查文件是否存在
        if not os.path.exists(json_file):
            self.stdout.write(
                self.style.ERROR(f'文件不存在: {json_file}')
            )
            return
        
        try:
            # 读取JSON文件
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                self.stdout.write(
                    self.style.ERROR('JSON文件格式错误，应为记录数组')
                )
                return
            
            self.stdout.write(f'找到 {len(data)} 条记录')
            
            # 清空现有数据
            if clear_existing:
                deleted_count, _ = WaterQualityRecord.objects.all().delete()
                self.stdout.write(
                    self.style.WARNING(f'已清空 {deleted_count} 条现有记录')
                )
            
            # 导入数据
            imported_count = 0
            skipped_count = 0
            error_count = 0
            
            with transaction.atomic():
                for i, record_data in enumerate(data):
                    try:
                        # 验证必要字段
                        if not all(key in record_data for key in ['point_id', 'date', 'time']):
                            self.stdout.write(
                                self.style.WARNING(f'跳过第 {i+1} 条记录：缺少必要字段')
                            )
                            skipped_count += 1
                            continue
                        
                        # 创建记录
                        record = WaterQualityRecord.objects.create(
                            point_id=record_data.get('point_id', ''),
                            date=record_data.get('date', '2026-01-01'),
                            time=record_data.get('time', '00:00'),
                            chlorine=record_data.get('chlorine', 0.0),
                            conductivity=record_data.get('conductivity', 0.0),
                            ph=record_data.get('ph', 7.0),
                            orp=record_data.get('orp', 0.0),
                            turbidity=record_data.get('turbidity', 0.0)
                        )
                        
                        imported_count += 1
                        
                        # 每100条记录显示一次进度
                        if (i + 1) % 100 == 0:
                            self.stdout.write(f'已处理 {i+1} 条记录...')
                    
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'第 {i+1} 条记录导入失败: {str(e)}')
                        )
                        error_count += 1
            
            # 显示结果
            self.stdout.write(
                self.style.SUCCESS(f'导入完成！')
            )
            self.stdout.write(f'  成功导入: {imported_count} 条')
            self.stdout.write(f'  跳过记录: {skipped_count} 条')
            self.stdout.write(f'  错误记录: {error_count} 条')
            
            # 验证导入结果
            total_records = WaterQualityRecord.objects.count()
            self.stdout.write(
                self.style.SUCCESS(f'数据库中现有 {total_records} 条记录')
            )
            
            # 显示统计信息
            stats = WaterQualityRecord.objects.aggregate(
                total=Count('id'),
                avg_chlorine=Avg('chlorine'),
                avg_conductivity=Avg('conductivity'),
                avg_ph=Avg('ph'),
                avg_orp=Avg('orp'),
                avg_turbidity=Avg('turbidity'),
            )
            
            self.stdout.write('\n数据统计:')
            self.stdout.write(f'  平均余氯: {stats["avg_chlorine"]:.2f} mg/L')
            self.stdout.write(f'  平均电导率: {stats["avg_conductivity"]:.2f} µS/cm')
            self.stdout.write(f'  平均pH值: {stats["avg_ph"]:.2f}')
            self.stdout.write(f'  平均ORP: {stats["avg_orp"]:.2f} mV')
            self.stdout.write(f'  平均浊度: {stats["avg_turbidity"]:.2f} NTU')
            
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'JSON文件解析错误: {str(e)}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'导入过程中发生错误: {str(e)}')
            )
