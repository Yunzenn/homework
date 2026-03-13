"""
建议Agent
负责生成水质管理建议和治理方案
"""

from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class AdvisoryRecommendation:
    """建议条目"""
    category: str  # "immediate", "short_term", "long_term"
    priority: str  # "high", "medium", "low"
    title: str
    description: str
    action_steps: List[str]
    expected_outcome: str
    time_frame: str

class AdvisoryAgent:
    """建议智能体"""
    
    def __init__(self):
        self.name = "建议Agent"
        self.description = "负责生成水质管理建议和治理方案"
        
        # 治理知识库
        self.treatment_knowledge = {
            "ph过高": {
                "immediate": [
                    "检查上游是否有碱性废水排放",
                    "增加酸性中和剂投加量"
                ],
                "short_term": [
                    "排查工业排放源",
                    "建立pH值预警机制"
                ],
                "long_term": [
                    "建设缓冲池调节pH",
                    "与上游企业协商排放标准"
                ]
            },
            "ph过低": {
                "immediate": [
                    "检查是否有酸性废水排放",
                    "投加碱性中和剂"
                ],
                "short_term": [
                    "排查酸雨影响",
                    "建立pH值监测网络"
                ],
                "long_term": [
                    "建设酸碱中和设施",
                    "制定酸雨应对预案"
                ]
            },
            "余氯过高": {
                "immediate": [
                    "减少消毒剂投加量",
                    "增加曝气促进余氯分解"
                ],
                "short_term": [
                    "优化消毒工艺",
                    "建立余氯自动控制系统"
                ],
                "long_term": [
                    "采用替代消毒方案",
                    "建设余氯回收利用设施"
                ]
            },
            "余氯过低": {
                "immediate": [
                    "增加消毒剂投加量",
                    "检查消毒设备运行状态"
                ],
                "short_term": [
                    "优化消毒点布局",
                    "建立余氯监测预警"
                ],
                "long_term": [
                    "升级消毒系统",
                    "采用多级消毒工艺"
                ]
            },
            "浊度过高": {
                "immediate": [
                    "增加混凝剂投加量",
                    "检查过滤系统运行状态"
                ],
                "short_term": [
                    "排查悬浮物来源",
                    "优化沉淀工艺"
                ],
                "long_term": [
                    "建设预处理设施",
                    "建立源头控制机制"
                ]
            },
            "电导率过高": {
                "immediate": [
                    "检查是否有盐分污染",
                    "增加离子交换处理"
                ],
                "short_term": [
                    "排查污染源",
                    "建立电导率监测"
                ],
                "long_term": [
                    "建设脱盐设施",
                    "制定污染源管控方案"
                ]
            },
            "orp异常": {
                "immediate": [
                    "检查氧化还原环境",
                    "调整曝气强度"
                ],
                "short_term": [
                    "优化曝气系统",
                    "建立ORP监测预警"
                ],
                "long_term": [
                    "升级曝气设备",
                    "建立氧化还原平衡控制"
                ]
            }
        }
        
        # 应急预案
        self.emergency_plans = {
            "严重超标": {
                "actions": [
                    "立即启动应急预案",
                    "通知环保监管部门",
                    "暂停相关排放源",
                    "加强监测频率"
                ],
                "notifications": ["监管部门", "下游用户", "应急管理部门"]
            },
            "中度超标": {
                "actions": [
                    "启动预警响应",
                    "通知相关责任单位",
                    "增加监测频次",
                    "准备应急物资"
                ],
                "notifications": ["责任单位", "监测部门"]
            },
            "轻微超标": {
                "actions": [
                    "加强日常监测",
                    "排查可能原因",
                    "准备应对措施"
                ],
                "notifications": ["运维人员"]
            }
        }
    
    async def execute(self, query: str, parameters: Dict = None) -> Dict:
        """
        执行建议生成任务
        
        Args:
            query: 用户查询
            parameters: 分析参数
            
        Returns:
            建议结果
        """
        try:
            # 分析当前状况
            current_status = await self._analyze_current_status(query, parameters)
            
            # 生成建议
            recommendations = self._generate_recommendations(current_status)
            
            # 评估风险
            risk_assessment = self._assess_risks(current_status)
            
            # 生成行动计划
            action_plan = self._create_action_plan(recommendations, risk_assessment)
            
            result = {
                "success": True,
                "agent": self.name,
                "current_status": current_status,
                "recommendations": [rec.__dict__ for rec in recommendations],
                "risk_assessment": risk_assessment,
                "action_plan": action_plan,
                "confidence": 0.8,
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
    
    async def _analyze_current_status(self, query: str, parameters: Dict = None) -> Dict:
        """分析当前水质状况"""
        # 从参数中获取分析结果
        analysis_result = parameters.get("analysis_result", {}) if parameters else {}
        
        current_status = {
            "overall_grade": "未知",
            "issues": [],
            "trends": [],
            "anomalies": []
        }
        
        # 获取水质等级
        if "quality_assessment" in analysis_result:
            current_status["overall_grade"] = analysis_result["quality_assessment"].get("grade", "未知")
        
        # 获取异常信息
        if "anomalies" in analysis_result:
            for anomaly in analysis_result["anomalies"]:
                current_status["anomalies"].append({
                    "indicator": anomaly["indicator"],
                    "type": anomaly["anomaly_type"],
                    "severity": anomaly["severity"]
                })
        
        # 获取趋势信息
        if "trends" in analysis_result:
            for trend in analysis_result["trends"]:
                current_status["trends"].append({
                    "indicator": trend["indicator"],
                    "direction": trend["trend"],
                    "confidence": trend["confidence"]
                })
        
        # 识别主要问题
        for anomaly in current_status["anomalies"]:
            if anomaly["severity"] == "严重":
                current_status["issues"].append(f"{anomaly['indicator']}{anomaly['type']}")
        
        return current_status
    
    def _generate_recommendations(self, current_status: Dict) -> List[AdvisoryRecommendation]:
        """生成建议"""
        recommendations = []
        
        # 基于异常生成针对性建议
        for anomaly in current_status["anomalies"]:
            indicator = anomaly["indicator"]
            anomaly_type = anomaly["type"]
            severity = anomaly["severity"]
            
            # 查找对应的治理方案
            issue_key = f"{indicator}{anomaly_type}"
            treatment_plan = self.treatment_knowledge.get(issue_key)
            
            if treatment_plan:
                # 立即措施
                if "immediate" in treatment_plan:
                    recommendations.append(AdvisoryRecommendation(
                        category="immediate",
                        priority="high" if severity == "严重" else "medium",
                        title=f"立即处理{indicator}{anomaly_type}",
                        description=f"针对{indicator}{anomaly_type}的紧急处理措施",
                        action_steps=treatment_plan["immediate"],
                        expected_outcome=f"快速控制{indicator}指标",
                        time_frame="立即执行"
                    ))
                
                # 短期措施
                if "short_term" in treatment_plan:
                    recommendations.append(AdvisoryRecommendation(
                        category="short_term",
                        priority="medium",
                        title=f"短期改善{indicator}",
                        description=f"{indicator}指标的短期改善方案",
                        action_steps=treatment_plan["short_term"],
                        expected_outcome=f"稳定{indicator}指标，防止复发",
                        time_frame="1-4周"
                    ))
                
                # 长期措施
                if "long_term" in treatment_plan:
                    recommendations.append(AdvisoryRecommendation(
                        category="long_term",
                        priority="low",
                        title=f"长期优化{indicator}管理",
                        description=f"{indicator}指标的长期管理策略",
                        action_steps=treatment_plan["long_term"],
                        expected_outcome=f"建立{indicator}长效管理机制",
                        time_frame="1-6个月"
                    ))
        
        # 基于趋势生成预防性建议
        for trend in current_status["trends"]:
            if trend["confidence"] > 0.7 and trend["direction"] in ["上升", "下降"]:
                indicator = trend["indicator"]
                recommendations.append(AdvisoryRecommendation(
                    category="preventive",
                    priority="medium",
                    title=f"预防{indicator}异常变化",
                    description=f"针对{indicator}呈{trend['direction']}趋势的预防措施",
                    action_steps=[
                        "加强{indicator}指标监测频率",
                        "排查影响{indicator}的因素",
                        "制定{indicator}异常应对预案"
                    ],
                    expected_outcome=f"防止{indicator}指标进一步恶化",
                    time_frame="持续进行"
                ))
        
        # 通用建议
        if current_status["overall_grade"] in ["差", "及格"]:
            recommendations.append(AdvisoryRecommendation(
                category="general",
                priority="high",
                title="整体水质改善",
                description="提升整体水质状况的综合建议",
                action_steps=[
                    "全面排查污染源",
                    "优化处理工艺参数",
                    "加强运行管理",
                    "建立质量改进计划"
                ],
                expected_outcome="整体水质等级提升",
                time_frame="2-8周"
            ))
        
        return recommendations
    
    def _assess_risks(self, current_status: Dict) -> Dict:
        """评估风险"""
        risk_level = "低"
        risk_factors = []
        mitigation_measures = []
        
        # 基于异常评估风险
        severe_anomalies = [a for a in current_status["anomalies"] if a["severity"] == "严重"]
        moderate_anomalies = [a for a in current_status["anomalies"] if a["severity"] == "中等"]
        
        if severe_anomalies:
            risk_level = "高"
            risk_factors.append(f"存在{len(severe_anomalies)}个严重异常指标")
            mitigation_measures.extend([
                "立即启动应急响应",
                "通知监管部门",
                "暂停相关排放源"
            ])
        elif moderate_anomalies:
            risk_level = "中"
            risk_factors.append(f"存在{len(moderate_anomalies)}个中度异常指标")
            mitigation_measures.extend([
                "启动预警响应",
                "加强监测频次",
                "准备应急物资"
            ])
        
        # 基于趋势评估风险
        adverse_trends = [t for t in current_status["trends"] 
                         if t["direction"] in ["上升", "下降"] and t["confidence"] > 0.7]
        
        if adverse_trends:
            risk_factors.append(f"存在{len(adverse_trends)}个不良趋势")
            mitigation_measures.append("密切关注趋势变化")
        
        # 基于整体等级评估风险
        if current_status["overall_grade"] in ["差"]:
            risk_level = "高"
            risk_factors.append("整体水质等级为差")
        elif current_status["overall_grade"] in ["及格"]:
            risk_level = "中"
            risk_factors.append("整体水质等级为及格")
        
        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "mitigation_measures": mitigation_measures,
            "assessment_time": datetime.now().isoformat()
        }
    
    def _create_action_plan(self, recommendations: List[AdvisoryRecommendation], risk_assessment: Dict) -> Dict:
        """创建行动计划"""
        # 按优先级排序
        high_priority = [r for r in recommendations if r.priority == "high"]
        medium_priority = [r for r in recommendations if r.priority == "medium"]
        low_priority = [r for r in recommendations if r.priority == "low"]
        
        # 创建时间线
        immediate_actions = []
        short_term_actions = []
        long_term_actions = []
        
        for rec in recommendations:
            if rec.category == "immediate":
                immediate_actions.append(rec)
            elif rec.category in ["short_term", "preventive"]:
                short_term_actions.append(rec)
            elif rec.category in ["long_term", "general"]:
                long_term_actions.append(rec)
        
        # 生成执行计划
        action_plan = {
            "timeline": {
                "immediate": {
                    "timeframe": "立即-24小时",
                    "actions": [rec.__dict__ for rec in immediate_actions],
                    "responsible": "现场运维人员"
                },
                "short_term": {
                    "timeframe": "1-4周",
                    "actions": [rec.__dict__ for rec in short_term_actions],
                    "responsible": "技术管理团队"
                },
                "long_term": {
                    "timeframe": "1-6个月",
                    "actions": [rec.__dict__ for rec in long_term_actions],
                    "responsible": "管理部门"
                }
            },
            "resource_requirements": self._estimate_resources(recommendations),
            "success_criteria": self._define_success_criteria(recommendations),
            "monitoring_plan": {
                "frequency": "每日监测关键指标",
                "reporting": "每周生成进展报告",
                "review": "每月评估计划执行情况"
            }
        }
        
        return action_plan
    
    def _estimate_resources(self, recommendations: List[AdvisoryRecommendation]) -> Dict:
        """估算资源需求"""
        resources = {
            "personnel": [],
            "equipment": [],
            "materials": [],
            "budget": "待评估"
        }
        
        for rec in recommendations:
            if "投加" in rec.title or "处理" in rec.title:
                resources["personnel"].extend(["现场操作员", "技术员"])
                resources["equipment"].extend(["投加设备", "监测仪器"])
                resources["materials"].extend(["化学药剂", "处理材料"])
            
            if "排查" in rec.title or "检查" in rec.title:
                resources["personnel"].extend(["巡检员", "分析师"])
                resources["equipment"].extend(["检测设备", "采样工具"])
        
        # 去重
        for key in resources:
            if isinstance(resources[key], list):
                resources[key] = list(set(resources[key]))
        
        return resources
    
    def _define_success_criteria(self, recommendations: List[AdvisoryRecommendation]) -> List[str]:
        """定义成功标准"""
        criteria = []
        
        # 基于建议定义成功标准
        if any("异常" in rec.title for rec in recommendations):
            criteria.append("异常指标恢复正常范围")
        
        if any("改善" in rec.title for rec in recommendations):
            criteria.append("水质等级提升")
        
        if any("优化" in rec.title for rec in recommendations):
            criteria.append("工艺参数达到最优")
        
        # 通用标准
        criteria.extend([
            "无新的异常指标出现",
            "系统运行稳定",
            "监测数据完整准确"
        ])
        
        return list(set(criteria))
