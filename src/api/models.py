from django.db import models
from django.utils import timezone


class WaterQualityRecord(models.Model):
    """水质记录模型"""
    point_id = models.CharField('监测点编号', max_length=50, db_index=True)
    date = models.DateField('日期', db_index=True)
    time = models.TimeField('时间', db_index=True)
    chlorine = models.FloatField('余氯(mg/L)')
    conductivity = models.FloatField('电导率(µS/cm)')
    ph = models.FloatField('pH值')
    orp = models.FloatField('氧化还原电位(mV)')
    turbidity = models.FloatField('浊度(NTU)')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'api_waterqualityrecord'
        ordering = ['-date', '-time']
        indexes = [
            models.Index(fields=['point_id']),
            models.Index(fields=['date']),
            models.Index(fields=['point_id', 'date']),
        ]
        verbose_name = '水质记录'
        verbose_name_plural = '水质记录'
    
    def __str__(self):
        return f"{self.point_id} - {self.date} {self.time}"
    
    @property
    def is_alert(self):
        """检查是否超标"""
        alerts = []
        
        if self.chlorine < 0.5 or self.chlorine > 4.0:
            alerts.append('余氯')
        if self.conductivity > 1000:
            alerts.append('电导率')
        if self.ph < 6.5 or self.ph > 8.5:
            alerts.append('pH值')
        if self.orp < 400:
            alerts.append('ORP')
        if self.turbidity > 5.0:
            alerts.append('浊度')
        
        return {
            'is_alert': len(alerts) > 0,
            'alert_items': alerts,
            'alert_level': 'danger' if len(alerts) > 1 else 'warning' if alerts else 'normal'
        }
    
    @classmethod
    def get_alert_records(cls):
        """获取所有超标记录"""
        return cls.objects.filter(
            models.Q(chlorine__lt=0.5) | models.Q(chlorine__gt=4.0) |
            models.Q(conductivity__gt=1000) |
            models.Q(ph__lt=6.5) | models.Q(ph__gt=8.5) |
            models.Q(orp__lt=400) |
            models.Q(turbidity__gt=5.0)
        )
    
    @classmethod
    def get_by_point_id(cls, point_id):
        """根据监测点获取记录"""
        return cls.objects.filter(point_id__icontains=point_id)
    
    @classmethod
    def get_by_date_range(cls, start_date=None, end_date=None):
        """根据日期范围获取记录"""
        queryset = cls.objects.all()
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        return queryset
    
    @classmethod
    def get_by_threshold(cls, field_name, min_value=None, max_value=None):
        """根据阈值获取记录"""
        filter_kwargs = {}
        if min_value is not None:
            filter_kwargs[f"{field_name}__gte"] = min_value
        if max_value is not None:
            filter_kwargs[f"{field_name}__lte"] = max_value
        
        if filter_kwargs:
            return cls.objects.filter(**filter_kwargs)
        return cls.objects.all()
