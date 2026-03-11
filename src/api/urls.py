from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WaterQualityRecordViewSet

# 创建路由器
router = DefaultRouter()
router.register(r'records', WaterQualityRecordViewSet, basename='waterquality')

# URL配置
urlpatterns = [
    path('', include(router.urls)),
]
