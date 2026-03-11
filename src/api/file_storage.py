import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from django.conf import settings


class FileStorageService:
    """自定义文件存储服务，替代数据库ORM"""
    
    def __init__(self):
        self.file_path = os.path.join(settings.DATA_DIR, 'water_quality.json')
        self._ensure_data_dir()
        self._ensure_file_exists()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(settings.DATA_DIR):
            os.makedirs(settings.DATA_DIR)
    
    def _ensure_file_exists(self):
        """确保数据文件存在"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def _read_file(self) -> List[Dict[str, Any]]:
        """读取数据文件"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _write_file(self, data: List[Dict[str, Any]]):
        """写入数据文件"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _get_next_id(self, data: List[Dict[str, Any]]) -> int:
        """获取下一个ID"""
        if not data:
            return 1
        return max(item.get('record_id', 0) for item in data) + 1
    
    def read_all(self) -> List[Dict[str, Any]]:
        """读取所有记录"""
        return self._read_file()
    
    def write_all(self, data: List[Dict[str, Any]]):
        """写入所有记录"""
        self._write_file(data)
    
    def find_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """按ID查找记录"""
        data = self._read_file()
        for item in data:
            if item.get('record_id') == record_id:
                return item
        return None
    
    def insert(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """插入新记录"""
        data = self._read_file()
        record['record_id'] = self._get_next_id(data)
        record['create_time'] = datetime.now().isoformat()
        data.append(record)
        self._write_file(data)
        return record
    
    def update(self, record_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新记录"""
        data = self._read_file()
        for i, item in enumerate(data):
            if item.get('record_id') == record_id:
                update_data['record_id'] = record_id
                update_data['create_time'] = item.get('create_time', datetime.now().isoformat())
                data[i] = update_data
                self._write_file(data)
                return update_data
        return None
    
    def delete(self, record_id: int) -> bool:
        """删除记录"""
        data = self._read_file()
        original_length = len(data)
        data = [item for item in data if item.get('record_id') != record_id]
        if len(data) < original_length:
            self._write_file(data)
            return True
        return False
    
    def query(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """复杂查询"""
        data = self._read_file()
        result = []
        
        for item in data:
            match = True
            
            # 监测点查询
            if 'point_id' in filters:
                if filters['point_id'] not in item.get('point_id', ''):
                    match = False
            
            # 日期范围查询
            if 'date_start' in filters and 'date_end' in filters:
                item_date = item.get('date', '')
                if not (filters['date_start'] <= item_date <= filters['date_end']):
                    match = False
            
            # 数值范围查询
            for field in ['chlorine', 'conductivity', 'ph', 'orp', 'turbidity']:
                if f'{field}_min' in filters:
                    if item.get(field, 0) < filters[f'{field}_min']:
                        match = False
                if f'{field}_max' in filters:
                    if item.get(field, 0) > filters[f'{field}_max']:
                        match = False
            
            if match:
                result.append(item)
        
        # 排序
        if 'sort_by' in filters:
            reverse = filters.get('sort_desc', False)
            result.sort(key=lambda x: x.get(filters['sort_by'], ''), reverse=reverse)
        
        return result
    
    def get_alerts(self, thresholds: Dict[str, Dict[str, float]]) -> List[Dict[str, Any]]:
        """获取超标报警记录"""
        data = self._read_file()
        alerts = []
        
        for item in data:
            alert_items = []
            alert_level = '一般'
            
            # 检查各项指标
            for field, threshold in thresholds.items():
                value = item.get(field)
                if value is None:
                    continue
                
                if 'min' in threshold and value < threshold['min']:
                    alert_items.append(f"{field}偏低")
                    alert_level = '严重'
                elif 'max' in threshold and value > threshold['max']:
                    alert_items.append(f"{field}偏高")
                    alert_level = '严重' if value > threshold['max'] * 1.5 else '警告'
            
            if alert_items:
                alert_record = item.copy()
                alert_record['alert_items'] = alert_items
                alert_record['alert_level'] = alert_level
                alerts.append(alert_record)
        
        return sorted(alerts, key=lambda x: x.get('date', ''), reverse=True)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计数据"""
        data = self._read_file()
        
        if not data:
            return {
                'total_records': 0,
                'avg_values': {},
                'max_values': {},
                'min_values': {},
                'alert_count': 0
            }
        
        # 超标阈值
        thresholds = {
            'chlorine': {'min': 0.5, 'max': 4.0},
            'conductivity': {'max': 1000},
            'ph': {'min': 6.5, 'max': 8.5},
            'orp': {'min': 400},
            'turbidity': {'max': 5.0}
        }
        
        numeric_fields = ['chlorine', 'conductivity', 'ph', 'orp', 'turbidity']
        stats = {
            'total_records': len(data),
            'avg_values': {},
            'max_values': {},
            'min_values': {},
            'alert_count': 0
        }
        
        # 计算各字段的统计值
        for field in numeric_fields:
            values = [item.get(field, 0) for item in data if item.get(field) is not None]
            if values:
                stats['avg_values'][field] = round(sum(values) / len(values), 2)
                stats['max_values'][field] = max(values)
                stats['min_values'][field] = min(values)
        
        # 计算报警数量
        stats['alert_count'] = len(self.get_alerts(thresholds))
        
        return stats
