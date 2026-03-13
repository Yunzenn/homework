"""
异常检测Agent
负责检测水质数据中的异常模式
"""
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any

class AnomalyDetectionAgent:
    """异常检测智能体"""
    
    def __init__(self):
        self.name = "异常检测Agent"
        self.description = "负责检测水质数据中的异常模式和潜在问题"
    
    async def execute(self, query: str, parameters: Dict = None) -> Dict:
        """执行异常检测任务"""
        try:
            # 获取检测数据
            detection_data = await self._get_detection_data(query, parameters)
            
            # 执行异常检测
            anomalies = self._detect_anomalies(detection_data)
            
            # 分析异常模式
            pattern_analysis = self._analyze_anomaly_patterns(anomalies)
            
            # 生成预警信息
            alerts = self._generate_alerts(anomalies, pattern_analysis)
            
            result = {
                "success": True,
                "agent": self.name,
                "anomalies": anomalies,
                "pattern_analysis": pattern_analysis,
                "alerts": alerts,
                "detection_summary": {
                    "total_anomalies": len(anomalies),
                    "severity_distribution": self._get_severity_distribution(anomalies),
                    "affected_indicators": list(set(a["indicator"] for a in anomalies))
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
    
    async def _get_detection_data(self, query: str, parameters: Dict = None) -> Dict:
        """获取检测所需数据"""
        from api.models import WaterQualityRecord
        from django.utils import timezone
        
        # 默认检测最近24小时数据
        queryset = WaterQualityRecord.objects.filter(
            date__gte=timezone.now().date() - timedelta(days=1)
        )
        
        # 解析查询中的监测点
        query_lower = query.lower()
        import re
        point_pattern = r'p-\d+|监测点\d+|point\d+'
        point_match = re.search(point_pattern, query_lower)
        if point_match:
            queryset = queryset.filter(point_id__icontains=point_match.group())
        
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
        
        return {"records": records}
    
    def _detect_anomalies(self, detection_data: Dict) -> List[Dict]:
        """检测异常"""
        records = detection_data["records"]
        anomalies = []
        
        indicators = ["ph", "chlorine", "turbidity", "conductivity", "orp"]
        
        for indicator in indicators:
            # 提取有效数值
            values = [r[indicator] for r in records if r.get(indicator) is not None]
            
            if len(values) < 5:
                continue
            
            # 3σ原则检测异常（不使用numpy）
            mean_val = sum(values) / len(values)
            variance = sum((v - mean_val) ** 2 for v in values) / len(values)
            std_val = math.sqrt(variance)
            
            threshold = 3 * std_val
            for i, record in enumerate(records):
                value = record.get(indicator)
                if value is None:
                    continue
                
                if abs(value - mean_val) > threshold:
                    # 判断异常类型
                    anomaly_type = self._classify_anomaly_type(indicator, value, mean_val, std_val)
                    severity = self._assess_anomaly_severity(value, mean_val, std_val)
                    
                    anomalies.append({
                        "indicator": indicator,
                        "point_id": record["point_id"],
                        "date": record["date"],
                        "time": record["time"],
                        "value": value,
                        "expected_range": f"{mean_val - 2*std_val:.2f} - {mean_val + 2*std_val:.2f}",
                        "anomaly_type": anomaly_type,
                        "severity": severity,
                        "deviation": abs(value - mean_val) / std_val if std_val > 0 else 0
                    })
        
        return anomalies
    
    def _classify_anomaly_type(self, indicator: str, value: float, mean: float, std: float) -> str:
        """分类异常类型"""
        # 水质标准
        standards = {
            "ph": {"min": 6.5, "max": 8.5},
            "chlorine": {"min": 0.3, "max": 2.0},
            "turbidity": {"min": 0, "max": 5.0},
            "conductivity": {"min": 200, "max": 1500},
            "orp": {"min": 200, "max": 600}
        }
        
        standard = standards.get(indicator, {})
        min_val = standard.get("min")
        max_val = standard.get("max")
        
        if min_val is not None and value < min_val:
            return "过低"
        elif max_val is not None and value > max_val:
            return "过高"
        else:
            return "波动异常"
    
    def _assess_anomaly_severity(self, value: float, mean: float, std: float) -> str:
        """评估异常严重程度"""
        if std == 0:
            return "轻微"
        
        deviation = abs(value - mean) / std
        
        if deviation > 4:
            return "严重"
        elif deviation > 3:
            return "中等"
        else:
            return "轻微"
    
    def _analyze_anomaly_patterns(self, anomalies: List[Dict]) -> Dict:
        """分析异常模式"""
        if not anomalies:
            return {
                "pattern_type": "无异常",
                "description": "未检测到异常模式",
                "affected_areas": [],
                "time_distribution": {}
            }
        
        # 分析时间分布
        time_distribution = {}
        for anomaly in anomalies:
            hour_key = f"{anomaly['time'].hour}:00" if anomaly['time'] else "未知"
            time_distribution[hour_key] = time_distribution.get(hour_key, 0) + 1
        
        # 分析空间分布
        affected_points = list(set(a["point_id"] for a in anomalies))
        
        # 分析指标分布
        indicator_distribution = {}
        for anomaly in anomalies:
            indicator = anomaly["indicator"]
            indicator_distribution[indicator] = indicator_distribution.get(indicator, 0) + 1
        
        # 识别模式类型
        pattern_type = "随机异常"
        description = "异常分布较为随机，无明显规律"
        
        if len(affected_points) == 1 and len(anomalies) > 2:
            pattern_type = "点位集中"
            description = f"异常集中在{affected_points[0]}监测点"
        elif len(time_distribution) == 1:
            pattern_type = "时间集中"
            description = f"异常集中在特定时间段"
        elif len(indicator_distribution) == 1:
            pattern_type = "指标集中"
            description = f"异常集中在{list(indicator_distribution.keys())[0]}指标"
        
        return {
            "pattern_type": pattern_type,
            "description": description,
            "affected_points": affected_points,
            "affected_indicators": list(indicator_distribution.keys()),
            "time_distribution": time_distribution,
            "indicator_distribution": indicator_distribution
        }
    
    def _generate_alerts(self, anomalies: List[Dict], pattern_analysis: Dict) -> List[Dict]:
        """生成预警信息"""
        alerts = []
        
        # 严重异常预警
        severe_anomalies = [a for a in anomalies if a["severity"] == "严重"]
        if severe_anomalies:
            alerts.append({
                "level": "紧急",
                "title": f"检测到{len(severe_anomalies)}个严重异常",
                "description": "立即需要关注和处理",
                "affected_items": [f"{a['indicator']}({a['point_id']})" for a in severe_anomalies],
                "recommended_actions": [
                    "立即现场核查",
                    "启动应急预案",
                    "通知相关部门"
                ]
            })
        
        # 中等异常预警
        moderate_anomalies = [a for a in anomalies if a["severity"] == "中等"]
        if moderate_anomalies:
            alerts.append({
                "level": "警告",
                "title": f"检测到{len(moderate_anomalies)}个中度异常",
                "description": "需要关注并准备应对措施",
                "affected_items": [f"{a['indicator']}({a['point_id']})" for a in moderate_anomalies],
                "recommended_actions": [
                    "加强监测频率",
                    "排查可能原因",
                    "准备应急物资"
                ]
            })
        
        # 模式预警
        if pattern_analysis["pattern_type"] in ["点位集中", "时间集中", "指标集中"]:
            alerts.append({
                "level": "关注",
                "title": f"检测到{pattern_analysis['pattern_type']}异常模式",
                "description": pattern_analysis["description"],
                "affected_items": [],
                "recommended_actions": [
                    "深入分析异常原因",
                    "制定针对性措施",
                    "建立预警机制"
                ]
            })
        
        return alerts
    
    def _get_severity_distribution(self, anomalies: List[Dict]) -> Dict:
        """获取严重程度分布"""
        distribution = {"严重": 0, "中等": 0, "轻微": 0}
        
        for anomaly in anomalies:
            severity = anomaly["severity"]
            distribution[severity] = distribution.get(severity, 0) + 1
        
        return distribution
