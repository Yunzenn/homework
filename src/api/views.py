from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Avg, Max, Min, Count
from django.http import HttpResponse

from .serializers import (
    WaterQualityRecordSerializer, 
    QueryFilterSerializer,
    AlertThresholdSerializer,
    StatisticsSerializer
)
from .models import WaterQualityRecord


class StandardResultsSetPagination(PageNumberPagination):
    """自定义分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class WaterQualityRecordViewSet(viewsets.ModelViewSet):
    """水质记录视图集"""
    serializer_class = WaterQualityRecordSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['point_id']
    ordering_fields = ['date', 'time', 'point_id', 'created_at']
    ordering = ['-date', '-time']
    
    def get_queryset(self):
        """获取查询集"""
        queryset = WaterQualityRecord.objects.all()
        
        # 搜索功能
        search_term = self.request.query_params.get('search', None)
        if search_term:
            queryset = queryset.filter(point_id__icontains=search_term)
        
        # 日期范围过滤
        date_after = self.request.query_params.get('date_after')
        date_before = self.request.query_params.get('date_before')
        if date_after:
            queryset = queryset.filter(date__gte=date_after)
        if date_before:
            queryset = queryset.filter(date__lte=date_before)
        
        # 监测点过滤
        point_id = self.request.query_params.get('point_id')
        if point_id:
            queryset = queryset.filter(point_id__icontains=point_id)
        
        # 指标阈值过滤
        chlorine_min = self.request.query_params.get('chlorine_min')
        chlorine_max = self.request.query_params.get('chlorine_max')
        if chlorine_min is not None:
            queryset = queryset.filter(chlorine__gte=chlorine_min)
        if chlorine_max is not None:
            queryset = queryset.filter(chlorine__lte=chlorine_max)
            
        conductivity_min = self.request.query_params.get('conductivity_min')
        conductivity_max = self.request.query_params.get('conductivity_max')
        if conductivity_min is not None:
            queryset = queryset.filter(conductivity__gte=conductivity_min)
        if conductivity_max is not None:
            queryset = queryset.filter(conductivity__lte=conductivity_max)
            
        ph_min = self.request.query_params.get('ph_min')
        ph_max = self.request.query_params.get('ph_max')
        if ph_min is not None:
            queryset = queryset.filter(ph__gte=ph_min)
        if ph_max is not None:
            queryset = queryset.filter(ph__lte=ph_max)
            
        orp_min = self.request.query_params.get('orp_min')
        orp_max = self.request.query_params.get('orp_max')
        if orp_min is not None:
            queryset = queryset.filter(orp__gte=orp_min)
        if orp_max is not None:
            queryset = queryset.filter(orp__lte=orp_max)
            
        turbidity_min = self.request.query_params.get('turbidity_min')
        turbidity_max = self.request.query_params.get('turbidity_max')
        if turbidity_min is not None:
            queryset = queryset.filter(turbidity__gte=turbidity_min)
        if turbidity_max is not None:
            queryset = queryset.filter(turbidity__lte=turbidity_max)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def query(self, request):
        """高级查询"""
        serializer = QueryFilterSerializer(data=request.data)
        if serializer.is_valid():
            filters = serializer.validated_data
            
            queryset = WaterQualityRecord.objects.all()
            
            # 应用过滤条件
            if filters.get('point_id'):
                queryset = queryset.filter(point_id__icontains=filters['point_id'])
                
            if filters.get('date_start'):
                queryset = queryset.filter(date__gte=filters['date_start'])
                
            if filters.get('date_end'):
                queryset = queryset.filter(date__lte=filters['date_end'])
            
            # 指标阈值过滤
            for field in ['chlorine', 'conductivity', 'ph', 'orp', 'turbidity']:
                min_val = filters.get(f'{field}_min')
                max_val = filters.get(f'{field}_max')
                if min_val is not None:
                    queryset = queryset.filter(**{f'{field}__gte': min_val})
                if max_val is not None:
                    queryset = queryset.filter(**{f'{field}__lte': max_val})
            
            # 排序
            sort_by = filters.get('sort_by', 'date')
            sort_desc = filters.get('sort_desc', False)
            if sort_by:
                if sort_desc:
                    queryset = queryset.order_by(f'-{sort_by}')
                else:
                    queryset = queryset.order_by(sort_by)
            
            # 序列化返回
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def alerts(self, request):
        """获取报警记录"""
        limit = int(request.query_params.get('limit', 50))
        alert_records = WaterQualityRecord.get_alert_records()[:limit]
        
        serializer = self.get_serializer(alert_records, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        """批量删除"""
        record_ids = request.data.get('record_ids', [])
        
        if not record_ids:
            return Response(
                {'error': '请提供要删除的记录ID列表'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count, _ = WaterQualityRecord.objects.filter(id__in=record_ids).delete()
        
        return Response({
            'message': f'成功删除 {deleted_count} 条记录',
            'deleted_count': deleted_count,
            'total_requested': len(record_ids)
        })
    
    @action(detail=False, methods=['get'])
    def alerts(self, request):
        """获取报警数据"""
        # 获取查询参数
        date_after = request.query_params.get('date_after')
        date_before = request.query_params.get('date_before')
        point_id = request.query_params.get('point_id')
        limit = int(request.query_params.get('limit', 50))
        
        # 获取报警记录
        alert_records = WaterQualityRecord.get_alert_records()
        
        # 应用过滤条件
        if date_after:
            alert_records = alert_records.filter(date__gte=date_after)
        if date_before:
            alert_records = alert_records.filter(date__lte=date_before)
        if point_id:
            alert_records = alert_records.filter(point_id__icontains=point_id)
        
        # 限制数量并排序
        alert_records = alert_records.order_by('-date', '-time')[:limit]
        
        # 序列化数据
        serializer = self.get_serializer(alert_records, many=True)
        
        # 统计报警类型
        alert_stats = {
            'chlorine': 0,
            'conductivity': 0,
            'ph': 0,
            'orp': 0,
            'turbidity': 0
        }
        
        alert_data = []
        for record in alert_records:
            alert_info = record.is_alert
            alert_data.append({
                'id': record.id,
                'point_id': record.point_id,
                'date': record.date,
                'time': record.time,
                'alert_items': alert_info['alert_items'],
                'chlorine': record.chlorine,
                'conductivity': record.conductivity,
                'ph': record.ph,
                'orp': record.orp,
                'turbidity': record.turbidity,
                'created_at': record.created_at
            })
            
            # 统计各类型报警数量
            for item in alert_info['alert_items']:
                if item in alert_stats:
                    alert_stats[item] += 1
        
        return Response({
            'alerts': alert_data,
            'total_count': len(alert_data),
            'alert_stats': alert_stats,
            'summary': {
                'total_alerts': len(alert_data),
                'unique_points': len(set(r['point_id'] for r in alert_data)),
                'most_common_alert': max(alert_stats.items(), key=lambda x: x[1])[0] if any(alert_stats.values()) else None
            }
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取统计数据"""
        # 基础统计
        total_records = WaterQualityRecord.objects.count()
        total_points = WaterQualityRecord.objects.values('point_id').distinct().count()
        
        # 报警统计
        alert_records = WaterQualityRecord.get_alert_records()
        alert_count = alert_records.count()
        
        # 平均值统计
        stats = WaterQualityRecord.objects.aggregate(
            avg_chlorine=Avg('chlorine'),
            avg_conductivity=Avg('conductivity'),
            avg_ph=Avg('ph'),
            avg_orp=Avg('orp'),
            avg_turbidity=Avg('turbidity'),
            max_chlorine=Max('chlorine'),
            max_conductivity=Max('conductivity'),
            max_ph=Max('ph'),
            max_orp=Max('orp'),
            max_turbidity=Max('turbidity'),
            min_chlorine=Min('chlorine'),
            min_conductivity=Min('conductivity'),
            min_ph=Min('ph'),
            min_orp=Min('orp'),
            min_turbidity=Min('turbidity'),
        )
        
        # 最近更新时间
        latest_record = WaterQualityRecord.objects.order_by('-created_at').first()
        
        return Response({
            'total_records': total_records,
            'total_points': total_points,
            'alert_count': alert_count,
            'alert_rate': round((alert_count / total_records * 100), 2) if total_records > 0 else 0,
            'statistics': {
                'chlorine': {
                    'avg': round(stats['avg_chlorine'], 2) if stats['avg_chlorine'] else 0,
                    'max': round(stats['max_chlorine'], 2) if stats['max_chlorine'] else 0,
                    'min': round(stats['min_chlorine'], 2) if stats['min_chlorine'] else 0,
                },
                'conductivity': {
                    'avg': round(stats['avg_conductivity'], 2) if stats['avg_conductivity'] else 0,
                    'max': round(stats['max_conductivity'], 2) if stats['max_conductivity'] else 0,
                    'min': round(stats['min_conductivity'], 2) if stats['min_conductivity'] else 0,
                },
                'ph': {
                    'avg': round(stats['avg_ph'], 2) if stats['avg_ph'] else 0,
                    'max': round(stats['max_ph'], 2) if stats['max_ph'] else 0,
                    'min': round(stats['min_ph'], 2) if stats['min_ph'] else 0,
                },
                'orp': {
                    'avg': round(stats['avg_orp'], 2) if stats['avg_orp'] else 0,
                    'max': round(stats['max_orp'], 2) if stats['max_orp'] else 0,
                    'min': round(stats['min_orp'], 2) if stats['min_orp'] else 0,
                },
                'turbidity': {
                    'avg': round(stats['avg_turbidity'], 2) if stats['avg_turbidity'] else 0,
                    'max': round(stats['max_turbidity'], 2) if stats['max_turbidity'] else 0,
                    'min': round(stats['min_turbidity'], 2) if stats['min_turbidity'] else 0,
                },
            },
            'latest_update': latest_record.created_at if latest_record else None
        })
    
    @action(detail=False, methods=['get'])
    def dashboard_data(self, request):
        """仪表盘数据"""
        # 基础统计
        total_records = WaterQualityRecord.objects.count()
        total_points = WaterQualityRecord.objects.values('point_id').distinct().count()
        
        # 报警统计
        alert_records = WaterQualityRecord.get_alert_records()
        alert_count = alert_records.count()
        
        # 平均值统计
        stats = WaterQualityRecord.objects.aggregate(
            avg_chlorine=Avg('chlorine'),
            avg_conductivity=Avg('conductivity'),
            avg_ph=Avg('ph'),
            avg_orp=Avg('orp'),
            avg_turbidity=Avg('turbidity'),
            max_chlorine=Max('chlorine'),
            max_conductivity=Max('conductivity'),
            max_ph=Max('ph'),
            max_orp=Max('orp'),
            max_turbidity=Max('turbidity'),
            min_chlorine=Min('chlorine'),
            min_conductivity=Min('conductivity'),
            min_ph=Min('ph'),
            min_orp=Min('orp'),
            min_turbidity=Min('turbidity'),
        )
        
        # 最近报警
        recent_alerts = alert_records.order_by('-created_at')[:5]
        
        # 当前记录（最新的）
        current_record = WaterQualityRecord.objects.order_by('-created_at').first()
        
        dashboard_data = {
            'stats': {
                'total_records': total_records,
                'total_points': total_points,
                'alert_count': alert_count,
                'avg_values': {
                    'chlorine': round(stats['avg_chlorine'] or 0, 2),
                    'conductivity': round(stats['avg_conductivity'] or 0, 2),
                    'ph': round(stats['avg_ph'] or 0, 2),
                    'orp': round(stats['avg_orp'] or 0, 2),
                    'turbidity': round(stats['avg_turbidity'] or 0, 2),
                },
                'max_values': {
                    'chlorine': round(stats['max_chlorine'] or 0, 2),
                    'conductivity': round(stats['max_conductivity'] or 0, 2),
                    'ph': round(stats['max_ph'] or 0, 2),
                    'orp': round(stats['max_orp'] or 0, 2),
                    'turbidity': round(stats['max_turbidity'] or 0, 2),
                },
                'min_values': {
                    'chlorine': round(stats['min_chlorine'] or 0, 2),
                    'conductivity': round(stats['min_conductivity'] or 0, 2),
                    'ph': round(stats['min_ph'] or 0, 2),
                    'orp': round(stats['min_orp'] or 0, 2),
                    'turbidity': round(stats['min_turbidity'] or 0, 2),
                }
            },
            'recent_alerts': WaterQualityRecordSerializer(recent_alerts, many=True).data,
            'current_record': WaterQualityRecordSerializer(current_record).data if current_record else None
        }
        
        return Response(dashboard_data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """统计数据"""
        total_records = WaterQualityRecord.objects.count()
        total_points = WaterQualityRecord.objects.values('point_id').distinct().count()
        alert_count = WaterQualityRecord.get_alert_records().count()
        
        # 计算平均值
        stats = WaterQualityRecord.objects.aggregate(
            avg_chlorine=Avg('chlorine'),
            avg_conductivity=Avg('conductivity'),
            avg_ph=Avg('ph'),
            avg_orp=Avg('orp'),
            avg_turbidity=Avg('turbidity'),
        )
        
        return Response({
            'total_records': total_records,
            'total_points': total_points,
            'alert_count': alert_count,
            'avg_chlorine': round(stats['avg_chlorine'] or 0, 2),
            'avg_conductivity': round(stats['avg_conductivity'] or 0, 2),
            'avg_ph': round(stats['avg_ph'] or 0, 2),
            'avg_orp': round(stats['avg_orp'] or 0, 2),
            'avg_turbidity': round(stats['avg_turbidity'] or 0, 2),
        })
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """导出数据"""
        queryset = self.get_queryset()
        
        # 生成CSV数据
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="water_quality_data.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            '监测点', '日期', '时间', '余氯(mg/L)', '电导率(µS/cm)', 
            'pH值', '氧化还原电位(mV)', '浊度(NTU)', '创建时间'
        ])
        
        for record in queryset:
            writer.writerow([
                record.point_id,
                record.date,
                record.time,
                record.chlorine,
                record.conductivity,
                record.ph,
                record.orp,
                record.turbidity,
                record.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
    @action(detail=False, methods=['get'])
    def analysis(self, request):
        """数据分析接口"""
        # 获取时间范围参数
        date_start = request.query_params.get('date_start')
        date_end = request.query_params.get('date_end')
        
        # 基础查询
        queryset = WaterQualityRecord.objects.all()
        
        if date_start:
            queryset = queryset.filter(date__gte=date_start)
        if date_end:
            queryset = queryset.filter(date__lte=date_end)
        
        # 基础统计
        total_records = queryset.count()
        total_points = queryset.values('point_id').distinct().count()
        
        # 计算超标记录
        alert_queryset = WaterQualityRecord.get_alert_records()
        if date_start:
            alert_queryset = alert_queryset.filter(date__gte=date_start)
        if date_end:
            alert_queryset = alert_queryset.filter(date__lte=date_end)
        
        alert_count = alert_queryset.count()
        
        # 计算数据完整率
        completeness_rate = ((total_records - alert_count) / total_records * 100) if total_records > 0 else 100
        
        # 按监测点分组统计
        point_stats = []
        points = queryset.values('point_id').distinct()
        
        for point in points:
            point_id = point['point_id']
            point_records = queryset.filter(point_id=point_id)
            
            # 计算该监测点的超标记录
            point_alerts = point_records.filter(
                models.Q(chlorine__lt=0.5) | models.Q(chlorine__gt=4.0) |
                models.Q(conductivity__gt=1000) |
                models.Q(ph__lt=6.5) | models.Q(ph__gt=8.5) |
                models.Q(orp__lt=400) |
                models.Q(turbidity__gt=5.0)
            )
            
            alert_count = point_alerts.count()
            record_count = point_records.count()
            alert_rate = (alert_count / record_count * 100) if record_count > 0 else 0
            
            # 计算平均值
            avg_values = point_records.aggregate(
                avg_chlorine=Avg('chlorine'),
                avg_conductivity=Avg('conductivity'),
                avg_ph=Avg('ph'),
                avg_orp=Avg('orp'),
                avg_turbidity=Avg('turbidity'),
                min_chlorine=Min('chlorine'),
                max_chlorine=Max('chlorine'),
                min_conductivity=Min('conductivity'),
                max_conductivity=Max('conductivity'),
                min_ph=Min('ph'),
                max_ph=Max('ph'),
                min_orp=Min('orp'),
                max_orp=Max('orp'),
                min_turbidity=Min('turbidity'),
                max_turbidity=Max('turbidity'),
            )
            
            point_stats.append({
                'point_id': point_id,
                'record_count': record_count,
                'alert_count': alert_count,
                'alert_rate': round(alert_rate, 2),
                'avg_chlorine': round(avg_values['avg_chlorine'] or 0, 2),
                'avg_conductivity': round(avg_values['avg_conductivity'] or 0, 2),
                'avg_ph': round(avg_values['avg_ph'] or 0, 2),
                'avg_orp': round(avg_values['avg_orp'] or 0, 2),
                'avg_turbidity': round(avg_values['avg_turbidity'] or 0, 2),
                'min_chlorine': round(avg_values['min_chlorine'] or 0, 2),
                'max_chlorine': round(avg_values['max_chlorine'] or 0, 2),
                'min_conductivity': round(avg_values['min_conductivity'] or 0, 2),
                'max_conductivity': round(avg_values['max_conductivity'] or 0, 2),
                'min_ph': round(avg_values['min_ph'] or 0, 2),
                'max_ph': round(avg_values['max_ph'] or 0, 2),
                'min_orp': round(avg_values['min_orp'] or 0, 2),
                'max_orp': round(avg_values['max_orp'] or 0, 2),
                'min_turbidity': round(avg_values['min_turbidity'] or 0, 2),
                'max_turbidity': round(avg_values['max_turbidity'] or 0, 2),
            })
        
        # 按日期分组统计（用于趋势图）
        trend_data = []
        if date_start and date_end:
            # 按天分组
            daily_stats = queryset.extra({
                'date': models.DateField('date')
            }).values('date').annotate(
                record_count=models.Count('id'),
                avg_chlorine=Avg('chlorine'),
                avg_conductivity=Avg('conductivity'),
                avg_ph=Avg('ph'),
                avg_orp=Avg('orp'),
                avg_turbidity=Avg('turbidity'),
            ).order_by('date')
            
            for stat in daily_stats:
                trend_data.append({
                    'date': stat['date'].strftime('%Y-%m-%d'),
                    'record_count': stat['record_count'],
                    'avg_chlorine': round(stat['avg_chlorine'] or 0, 2),
                    'avg_conductivity': round(stat['avg_conductivity'] or 0, 2),
                    'avg_ph': round(stat['avg_ph'] or 0, 2),
                    'avg_orp': round(stat['avg_orp'] or 0, 2),
                    'avg_turbidity': round(stat['avg_turbidity'] or 0, 2),
                })
        
        # 指标分布统计
        distribution_data = {
            'points': list(points.values_list('point_id', flat=True)),
            'chlorine_ranges': self._get_distribution_ranges(queryset, 'chlorine', [0.5, 1.0, 2.0, 4.0]),
            'conductivity_ranges': self._get_distribution_ranges(queryset, 'conductivity', [200, 500, 800, 1000]),
            'ph_ranges': self._get_distribution_ranges(queryset, 'ph', [6.0, 6.5, 8.0, 8.5]),
            'orp_ranges': self._get_distribution_ranges(queryset, 'orp', [300, 400, 600, 800]),
            'turbidity_ranges': self._get_distribution_ranges(queryset, 'turbidity', [1.0, 2.0, 3.0, 5.0]),
        }
        
        # 相关性数据
        correlation_data = self._calculate_correlations(queryset)
        
        return Response({
            'overview': {
                'total_records': total_records,
                'total_points': total_points,
                'alert_count': alert_count,
                'completeness_rate': round(completeness_rate, 2),
            },
            'point_analysis': point_stats,
            'trend_data': trend_data,
            'distribution_data': distribution_data,
            'correlation_data': correlation_data,
        })
    
    def _get_distribution_ranges(self, queryset, field, ranges):
        """获取字段分布范围统计"""
        distribution = []
        
        for i, range_value in enumerate(ranges):
            if i == 0:
                # 第一个范围：小于第一个值
                count = queryset.filter(**{f'{field}__lt': range_value}).count()
                label = f'< {range_value}'
            elif i == len(ranges) - 1:
                # 最后一个范围：大于等于最后一个值
                count = queryset.filter(**{f'{field}__gte': range_value}).count()
                label = f'≥ {range_value}'
            else:
                # 中间范围：大于等于前一个值，小于当前值
                prev_range = ranges[i-1]
                count = queryset.filter(**{f'{field}__gte': prev_range, f'{field}__lt': range_value}).count()
                label = f'{prev_range} - {range_value}'
            
            distribution.append({
                'label': label,
                'count': count,
                'percentage': round((count / queryset.count() * 100), 2) if queryset.count() > 0 else 0
            })
        
        return distribution
    
    def _calculate_correlations(self, queryset):
        """计算指标之间的相关性"""
        metrics = ['chlorine', 'conductivity', 'ph', 'orp', 'turbidity']
        correlation_matrix = []
        
        # 获取所有数值数据
        data = queryset.values(*metrics)
        
        # 计算相关系数矩阵
        import numpy as np
        
        try:
            # 构建数据矩阵
            matrix = []
            for metric in metrics:
                values = [item[metric] or 0 for item in data]
                matrix.append(values)
            
            # 计算相关系数
            corr_matrix = np.corrcoef(matrix)
            
            # 转换为前端可用的格式
            for i in range(len(metrics)):
                for j in range(len(metrics)):
                    correlation_matrix.append({
                        'metric1': metrics[i],
                        'metric2': metrics[j],
                        'correlation': round(float(corr_matrix[i][j]), 3)
                    })
        except ImportError:
            # 如果没有numpy，使用简化的相关性计算
            for i in range(len(metrics)):
                for j in range(len(metrics)):
                    correlation = self._simple_correlation(data, metrics[i], metrics[j])
                    correlation_matrix.append({
                        'metric1': metrics[i],
                        'metric2': metrics[j],
                        'correlation': round(correlation, 3)
                    })
        
        return correlation_matrix
    
    def _simple_correlation(self, data, field1, field2):
        """简化的相关系数计算"""
        values1 = [item[field1] or 0 for item in data]
        values2 = [item[field2] or 0 for item in data]
        
        if len(values1) != len(values2) or len(values1) == 0:
            return 0.0
        
        # 计算平均值
        mean1 = sum(values1) / len(values1)
        mean2 = sum(values2) / len(values2)
        
        # 计算协方差
        covariance = sum((values1[i] - mean1) * (values2[i] - mean2) for i in range(len(values1)))
        
        # 计算标准差
        std1 = (sum((values1[i] - mean1) ** 2 for i in range(len(values1))) / len(values1)) ** 0.5
        std2 = (sum((values2[i] - mean2) ** 2 for i in range(len(values2))) / len(values2)) ** 0.5
        
        # 计算相关系数
        if std1 == 0 or std2 == 0:
            return 0.0
        
        return covariance / (len(values1) * std1 * std2)
    
    @action(detail=False, methods=['get'])
    def export_analysis(self, request):
        """导出分析报告"""
        # 获取分析数据
        analysis_response = self.analysis(request)
        if analysis_response.status_code != 200:
            return analysis_response
        
        analysis_data = analysis_response.data
        
        # 生成CSV报告
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="data_analysis_report.csv"'
        
        writer = csv.writer(response)
        
        # 写入概览信息
        writer.writerow(['数据分析报告'])
        writer.writerow(['生成时间', timezone.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        writer.writerow(['概览统计'])
        writer.writerow(['总记录数', '监测点数量', '超标数量', '数据完整率'])
        writer.writerow([
            analysis_data['overview']['total_records'],
            analysis_data['overview']['total_points'],
            analysis_data['overview']['alert_count'],
            f"{analysis_data['overview']['completeness_rate']}%"
        ])
        writer.writerow([])
        
        # 写入监测点分析
        writer.writerow(['监测点分析'])
        writer.writerow([
            '监测点', '记录数', '超标数', '超标率', 
            '平均余氯', '平均电导率', '平均pH值', '平均ORP', '平均浊度'
        ])
        
        for point in analysis_data['point_analysis']:
            writer.writerow([
                point['point_id'],
                point['record_count'],
                point['alert_count'],
                f"{point['alert_rate']}%",
                point['avg_chlorine'],
                point['avg_conductivity'],
                point['avg_ph'],
                point['avg_orp'],
                point['avg_turbidity']
            ])
        
        return response
