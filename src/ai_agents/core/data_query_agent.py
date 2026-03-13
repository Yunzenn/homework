"""
数据查询Agent
负责处理水质数据的查询和检索
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.db.models import Avg, Max, Min, Count
from api.models import WaterQualityRecord

class DataQueryAgent:
    """数据查询智能体"""
    
    def __init__(self):
        self.name = "数据查询Agent"
        self.description = "负责水质数据的查询、检索和基础统计"
    
    async def execute(self, query: str, parameters: Dict = None) -> Dict:
        """
        执行数据查询任务
        
        Args:
            query: 用户查询
            parameters: 查询参数
            
        Returns:
            查询结果
        """
        try:
            # 解析查询意图
            query_info = self._parse_query(query)
            
            # 执行数据查询
            data = await self._query_data(query_info)
            
            # 格式化结果
            result = {
                "success": True,
                "agent": self.name,
                "query_type": query_info["type"],
                "data": data,
                "summary": self._generate_summary(data, query_info),
                "confidence": 0.95,
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "confidence": 0.0
            }
    
    def _parse_query(self, query: str) -> Dict:
        """解析用户查询"""
        query_lower = query.lower()
        
        query_info = {
            "type": "general",
            "point_id": None,
            "indicators": [],
            "time_range": None,
            "aggregation": None
        }
        
        # 提取监测点ID
        import re
        point_pattern = r'p-\d+|监测点\d+|point\d+'
        point_match = re.search(point_pattern, query_lower)
        if point_match:
            query_info["point_id"] = point_match.group().upper()
        
        # 提取指标
        indicator_keywords = {
            "ph": ["ph", "ph值", "酸碱度"],
            "chlorine": ["余氯", "氯", "chlorine"],
            "turbidity": ["浊度", "turbidity"],
            "conductivity": ["电导率", "conductivity"],
            "orp": ["orp", "氧化还原电位"]
        }
        
        for indicator, keywords in indicator_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                query_info["indicators"].append(indicator)
        
        # 如果没有指定指标，查询所有指标
        if not query_info["indicators"]:
            query_info["indicators"] = ["ph", "chlorine", "turbidity", "conductivity", "orp"]
        
        # 提取时间范围
        time_keywords = {
            "today": ("今天", "今日", "today"),
            "yesterday": ("昨天", "昨日", "yesterday"), 
            "week": ("本周", "这周", "week"),
            "month": ("本月", "这个月", "month"),
            "latest": ("最新", "最近", "当前", "latest")
        }
        
        for time_type, keywords in time_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                query_info["time_range"] = time_type
                break
        
        # 提取聚合类型
        if any(word in query_lower for word in ["平均", "均值", "average"]):
            query_info["aggregation"] = "avg"
        elif any(word in query_lower for word in ["最大", "最高", "max"]):
            query_info["aggregation"] = "max"
        elif any(word in query_lower for word in ["最小", "最低", "min"]):
            query_info["aggregation"] = "min"
        
        return query_info
    
    async def _query_data(self, query_info: Dict) -> Dict:
        """执行数据库查询"""
        from django.utils import timezone
        
        # 基础查询
        queryset = WaterQualityRecord.objects.all()
        
        # 筛选监测点
        if query_info["point_id"]:
            queryset = queryset.filter(point_id__icontains=query_info["point_id"])
        
        # 筛选时间范围
        now = timezone.now()
        if query_info["time_range"] == "today":
            queryset = queryset.filter(date=now.date())
        elif query_info["time_range"] == "yesterday":
            queryset = queryset.filter(date=now.date() - timedelta(days=1))
        elif query_info["time_range"] == "week":
            queryset = queryset.filter(date__gte=now.date() - timedelta(days=7))
        elif query_info["time_range"] == "month":
            queryset = queryset.filter(date__gte=now.date() - timedelta(days=30))
        elif query_info["time_range"] == "latest":
            # 获取最新数据
            latest_date = queryset.aggregate(Max('date'))['date__max']
            if latest_date:
                queryset = queryset.filter(date=latest_date)
        
        # 排序
        queryset = queryset.order_by('-date', '-time')
        
        # 限制数据量
        if query_info["time_range"] == "latest":
            queryset = queryset[:10]  # 最新10条记录
        else:
            queryset = queryset[:100]  # 最多100条记录
        
        # 转换为字典
        records = []
        for record in queryset:
            records.append({
                "point_id": record.point_id,
                "date": record.date.strftime('%Y-%m-%d'),
                "time": record.time.strftime('%H:%M') if record.time else '',
                "ph": record.ph,
                "chlorine": record.chlorine,
                "turbidity": record.turbidity,
                "conductivity": record.conductivity,
                "orp": record.orp
            })
        
        # 计算聚合统计
        stats = {}
        if query_info["aggregation"] and records:
            for indicator in query_info["indicators"]:
                values = [r.get(indicator) for r in records if r.get(indicator) is not None]
                if values:
                    if query_info["aggregation"] == "avg":
                        stats[indicator] = sum(values) / len(values)
                    elif query_info["aggregation"] == "max":
                        stats[indicator] = max(values)
                    elif query_info["aggregation"] == "min":
                        stats[indicator] = min(values)
        
        return {
            "records": records,
            "count": len(records),
            "statistics": stats,
            "query_params": query_info
        }
    
    def _generate_summary(self, data: Dict, query_info: Dict) -> str:
        """生成查询结果摘要"""
        if not data["records"]:
            return "未找到相关数据"
        
        count = data["count"]
        point_id = query_info["point_id"] or "所有监测点"
        time_range = query_info["time_range"]
        
        summary = f"在{point_id}找到{count}条记录"
        
        if time_range == "today":
            summary += "（今天）"
        elif time_range == "yesterday":
            summary += "（昨天）"
        elif time_range == "week":
            summary += "（本周）"
        elif time_range == "latest":
            summary += "（最新数据）"
        
        # 添加统计信息
        if data["statistics"]:
            stats_parts = []
            for indicator, value in data["statistics"].items():
                indicator_names = {
                    "ph": "pH值",
                    "chlorine": "余氯",
                    "turbidity": "浊度", 
                    "conductivity": "电导率",
                    "orp": "ORP"
                }
                stats_parts.append(f"{indicator_names.get(indicator, indicator)}{value:.2f}")
            
            if stats_parts:
                aggregation_type = query_info["aggregation"]
                if aggregation_type == "avg":
                    summary += f"，平均值：{', '.join(stats_parts)}"
                elif aggregation_type == "max":
                    summary += f"，最大值：{', '.join(stats_parts)}"
                elif aggregation_type == "min":
                    summary += f"，最小值：{', '.join(stats_parts)}"
        
        return summary
