"""
AI Agent API视图
提供智能问答和分析接口
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import json
import asyncio
from datetime import datetime
import sys

from ..core.agent_manager import agent_manager
from ..core.data_query_agent import DataQueryAgent
from ..core.analysis_agent import AnalysisAgent
from ..core.advisory_agent import AdvisoryAgent
from ..core.prediction_agent import PredictionAgent
from ..core.anomaly_agent import AnomalyDetectionAgent
from ..core.report_agent import ReportGenerationAgent
from ..core.smart_chat_agent import SmartChatAgent
from ..core.model_interface import ModelConfig, ModelType

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_chat(request):
    """
    AI智能对话接口
    
    POST /api/ai/chat/
    {
        "message": "P-042今天水质怎么样？",
        "context": {
            "user_id": "user123",
            "session_id": "session456"
        },
        "ai_config": {
            "modelType": "local",
            "localUrl": "http://localhost:11434/v1",
            "localModel": "qwen2.5-coder:7b"
        }
    }
    """
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        context = data.get('context', {})
        ai_config = data.get('ai_config', {})
        
        if not message:
            return Response({
                'success': False,
                'error': '消息内容不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 异步处理AI查询
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 如果有用户配置，使用用户配置，否则使用默认配置
            if ai_config:
                model_type_key = ai_config.get('modelType', 'local')

                model_type_map = {
                    'local': ModelType.LOCAL_LLM,
                    'openai': ModelType.OPENAI_API,
                    'claude': ModelType.CLAUDE_API,
                    'custom': ModelType.OPENAI_API
                }

                model_name_map = {
                    'local': ai_config.get('localModel', 'qwen2.5-coder:7b'),
                    'openai': ai_config.get('openaiModel', 'gpt-3.5-turbo'),
                    'claude': ai_config.get('claudeModel', 'claude-3-sonnet-20240229'),
                    'custom': ai_config.get('customModel', 'custom-model')
                }

                api_url_map = {
                    'local': ai_config.get('localUrl', 'http://localhost:11434/v1'),
                    'openai': ai_config.get('openaiUrl', 'https://api.openai.com/v1'),
                    'claude': ai_config.get('claudeUrl', 'https://api.anthropic.com/v1'),
                    'custom': ai_config.get('customUrl', 'http://localhost:11434/v1')
                }

                api_key_map = {
                    'openai': ai_config.get('openaiApiKey'),
                    'claude': ai_config.get('claudeApiKey'),
                    'custom': ai_config.get('customApiKey')
                }

                custom_headers = None
                if model_type_key == 'custom' and api_key_map.get('custom'):
                    custom_headers = {
                        'Authorization': f"Bearer {api_key_map['custom']}"
                    }

                # 创建模型配置
                model_config = ModelConfig(
                    model_type=model_type_map.get(model_type_key, ModelType.LOCAL_LLM),
                    api_key=api_key_map.get(model_type_key),
                    api_url=api_url_map.get(model_type_key, 'http://localhost:11434/v1'),
                    model_name=model_name_map.get(model_type_key, 'qwen2.5-coder:7b'),
                    temperature=ai_config.get('temperature', 0.7),
                    max_tokens=ai_config.get('maxTokens', 2000),
                    timeout=120,  # 增加超时时间到120秒
                    custom_headers=custom_headers
                )
            else:
                # 使用默认配置
                model_config = ModelConfig(
                    model_type=ModelType.LOCAL_LLM,
                    api_url='http://localhost:11434/v1',
                    model_name='qwen2.5-coder:7b',
                    temperature=0.7,
                    max_tokens=2000,
                    timeout=120
                )
                model_type_key = 'local'
                
            # 创建模型接口
            if model_type_key in ['local', 'custom']:
                from ..core.model_interface import LocalLLMModel
                model_interface = LocalLLMModel(model_config)
            elif model_config.model_type == ModelType.CLAUDE_API:
                from ..core.model_interface import ClaudeModel
                model_interface = ClaudeModel(model_config)
            else:
                from ..core.model_interface import OpenAIModel
                model_interface = OpenAIModel(model_config)
            
            # 创建智能对话Agent并处理 - 始终使用重构的SmartChatAgent
            agent = SmartChatAgent(model_interface)
            result = loop.run_until_complete(
                agent.process_query(message, context)
            )
        finally:
            loop.close()
        
        # 记录对话历史
        _save_chat_history(request.user, message, result)
        
        return JsonResponse({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        }, json_dumps_params={'ensure_ascii': False}, status=status.HTTP_200_OK)
        
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'error': '无效的JSON格式'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': f'处理请求时发生错误: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def data_query(request):
    """
    数据查询接口
    
    POST /api/ai/query/
    {
        "query": "查询P-042今天的pH值",
        "parameters": {
            "point_id": "P-042",
            "indicators": ["ph"],
            "time_range": "today"
        }
    }
    """
    try:
        data = json.loads(request.body)
        query = data.get('query', '')
        parameters = data.get('parameters', {})
        
        agent = DataQueryAgent()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                agent.execute(query, parameters)
            )
        finally:
            loop.close()
        
        return Response({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analysis(request):
    """
    数据分析接口
    
    POST /api/ai/analysis/
    {
        "query": "分析P-042最近一周的水质趋势",
        "parameters": {}
    }
    """
    try:
        data = json.loads(request.body)
        query = data.get('query', '')
        parameters = data.get('parameters', {})
        
        agent = AnalysisAgent()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                agent.execute(query, parameters)
            )
        finally:
            loop.close()
        
        return Response({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def prediction(request):
    """
    趋势预测接口
    
    POST /api/ai/prediction/
    {
        "query": "预测P-042未来三天的pH值",
        "parameters": {}
    }
    """
    try:
        data = json.loads(request.body)
        query = data.get('query', '')
        parameters = data.get('parameters', {})
        
        agent = PredictionAgent()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                agent.execute(query, parameters)
            )
        finally:
            loop.close()
        
        return Response({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def anomaly_detection(request):
    """
    异常检测接口
    
    POST /api/ai/anomaly/
    {
        "query": "检测P-042今天的异常数据",
        "parameters": {}
    }
    """
    try:
        data = json.loads(request.body)
        query = data.get('query', '')
        parameters = data.get('parameters', {})
        
        agent = AnomalyDetectionAgent()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                agent.execute(query, parameters)
            )
        finally:
            loop.close()
        
        return Response({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def advisory(request):
    """
    建议生成接口
    
    POST /api/ai/advisory/
    {
        "query": "P-042pH值过高，应该怎么办？",
        "parameters": {
            "analysis_result": {...}
        }
    }
    """
    try:
        data = json.loads(request.body)
        query = data.get('query', '')
        parameters = data.get('parameters', {})
        
        agent = AdvisoryAgent()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                agent.execute(query, parameters)
            )
        finally:
            loop.close()
        
        return Response({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_generation(request):
    """
    报告生成接口
    
    POST /api/ai/report/
    {
        "query": "生成今天的水质监测日报",
        "parameters": {}
    }
    """
    try:
        data = json.loads(request.body)
        query = data.get('query', '')
        parameters = data.get('parameters', {})
        
        agent = ReportGenerationAgent()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                agent.execute(query, parameters)
            )
        finally:
            loop.close()
        
        return Response({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_history(request):
    """
    获取对话历史
    
    GET /api/ai/history/?user_id=user123&limit=10
    """
    try:
        user_id = request.GET.get('user_id', request.user.id)
        limit = int(request.GET.get('limit', 20))
        
        history = _get_chat_history(user_id, limit)
        
        return Response({
            'success': True,
            'data': history
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_chat_history(request):
    """
    清空对话历史
    
    DELETE /api/ai/history/?user_id=user123
    """
    try:
        user_id = request.GET.get('user_id', request.user.id)
        
        _clear_chat_history(user_id)
        
        return Response({
            'success': True,
            'message': '对话历史已清空'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def _save_chat_history(user, message, result):
    """保存对话历史"""
    # 这里可以实现具体的保存逻辑
    # 比如保存到数据库或文件
    pass

def _get_chat_history(user_id, limit):
    """获取对话历史"""
    # 这里可以实现具体的获取逻辑
    return []

def _clear_chat_history(user_id):
    """清空对话历史"""
    # 这里可以实现具体的清空逻辑
    pass
