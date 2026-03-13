"""
AI Agent模块URL配置
"""

from django.urls import path, include

urlpatterns = [
    path('ai/', include('ai_agents.api.urls')),
]
