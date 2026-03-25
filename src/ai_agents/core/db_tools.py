"""
数据库查询工具
提供AI查询数据库的工具函数
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from django.db.models import Avg, Max, Min, Count, Q
from django.utils import timezone
import pandas as pd
import numpy as np

from api.models import WaterQualityRecord, MonitoringPoint


class DatabaseQueryTools:
    """数据库查询工具类"""
    
    @staticmethod
    def get_water_quality_data(
        point_ids: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        indicators: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        获取水质数据
        
        Args:
            point_ids: 监测点ID列表
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            indicators: 指标列表 ['chlorine', 'ph', 'conductivity', 'orp', 'turbidity']
            limit: 限制返回条数
        
        Returns:
            水质数据列表
        """
        queryset = WaterQualityRecord.objects.all()
        
        # 监测点过滤
        if point_ids:
            queryset = queryset.filter(point_id__in=point_ids)
        
        # 日期过滤
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # 排序
        queryset = queryset.order_by('-date', '-time')
        
        # 限制条数
        if limit:
            queryset = queryset[:limit]
        
        # 转换为字典列表
        data = []
        for record in queryset:
            item = {
                'id': record.id,
                'point_id': record.point_id,
                'date': record.date.strftime('%Y-%m-%d'),
                'time': record.time.strftime('%H:%M:%S'),
                'datetime': f"{record.date.strftime('%Y-%m-%d')} {record.time.strftime('%H:%M:%S')}",
                'chlorine': record.chlorine,
                'conductivity': record.conductivity,
                'ph': record.ph,
                'orp': record.orp,
                'turbidity': record.turbidity,
                'created_at': record.created_at.isoformat()
            }
            
            # 只返回指定的指标
            if indicators:
                item = {k: v for k, v in item.items() 
                       if k in ['id', 'point_id', 'date', 'time', 'datetime', 'created_at'] + indicators}
            
            data.append(item)
        
        return data
    
    @staticmethod
    def get_latest_data(point_ids: Optional[List[str]] = None) -> List[Dict]:
        """
        获取最新数据
        
        Args:
            point_ids: 监测点ID列表
        
        Returns:
            最新数据列表
        """
        queryset = WaterQualityRecord.objects.all()
        
        if point_ids:
            queryset = queryset.filter(point_id__in=point_ids)
        
        # 按监测点分组获取最新记录
        latest_data = []
        point_ids_list = queryset.values_list('point_id', flat=True).distinct()
        
        for point_id in point_ids_list:
            latest_record = queryset.filter(point_id=point_id).first()
            if latest_record:
                latest_data.append({
                    'id': latest_record.id,
                    'point_id': latest_record.point_id,
                    'date': latest_record.date.strftime('%Y-%m-%d'),
                    'time': latest_record.time.strftime('%H:%M:%S'),
                    'datetime': f"{latest_record.date.strftime('%Y-%m-%d')} {latest_record.time.strftime('%H:%M:%S')}",
                    'chlorine': latest_record.chlorine,
                    'conductivity': latest_record.conductivity,
                    'ph': latest_record.ph,
                    'orp': latest_record.orp,
                    'turbidity': latest_record.turbidity,
                    'is_alert': latest_record.is_alert
                })
        
        return latest_data
    
    @staticmethod
    def get_statistics(
        point_ids: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        indicators: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        获取统计数据
        
        Args:
            point_ids: 监测点ID列表
            start_date: 开始日期
            end_date: 结束日期
            indicators: 指标列表
        
        Returns:
            统计数据字典
        """
        queryset = WaterQualityRecord.objects.all()
        
        # 过滤条件
        if point_ids:
            queryset = queryset.filter(point_id__in=point_ids)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # 基础统计
        total_records = queryset.count()
        if total_records == 0:
            return {'error': '没有找到数据'}
        
        # 指标统计
        stats = {}
        indicator_fields = indicators or ['chlorine', 'conductivity', 'ph', 'orp', 'turbidity']
        
        for field in indicator_fields:
            field_stats = queryset.aggregate(
                avg=Avg(field),
                max=Max(field),
                min=Min(field),
                count=Count(field)
            )
            
            stats[field] = {
                'avg': round(field_stats['avg'] or 0, 2),
                'max': round(field_stats['max'] or 0, 2),
                'min': round(field_stats['min'] or 0, 2),
                'count': field_stats['count']
            }
        
        # 报警统计
        alert_records = WaterQualityRecord.get_alert_records()
        if point_ids:
            alert_records = alert_records.filter(point_id__in=point_ids)
        if start_date:
            alert_records = alert_records.filter(date__gte=start_date)
        if end_date:
            alert_records = alert_records.filter(date__lte=end_date)
        
        alert_count = alert_records.count()
        
        # 监测点统计
        point_count = queryset.values('point_id').distinct().count()
        
        return {
            'total_records': total_records,
            'point_count': point_count,
            'alert_count': alert_count,
            'alert_rate': round((alert_count / total_records * 100), 2),
            'indicators': stats,
            'date_range': {
                'start': start_date,
                'end': end_date
            }
        }
    
    @staticmethod
    def get_alert_data(
        point_ids: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = 50
    ) -> List[Dict]:
        """
        获取报警数据
        
        Args:
            point_ids: 监测点ID列表
            start_date: 开始日期
            end_date: 结束日期
            limit: 限制条数
        
        Returns:
            报警数据列表
        """
        alert_records = WaterQualityRecord.get_alert_records()
        
        # 过滤条件
        if point_ids:
            alert_records = alert_records.filter(point_id__in=point_ids)
        if start_date:
            alert_records = alert_records.filter(date__gte=start_date)
        if end_date:
            alert_records = alert_records.filter(date__lte=end_date)
        
        # 排序和限制
        alert_records = alert_records.order_by('-date', '-time')[:limit]
        
        # 转换为字典列表
        alert_data = []
        for record in alert_records:
            alert_info = record.is_alert
            alert_data.append({
                'id': record.id,
                'point_id': record.point_id,
                'date': record.date.strftime('%Y-%m-%d'),
                'time': record.time.strftime('%H:%M:%S'),
                'datetime': f"{record.date.strftime('%Y-%m-%d')} {record.time.strftime('%H:%M:%S')}",
                'alert_items': alert_info['alert_items'],
                'alert_level': alert_info['alert_level'],
                'chlorine': record.chlorine,
                'conductivity': record.conductivity,
                'ph': record.ph,
                'orp': record.orp,
                'turbidity': record.turbidity
            })
        
        return alert_data
    
    @staticmethod
    def get_trend_data(
        point_id: str,
        indicator: str,
        days: int = 7
    ) -> List[Dict]:
        """
        获取趋势数据
        
        Args:
            point_id: 监测点ID
            indicator: 指标名称
            days: 天数
        
        Returns:
            趋势数据列表
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        records = WaterQualityRecord.objects.filter(
            point_id=point_id,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date', 'time')
        
        trend_data = []
        for record in records:
            trend_data.append({
                'date': record.date.strftime('%Y-%m-%d'),
                'time': record.time.strftime('%H:%M:%S'),
                'datetime': f"{record.date.strftime('%Y-%m-%d')} {record.time.strftime('%H:%M:%S')}",
                'value': getattr(record, indicator)
            })
        
        return trend_data
    
    @staticmethod
    def get_monitoring_points(active_only: bool = True) -> List[Dict]:
        """
        获取监测点信息
        
        Args:
            active_only: 是否只获取启用的监测点
        
        Returns:
            监测点信息列表
        """
        queryset = MonitoringPoint.objects.all()
        
        if active_only:
            queryset = queryset.filter(is_active=True)
        
        points = []
        for point in queryset:
            points.append({
                'id': point.id,
                'point_id': point.point_id,
                'name': point.name,
                'latitude': float(point.latitude),
                'longitude': float(point.longitude),
                'location_description': point.location_description,
                'is_active': point.is_active,
                'created_at': point.created_at.isoformat()
            })
        
        return points
    
    @staticmethod
    def search_by_keyword(keyword: str, limit: int = 20) -> List[Dict]:
        """
        关键词搜索
        
        Args:
            keyword: 搜索关键词
            limit: 限制条数
        
        Returns:
            搜索结果列表
        """
        # 搜索监测点
        points = MonitoringPoint.objects.filter(
            Q(point_id__icontains=keyword) |
            Q(name__icontains=keyword) |
            Q(location_description__icontains=keyword)
        )
        
        # 搜索水质记录
        records = WaterQualityRecord.objects.filter(
            point_id__icontains=keyword
        ).order_by('-date', '-time')[:limit]
        
        results = {
            'monitoring_points': [
                {
                    'id': point.id,
                    'point_id': point.point_id,
                    'name': point.name,
                    'location_description': point.location_description
                }
                for point in points
            ],
            'water_quality_records': [
                {
                    'id': record.id,
                    'point_id': record.point_id,
                    'date': record.date.strftime('%Y-%m-%d'),
                    'time': record.time.strftime('%H:%M:%S'),
                    'chlorine': record.chlorine,
                    'conductivity': record.conductivity,
                    'ph': record.ph,
                    'orp': record.orp,
                    'turbidity': record.turbidity
                }
                for record in records
            ]
        }
        
        return results


# 水质标准阈值
WATER_QUALITY_STANDARDS = {
    'chlorine': {'min': 0.5, 'max': 4.0, 'unit': 'mg/L', 'name': '余氯'},
    'conductivity': {'max': 1000, 'unit': 'µS/cm', 'name': '电导率'},
    'ph': {'min': 6.5, 'max': 8.5, 'unit': '', 'name': 'pH值'},
    'orp': {'min': 400, 'unit': 'mV', 'name': '氧化还原电位'},
    'turbidity': {'max': 5.0, 'unit': 'NTU', 'name': '浊度'}
}


def check_water_quality_standard(indicator: str, value: float) -> Dict[str, Any]:
    """
    检查水质指标是否符合标准
    
    Args:
        indicator: 指标名称
        value: 指标值
    
    Returns:
        检查结果
    """
    if indicator not in WATER_QUALITY_STANDARDS:
        return {'valid': False, 'error': '未知指标'}
    
    standard = WATER_QUALITY_STANDARDS[indicator]
    result = {
        'indicator': indicator,
        'name': standard['name'],
        'value': value,
        'unit': standard['unit'],
        'standard': standard,
        'is_normal': True,
        'status': '正常'
    }
    
    # 检查是否超标
    if 'min' in standard and value < standard['min']:
        result['is_normal'] = False
        result['status'] = '过低'
    elif 'max' in standard and value > standard['max']:
        result['is_normal'] = False
        result['status'] = '过高'
    
    return result


def format_water_quality_data(data: List[Dict], indicators: List[str] = None) -> str:
    """
    格式化水质数据为可读文本
    
    Args:
        data: 水质数据列表
        indicators: 要显示的指标列表
    
    Returns:
        格式化后的文本
    """
    if not data:
        return "没有找到数据"
    
    indicators = indicators or ['chlorine', 'conductivity', 'ph', 'orp', 'turbidity']
    lines = []
    
    for i, record in enumerate(data[:10], 1):  # 最多显示10条
        lines.append(f"{i}. {record['point_id']} - {record['date']} {record['time']}")
        
        for indicator in indicators:
            if indicator in record:
                value = record[indicator]
                standard = WATER_QUALITY_STANDARDS.get(indicator, {})
                unit = standard.get('unit', '')
                name = standard.get('name', indicator)
                
                # 检查是否异常
                status = ""
                if 'min' in standard and value < standard['min']:
                    status = " ⚠️过低"
                elif 'max' in standard and value > standard['max']:
                    status = " ⚠️过高"
                
                lines.append(f"   {name}: {value}{unit}{status}")
        
        lines.append("")
    
    if len(data) > 10:
        lines.append(f"... 还有 {len(data) - 10} 条数据")
    
    return "\n".join(lines)
