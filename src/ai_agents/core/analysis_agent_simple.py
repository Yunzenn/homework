"""
数据分析Agent - 简化版本
负责水质数据的深度分析和洞察发现
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class TrendAnalysis:
    """趋势分析结果"""
    indicator: str
    trend: str  # "上升", "下降", "稳定"
    change_rate: float
    confidence: float
    time_period: str

@dataclass 
class AnomalyInsight:
    """异常洞察"""
    indicator: str
    anomaly_type: str
    severity: str  # "轻微", "中等", "严重"
    description: str
    possible_causes: List[str]

class AnalysisAgent:
    """数据分析智能体"""
    
    def __init__(self):
        self.name = "数据分析Agent"
        self.description = "负责水质数据的深度分析、趋势识别和异常检测"
        
        # 水质标准阈值
        self.water_quality_standards = {
            "ph": {"min": 6.5, "max": 8.5, "optimal": (7.0, 7.5)},
            "chlorine": {"min": 0.3, "max": 2.0, "optimal": (0.5, 1.0)},
            "turbidity": {"min": 0, "max": 5.0, "optimal": (0, 1.0)},
            "conductivity": {"min": 200, "max": 1500, "optimal": (400, 800)},
            "orp": {"min": 200, "max": 600, "optimal": (300, 500)}
        }
    
    async def execute(self, query: str, parameters: Dict = None) -> Dict:
        """执行数据分析任务"""
        try:
            # 获取数据
            data = await self._get_analysis_data(query, parameters)
            
            if not data["records"]:
                return {
                    "success": False,
                    "agent": self.name,
                    "message": "没有足够的数据进行分析",
                    "confidence": 0.0
                }
            
            # 执行各种分析
            trends = self._analyze_trends(data["records"])
            anomalies = self._detect_anomalies(data["records"])
            quality_assessment = self._assess_water_quality(data["records"])
            insights = self._generate_insights(trends, anomalies, quality_assessment)
            
            result = {
                "success": True,
                "agent": self.name,
                "analysis_type": "comprehensive",
                "trends": [trend.__dict__ for trend in trends],
                "anomalies": [anomaly.__dict__ for anomaly in anomalies],
                "quality_assessment": quality_assessment,
                "insights": insights,
                "data_summary": {
                    "total_records": len(data["records"]),
                    "time_range": data["time_range"],
                    "monitoring_points": data["points"]
                },
                "confidence": 0.85,
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
    
    async def _get_analysis_data(self, query: str, parameters: Dict = None) -> Dict:
        """获取分析所需的数据"""
        from api.models import WaterQualityRecord
        from django.utils import timezone
        
        # 解析查询参数
        query_lower = query.lower()
        
        # 确定时间范围（默认7天）
        days = 7
        if "今天" in query or "今日" in query:
            days = 1
        elif "昨天" in query or "昨日" in query:
            days = 2  # 包括昨天和今天
        elif "本周" in query or "这周" in query:
            days = 7
        elif "本月" in query or "这个月" in query:
            days = 30
        
        # 确定监测点
        point_id = None
        import re
        point_pattern = r'p-\d+|监测点\d+|point\d+'
        point_match = re.search(point_pattern, query_lower)
        if point_match:
            point_id = point_match.group().upper()
        
        # 查询数据
        queryset = WaterQualityRecord.objects.filter(
            date__gte=timezone.now().date() - timedelta(days=days)
        )
        
        if point_id:
            queryset = queryset.filter(point_id__icontains=point_id)
        
        queryset = queryset.order_by('date', 'time')
        
        # 转换为字典
        records = []
        points = set()
        for record in queryset:
            points.add(record.point_id)
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
        
        return {
            "records": records,
            "time_range": f"最近{days}天",
            "points": list(points)
        }
    
    def _analyze_trends(self, records: List[Dict]) -> List[TrendAnalysis]:
        """分析数据趋势"""
        trends = []
        indicators = ["ph", "chlorine", "turbidity", "conductivity", "orp"]
        
        for indicator in indicators:
            # 提取有效数值
            values = [r[indicator] for r in records if r[indicator] is not None]
            
            if len(values) < 3:  # 至少需要3个数据点才能分析趋势
                continue
            
            # 简单趋势分析
            first_value = values[0]
            last_value = values[-1]
            
            # 计算变化率
            if first_value != 0:
                change_rate = (last_value - first_value) / first_value * 100
            else:
                change_rate = 0
            
            # 判断趋势方向
            if abs(change_rate) < 5:
                trend = "稳定"
                confidence = 0.9
            elif change_rate > 0:
                trend = "上升"
                confidence = min(0.9, abs(change_rate) / 10)
            else:
                trend = "下降"
                confidence = min(0.9, abs(change_rate) / 10)
            
            trends.append(TrendAnalysis(
                indicator=indicator,
                trend=trend,
                change_rate=change_rate,
                confidence=confidence,
                time_period="分析期间"
            ))
        
        return trends
    
    def _detect_anomalies(self, records: List[Dict]) -> List[AnomalyInsight]:
        """检测异常值"""
        anomalies = []
        indicators = ["ph", "chlorine", "turbidity", "conductivity", "orp"]
        
        for indicator in indicators:
            # 提取有效数值
            values = [r[indicator] for r in records if r[indicator] is not None]
            
            if len(values) < 5:  # 数据点太少，无法检测异常
                continue
            
            # 简单异常检测：基于标准差
            mean_val = sum(values) / len(values)
            variance = sum((v - mean_val) ** 2 for v in values) / len(values)
            std_val = variance ** 0.5
            
            threshold = 3 * std_val
            for i, value in enumerate(values):
                if abs(value - mean_val) > threshold:
                    # 判断异常类型和严重程度
                    standard = self.water_quality_standards.get(indicator, {})
                    
                    if value < standard.get("min", 0):
                        anomaly_type = "过低"
                    elif value > standard.get("max", float('inf')):
                        anomaly_type = "过高"
                    else:
                        anomaly_type = "波动异常"
                    
                    # 判断严重程度
                    deviation = abs(value - mean_val) / std_val if std_val > 0 else 0
                    if deviation > 4:
                        severity = "严重"
                    elif deviation > 3:
                        severity = "中等"
                    else:
                        severity = "轻微"
                    
                    # 推测可能原因
                    possible_causes = self._get_possible_causes(indicator, anomaly_type, value)
                    
                    anomalies.append(AnomalyInsight(
                        indicator=indicator,
                        anomaly_type=anomaly_type,
                        severity=severity,
                        description=f"{indicator}值{anomaly_type}，当前值{value:.2f}",
                        possible_causes=possible_causes
                    ))
        
        return anomalies
    
    def _assess_water_quality(self, records: List[Dict]) -> Dict:
        """评估水质状况"""
        if not records:
            return {"overall_score": 0, "grade": "无数据", "indicator_scores": {}}
        
        indicator_scores = {}
        indicators = ["ph", "chlorine", "turbidity", "conductivity", "orp"]
        
        for indicator in indicators:
            values = [r[indicator] for r in records if r[indicator] is not None]
            
            if not values:
                indicator_scores[indicator] = 0
                continue
            
            # 计算最新值的得分
            latest_value = values[-1]
            standard = self.water_quality_standards.get(indicator, {})
            
            min_val = standard.get("min", 0)
            max_val = standard.get("max", 100)
            optimal_min, optimal_max = standard.get("optimal", (min_val, max_val))
            
            if optimal_min <= latest_value <= optimal_max:
                score = 100
            elif min_val <= latest_value <= max_val:
                # 在标准范围内但不在最优范围
                distance_to_optimal = min(abs(latest_value - optimal_min), abs(latest_value - optimal_max))
                score = 80 - distance_to_optimal * 10
                score = max(60, min(80, score))
            else:
                # 超出标准范围
                if latest_value < min_val:
                    deviation = min_val - latest_value
                else:
                    deviation = latest_value - max_val
                score = max(0, 60 - deviation * 5)
            
            indicator_scores[indicator] = round(score, 1)
        
        # 计算总体得分
        valid_scores = [score for score in indicator_scores.values() if score > 0]
        overall_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
        
        # 评级
        if overall_score >= 90:
            grade = "优"
        elif overall_score >= 80:
            grade = "良"
        elif overall_score >= 70:
            grade = "中"
        elif overall_score >= 60:
            grade = "及格"
        else:
            grade = "差"
        
        return {
            "overall_score": round(overall_score, 1),
            "grade": grade,
            "indicator_scores": indicator_scores,
            "assessment_time": datetime.now().isoformat()
        }
    
    def _generate_insights(self, trends: List[TrendAnalysis], anomalies: List[AnomalyInsight], quality_assessment: Dict) -> List[str]:
        """生成洞察和建议"""
        insights = []
        
        # 水质总体评价
        grade = quality_assessment.get("grade", "未知")
        score = quality_assessment.get("overall_score", 0)
        insights.append(f"当前水质综合评分为{score}分，等级为'{grade}'")
        
        # 趋势洞察
        significant_trends = [t for t in trends if t.confidence > 0.7]
        if significant_trends:
            trend_insights = []
            for trend in significant_trends:
                indicator_names = {
                    "ph": "pH值",
                    "chlorine": "余氯",
                    "turbidity": "浊度",
                    "conductivity": "电导率",
                    "orp": "ORP"
                }
                name = indicator_names.get(trend.indicator, trend.indicator)
                change_desc = f"变化率{trend.change_rate:+.1f}%" if trend.change_rate != 0 else "保持稳定"
                trend_insights.append(f"{name}呈{trend.trend}趋势，{change_desc}")
            
            if trend_insights:
                insights.append("趋势分析：" + "；".join(trend_insights))
        
        # 异常洞察
        if anomalies:
            anomaly_insights = []
            for anomaly in anomalies:
                indicator_names = {
                    "ph": "pH值",
                    "chlorine": "余氯", 
                    "turbidity": "浊度",
                    "conductivity": "电导率",
                    "orp": "ORP"
                }
                name = indicator_names.get(anomaly.indicator, anomaly.indicator)
                anomaly_insights.append(f"{name}{anomaly.anomaly_type}（{anomaly.severity}）")
            
            insights.append("检测到异常：" + "；".join(anomaly_insights))
        
        # 综合建议
        if anomalies:
            insights.append("建议：关注异常指标，及时排查原因并采取相应措施")
        elif grade in ["优", "良"]:
            insights.append("建议：水质状况良好，继续保持现有监测频率")
        else:
            insights.append("建议：水质需要改善，建议增加监测频率并排查影响因素")
        
        return insights
    
    def _get_possible_causes(self, indicator: str, anomaly_type: str, value: float) -> List[str]:
        """推测异常可能原因"""
        causes_map = {
            "ph": {
                "过高": ["工业废水排放", "农业径流", "碱性物质泄漏"],
                "过低": ["酸性废水排放", "酸雨", "有机物分解"]
            },
            "chlorine": {
                "过高": ["消毒剂投加过量", "氯化物污染"],
                "过低": ["消毒剂投加不足", "余氯消耗过快"]
            },
            "turbidity": {
                "过高": ["悬浮物增多", "藻类爆发", "泥沙冲刷", "有机物污染"]
            },
            "conductivity": {
                "过高": ["盐分污染", "重金属污染", "溶解固体增多"],
                "过低": ["淡水稀释", "离子浓度降低"]
            },
            "orp": {
                "过高": ["氧化剂污染", "强氧化环境"],
                "过低": ["还原性污染", "缺氧环境"]
            }
        }
        
        return causes_map.get(indicator, {}).get(anomaly_type, ["未知原因"])
