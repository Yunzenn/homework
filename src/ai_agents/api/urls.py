"""
AI Agent API URL配置
"""

from django.urls import path
from . import views
from . import test_ollama
from . import enhanced_analysis

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
    
    # Ollama测试接口
    path('test-ollama/', test_ollama.test_ollama_connection, name='test_ollama'),
    path('ollama-models/', test_ollama.get_ollama_models, name='ollama_models'),
    
    # 数据分析增强接口
    path('analysis/pollution-trace/', enhanced_analysis.pollution_trace_analysis, name='pollution_trace'),
    path('analysis/water-quality-prediction/', enhanced_analysis.water_quality_prediction, name='water_quality_prediction'),
    path('analysis/comprehensive/', enhanced_analysis.comprehensive_analysis, name='comprehensive_analysis'),
    path('analysis/capabilities/', enhanced_analysis.get_analysis_capabilities, name='analysis_capabilities'),
    
    # 对话历史管理
    path('history/', views.chat_history, name='chat_history'),
    path('history/clear/', views.clear_chat_history, name='clear_chat_history'),
]
