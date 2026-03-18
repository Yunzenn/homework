"""
Ollama连接测试接口
用于诊断和修复本地模型调用问题
"""

import json
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_ollama_connection(request):
    """
    测试Ollama连接
    
    POST /api/ai/test-ollama/
    {
        "model": "qwen2.5-coder:7b",
        "prompt": "你好，请回复一个简单的问候"
    }
    """
    try:
        data = json.loads(request.body)
        model = data.get('model', 'qwen2.5-coder:7b')
        prompt = data.get('prompt', '你好，请回复一个简单的问候')
        
        # Ollama API端点
        ollama_url = 'http://localhost:11434/api/generate'
        
        # 请求数据
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 100
            }
        }
        
        # 发送请求
        response = requests.post(
            ollama_url,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return Response({
                'success': True,
                'data': {
                    'model': model,
                    'response': result.get('response', ''),
                    'done': result.get('done', False),
                    'total_duration': result.get('total_duration', 0),
                    'prompt_eval_count': result.get('prompt_eval_count', 0),
                    'eval_count': result.get('eval_count', 0)
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            return Response({
                'success': False,
                'error': f'Ollama API错误: {response.status_code}',
                'details': response.text
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except requests.exceptions.ConnectionError:
        return Response({
            'success': False,
            'error': '无法连接到Ollama服务',
            'details': '请确保Ollama服务正在运行 (http://localhost:11434)'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
    except requests.exceptions.Timeout:
        return Response({
            'success': False,
            'error': '请求超时',
            'details': 'Ollama服务响应时间过长'
        }, status=status.HTTP_408_REQUEST_TIMEOUT)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'测试失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ollama_models(request):
    """
    获取Ollama可用模型列表
    
    GET /api/ai/ollama-models/
    """
    try:
        # Ollama模型列表端点
        ollama_url = 'http://localhost:11434/api/tags'
        
        response = requests.get(ollama_url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            models = []
            
            for model in result.get('models', []):
                models.append({
                    'name': model.get('name', ''),
                    'size': model.get('size', 0),
                    'modified_at': model.get('modified_at', ''),
                    'digest': model.get('digest', '')[:12] + '...'  # 只显示前12位
                })
            
            return Response({
                'success': True,
                'data': {
                    'models': models,
                    'total_count': len(models)
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            return Response({
                'success': False,
                'error': f'获取模型列表失败: {response.status_code}',
                'details': response.text
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except requests.exceptions.ConnectionError:
        return Response({
            'success': False,
            'error': '无法连接到Ollama服务',
            'details': '请确保Ollama服务正在运行 (http://localhost:11434)'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'获取模型列表失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
