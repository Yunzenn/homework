"""
AI Agent配置管理
"""

import os
from typing import Dict, Any
from django.conf import settings
from .core.model_interface import ModelType, ModelConfig

class AIConfig:
    """AI配置管理类"""
    
    @staticmethod
    def get_model_configs() -> Dict[str, ModelConfig]:
        """获取所有模型配置"""
        configs = {}
        
        # 本地LLM配置
        configs['local'] = ModelConfig(
            model_type=ModelType.LOCAL_LLM,
            api_url=getattr(settings, 'AI_LOCAL_URL', 'http://localhost:8000/v1'),
            model_name=getattr(settings, 'AI_LOCAL_MODEL', 'local-model'),
            temperature=getattr(settings, 'AI_TEMPERATURE', 0.7),
            max_tokens=getattr(settings, 'AI_MAX_TOKENS', 2000),
            timeout=getattr(settings, 'AI_TIMEOUT', 30)
        )
        
        # OpenAI配置
        openai_key = getattr(settings, 'OPENAI_API_KEY', os.getenv('OPENAI_API_KEY'))
        if openai_key:
            configs['openai'] = ModelConfig(
                model_type=ModelType.OPENAI_API,
                api_key=openai_key,
                api_url=getattr(settings, 'OPENAI_API_URL', 'https://api.openai.com/v1'),
                model_name=getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo'),
                temperature=getattr(settings, 'AI_TEMPERATURE', 0.7),
                max_tokens=getattr(settings, 'AI_MAX_TOKENS', 2000),
                timeout=getattr(settings, 'AI_TIMEOUT', 30)
            )
        
        # Claude配置
        claude_key = getattr(settings, 'CLAUDE_API_KEY', os.getenv('CLAUDE_API_KEY'))
        if claude_key:
            configs['claude'] = ModelConfig(
                model_type=ModelType.CLAUDE_API,
                api_key=claude_key,
                api_url=getattr(settings, 'CLAUDE_API_URL', 'https://api.anthropic.com/v1'),
                model_name=getattr(settings, 'CLAUDE_MODEL', 'claude-3-sonnet-20240229'),
                temperature=getattr(settings, 'AI_TEMPERATURE', 0.7),
                max_tokens=getattr(settings, 'AI_MAX_TOKENS', 2000),
                timeout=getattr(settings, 'AI_TIMEOUT', 30)
            )
        
        # Gemini配置
        gemini_key = getattr(settings, 'GEMINI_API_KEY', os.getenv('GEMINI_API_KEY'))
        if gemini_key:
            configs['gemini'] = ModelConfig(
                model_type=ModelType.GEMINI_API,
                api_key=gemini_key,
                api_url=getattr(settings, 'GEMINI_API_URL', 'https://generativelanguage.googleapis.com/v1beta'),
                model_name=getattr(settings, 'GEMINI_MODEL', 'gemini-pro'),
                temperature=getattr(settings, 'AI_TEMPERATURE', 0.7),
                max_tokens=getattr(settings, 'AI_MAX_TOKENS', 2000),
                timeout=getattr(settings, 'AI_TIMEOUT', 30)
            )
        
        # 自定义API配置
        custom_url = getattr(settings, 'AI_CUSTOM_API_URL', os.getenv('AI_CUSTOM_API_URL'))
        if custom_url:
            configs['custom'] = ModelConfig(
                model_type=ModelType.CUSTOM_API,
                api_url=custom_url,
                api_key=getattr(settings, 'AI_CUSTOM_API_KEY', os.getenv('AI_CUSTOM_API_KEY')),
                model_name=getattr(settings, 'AI_CUSTOM_MODEL', 'custom-model'),
                temperature=getattr(settings, 'AI_TEMPERATURE', 0.7),
                max_tokens=getattr(settings, 'AI_MAX_TOKENS', 2000),
                timeout=getattr(settings, 'AI_TIMEOUT', 30),
                custom_headers=getattr(settings, 'AI_CUSTOM_HEADERS', {})
            )
        
        return configs
    
    @staticmethod
    def get_primary_config() -> ModelConfig:
        """获取主配置"""
        configs = AIConfig.get_model_configs()
        
        # 优先级顺序
        priority = ['openai', 'claude', 'gemini', 'local', 'custom']
        
        for model_name in priority:
            if model_name in configs:
                return configs[model_name]
        
        # 如果都没有，返回默认本地配置
        return configs.get('local', ModelConfig(model_type=ModelType.LOCAL_LLM))
    
    @staticmethod
    def get_fallback_configs() -> list:
        """获取降级配置列表"""
        configs = AIConfig.get_model_configs()
        primary = AIConfig.get_primary_config()
        
        fallbacks = []
        for name, config in configs.items():
            if config != primary:
                fallbacks.append(config)
        
        return fallbacks
    
    @staticmethod
    def get_agent_config(agent_type: str) -> Dict[str, Any]:
        """获取特定Agent的配置"""
        base_config = {
            'enable_fallback': getattr(settings, 'AI_ENABLE_FALLBACK', True),
            'max_retries': getattr(settings, 'AI_MAX_RETRIES', 3),
            'cache_results': getattr(settings, 'AI_CACHE_RESULTS', True),
            'cache_timeout': getattr(settings, 'AI_CACHE_TIMEOUT', 300),  # 5分钟
        }
        
        # 特定Agent的配置
        agent_configs = {
            'data_query': {
                **base_config,
                'max_results': getattr(settings, 'DATA_QUERY_MAX_RESULTS', 100),
                'enable_suggestions': getattr(settings, 'DATA_QUERY_ENABLE_SUGGESTIONS', True),
            },
            'analysis': {
                **base_config,
                'analysis_depth': getattr(settings, 'ANALYSIS_DEPTH', 'standard'),  # basic, standard, deep
                'include_visualization': getattr(settings, 'ANALYSIS_INCLUDE_VIZ', True),
            },
            'prediction': {
                **base_config,
                'prediction_days': getattr(settings, 'PREDICTION_DAYS', 7),
                'confidence_threshold': getattr(settings, 'PREDICTION_CONFIDENCE_THRESHOLD', 0.7),
            },
            'anomaly_detection': {
                **base_config,
                'anomaly_threshold': getattr(settings, 'ANOMALY_THRESHOLD', 2.0),  # 标准差倍数
                'min_data_points': getattr(settings, 'ANOMALY_MIN_DATA_POINTS', 10),
            },
            'report_generation': {
                **base_config,
                'report_format': getattr(settings, 'REPORT_FORMAT', 'json'),  # json, markdown, html
                'include_charts': getattr(settings, 'REPORT_INCLUDE_CHARTS', True),
            },
            'advisory': {
                **base_config,
                'risk_level': getattr(settings, 'ADVISORY_RISK_LEVEL', 'medium'),  # low, medium, high
                'actionable_only': getattr(settings, 'ADVISORY_ACTIONABLE_ONLY', False),
            }
        }
        
        return agent_configs.get(agent_type, base_config)

# 环境变量配置示例
ENVIRONMENT_CONFIG_EXAMPLE = """
# AI配置环境变量示例

# 本地LLM配置
AI_LOCAL_URL=http://localhost:8000/v1
AI_LOCAL_MODEL=local-model

# OpenAI配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo

# Claude配置
CLAUDE_API_KEY=your_claude_api_key
CLAUDE_MODEL=claude-3-sonnet-20240229

# Gemini配置
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-pro

# 自定义API配置
AI_CUSTOM_API_URL=http://your-custom-api.com/v1
AI_CUSTOM_API_KEY=your_custom_api_key
AI_CUSTOM_MODEL=your-model-name

# 通用AI配置
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2000
AI_TIMEOUT=30
AI_ENABLE_FALLBACK=true
AI_MAX_RETRIES=3
AI_CACHE_RESULTS=true
AI_CACHE_TIMEOUT=300

# Agent特定配置
DATA_QUERY_MAX_RESULTS=100
DATA_QUERY_ENABLE_SUGGESTIONS=true
ANALYSIS_DEPTH=standard
PREDICTION_DAYS=7
ANOMALY_THRESHOLD=2.0
REPORT_FORMAT=json
ADVISORY_RISK_LEVEL=medium
"""
