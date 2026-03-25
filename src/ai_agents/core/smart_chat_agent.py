"""
智能对话Agent - 重构增强版
集成数据库查询工具，能够理解自然语言并查询数据库
"""

import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from django.db.models import Avg, Max, Min, Count, Q
from django.utils import timezone
from asgiref.sync import sync_to_async
import pandas as pd
import numpy as np
from .model_interface import BaseModelInterface, ModelConfig
from .db_tools import DatabaseQueryTools, format_water_quality_data, check_water_quality_standard

logger = logging.getLogger(__name__)


class SmartChatAgent:
    """智能对话Agent - 重构增强版"""
    
    def __init__(self, model_interface: BaseModelInterface):
        self.model = model_interface
        self.db_tools = DatabaseQueryTools()
        
    async def process_query(self, message: str, context: Dict = None) -> Dict[str, Any]:
        """
        处理用户查询
        
        Args:
            message: 用户消息
            context: 上下文信息
        
        Returns:
            处理结果
        """
        try:
            # 意图追踪
            logger.info(f"Incoming message: {message}")
            print(f"DEBUG: SmartChatAgent.process_query 收到消息: {message}")
            
            # 1. 分析用户意图
            intent = await self._analyze_intent(message)
            print(f"DEBUG: 分析到的意图: {intent['type']}")
            logger.info(f"Analyzed intent: {intent['type']} - {intent.get('matched_text', '')}")
            
            # 2. 根据意图执行相应操作
            if intent['type'] == 'data_query':
                print("DEBUG: 进入 data_query 处理流程")
                result = await self._handle_data_query(message, intent)
            elif intent['type'] == 'analysis':
                result = await self._handle_analysis_query(message, intent)
            elif intent['type'] == 'health_check':
                result = await self._handle_health_check_query(message, intent)
            elif intent['type'] == 'maintenance':
                result = await self._handle_maintenance_query(message, intent)
            elif intent['type'] == 'comparison':
                result = await self._handle_comparison_query(message, intent)
            elif intent['type'] == 'equipment_query':
                result = await self._handle_equipment_query(message, intent)
            elif intent['type'] == 'alert_query':
                result = await self._handle_alert_query(message, intent)
            elif intent['type'] == 'statistics':
                result = await self._handle_statistics_query(message, intent)
            elif intent['type'] == 'monitoring_point':
                result = await self._handle_monitoring_point_query(message, intent)
            elif intent['type'] == 'trend':
                result = await self._handle_trend_query(message, intent)
            else:
                print("DEBUG: 进入 general 处理流程")
                # 通用对话
                result = await self._handle_general_chat(message, context)
            
            print(f"DEBUG: 处理结果类型: {result.get('type', 'unknown')}")
            
            # 统一返回校验
            if not result.get('message'):
                logger.warning("AI backend returned empty message, using fallback")
                result['message'] = "Error: AI backend returned empty string"
            
            logger.info(f"Final result type: {result.get('type', 'unknown')}, message length: {len(result.get('message', ''))}")
            
            return {
                'success': True,
                'type': intent['type'],
                'data': result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"处理查询失败: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': f'处理查询时发生错误: {str(e)}',
                'type': 'error'
            }
    
    async def _analyze_intent(self, message: str) -> Dict[str, Any]:
        """分析用户意图 - 重构增强版"""
        
        # 意图关键词映射 - 扩展版
        intent_patterns = {
            'data_query': [
                r'查询.*水质', r'获取.*数据', r'显示.*记录', r'看看.*数据',
                r'.*水质.*怎么样', r'.*监测点.*数据', r'.*指标.*值',
                r'找.*水质.*数据', r'查找.*水质', r'搜索.*水质', r'水质.*数据',
                r'找.*水质', r'.*水质.*数据', r'杭州.*水质', r'水质.*杭州'
            ],
            'analysis': [
                r'分析.*趋势', r'比较.*数据', r'统计.*分析', r'数据.*分析',
                r'水质.*分析', r'变化.*趋势'
            ],
            'health_check': [
                # 健康度查询
                r'水质.*稳吗', r'水质.*达标吗', r'有没有好转', r'水质.*健康',
                r'水质.*正常', r'水质.*状况', r'水质.*状态'
            ],
            'maintenance': [
                # 运维意图
                r'清洗', r'校准', r'离线', r'维护', r'维修', r'保养',
                r'设备.*清洗', r'传感器.*校准', r'设备.*离线', r'维护.*记录'
            ],
            'comparison': [
                # 对比意图
                r'比一下', r'对比', r'区别', r'比较.*差异', r'差异.*对比',
                r'A.*对比.*B', r'哪个.*更好', r'有什么区别'
            ],
            'equipment_query': [
                # 设备/运维查询
                r'传感器.*在线吗', r'什么时候.*清洗', r'设备.*坏了没',
                r'传感器.*状态', r'设备.*状态', r'运维.*情况', r'设备.*维护',
                r'清洗.*记录', r'维护.*记录'
            ],
            'alert_query': [
                r'报警', r'异常', r'超标', r'警告', r'警报',
                r'.*异常.*数据', r'.*超标.*记录'
            ],
            'statistics': [
                r'统计', r'汇总', r'总数', r'平均', r'最大', r'最小',
                r'数据.*统计', r'汇总.*报告'
            ],
            'monitoring_point': [
                r'监测点', r'监控点', r'测点', r'站点',
                r'有哪些.*监测点', r'监测点.*信息'
            ],
            'trend': [
                r'趋势', r'变化', r'走势', r'发展',
                r'.*趋势.*分析', r'.*变化.*情况'
            ]
        }
        
        message_lower = message.lower()
        
        # 匹配意图 - 增加日志记录
        for intent_type, patterns in intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, message_lower)
                if match:
                    logger.info(f"意图匹配成功: {intent_type}, 模式: {pattern}, 消息: {message}")
                    return {
                        'type': intent_type,
                        'confidence': 0.8,
                        'message': message,
                        'matched_pattern': pattern,
                        'matched_text': match.group()
                    }
        
        # 默认为通用对话
        logger.info(f"未匹配到具体意图，使用通用对话: {message}")
        return {
            'type': 'general',
            'confidence': 0.5,
            'message': message
        }
    
    def _extract_query_conditions(self, message: str) -> Dict[str, Any]:
        """从消息中提取查询条件 - 重构版"""
        conditions = {}
        
        try:
            # 提取监测点ID - 重构版
            point_ids = self._extract_point_ids(message)
            if point_ids:
                conditions['point_ids'] = point_ids
            
            # 提取地理位置关键词
            location = self._extract_location(message)
            if location:
                conditions['location'] = location
            
            # 提取时间范围 - 增强版
            date_range = self._extract_date_range(message)
            if date_range:
                conditions.update(date_range)
            
            # 提取指标 - 增强版
            indicators = self._extract_indicators(message)
            if indicators:
                conditions['indicators'] = indicators
            
            # 提取限制条数
            limit = self._extract_limit(message)
            if limit:
                conditions['limit'] = limit
            
            logger.info(f"提取的查询条件: {conditions}")
            return conditions
            
        except Exception as e:
            logger.error(f"查询条件提取失败: {str(e)}")
            return conditions
    
    def _extract_point_ids(self, message: str) -> Optional[List[str]]:
        """提取监测点ID - 重构版，支持复杂格式"""
        point_ids = []
        
        # 动态匹配监测点ID模式 - 增强版
        patterns = [
            r'P-\d+',  # P-042
            r'监测点\d+',  # 监测点001
            r'MP\d+',  # MP001
            r'[A-Z]{2,}\d{3,}',  # HZ001, TEST001等 (至少2个字母+3个数字)
            r'[a-z]+\d+',  # p1, p2等
            r'[A-Z]\d+-\d+',  # A1-01, B2-03等
            r'[A-Z]{2,}_\d{3,}',  # SITE_002, LOC_001等
            r'[A-Z]{2,}-\d{3,}',  # SITE-002, LOC-001等
            r'\w+-\d+-\d+',  # 其他复杂格式
        ]
        
        for pattern in patterns:
            try:
                matches = re.findall(pattern, message, re.IGNORECASE)
                point_ids.extend(matches)
            except re.error as e:
                logger.warning(f"正则模式匹配失败 {pattern}: {e}")
        
        # 去重并返回
        return list(set(point_ids)) if point_ids else None
    
    def _extract_location(self, message: str) -> Optional[str]:
        """提取地理位置关键词"""
        # 常见地理位置关键词
        location_keywords = ['杭州', '西湖', '钱塘江', '北京', '上海', '广州', '深圳', '天津', '重庆', 
                           '成都', '武汉', '西安', '南京', '苏州', '青岛', '大连', '厦门', '宁波', '无锡']
        
        for location in location_keywords:
            if location in message:
                return location
        
        return None
    
    def _extract_indicators(self, message: str) -> Optional[List[str]]:
        """提取水质指标 - 增强版"""
        indicator_mapping = {
            # 原有指标
            'ph': 'ph',
            'ph值': 'ph',
            '余氯': 'chlorine',
            '氯': 'chlorine',
            '电导率': 'conductivity',
            'orp': 'orp',
            '氧化还原': 'orp',
            '浊度': 'turbidity',
            '浑浊度': 'turbidity',
            
            # 新增指标 - 完整版
            '氨氮': 'ammonia_nitrogen',
            'nh3-n': 'ammonia_nitrogen',
            'nh3n': 'ammonia_nitrogen',
            '总磷': 'total_phosphorus',
            'tp': 'total_phosphorus',
            '总氮': 'total_nitrogen',
            'tn': 'total_nitrogen',
            'cod': 'cod',
            '化学需氧量': 'cod',
            '耗氧量': 'cod',
            '高锰酸盐指数': 'permanganate_index',
            '溶解氧': 'dissolved_oxygen',
            'do': 'dissolved_oxygen',
            '含氧量': 'dissolved_oxygen',
            '生化需氧量': 'bod',
            'bod': 'bod',
            '电导率': 'conductivity',
            '电导': 'conductivity'
        }
        
        indicators = []
        message_lower = message.lower()
        
        for keyword, field in indicator_mapping.items():
            if keyword in message_lower:
                indicators.append(field)
        
        # 去重并返回
        return list(set(indicators)) if indicators else None
    
    def _extract_date_range(self, message: str) -> Dict[str, Any]:
        """提取日期范围 - 增强版"""
        today = datetime.now().date()
        
        # 时间关键词映射 - 扩展版
        time_mapping = {
            '今天': today,
            '昨天': today - timedelta(days=1),
            '前天': today - timedelta(days=2),
            '大前天': today - timedelta(days=3),
            '最近7天': today - timedelta(days=7),
            '最近一周': today - timedelta(days=7),
            '最近30天': today - timedelta(days=30),
            '最近一月': today - timedelta(days=30),
            '本周': today - timedelta(days=today.weekday()),
            '本月': today.replace(day=1),
            '上周': today - timedelta(days=7 + today.weekday()),
            '上个月': (today.replace(day=1) - timedelta(days=1)).replace(day=1),
            '上个礼拜': today - timedelta(days=7),
            '前阵子': today - timedelta(days=14),
        }
        
        # 支持小时级别查询
        hour_mapping = {
            '最近1小时': today - timedelta(hours=1),
            '最近2小时': today - timedelta(hours=2),
            '最近6小时': today - timedelta(hours=6),
            '最近12小时': today - timedelta(hours=12),
            '最近24小时': today - timedelta(hours=24),
        }
        
        # 检查时间关键词
        all_time_mapping = {**time_mapping, **hour_mapping}
        for keyword, date in all_time_mapping.items():
            if keyword in message:
                if keyword in ['今天', '昨天', '前天', '大前天']:
                    return {
                        'start_date': date.strftime('%Y-%m-%d'),
                        'end_date': date.strftime('%Y-%m-%d')
                    }
                elif '小时' in keyword:
                    return {
                        'start_date': date.strftime('%Y-%m-%d'),
                        'start_time': (datetime.now() - timedelta(hours=int(keyword.split('最近')[1].split('小时')[0]))).strftime('%H:%M:%S'),
                        'end_date': today.strftime('%Y-%m-%d'),
                        'end_time': datetime.now().strftime('%H:%M:%S')
                    }
                else:
                    return {
                        'start_date': date.strftime('%Y-%m-%d'),
                        'end_date': today.strftime('%Y-%m-%d')
                    }
        
        # 匹配具体日期格式 - 支持多种分隔符
        date_patterns = [
            r'(\d{4}-\d{1,2}-\d{1,2})',  # 2023-10-01
            r'(\d{4}/\d{1,2}/\d{1,2})',  # 2023/10/01
            r'(\d{4}\.\d{1,2}\.\d{1,2})', # 2023.10.01
            r'(\d{1,2}-\d{1,2}-\d{4})',  # 01-10-2023
        ]
        
        for pattern in date_patterns:
            try:
                dates = re.findall(pattern, message)
                if dates:
                    # 标准化日期格式
                    normalized_dates = []
                    for date_str in dates:
                        if '/' in date_str or '.' in date_str:
                            date_str = date_str.replace('/', '-').replace('.', '-')
                        if len(date_str.split('-')[0]) == 2:  # MM-DD-YYYY -> YYYY-MM-DD
                            parts = date_str.split('-')
                            date_str = f"{parts[2]}-{parts[0]}-{parts[1]}"
                        normalized_dates.append(date_str)
                    
                    if len(normalized_dates) == 1:
                        return {
                            'start_date': normalized_dates[0],
                            'end_date': normalized_dates[0]
                        }
                    elif len(normalized_dates) == 2:
                        return {
                            'start_date': normalized_dates[0],
                            'end_date': normalized_dates[1]
                        }
            except re.error as e:
                logger.warning(f"日期模式匹配失败 {pattern}: {e}")
        
        return None
    
    def _extract_limit(self, message: str) -> Optional[int]:
        """提取限制条数"""
        match = re.search(r'限制(\d+)|只显示(\d+)|前(\d+)条', message)
        if match:
            for group in match.groups():
                if group:
                    return int(group)
        return None
    
    # 处理方法保持原有结构，但增加新的处理方法
    async def _handle_maintenance_query(self, message: str, intent: Dict) -> Dict[str, Any]:
        """处理运维查询"""
        try:
            return {
                'message': '设备运维查询功能正在开发中。您可以查询传感器清洗记录、校准状态、设备离线时间等信息。',
                'type': 'maintenance'
            }
        except Exception as e:
            import traceback
            logger.error(f"Maintenance query error: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {
                'message': f'运维查询时发生错误: {str(e)}',
                'type': 'maintenance'
            }
    
    async def _handle_comparison_query(self, message: str, intent: Dict) -> Dict[str, Any]:
        """处理对比查询"""
        try:
            return {
                'message': '数据对比功能正在开发中。您可以对比不同监测点、不同时间段的水质指标差异。',
                'type': 'comparison'
            }
        except Exception as e:
            import traceback
            logger.error(f"Comparison query error: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {
                'message': f'对比查询时发生错误: {str(e)}',
                'type': 'comparison'
            }
    
    async def _handle_health_check_query(self, message: str, intent: Dict) -> Dict[str, Any]:
        """处理健康度查询"""
        try:
            return {
                'message': '水质健康度评估功能正在开发中，请稍后重试。',
                'type': 'health_check'
            }
        except Exception as e:
            import traceback
            logger.error(f"Health check query error: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {
                'message': f'健康度查询时发生错误: {str(e)}',
                'type': 'health_check'
            }
    
    async def _handle_equipment_query(self, message: str, intent: Dict) -> Dict[str, Any]:
        """处理设备运维查询"""
        try:
            return {
                'message': '设备运维查询功能正在开发中，请稍后重试。',
                'type': 'equipment_query'
            }
        except Exception as e:
            import traceback
            logger.error(f"Equipment query error: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {
                'message': f'设备查询时发生错误: {str(e)}',
                'type': 'equipment_query'
            }
    
    # 其他处理方法的占位符
    async def _handle_analysis_query(self, message: str, intent: Dict) -> Dict[str, Any]:
        try:
            return await self._handle_general_chat(message)
        except Exception as e:
            import traceback
            logger.error(f"Analysis query error: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {
                'message': f'分析查询时发生错误: {str(e)}',
                'type': 'analysis'
            }
    
    async def _handle_alert_query(self, message: str, intent: Dict) -> Dict[str, Any]:
        try:
            return await self._handle_general_chat(message)
        except Exception as e:
            import traceback
            logger.error(f"Alert query error: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {
                'message': f'报警查询时发生错误: {str(e)}',
                'type': 'alert_query'
            }
    
    async def _handle_statistics_query(self, message: str, intent: Dict) -> Dict[str, Any]:
        try:
            return await self._handle_general_chat(message)
        except Exception as e:
            import traceback
            logger.error(f"Statistics query error: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {
                'message': f'统计查询时发生错误: {str(e)}',
                'type': 'statistics'
            }
    
    async def _handle_monitoring_point_query(self, message: str, intent: Dict) -> Dict[str, Any]:
        try:
            return await self._handle_general_chat(message)
        except Exception as e:
            import traceback
            logger.error(f"Monitoring point query error: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {
                'message': f'监测点查询时发生错误: {str(e)}',
                'type': 'monitoring_point'
            }
    
    async def _handle_trend_query(self, message: str, intent: Dict) -> Dict[str, Any]:
        try:
            return await self._handle_general_chat(message)
        except Exception as e:
            import traceback
            logger.error(f"Trend query error: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {
                'message': f'趋势查询时发生错误: {str(e)}',
                'type': 'trend'
            }
    
    async def _handle_data_query(self, message: str, intent: Dict) -> Dict[str, Any]:
        """处理数据查询"""
        
        try:
            # 提取查询条件
            conditions = self._extract_query_conditions(message)
            print(f"DEBUG: 提取的查询条件: {conditions}")
            logger.info(f"Extracted conditions: {conditions}")
            
            # 使用sync_to_async包装数据库查询
            get_data = sync_to_async(self.db_tools.get_water_quality_data)
            
            # 查询数据库
            data = await get_data(
                point_ids=conditions.get('point_ids'),
                start_date=conditions.get('start_date'),
                end_date=conditions.get('end_date'),
                indicators=conditions.get('indicators'),
                limit=conditions.get('limit', 20)
            )
            print(f"DEBUG: 查询到的数据条数: {len(data) if data else 0}")
            logger.info(f"Database query returned {len(data) if data else 0} records")
            
            if not data:
                return {
                    'message': '没有找到符合条件的数据',
                    'conditions': conditions,
                    'data': []
                }
            
            # 格式化数据
            formatted_data = format_water_quality_data(data, conditions.get('indicators'))
            
            # 生成AI回复
            ai_response = await self._generate_data_response(message, data, conditions)
            
            return {
                'message': ai_response,
                'conditions': conditions,
                'data': data,
                'formatted_data': formatted_data,
                'count': len(data)
            }
        except Exception as e:
            print(f"DEBUG: 数据查询错误: {str(e)}")
            import traceback
            logger.error(f"Data query error: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {
                'message': f'数据查询时发生错误: {str(e)}',
                'conditions': conditions if 'conditions' in locals() else {},
                'data': []
            }
    
    async def _generate_data_response(self, message: str, data: List[Dict], conditions: Dict) -> str:
        """生成数据查询回复 - 优化版"""
        
        data_summary = f"找到 {len(data)} 条记录"
        if conditions.get('point_ids'):
            data_summary += f"，监测点：{', '.join(conditions['point_ids'])}"
        
        system_prompt = """# Role: 水质检测系统 AI 数据分析专家

## Profile
你是一款集成在水质监测系统中的高级数据分析助手。你擅长将枯燥的传感器数据转化为易于理解的洞察，并能针对水质参数（pH、浊度、溶解氧、电导率等）提供专业、科学的解释。

## Output Guidelines (Strict)
- **语言风格**：专业、严谨但不过于晦涩。使用 Markdown 格式输出以确保前端展示美观。
- **结构要求**：
  - 如果是数据分析：[状态概览] -> [详细指标评估] -> [优化/处理建议]。
  - 如果是普通问答：直接给出结论 -> 补充背景知识。
- **约束条件**：
  - 若数据缺失或超出分析范围，请诚实告知。
  - 避免生成误导性的结论，对敏感指标波动需提示"以实验室复检为准"。
  - 输出内容应保持简洁，适配前端显示空间。

请基于以下水质数据，按照[状态概览] -> [详细指标评估] -> [优化/处理建议]的结构进行专业分析。"""

        # 限制数据样本数量，减少prompt长度
        sample_size = min(3, len(data))
        
        prompt = f"""用户查询：{message}

查询结果：{data_summary}

数据样本（前{sample_size}条）：
{format_water_quality_data(data[:sample_size], conditions.get('indicators'))}

请基于以上数据，用专业的水质检测专家角度进行分析回答。要求：
1. 按照[状态概览] -> [详细指标评估] -> [优化/处理建议]的结构
2. 突出关键数据和异常值
3. 参考GB 3838-2002等水质标准进行评估
4. 使用Markdown格式输出
5. 保持专业严谨但易懂的语言风格
6. 回复控制在500字以内，确保响应速度"""
        
        try:
            # 模型输入输出监控
            logger.info(f"Data analysis model input (first 100 chars): {prompt[:100]}")
            
            # 减少max_tokens以提高响应速度
            response = await self.model.generate_text(prompt, {
                'system_prompt': system_prompt,
                'context_data': conditions,
                'max_tokens': 800  # 限制token数量
            })
            
            # 监控模型输出
            logger.info(f"Data analysis model response (first 100 chars): {response[:100]}")
            
            return response
        except Exception as e:
            import traceback
            logger.error(f"Data response generation error: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return f"数据分析生成失败: {str(e)}"
    
    # 其他处理方法的占位符
    async def _handle_analysis_query(self, message: str, intent: Dict) -> Dict[str, Any]:
        return await self._handle_general_chat(message)
    
    async def _handle_alert_query(self, message: str, intent: Dict) -> Dict[str, Any]:
        return await self._handle_general_chat(message)
    
    async def _handle_statistics_query(self, message: str, intent: Dict) -> Dict[str, Any]:
        return await self._handle_general_chat(message)
    
    async def _handle_monitoring_point_query(self, message: str, intent: Dict) -> Dict[str, Any]:
        return await self._handle_general_chat(message)
    
    async def _handle_trend_query(self, message: str, intent: Dict) -> Dict[str, Any]:
        return await self._handle_general_chat(message)
    
    async def _handle_general_chat(self, message: str, context: Dict = None) -> Dict[str, Any]:
        """处理通用对话"""
        
        system_prompt = """# Role: 水质检测系统 AI 数据分析专家

## Profile
你是一款集成在水质监测系统中的高级数据分析助手。你擅长将枯燥的传感器数据转化为易于理解的洞察，并能针对水质参数（pH、浊度、溶解氧、电导率等）提供专业、科学的解释。

## Context & Data Source
- **数据来源**：你将接收到来自数据库的实时/历史水质 JSON 数据。
- **目标用户**：水厂管理员或环境监测人员。
- **运行环境**：集成于 web/移动端前端，通过 API 或本地 Ollama 驱动。

## Skills & Goals
1. **数据解读**：分析输入的数据，识别异常值（参考标准：GB 3838-2002 等相关水质标准）。
2. **通识问答**：回答用户关于水质指标含义、超标危害、处理流程等通用问题。
3. **趋势预测**：基于历史数据简述水质变化趋势。
4. **决策辅助**：在数据异常时，给出初步的排查建议或操作指引。

## Output Guidelines (Strict)
- **语言风格**：专业、严谨但不过于晦涩。使用 Markdown 格式输出以确保前端展示美观。
- **结构要求**：
  - 如果是数据分析：[状态概览] -> [详细指标评估] -> [优化/处理建议]。
  - 如果是普通问答：直接给出结论 -> 补充背景知识。
- **约束条件**：
  - 若数据缺失或超出分析范围，请诚实告知。
  - 避免生成误导性的结论，对敏感指标波动需提示"以实验室复检为准"。
  - 输出内容应保持简洁，适配前端显示空间。

请基于以上角色设定，专业地回答用户的水质相关问题。"""
        
        try:
            # 模型输入输出监控
            logger.info(f"Model input prompt (first 100 chars): {message[:100]}")
            
            response = await self.model.generate_text(message, {
                'system_prompt': system_prompt,
                'context_data': context or {}
            })
            
            # 监控模型输出
            logger.info(f"Model response (first 100 chars): {response[:100]}")
            
            return {
                'message': response,
                'type': 'general'
            }
            
        except Exception as e:
            import traceback
            logger.error(f"General chat error: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {
                'message': f'抱歉，我现在无法回答这个问题。错误：{str(e)}',
                'type': 'general'
            }
