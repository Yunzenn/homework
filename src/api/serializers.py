from rest_framework import serializers
from .models import WaterQualityRecord, AlertThreshold
from .file_storage import FileStorageService


class WaterQualityRecordSerializer(serializers.Serializer):
    """水质记录序列化器"""
    record_id = serializers.IntegerField(read_only=True)
    point_id = serializers.CharField(max_length=50, error_messages={
        'required': '监测点ID不能为空',
        'blank': '监测点ID不能为空'
    })
    date = serializers.DateField(error_messages={
        'required': '日期不能为空',
        'invalid': '日期格式错误，请使用YYYY-MM-DD格式'
    })
    time = serializers.TimeField(error_messages={
        'required': '时间不能为空',
        'invalid': '时间格式错误，请使用HH:MM格式'
    })
    chlorine = serializers.FloatField(min_value=0, error_messages={
        'required': '余氯值不能为空',
        'min_value': '余氯值不能为负数'
    })
    conductivity = serializers.FloatField(min_value=0, error_messages={
        'required': '电导率不能为空',
        'min_value': '电导率不能为负数'
    })
    ph = serializers.FloatField(min_value=0, max_value=14, error_messages={
        'required': 'pH值不能为空',
        'min_value': 'pH值不能小于0',
        'max_value': 'pH值不能大于14'
    })
    orp = serializers.FloatField(error_messages={
        'required': '氧化还原电位不能为空'
    })
    turbidity = serializers.FloatField(min_value=0, error_messages={
        'required': '浊度不能为空',
        'min_value': '浊度不能为负数'
    })
    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    
    def validate_point_id(self, value):
        """验证监测点ID"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError('监测点ID不能为空')
        return value.strip()
    
    def validate(self, attrs):
        """交叉验证"""
        # 可以在这里添加更复杂的验证逻辑
        return attrs
    
    def create(self, validated_data):
        """创建记录"""
        storage = FileStorageService()
        record = storage.insert(validated_data)
        return record
    
    def update(self, instance, validated_data):
        """更新记录"""
        storage = FileStorageService()
        record_id = instance.get('record_id')
        updated_record = storage.update(record_id, validated_data)
        return updated_record


class QueryFilterSerializer(serializers.Serializer):
    """查询过滤器序列化器"""
    point_id = serializers.CharField(max_length=50, required=False, allow_blank=True)
    date_start = serializers.DateField(required=False)
    date_end = serializers.DateField(required=False)
    chlorine_min = serializers.FloatField(required=False, min_value=0)
    chlorine_max = serializers.FloatField(required=False, min_value=0)
    conductivity_min = serializers.FloatField(required=False, min_value=0)
    conductivity_max = serializers.FloatField(required=False, min_value=0)
    ph_min = serializers.FloatField(required=False, min_value=0, max_value=14)
    ph_max = serializers.FloatField(required=False, min_value=0, max_value=14)
    orp_min = serializers.FloatField(required=False)
    orp_max = serializers.FloatField(required=False)
    turbidity_min = serializers.FloatField(required=False, min_value=0)
    turbidity_max = serializers.FloatField(required=False, min_value=0)
    sort_by = serializers.CharField(required=False, allow_blank=True)
    sort_desc = serializers.BooleanField(required=False, default=False)
    
    def validate(self, attrs):
        """验证日期范围"""
        date_start = attrs.get('date_start')
        date_end = attrs.get('date_end')
        
        if date_start and date_end and date_start > date_end:
            raise serializers.ValidationError('开始日期不能大于结束日期')
        
        # 验证数值范围
        for field in ['chlorine', 'conductivity', 'ph', 'orp', 'turbidity']:
            min_val = attrs.get(f'{field}_min')
            max_val = attrs.get(f'{field}_max')
            
            if min_val is not None and max_val is not None and min_val > max_val:
                raise serializers.ValidationError(f'{field}的最小值不能大于最大值')
        
        return attrs


class AlertThresholdSerializer(serializers.Serializer):
    """报警阈值序列化器"""
    chlorine = serializers.DictField(required=False)
    conductivity = serializers.DictField(required=False)
    ph = serializers.DictField(required=False)
    orp = serializers.DictField(required=False)
    turbidity = serializers.DictField(required=False)


class StatisticsSerializer(serializers.Serializer):
    """统计数据序列化器"""
    total_records = serializers.IntegerField(read_only=True)
    avg_values = serializers.DictField(read_only=True)
    max_values = serializers.DictField(read_only=True)
    min_values = serializers.DictField(read_only=True)
    alert_count = serializers.IntegerField(read_only=True)
