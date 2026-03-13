"""
报告生成Agent
负责自动生成水质分析报告
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any

class ReportGenerationAgent:
    """报告生成智能体"""
    
    def __init__(self):
        self.name = "报告生成Agent"
        self.description = "负责自动生成水质分析报告和统计汇总"
    
    async def execute(self, query: str, parameters: Dict = None) -> Dict:
        """执行报告生成任务"""
        try:
            # 解析报告需求
            report_info = self._parse_report_query(query)
            
            # 收集报告数据
            report_data = await self._collect_report_data(report_info)
            
            # 生成报告内容
            report_content = self._generate_report_content(report_info, report_data)
            
            # 生成报告摘要
            summary = self._generate_report_summary(report_content)
            
            result = {
                "success": True,
                "agent": self.name,
                "report_type": report_info["type"],
                "report_period": report_info["period"],
                "content": report_content,
                "summary": summary,
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "data_points": len(report_data.get("records", [])),
                    "monitoring_points": len(set(r["point_id"] for r in report_data.get("records", [])))
                },
                "confidence": 0.9,
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
    
    def _parse_report_query(self, query: str) -> Dict:
        """解析报告查询"""
        query_lower = query.lower()
        
        report_info = {
            "type": "summary",
            "period": "daily",
            "point_id": None,
            "indicators": ["ph", "chlorine", "turbidity", "conductivity", "orp"]
        }
        
        # 确定报告类型
        if "日报" in query or "每日" in query or "今天" in query:
            report_info["type"] = "daily"
            report_info["period"] = "daily"
        elif "周报" in query or "本周" in query or "一周" in query:
            report_info["type"] = "weekly"
            report_info["period"] = "weekly"
        elif "月报" in query or "本月" in query or "一个月" in query:
            report_info["type"] = "monthly"
            report_info["period"] = "monthly"
        elif "异常" in query or "超标" in query:
            report_info["type"] = "anomaly"
        elif "统计" in query or "汇总" in query:
            report_info["type"] = "summary"
        
        # 提取监测点
        import re
        point_pattern = r'p-\d+|监测点\d+|point\d+'
        point_match = re.search(point_pattern, query_lower)
        if point_match:
            report_info["point_id"] = point_match.group().upper()
        
        return report_info
    
    async def _collect_report_data(self, report_info: Dict) -> Dict:
        """收集报告数据"""
        from api.models import WaterQualityRecord
        from django.utils import timezone
        
        # 确定时间范围
        now = timezone.now()
        if report_info["period"] == "daily":
            start_date = now.date()
        elif report_info["period"] == "weekly":
            start_date = now.date() - timedelta(days=7)
        elif report_info["period"] == "monthly":
            start_date = now.date() - timedelta(days=30)
        else:
            start_date = now.date() - timedelta(days=1)
        
        # 查询数据
        queryset = WaterQualityRecord.objects.filter(date__gte=start_date)
        
        if report_info["point_id"]:
            queryset = queryset.filter(point_id__icontains=report_info["point_id"])
        
        queryset = queryset.order_by('date', 'time')
        
        # 转换为字典
        records = []
        for record in queryset:
            records.append({
                "point_id": record.point_id,
                "date": record.date,
                "time": record.time,
                "ph": record.ph,
                "chlorine": record.chlorine,
                "turbidity": record.turbidity,
                "conductivity": record.conductivity,
                "orp": record.orp
            })
        
        return {"records": records, "period": report_info["period"]}
    
    def _generate_report_content(self, report_info: Dict, report_data: Dict) -> Dict:
        """生成报告内容"""
        records = report_data["records"]
        
        if not records:
            return {
                "title": f"{report_info['type']}报告",
                "overview": "报告期内无监测数据",
                "sections": {}
            }
        
        # 基础统计
        basic_stats = self._calculate_basic_statistics(records)
        
        # 趋势分析
        trend_analysis = self._analyze_trends(records)
        
        # 异常统计
        anomaly_stats = self._analyze_anomalies(records)
        
        # 水质评估
        quality_assessment = self._assess_water_quality(records)
        
        # 构建报告内容
        content = {
            "title": self._generate_report_title(report_info),
            "overview": self._generate_overview(basic_stats, quality_assessment),
            "sections": {
                "basic_statistics": basic_stats,
                "trend_analysis": trend_analysis,
                "anomaly_statistics": anomaly_stats,
                "quality_assessment": quality_assessment
            }
        }
        
        return content
    
    def _generate_report_title(self, report_info: Dict) -> str:
        """生成报告标题"""
        period_names = {
            "daily": "日报",
            "weekly": "周报", 
            "monthly": "月报"
        }
        
        type_names = {
            "daily": "水质监测日报",
            "weekly": "水质监测周报",
            "monthly": "水质监测月报",
            "anomaly": "异常分析报告",
            "summary": "统计汇总报告"
        }
        
        title = type_names.get(report_info["type"], "水质监测报告")
        
        if report_info["point_id"]:
            title += f" - {report_info['point_id']}"
        
        return title
    
    def _generate_overview(self, basic_stats: Dict, quality_assessment: Dict) -> str:
        """生成报告概述"""
        total_records = basic_stats.get("total_records", 0)
        monitoring_points = basic_stats.get("monitoring_points", 0)
        overall_grade = quality_assessment.get("overall_grade", "未知")
        
        overview = f"本报告期内共收集{total_records}条监测数据，覆盖{monitoring_points}个监测点。"
        overview += f"整体水质等级为'{overall_grade}'。"
        
        # 添加关键信息
        anomaly_count = basic_stats.get("anomaly_count", 0)
        if anomaly_count > 0:
            overview += f"检测到{anomaly_count}个异常数据点，需要重点关注。"
        
        return overview
    
    def _calculate_basic_statistics(self, records: List[Dict]) -> Dict:
        """计算基础统计"""
        if not records:
            return {}
        
        indicators = ["ph", "chlorine", "turbidity", "conductivity", "orp"]
        stats = {}
        
        for indicator in indicators:
            values = [r[indicator] for r in records if r.get(indicator) is not None]
            
            if values:
                import numpy as np
                stats[indicator] = {
                    "count": len(values),
                    "mean": round(np.mean(values), 2),
                    "min": round(np.min(values), 2),
                    "max": round(np.max(values), 2),
                    "std": round(np.std(values), 2)
                }
        
        return {
            "total_records": len(records),
            "monitoring_points": len(set(r["point_id"] for r in records)),
            "date_range": {
                "start": min(r["date"] for r in records),
                "end": max(r["date"] for r in records)
            },
            "indicator_statistics": stats,
            "anomaly_count": len([r for r in records if self._is_anomaly_record(r)])
        }
    
    def _analyze_trends(self, records: List[Dict]) -> Dict:
        """分析趋势"""
        indicators = ["ph", "chlorine", "turbidity", "conductivity", "orp"]
        trends = {}
        
        for indicator in indicators:
            values = [r[indicator] for r in records if r.get(indicator) is not None]
            
            if len(values) < 3:
                trends[indicator] = {"trend": "数据不足", "change_rate": 0}
                continue
            
            # 简单趋势分析
            import numpy as np
            x = np.arange(len(values))
            y = np.array(values)
            
            coeffs = np.polyfit(x, y, 1)
            slope = coeffs[0]
            
            if abs(slope) < 0.01:
                trend = "稳定"
            elif slope > 0:
                trend = "上升"
            else:
                trend = "下降"
            
            change_rate = (values[-1] - values[0]) / values[0] * 100 if values[0] != 0 else 0
            
            trends[indicator] = {
                "trend": trend,
                "change_rate": round(change_rate, 2)
            }
        
        return trends
    
    def _analyze_anomalies(self, records: List[Dict]) -> Dict:
        """分析异常"""
        anomalies = []
        
        for record in records:
            if self._is_anomaly_record(record):
                anomalies.append({
                    "point_id": record["point_id"],
                    "date": record["date"],
                    "time": record["time"],
                    "anomaly_indicators": self._get_anomaly_indicators(record)
                })
        
        return {
            "total_anomalies": len(anomalies),
            "anomaly_records": anomalies[:10],  # 只显示前10个
            "anomaly_rate": round(len(anomalies) / len(records) * 100, 2) if records else 0
        }
    
    def _assess_water_quality(self, records: List[Dict]) -> Dict:
        """评估水质"""
        if not records:
            return {"overall_grade": "无数据"}
        
        # 水质标准
        standards = {
            "ph": {"min": 6.5, "max": 8.5},
            "chlorine": {"min": 0.3, "max": 2.0},
            "turbidity": {"min": 0, "max": 5.0},
            "conductivity": {"min": 200, "max": 1500},
            "orp": {"min": 200, "max": 600}
        }
        
        # 计算合规率
        indicators = ["ph", "chlorine", "turbidity", "conductivity", "orp"]
        compliance_rates = {}
        
        for indicator in indicators:
            values = [r[indicator] for r in records if r.get(indicator) is not None]
            
            if values:
                standard = standards.get(indicator, {})
                compliant_count = sum(1 for v in values 
                                    if standard.get("min", 0) <= v <= standard.get("max", float('inf')))
                compliance_rates[indicator] = round(compliant_count / len(values) * 100, 2)
        
        # 计算总体等级
        avg_compliance = sum(compliance_rates.values()) / len(compliance_rates) if compliance_rates else 0
        
        if avg_compliance >= 95:
            overall_grade = "优"
        elif avg_compliance >= 85:
            overall_grade = "良"
        elif avg_compliance >= 75:
            overall_grade = "中"
        elif avg_compliance >= 60:
            overall_grade = "及格"
        else:
            overall_grade = "差"
        
        return {
            "overall_grade": overall_grade,
            "compliance_rates": compliance_rates,
            "average_compliance": round(avg_compliance, 2)
        }
    
    def _generate_report_summary(self, content: Dict) -> str:
        """生成报告摘要"""
        overview = content.get("overview", "")
        sections = content.get("sections", {})
        
        summary = overview + "\n\n"
        
        # 添加关键统计
        basic_stats = sections.get("basic_statistics", {})
        if basic_stats:
            summary += f"关键指标："
            indicator_stats = basic_stats.get("indicator_statistics", {})
            for indicator, stats in indicator_stats.items():
                summary += f"{indicator}均值{stats['mean']}，"
            summary = summary.rstrip("，") + "。\n"
        
        # 添加趋势信息
        trend_analysis = sections.get("trend_analysis", {})
        if trend_analysis:
            summary += "趋势分析："
            for indicator, trend_info in trend_analysis.items():
                summary += f"{indicator}呈{trend_info['trend']}趋势，"
            summary = summary.rstrip("，") + "。\n"
        
        # 添加异常信息
        anomaly_stats = sections.get("anomaly_statistics", {})
        if anomaly_stats.get("total_anomalies", 0) > 0:
            summary += f"共检测到{anomaly_stats['total_anomalies']}个异常，异常率{anomaly_stats['anomaly_rate']}%。\n"
        
        return summary
    
    def _is_anomaly_record(self, record: Dict) -> bool:
        """判断是否为异常记录"""
        indicators = ["ph", "chlorine", "turbidity", "conductivity", "orp"]
        
        # 水质标准
        standards = {
            "ph": {"min": 6.5, "max": 8.5},
            "chlorine": {"min": 0.3, "max": 2.0},
            "turbidity": {"min": 0, "max": 5.0},
            "conductivity": {"min": 200, "max": 1500},
            "orp": {"min": 200, "max": 600}
        }
        
        for indicator in indicators:
            value = record.get(indicator)
            if value is not None:
                standard = standards.get(indicator, {})
                if value < standard.get("min", 0) or value > standard.get("max", float('inf')):
                    return True
        
        return False
    
    def _get_anomaly_indicators(self, record: Dict) -> List[str]:
        """获取异常指标"""
        indicators = ["ph", "chlorine", "turbidity", "conductivity", "orp"]
        anomaly_indicators = []
        
        standards = {
            "ph": {"min": 6.5, "max": 8.5},
            "chlorine": {"min": 0.3, "max": 2.0},
            "turbidity": {"min": 0, "max": 5.0},
            "conductivity": {"min": 200, "max": 1500},
            "orp": {"min": 200, "max": 600}
        }
        
        for indicator in indicators:
            value = record.get(indicator)
            if value is not None:
                standard = standards.get(indicator, {})
                if value < standard.get("min", 0) or value > standard.get("max", float('inf')):
                    anomaly_indicators.append(indicator)
        
        return anomaly_indicators
