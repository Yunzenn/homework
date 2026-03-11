from datetime import datetime, timedelta
from typing import Dict, List, Any


def generate_sample_data(count: int = 100) -> List[Dict[str, Any]]:
    """生成示例数据"""
    import random
    
    monitoring_points = ['监测点001', '监测点002', '监测点003', '监测点004', '监测点005']
    
    data = []
    base_date = datetime.now() - timedelta(days=count)
    
    for i in range(count):
        date = base_date + timedelta(days=i)
        
        # 每天生成2-4条记录
        records_per_day = random.randint(2, 4)
        for j in range(records_per_day):
            hour = random.randint(8, 18)
            minute = random.choice([0, 15, 30, 45])
            
            record = {
                'point_id': random.choice(monitoring_points),
                'date': date.strftime('%Y-%m-%d'),
                'time': f"{hour:02d}:{minute:02d}",
                'chlorine': round(random.uniform(0.8, 3.5), 2),
                'conductivity': round(random.uniform(300, 800), 1),
                'ph': round(random.uniform(6.8, 8.2), 2),
                'orp': round(random.uniform(450, 750), 1),
                'turbidity': round(random.uniform(0.5, 4.5), 2)
            }
            
            # 随机生成一些超标数据
            if random.random() < 0.1:  # 10%的概率超标
                field = random.choice(['chlorine', 'conductivity', 'ph', 'turbidity'])
                if field == 'chlorine':
                    record['chlorine'] = round(random.uniform(4.5, 6.0), 2)
                elif field == 'conductivity':
                    record['conductivity'] = round(random.uniform(1000, 1200), 1)
                elif field == 'ph':
                    record['ph'] = round(random.uniform(8.8, 9.2), 2)
                elif field == 'turbidity':
                    record['turbidity'] = round(random.uniform(5.5, 8.0), 2)
            
            data.append(record)
    
    return data


def format_datetime(dt_str: str) -> str:
    """格式化日期时间字符串"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return dt_str


def calculate_alert_level(value: float, threshold: Dict[str, float]) -> str:
    """计算报警级别"""
    if 'min' in threshold and value < threshold['min']:
        return '严重'
    if 'max' in threshold and value > threshold['max']:
        if value > threshold['max'] * 1.5:
            return '严重'
        return '警告'
    return '正常'


def validate_water_quality_data(data: Dict[str, Any]) -> List[str]:
    """验证水质数据，返回错误信息列表"""
    errors = []
    
    required_fields = ['point_id', 'date', 'time', 'chlorine', 'conductivity', 'ph', 'orp', 'turbidity']
    
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(f'{field} 字段不能为空')
    
    # 验证数值范围
    if 'ph' in data and data['ph'] is not None:
        if not (0 <= data['ph'] <= 14):
            errors.append('pH值必须在0-14之间')
    
    numeric_fields = ['chlorine', 'conductivity', 'turbidity']
    for field in numeric_fields:
        if field in data and data[field] is not None:
            if data[field] < 0:
                errors.append(f'{field} 不能为负数')
    
    return errors
