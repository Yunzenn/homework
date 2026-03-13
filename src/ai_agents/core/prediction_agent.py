"""
预测Agent
负责水质指标的趋势预测
"""
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any

class PredictionAgent:
    """预测智能体"""
    
    def __init__(self):
        self.name = "预测Agent"
        self.description = "负责水质指标的趋势预测和风险评估"
    
    async def execute(self, query: str, parameters: Dict = None) -> Dict:
        """执行预测任务"""
        try:
            # 解析预测需求
            prediction_info = self._parse_prediction_query(query)
            
            # 获取历史数据
            historical_data = await self._get_historical_data(prediction_info)
            
            # 执行预测
            predictions = self._make_predictions(historical_data, prediction_info)
            
            # 评估风险
            risk_assessment = self._assess_prediction_risks(predictions)
            
            result = {
                "success": True,
                "agent": self.name,
                "prediction_type": prediction_info["type"],
                "predictions": predictions,
                "risk_assessment": risk_assessment,
                "confidence": 0.75,
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
    
    def _parse_prediction_query(self, query: str) -> Dict:
        """解析预测查询"""
        query_lower = query.lower()
        
        prediction_info = {
            "type": "short_term",
            "time_horizon": 24,  # 小时
            "indicators": ["ph", "chlorine", "turbidity", "conductivity", "orp"],
            "point_id": None
        }
        
        # 提取时间范围
        if "明天" in query or "24小时" in query:
            prediction_info["time_horizon"] = 24
            prediction_info["type"] = "short_term"
        elif "后天" in query or "48小时" in query:
            prediction_info["time_horizon"] = 48
            prediction_info["type"] = "short_term"
        elif "三天" in query or "72小时" in query:
            prediction_info["time_horizon"] = 72
            prediction_info["type"] = "medium_term"
        elif "一周" in query or "7天" in query:
            prediction_info["time_horizon"] = 168  # 7天
            prediction_info["type"] = "long_term"
        
        # 提取监测点
        import re
        point_pattern = r'p-\d+|监测点\d+|point\d+'
        point_match = re.search(point_pattern, query_lower)
        if point_match:
            prediction_info["point_id"] = point_match.group().upper()
        
        return prediction_info
    
    async def _get_historical_data(self, prediction_info: Dict) -> Dict:
        """获取历史数据"""
        from api.models import WaterQualityRecord
        from django.utils import timezone
        
        # 获取过去7天的数据
        queryset = WaterQualityRecord.objects.filter(
            date__gte=timezone.now().date() - timedelta(days=7)
        )
        
        if prediction_info["point_id"]:
            queryset = queryset.filter(point_id__icontains=prediction_info["point_id"])
        
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
    
    def _make_predictions(self, historical_data: Dict, prediction_info: Dict) -> List[Dict]:
        """执行预测"""
        predictions = []
        records = historical_data["records"]
        
        if len(records) < 5:
            # 数据不足，返回简单预测
            for indicator in prediction_info["indicators"]:
                latest_values = [r.get(indicator) for r in records[-5:] if r.get(indicator) is not None]
                if latest_values:
                    avg_value = np.mean(latest_values)
                    predictions.append({
                        "indicator": indicator,
                        "predicted_values": [avg_value] * 3,  # 未来3个时间点
                        "time_points": ["24小时后", "48小时后", "72小时后"],
                        "method": "平均值预测",
                        "confidence": 0.5
                    })
            return predictions
        
        # 简单线性预测
        for indicator in prediction_info["indicators"]:
            values = [r.get(indicator) for r in records if r.get(indicator) is not None]
            
            if len(values) < 3:
                continue
            
            # 简单线性回归预测（不使用numpy）
            n = len(values)
            if n < 2:
                continue
            
            # 计算线性回归系数
            x = list(range(n))
            y = values
            
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(x[i] * x[i] for i in range(n))
            
            denominator = (n * sum_x2 - sum_x * sum_x)
            slope = (n * sum_xy - sum_x * sum_y) / denominator if denominator != 0 else 0
            intercept = (sum_y - slope * sum_x) / n
            
            # 预测未来值
            future_steps = min(3, prediction_info["time_horizon"] // 24)
            predicted_values = []
            time_points = []
            
            for i in range(1, future_steps + 1):
                future_x = len(values) + i * (len(values) // future_steps)
                predicted_value = slope * future_x + intercept
                predicted_values.append(max(0, predicted_value))  # 确保非负
                time_points.append(f"{i * 24}小时后")
            
            predictions.append({
                "indicator": indicator,
                "predicted_values": predicted_values,
                "time_points": time_points,
                "method": "线性回归",
                "confidence": 0.7
            })
        
        return predictions
    
    def _assess_prediction_risks(self, predictions: List[Dict]) -> Dict:
        """评估预测风险"""
        risk_assessment = {
            "overall_risk": "低",
            "risk_indicators": [],
            "recommendations": []
        }
        
        # 水质标准
        standards = {
            "ph": {"min": 6.5, "max": 8.5},
            "chlorine": {"min": 0.3, "max": 2.0},
            "turbidity": {"min": 0, "max": 5.0},
            "conductivity": {"min": 200, "max": 1500},
            "orp": {"min": 200, "max": 600}
        }
        
        high_risk_count = 0
        
        for prediction in predictions:
            indicator = prediction["indicator"]
            predicted_values = prediction["predicted_values"]
            
            if indicator not in standards:
                continue
            
            standard = standards[indicator]
            
            # 检查预测值是否可能超标
            for i, value in enumerate(predicted_values):
                if value < standard["min"] or value > standard["max"]:
                    risk_assessment["risk_indicators"].append({
                        "indicator": indicator,
                        "time_point": prediction["time_points"][i],
                        "predicted_value": value,
                        "risk_type": "过低" if value < standard["min"] else "过高",
                        "standard_range": f"{standard['min']}-{standard['max']}"
                    })
                    high_risk_count += 1
        
        # 评估整体风险
        if high_risk_count >= 3:
            risk_assessment["overall_risk"] = "高"
            risk_assessment["recommendations"] = [
                "加强监测频率",
                "准备应急措施",
                "排查潜在风险源"
            ]
        elif high_risk_count >= 1:
            risk_assessment["overall_risk"] = "中"
            risk_assessment["recommendations"] = [
                "密切关注风险指标",
                "制定应对预案"
            ]
        else:
            risk_assessment["overall_risk"] = "低"
            risk_assessment["recommendations"] = [
                "保持常规监测",
                "继续观察趋势"
            ]
        
        return risk_assessment
