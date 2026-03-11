from rest_framework import serializers
from .models import WaterQualityRecord


class WaterQualityRecordSerializer(serializers.ModelSerializer):
    """水质记录序列化器"""
    
    class Meta:
        model = WaterQualityRecord
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def validate_point_id(self, value):
        """验证监测点ID"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError('监测点ID不能为空')
        return value.strip()
    
    def validate_chlorine(self, value):
        """验证余氯值"""
        if value is not None and value < 0:
            raise serializers.ValidationError('余氯值不能为负数')
        return value
    
    def validate_conductivity(self, value):
        """验证电导率"""
        if value is not None and value < 0:
            raise serializers.ValidationError('电导率不能为负数')
        return value
    
    def validate_ph(self, value):
        """验证pH值"""
        if value is not None and not (0 <= value <= 14):
            raise serializers.ValidationError('pH值必须在0-14之间')
        return value
    
    def validate_orp(self, value):
        """验证ORP值"""
        return value
    
    def validate_turbidity(self, value):
        """验证浊度"""
        if value is not None and value < 0:
            raise serializers.ValidationError('浊度不能为负数')
        return value
    
    def to_representation(self, instance):
        """自定义输出格式"""
        data = super().to_representation(instance)
        
        # 添加报警状态
        alert_info = instance.is_alert
        data['status'] = alert_info['alert_level']
        data['alert_items'] = alert_info['alert_items']
        
        # 格式化日期时间
        if instance.date:
            data['date'] = instance.date.strftime('%Y-%m-%d')
        if instance.time:
            data['time'] = instance.time.strftime('%H:%M')
        
        return data


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
    sort_by = serializers.CharField(required=False)
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
