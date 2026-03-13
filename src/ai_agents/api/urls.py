"""
AI Agent API URL配置
"""

from django.urls import path
from . import views

app_name = 'ai_agents'

urlpatterns = [
    # AI对话接口
    path('chat/', views.ai_chat, name='ai_chat'),
    
    # 专项功能接口
    path('query/', views.data_query, name='data_query'),
    path('analysis/', views.analysis, name='analysis'),
    path('prediction/', views.prediction, name='prediction'),
    path('anomaly/', views.anomaly_detection, name='anomaly_detection'),
    path('advisory/', views.advisory, name='advisory'),
    path('report/', views.report_generation, name='report_generation'),
    
    # 对话历史管理
    path('history/', views.chat_history, name='chat_history'),
    path('history/clear/', views.clear_chat_history, name='clear_chat_history'),
]
