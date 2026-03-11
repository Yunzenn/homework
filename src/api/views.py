from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .serializers import (
    WaterQualityRecordSerializer, 
    QueryFilterSerializer,
    AlertThresholdSerializer,
    StatisticsSerializer
)
from .file_storage import FileStorageService


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
    ordering_fields = ['date', 'time', 'point_id', 'create_time']
    ordering = ['-date', '-time']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage = FileStorageService()
    
    def get_queryset(self):
        """获取查询集"""
        return self.storage.read_all()
    
    def list(self, request, *args, **kwargs):
        """获取列表"""
        queryset = self.get_queryset()
        
        # 应用搜索
        search_term = request.query_params.get('search', None)
        if search_term:
            queryset = [item for item in queryset 
                       if search_term.lower() in str(item.get('point_id', '')).lower()]
        
        # 应用排序
        ordering = request.query_params.get('ordering', '-date,-time')
        if ordering:
            sort_fields = ordering.split(',')
            for field in sort_fields:
                reverse = field.startswith('-')
                sort_field = field.lstrip('-')
                queryset.sort(key=lambda x: x.get(sort_field, ''), reverse=reverse)
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """获取单条记录"""
        record_id = int(kwargs.get('pk'))
        record = self.storage.find_by_id(record_id)
        if not record:
            return Response(
                {'error': '记录不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(record)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建记录"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """更新记录"""
        record_id = int(kwargs.get('pk'))
        existing_record = self.storage.find_by_id(record_id)
        if not existing_record:
            return Response(
                {'error': '记录不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(existing_record, data=request.data)
        serializer.is_valid(raise_exception=True)
        record = serializer.save()
        return Response(record)
    
    def destroy(self, request, *args, **kwargs):
        """删除记录"""
        record_id = int(kwargs.get('pk'))
        success = self.storage.delete(record_id)
        if not success:
            return Response(
                {'error': '记录不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['post'])
    def query(self, request):
        """高级查询"""
        filter_serializer = QueryFilterSerializer(data=request.data)
        filter_serializer.is_valid(raise_exception=True)
        
        filters = filter_serializer.validated_data
        results = self.storage.query(filters)
        
        # 分页处理
        page = self.paginate_queryset(results)
        if page is not None:
            return self.get_paginated_response(page)
        
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def alerts(self, request):
        """获取超标报警记录"""
        # 获取查询参数中的limit，默认返回最近50条
        limit = int(request.query_params.get('limit', 50))
        
        thresholds = {
            'chlorine': {'min': 0.5, 'max': 4.0},
            'conductivity': {'max': 1000},
            'ph': {'min': 6.5, 'max': 8.5},
            'orp': {'min': 400},
            'turbidity': {'max': 5.0}
        }
        
        alerts = self.storage.get_alerts(thresholds)
        
        # 限制返回数量
        limited_alerts = alerts[:limit]
        
        # 分页处理
        page = self.paginate_queryset(limited_alerts)
        if page is not None:
            return self.get_paginated_response(page)
        
        return Response(limited_alerts)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取统计数据"""
        stats = self.storage.get_statistics()
        serializer = StatisticsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard_data(self, request):
        """获取仪表盘数据"""
        stats = self.storage.get_statistics()
        
        # 获取最近7天的趋势数据
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        filters = {
            'date_start': start_date.strftime('%Y-%m-%d'),
            'date_end': end_date.strftime('%Y-%m-%d'),
            'sort_by': 'date,time',
            'sort_desc': False
        }
        
        trend_data = self.storage.query(filters)
        
        # 获取最新的5条报警
        thresholds = {
            'chlorine': {'min': 0.5, 'max': 4.0},
            'conductivity': {'max': 1000},
            'ph': {'min': 6.5, 'max': 8.5},
            'orp': {'min': 400},
            'turbidity': {'max': 5.0}
        }
        
        recent_alerts = self.storage.get_alerts(thresholds)[:5]
        
        # 获取最新的一条记录用于显示当前指标
        all_records = self.storage.read_all()
        current_record = all_records[-1] if all_records else None
        
        dashboard_data = {
            'stats': stats,
            'trend_data': trend_data,
            'recent_alerts': recent_alerts,
            'current_record': current_record
        }
        
        return Response(dashboard_data)
    
    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        """批量删除"""
        record_ids = request.data.get('record_ids', [])
        if not record_ids:
            return Response(
                {'error': '请提供要删除的记录ID列表'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count = 0
        for record_id in record_ids:
            if self.storage.delete(record_id):
                deleted_count += 1
        
        return Response({
            'message': f'成功删除 {deleted_count} 条记录',
            'deleted_count': deleted_count,
            'total_requested': len(record_ids)
        })
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """导出数据"""
        queryset = self.get_queryset()
        
        # 应用搜索和过滤
        search_term = request.query_params.get('search', None)
        if search_term:
            queryset = [item for item in queryset 
                       if search_term.lower() in str(item.get('point_id', '')).lower()]
        
        return Response({
            'data': queryset,
            'total': len(queryset),
            'export_time': datetime.now().isoformat()
        })
