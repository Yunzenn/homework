from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器
router = DefaultRouter()
router.register(r'records', views.WaterQualityRecordViewSet, basename='waterqualityrecord')

# URL配置
urlpatterns = [
    path('', include(router.urls)),
    # 移除单独的 dashboard_data 路径，因为它已经包含在 ViewSet 的 @action 中
    path('records/analysis/', views.WaterQualityRecordViewSet.as_view({'get': 'analysis'}), name='analysis'),
    path('records/export-analysis/', views.WaterQualityRecordViewSet.as_view({'get': 'export_analysis'}), name='export_analysis'),
]
