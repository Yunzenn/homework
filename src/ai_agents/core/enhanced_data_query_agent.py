"""
增强的数据查询Agent
支持多种AI模型接入
"""

import json
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .enhanced_agent import EnhancedBaseAgent, AgentResponse
from .model_interface import ModelConfig, ModelType
from api.models import WaterQualityRecord

logger = logging.getLogger(__name__)

class EnhancedDataQueryAgent(EnhancedBaseAgent):
    """增强的数据查询Agent"""
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的水质监控数据分析助手。你的职责是：

1. 理解用户的自然语言查询需求
2. 将自然语言转换为具体的数据查询条件
3. 提供准确的数据查询结果
4. 对查询结果进行简要分析和总结

你能够处理的查询类型：
- 时间范围查询（最近7天、本月、本季度等）
- 地点查询（某个监测点、区域等）
- 水质指标查询（pH值、溶解氧、浊度等）
- 数值范围查询（大于、小于、等于某个值）
- 组合查询（多个条件组合）

请始终以JSON格式返回查询结果，包含以下字段：
- query_type: 查询类型
- conditions: 查询条件
- results: 查询结果数据
- summary: 结果摘要
- suggestions: 相关建议
"""

    def _get_response_schema(self) -> Dict:
        """获取响应数据结构"""
        return {
            "type": "object",
            "properties": {
                "query_type": {"type": "string"},
                "conditions": {"type": "object"},
                "results": {"type": "array"},
                "summary": {"type": "string"},
                "suggestions": {"type": "array"}
            }
        }
    
    async def _prepare_context(self, parameters: Dict) -> Dict:
        """准备上下文数据"""
        context = {}
        
        # 获取数据库结构信息
        context['database_schema'] = {
            "table": "water_quality_record",
            "fields": {
                "id": "记录ID",
                "location": "监测地点",
                "ph_value": "pH值",
                "dissolved_oxygen": "溶解氧(mg/L)",
                "turbidity": "浊度(NTU)",
                "temperature": "温度(°C)",
                "conductivity": "电导率(μS/cm)",
                "ammonia_nitrogen": "氨氮(mg/L)",
                "total_phosphorus": "总磷(mg/L)",
                "record_time": "记录时间",
                "created_at": "创建时间"
            }
        }
        
        # 获取最近的样本数据
        try:
            recent_records = WaterQualityRecord.objects.all()[:5]
            context['sample_data'] = [
                {
                    "location": record.location,
                    "ph_value": record.ph_value,
                    "dissolved_oxygen": record.dissolved_oxygen,
                    "turbidity": record.turbidity,
                    "temperature": record.temperature,
                    "record_time": record.record_time.isoformat()
                }
                for record in recent_records
            ]
        except Exception as e:
            logger.error(f"获取样本数据失败: {str(e)}")
            context['sample_data'] = []
        
        # 获取统计信息
        try:
            total_count = WaterQualityRecord.objects.count()
            context['statistics'] = {
                "total_records": total_count,
                "locations": list(WaterQualityRecord.objects.values_list('location', flat=True).distinct())
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            context['statistics'] = {"total_records": 0, "locations": []}
        
        return context
    
    async def _execute_query(self, conditions: Dict) -> List[Dict]:
        """执行数据查询"""
        try:
            queryset = WaterQualityRecord.objects.all()
            
            # 应用查询条件
            if 'location' in conditions:
                queryset = queryset.filter(location__icontains=conditions['location'])
            
            if 'ph_min' in conditions:
                queryset = queryset.filter(ph_value__gte=conditions['ph_min'])
            
            if 'ph_max' in conditions:
                queryset = queryset.filter(ph_value__lte=conditions['ph_max'])
            
            if 'do_min' in conditions:
                queryset = queryset.filter(dissolved_oxygen__gte=conditions['do_min'])
            
            if 'do_max' in conditions:
                queryset = queryset.filter(dissolved_oxygen__lte=conditions['do_max'])
            
            if 'turbidity_max' in conditions:
                queryset = queryset.filter(turbidity__lte=conditions['turbidity_max'])
            
            # 时间范围查询
            if 'start_date' in conditions:
                queryset = queryset.filter(record_time__gte=conditions['start_date'])
            
            if 'end_date' in conditions:
                queryset = queryset.filter(record_time__lte=conditions['end_date'])
            
            # 最近时间查询
            if 'recent_days' in conditions:
                start_date = datetime.now() - timedelta(days=conditions['recent_days'])
                queryset = queryset.filter(record_time__gte=start_date)
            
            # 限制结果数量
            limit = conditions.get('limit', 100)
            queryset = queryset[:limit]
            
            # 转换为字典格式
            results = []
            for record in queryset:
                results.append({
                    "id": record.id,
                    "location": record.location,
                    "ph_value": float(record.ph_value) if record.ph_value else None,
                    "dissolved_oxygen": float(record.dissolved_oxygen) if record.dissolved_oxygen else None,
                    "turbidity": float(record.turbidity) if record.turbidity else None,
                    "temperature": float(record.temperature) if record.temperature else None,
                    "conductivity": float(record.conductivity) if record.conductivity else None,
                    "ammonia_nitrogen": float(record.ammonia_nitrogen) if record.ammonia_nitrogen else None,
                    "total_phosphorus": float(record.total_phosphorus) if record.total_phosphorus else None,
                    "record_time": record.record_time.isoformat() if record.record_time else None,
                    "created_at": record.created_at.isoformat() if record.created_at else None
                })
            
            return results
            
        except Exception as e:
            logger.error(f"执行查询失败: {str(e)}")
            return []
    
    async def _parse_response(self, response_text: str) -> Dict:
        """解析模型响应"""
        try:
            # 尝试解析JSON
            response_data = json.loads(response_text)
            
            # 如果包含查询条件，执行实际查询
            if 'conditions' in response_data:
                conditions = response_data['conditions']
                actual_results = await self._execute_query(conditions)
                
                # 更新响应数据中的结果
                response_data['results'] = actual_results
                
                # 生成结果摘要
                response_data['summary'] = self._generate_summary(actual_results, conditions)
                
                # 生成建议
                response_data['suggestions'] = self._generate_suggestions(actual_results, conditions)
            
            return response_data
            
        except json.JSONDecodeError:
            # 如果不是JSON格式，尝试解析自然语言
            return await self._parse_natural_language(response_text)
        except Exception as e:
            logger.error(f"解析响应失败: {str(e)}")
            return {
                "error": "响应解析失败",
                "raw_response": response_text,
                "error_details": str(e)
            }
    
    def _generate_summary(self, results: List[Dict], conditions: Dict) -> str:
        """生成结果摘要"""
        if not results:
            return "未找到符合条件的数据记录。"
        
        count = len(results)
        
        # 基本统计
        ph_values = [r['ph_value'] for r in results if r['ph_value']]
        do_values = [r['dissolved_oxygen'] for r in results if r['dissolved_oxygen']]
        turbidity_values = [r['turbidity'] for r in results if r['turbidity']]
        
        summary_parts = [f"找到{count}条记录"]
        
        if ph_values:
            avg_ph = sum(ph_values) / len(ph_values)
            summary_parts.append(f"平均pH值: {avg_ph:.2f}")
        
        if do_values:
            avg_do = sum(do_values) / len(do_values)
            summary_parts.append(f"平均溶解氧: {avg_do:.2f}mg/L")
        
        if turbidity_values:
            avg_turbidity = sum(turbidity_values) / len(turbidity_values)
            summary_parts.append(f"平均浊度: {avg_turbidity:.2f}NTU")
        
        # 地点信息
        locations = list(set(r['location'] for r in results if r['location']))
        if locations:
            summary_parts.append(f"监测点: {', '.join(locations[:3])}")
            if len(locations) > 3:
                summary_parts.append(f"等{len(locations)}个地点")
        
        return "，".join(summary_parts) + "。"
    
    def _generate_suggestions(self, results: List[Dict], conditions: Dict) -> List[str]:
        """生成建议"""
        suggestions = []
        
        if not results:
            suggestions.append("建议调整查询条件或检查数据是否存在。")
            return suggestions
        
        # 基于结果生成建议
        ph_values = [r['ph_value'] for r in results if r['ph_value']]
        do_values = [r['dissolved_oxygen'] for r in results if r['dissolved_oxygen]]
        turbidity_values = [r['turbidity'] for r in results if r['turbidity']]
        
        # pH值建议
        if ph_values:
            avg_ph = sum(ph_values) / len(ph_values)
            if avg_ph < 6.5:
                suggestions.append("pH值偏低，建议检查酸性物质来源。")
            elif avg_ph > 8.5:
                suggestions.append("pH值偏高，建议检查碱性物质来源。")
        
        # 溶解氧建议
        if do_values:
            avg_do = sum(do_values) / len(do_values)
            if avg_do < 5:
                suggestions.append("溶解氧偏低，可能影响水生生物，建议增氧。")
            elif avg_do > 10:
                suggestions.append("溶解氧较高，水体自净能力良好。")
        
        # 浊度建议
        if turbidity_values:
            avg_turbidity = sum(turbidity_values) / len(turbidity_values)
            if avg_turbidity > 5:
                suggestions.append("浊度偏高，建议检查悬浮物质来源。")
        
        # 数据量建议
        if len(results) < 10:
            suggestions.append("数据量较少，建议扩大查询范围或时间跨度。")
        elif len(results) >= 100:
            suggestions.append("数据量较大，建议添加更多筛选条件。")
        
        return suggestions
    
    async def _parse_natural_language(self, text: str) -> Dict:
        """解析自然语言查询"""
        # 简单的自然语言解析逻辑
        text_lower = text.lower()
        
        conditions = {}
        
        # 时间解析
        if '最近' in text_lower or '近期' in text_lower:
            if '7' in text_lower or '七' in text_lower:
                conditions['recent_days'] = 7
            elif '30' in text_lower or '三十' in text_lower or '月' in text_lower:
                conditions['recent_days'] = 30
            elif '90' in text_lower or '九十' in text_lower or '季度' in text_lower:
                conditions['recent_days'] = 90
        
        # 地点解析
        locations = ['监测点A', '监测点B', '监测点C', '东区', '西区', '南区', '北区']
        for location in locations:
            if location in text:
                conditions['location'] = location
                break
        
        # pH值解析
        if 'ph' in text_lower:
            if '大于' in text_lower or '高于' in text_lower:
                # 提取数值
                import re
                numbers = re.findall(r'\d+\.?\d*', text)
                if numbers:
                    conditions['ph_min'] = float(numbers[0])
            elif '小于' in text_lower or '低于' in text_lower:
                import re
                numbers = re.findall(r'\d+\.?\d*', text)
                if numbers:
                    conditions['ph_max'] = float(numbers[0])
        
        # 执行查询
        results = await self._execute_query(conditions)
        
        return {
            "query_type": "natural_language",
            "conditions": conditions,
            "results": results,
            "summary": self._generate_summary(results, conditions),
            "suggestions": self._generate_suggestions(results, conditions),
            "original_query": text
        }
