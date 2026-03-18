"""
数据分析增强API接口
提供污染溯源和水质预测的RESTful API
"""

import json
import asyncio
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..core.pollution_trace_agent import PollutionTraceAgent
from ..core.enhanced_prediction_agent import EnhancedPredictionAgent
from ..core.model_interface import ModelConfig, ModelType

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pollution_trace_analysis(request):
    """
    污染溯源分析接口
    
    POST /api/analysis/pollution-trace/
    {
        "target_location": "P-042",
        "analysis_type": "full",  # full, correlation_only, contribution_only
        "time_range": "7d",  # 7d, 30d, 90d
        "ai_config": {
            "modelType": "local",
            "localUrl": "http://localhost:11434/v1",
            "localModel": "qwen2.5-coder:7b"
        }
    }
    """
    try:
        data = json.loads(request.body)
        target_location = data.get('target_location', 'P-042')
        analysis_type = data.get('analysis_type', 'full')
        time_range = data.get('time_range', '7d')
        ai_config = data.get('ai_config', {})
        
        # 创建溯源分析Agent
        model_config = ModelConfig(
            model_type=ModelType.LOCAL_LLM if ai_config.get('modelType') == 'local' else ModelType.OPENAI_API,
            api_url=ai_config.get('localUrl', 'http://localhost:11434/v1'),
            model_name=ai_config.get('localModel', 'qwen2.5-coder:7b'),
            temperature=0.7,
            max_tokens=3000,
            timeout=60
        )
        
        agent = PollutionTraceAgent(model_config)
        
        # 准备分析参数
        parameters = {
            'target_location': target_location,
            'analysis_type': analysis_type,
            'time_range': time_range
        }
        
        # 执行溯源分析
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                agent.process_query("执行污染溯源分析", parameters)
            )
        finally:
            loop.close()
        
        return Response({
            'success': True,
            'data': result,
            'analysis_type': analysis_type,
            'target_location': target_location,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'溯源分析失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def water_quality_prediction(request):
    """
    水质预测分析接口
    
    POST /api/analysis/water-quality-prediction/
    {
        "target_location": "P-042",
        "prediction_hours": 48,
        "include_weather": true,
        "include_extreme_events": true,
        "ai_config": {
            "modelType": "local",
            "localUrl": "http://localhost:11434/v1",
            "localModel": "qwen2.5-coder:7b"
        }
    }
    """
    try:
        data = json.loads(request.body)
        target_location = data.get('target_location', 'P-042')
        prediction_hours = data.get('prediction_hours', 48)
        include_weather = data.get('include_weather', True)
        include_extreme_events = data.get('include_extreme_events', True)
        ai_config = data.get('ai_config', {})
        
        # 创建预测分析Agent
        model_config = ModelConfig(
            model_type=ModelType.LOCAL_LLM if ai_config.get('modelType') == 'local' else ModelType.OPENAI_API,
            api_url=ai_config.get('localUrl', 'http://localhost:11434/v1'),
            model_name=ai_config.get('localModel', 'qwen2.5-coder:7b'),
            temperature=0.7,
            max_tokens=3000,
            timeout=60
        )
        
        agent = EnhancedPredictionAgent(model_config)
        
        # 准备预测参数
        parameters = {
            'target_location': target_location,
            'prediction_hours': prediction_hours,
            'include_weather': include_weather,
            'include_extreme_events': include_extreme_events
        }
        
        # 执行预测分析
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                agent.process_query("执行水质预测分析", parameters)
            )
        finally:
            loop.close()
        
        return Response({
            'success': True,
            'data': result,
            'prediction_hours': prediction_hours,
            'target_location': target_location,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'预测分析失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comprehensive_analysis(request):
    """
    综合分析接口（溯源+预测）
    
    POST /api/analysis/comprehensive/
    {
        "target_location": "P-042",
        "include_trace": true,
        "include_prediction": true,
        "prediction_hours": 48,
        "ai_config": {
            "modelType": "local",
            "localUrl": "http://localhost:11434/v1",
            "localModel": "qwen2.5-coder:7b"
        }
    }
    """
    try:
        data = json.loads(request.body)
        target_location = data.get('target_location', 'P-042')
        include_trace = data.get('include_trace', True)
        include_prediction = data.get('include_prediction', True)
        prediction_hours = data.get('prediction_hours', 48)
        ai_config = data.get('ai_config', {})
        
        results = {}
        
        # 并行执行溯源和预测分析
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            tasks = []
            
            if include_trace:
                # 创建溯源Agent
                trace_model_config = ModelConfig(
                    model_type=ModelType.LOCAL_LLM if ai_config.get('modelType') == 'local' else ModelType.OPENAI_API,
                    api_url=ai_config.get('localUrl', 'http://localhost:11434/v1'),
                    model_name=ai_config.get('localModel', 'qwen2.5-coder:7b'),
                    temperature=0.7,
                    max_tokens=3000,
                    timeout=60
                )
                trace_agent = PollutionTraceAgent(trace_model_config)
                trace_task = trace_agent.process_query(
                    "执行污染溯源分析", 
                    {'target_location': target_location, 'analysis_type': 'full', 'time_range': '7d'}
                )
                tasks.append(('trace', trace_task))
            
            if include_prediction:
                # 创建预测Agent
                pred_model_config = ModelConfig(
                    model_type=ModelType.LOCAL_LLM if ai_config.get('modelType') == 'local' else ModelType.OPENAI_API,
                    api_url=ai_config.get('localUrl', 'http://localhost:11434/v1'),
                    model_name=ai_config.get('localModel', 'qwen2.5-coder:7b'),
                    temperature=0.7,
                    max_tokens=3000,
                    timeout=60
                )
                pred_agent = EnhancedPredictionAgent(pred_model_config)
                pred_task = pred_agent.process_query(
                    "执行水质预测分析",
                    {
                        'target_location': target_location,
                        'prediction_hours': prediction_hours,
                        'include_weather': True,
                        'include_extreme_events': True
                    }
                )
                tasks.append(('prediction', pred_task))
            
            # 执行所有任务
            task_results = loop.run_until_complete(asyncio.gather(*[task for _, task in tasks]))
            
            # 整理结果
            for i, (task_type, _) in enumerate(tasks):
                results[task_type] = task_results[i]
                
        finally:
            loop.close()
        
        # 生成综合分析报告
        comprehensive_report = generate_comprehensive_report(results, target_location)
        
        return Response({
            'success': True,
            'data': {
                'analysis_results': results,
                'comprehensive_report': comprehensive_report
            },
            'target_location': target_location,
            'analysis_components': list(results.keys()),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'综合分析失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_analysis_capabilities(request):
    """
    获取分析能力信息
    
    GET /api/analysis/capabilities/
    """
    try:
        capabilities = {
            'pollution_trace': {
                'description': '污染溯源分析',
                'features': [
                    '上下游关联分析',
                    '扩散模型模拟',
                    '贡献度分析',
                    '反向追溯'
                ],
                'supported_analysis_types': ['full', 'correlation_only', 'contribution_only'],
                'supported_time_ranges': ['7d', '30d', '90d'],
                'typical_processing_time': '30-60秒'
            },
            'water_quality_prediction': {
                'description': '水质预测分析',
                'features': [
                    '多因素预测',
                    '极端事件预警',
                    '影响范围预测',
                    '修复效果模拟'
                ],
                'supported_prediction_hours': [24, 48, 72],
                'supported_metrics': ['ph_value', 'dissolved_oxygen', 'turbidity', 'conductivity', 'ammonia_nitrogen'],
                'typical_processing_time': '45-90秒'
            },
            'comprehensive': {
                'description': '综合分析',
                'features': [
                    '污染溯源 + 水质预测',
                    '智能决策支持',
                    '综合风险评估',
                    '治理建议生成'
                ],
                'typical_processing_time': '60-120秒'
            }
        }
        
        return Response({
            'success': True,
            'data': capabilities,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'获取分析能力失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def generate_comprehensive_report(results: dict, target_location: str) -> dict:
    """生成综合分析报告"""
    try:
        report = {
            'executive_summary': {
                'location': target_location,
                'analysis_time': datetime.now().isoformat(),
                'overall_risk_level': 'medium',
                'key_findings': [],
                'recommendations': []
            },
            'pollution_trace_summary': {},
            'prediction_summary': {},
            'risk_assessment': {},
            'action_plan': []
        }
        
        # 处理溯源分析结果
        if 'trace' in results:
            trace_result = results['trace']
            if trace_result.get('success', False):
                trace_data = trace_result.get('data', {})
                
                report['pollution_trace_summary'] = {
                    'confidence_score': trace_data.get('confidence_score', 0),
                    'dominant_sources': [],
                    'upstream_correlations': len(trace_data.get('upstream_correlations', [])),
                    'trace_quality': 'good' if trace_data.get('confidence_score', 0) > 0.7 else 'medium'
                }
                
                # 提取主要污染源
                contributions = trace_data.get('contribution_analysis', {}).get('contributions', [])
                if contributions:
                    report['pollution_trace_summary']['dominant_sources'] = [
                        {
                            'name': contrib.get('name', '未知'),
                            'contribution': contrib.get('contribution_percentage', 0),
                            'type': contrib.get('type', 'unknown')
                        }
                        for contrib in contributions[:3]
                    ]
                
                # 添加关键发现
                if contributions and contributions[0].get('contribution_percentage', 0) > 40:
                    report['executive_summary']['key_findings'].append(
                        f"发现主要污染源：{contributions[0].get('name', '未知')}，贡献度{contributions[0].get('contribution_percentage', 0):.1f}%"
                    )
        
        # 处理预测分析结果
        if 'prediction' in results:
            pred_result = results['prediction']
            if pred_result.get('success', False):
                pred_data = pred_result.get('data', {})
                
                # 统计极端事件
                extreme_events = pred_data.get('extreme_events', [])
                red_events = [e for e in extreme_events if e.get('severity') == 'red']
                orange_events = [e for e in extreme_events if e.get('severity') == 'orange']
                
                report['prediction_summary'] = {
                    'prediction_hours': 48,
                    'extreme_events_count': len(extreme_events),
                    'critical_events_count': len(red_events),
                    'warning_events_count': len(orange_events),
                    'model_reliability': pred_data.get('model_performance', {}).get('model_reliability', 'medium')
                }
                
                # 评估整体风险等级
                if len(red_events) > 0:
                    report['executive_summary']['overall_risk_level'] = 'high'
                elif len(orange_events) > 2:
                    report['executive_summary']['overall_risk_level'] = 'medium'
                else:
                    report['executive_summary']['overall_risk_level'] = 'low'
                
                # 添加关键发现
                if len(red_events) > 0:
                    report['executive_summary']['key_findings'].append(
                        f"预测未来48小时内可能出现{len(red_events)}起严重超标事件"
                    )
                
                # 提取修复建议
                remediation = pred_data.get('remediation_effects', [])
                if remediation:
                    best_measure = max(remediation, key=lambda x: x.get('recommendation_score', 0))
                    report['action_plan'].append({
                        'measure': best_measure.get('measure_name', '未知措施'),
                        'priority': 'high',
                        'expected_improvement': best_measure.get('predicted_effects', {}),
                        'implementation_cost': best_measure.get('cost_analysis', {}).get('implementation_cost', 0),
                        'suitability': best_measure.get('suitability', 'medium')
                    })
        
        # 生成综合建议
        if report['executive_summary']['overall_risk_level'] == 'high':
            report['executive_summary']['recommendations'].extend([
                "立即启动应急预案",
                "加强监测频次至每小时一次",
                "通知相关部门和下游用户"
            ])
        elif report['executive_summary']['overall_risk_level'] == 'medium':
            report['executive_summary']['recommendations'].extend([
                "增加监测频次",
                "准备应急物资",
                "排查潜在污染源"
            ])
        else:
            report['executive_summary']['recommendations'].extend([
                "保持常规监测",
                "定期检查治理设施",
                "关注天气变化影响"
            ])
        
        return report
        
    except Exception as e:
        return {
            'error': f'报告生成失败: {str(e)}',
            'executive_summary': {'error': '报告生成失败'}
        }
