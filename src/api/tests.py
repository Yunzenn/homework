from django.test import TestCase
from .file_storage import FileStorageService
from .utils import generate_sample_data, validate_water_quality_data


class FileStorageServiceTest(TestCase):
    """文件存储服务测试"""
    
    def setUp(self):
        self.storage = FileStorageService()
    
    def test_insert_and_find(self):
        """测试插入和查找"""
        record = {
            'point_id': '测试点001',
            'date': '2024-01-15',
            'time': '09:30',
            'chlorine': 2.5,
            'conductivity': 450.0,
            'ph': 7.2,
            'orp': 650.0,
            'turbidity': 1.8
        }
        
        # 插入记录
        inserted_record = self.storage.insert(record)
        self.assertIsNotNone(inserted_record.get('record_id'))
        
        # 查找记录
        found_record = self.storage.find_by_id(inserted_record['record_id'])
        self.assertIsNotNone(found_record)
        self.assertEqual(found_record['point_id'], '测试点001')
    
    def test_update(self):
        """测试更新"""
        record = {
            'point_id': '测试点002',
            'date': '2024-01-16',
            'time': '10:30',
            'chlorine': 3.0,
            'conductivity': 500.0,
            'ph': 7.5,
            'orp': 700.0,
            'turbidity': 2.0
        }
        
        inserted_record = self.storage.insert(record)
        record_id = inserted_record['record_id']
        
        # 更新记录
        update_data = record.copy()
        update_data['ph'] = 8.0
        updated_record = self.storage.update(record_id, update_data)
        
        self.assertEqual(updated_record['ph'], 8.0)
    
    def test_delete(self):
        """测试删除"""
        record = {
            'point_id': '测试点003',
            'date': '2024-01-17',
            'time': '11:30',
            'chlorine': 1.5,
            'conductivity': 400.0,
            'ph': 7.0,
            'orp': 600.0,
            'turbidity': 1.5
        }
        
        inserted_record = self.storage.insert(record)
        record_id = inserted_record['record_id']
        
        # 删除记录
        success = self.storage.delete(record_id)
        self.assertTrue(success)
        
        # 验证删除
        found_record = self.storage.find_by_id(record_id)
        self.assertIsNone(found_record)
    
    def test_query(self):
        """测试查询"""
        # 生成测试数据
        sample_data = generate_sample_data(10)
        for record in sample_data:
            self.storage.insert(record)
        
        # 测试日期范围查询
        filters = {
            'date_start': '2024-01-01',
            'date_end': '2024-01-31'
        }
        results = self.storage.query(filters)
        self.assertGreater(len(results), 0)
        
        # 测试数值范围查询
        filters = {
            'ph_min': 7.0,
            'ph_max': 8.0
        }
        results = self.storage.query(filters)
        for result in results:
            self.assertGreaterEqual(result['ph'], 7.0)
            self.assertLessEqual(result['ph'], 8.0)


class UtilsTest(TestCase):
    """工具函数测试"""
    
    def test_generate_sample_data(self):
        """测试生成示例数据"""
        data = generate_sample_data(5)
        self.assertEqual(len(data), 50)  # 5天 * 每天2-4条记录
        
        # 验证数据格式
        for record in data:
            self.assertIn('point_id', record)
            self.assertIn('date', record)
            self.assertIn('time', record)
            self.assertIn('chlorine', record)
            self.assertIn('conductivity', record)
            self.assertIn('ph', record)
            self.assertIn('orp', record)
            self.assertIn('turbidity', record)
    
    def test_validate_water_quality_data(self):
        """测试数据验证"""
        # 测试有效数据
        valid_data = {
            'point_id': '测试点',
            'date': '2024-01-15',
            'time': '09:30',
            'chlorine': 2.5,
            'conductivity': 450.0,
            'ph': 7.2,
            'orp': 650.0,
            'turbidity': 1.8
        }
        errors = validate_water_quality_data(valid_data)
        self.assertEqual(len(errors), 0)
        
        # 测试无效数据
        invalid_data = {
            'point_id': '',  # 空值
            'date': '2024-01-15',
            'time': '09:30',
            'chlorine': -1.0,  # 负数
            'conductivity': 450.0,
            'ph': 15.0,  # 超出范围
            'orp': 650.0,
            'turbidity': 1.8
        }
        errors = validate_water_quality_data(invalid_data)
        self.assertGreater(len(errors), 0)
