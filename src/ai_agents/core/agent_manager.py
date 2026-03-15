"""
AI Agent管理器
负责调度和管理各个专业智能体
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class AgentType(Enum):
    """智能体类型"""
    DATA_QUERY = "data_query"          # 数据查询Agent
    ANALYSIS = "analysis"              # 分析Agent  
    PREDICTION = "prediction"          # 预测Agent
    ANOMALY_DETECTION = "anomaly"      # 异常检测Agent
    REPORT_GENERATION = "report"       # 报告生成Agent
    ADVISORY = "advisory"              # 建议Agent

@dataclass
class AgentTask:
    """Agent任务"""
    task_id: str
    agent_type: AgentType
    query: str
    parameters: Dict[str, Any]
    priority: int = 1
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class AgentResult:
    """Agent执行结果"""
    task_id: str
    agent_type: AgentType
    success: bool
    result: Any
    confidence: float
    execution_time: float
    error_message: Optional[str] = None

class AgentManager:
    """AI Agent管理器"""
    
    def __init__(self):
        self.agents = {}
        self.task_queue = asyncio.Queue()
        self.results_cache = {}
        self._register_agents()
    
    def _register_agents(self):
        """注册所有智能体"""
        from .enhanced_data_query_agent import EnhancedDataQueryAgent
        from .enhanced_agent import SmartAgentRouter
        
        # 创建增强数据查询Agent
        self.data_query_agent = EnhancedDataQueryAgent()
        
        # 创建智能路由器
        self.router = SmartAgentRouter()
        
        # 注册到agents字典
        self.agents = {
            AgentType.DATA_QUERY: self.data_query_agent,
        }
    
    async def process_query(self, user_query: str, context: Dict = None) -> Dict:
        """
        处理用户查询
        
        Args:
            user_query: 用户查询
            context: 上下文信息
            
        Returns:
            处理结果
        """
        try:
            # 使用增强数据查询Agent处理查询
            result = await self.data_query_agent.process_query(user_query, context)
            return result
        except Exception as e:
            return {
                'success': False,
                'error': f'查询处理失败: {str(e)}',
                'agent': 'data_query',
                'confidence': 0.0
            }
    
    async def _identify_intent(self, query: str) -> AgentType:
        """识别用户意图"""
        query_lower = query.lower()
        
        # 关键词匹配进行意图识别
        intent_keywords = {
            AgentType.DATA_QUERY: ['查询', '多少', '数据', '当前', '最新', '实时'],
            AgentType.ANALYSIS: ['分析', '趋势', '变化', '原因', '为什么', '怎么样'],
            AgentType.PREDICTION: ['预测', '未来', '明天', '后天', '会', '预计'],
            AgentType.ANOMALY_DETECTION: ['异常', '超标', '警告', '危险', '不正常'],
            AgentType.REPORT_GENERATION: ['报告', '总结', '汇总', '统计'],
            AgentType.ADVISORY: ['建议', '怎么办', '如何', '措施', '解决方案']
        }
        
        for agent_type, keywords in intent_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return agent_type
        
        # 默认返回数据查询
        return AgentType.DATA_QUERY
    
    async def _decompose_task(self, query: str, intent: AgentType, context: Dict) -> List[AgentTask]:
        """分解复杂任务为子任务"""
        tasks = []
        
        if intent == AgentType.ANALYSIS:
            # 分析任务可能需要多个子任务
            tasks.append(AgentTask(
                task_id="data_collection",
                agent_type=AgentType.DATA_QUERY,
                query=query,
                parameters={"context": context}
            ))
            tasks.append(AgentTask(
                task_id="analysis",
                agent_type=AgentType.ANALYSIS,
                query=query,
                parameters={"context": context}
            ))
            tasks.append(AgentTask(
                task_id="advisory",
                agent_type=AgentType.ADVISORY,
                query=query,
                parameters={"context": context}
            ))
        else:
            # 单一任务
            tasks.append(AgentTask(
                task_id="main_task",
                agent_type=intent,
                query=query,
                parameters={"context": context}
            ))
        
        return tasks
    
    async def _execute_tasks(self, tasks: List[AgentTask]) -> List[AgentResult]:
        """并行执行任务"""
        async def execute_single_task(task: AgentTask) -> AgentResult:
            agent = self.agents[task.agent_type]
            start_time = datetime.now()
            
            try:
                result = await agent.execute(task.query, task.parameters)
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return AgentResult(
                    task_id=task.task_id,
                    agent_type=task.agent_type,
                    success=True,
                    result=result,
                    confidence=result.get('confidence', 0.8),
                    execution_time=execution_time
                )
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds()
                return AgentResult(
                    task_id=task.task_id,
                    agent_type=task.agent_type,
                    success=False,
                    result=None,
                    confidence=0.0,
                    execution_time=execution_time,
                    error_message=str(e)
                )
        
        # 并行执行所有任务
        results = await asyncio.gather(*[execute_single_task(task) for task in tasks])
        return results
    
    async def _synthesize_results(self, query: str, intent: AgentType, results: List[AgentResult]) -> Dict:
        """融合多个Agent的结果"""
        successful_results = [r for r in results if r.success]
        
        if not successful_results:
            return {
                "success": False,
                "message": "抱歉，处理您的请求时遇到了问题",
                "suggestions": ["请检查查询内容是否正确", "稍后重试"]
            }
        
        if len(successful_results) == 1:
            # 单一结果直接返回
            result = successful_results[0].result
            result["agent_type"] = successful_results[0].agent_type.value
            result["confidence"] = successful_results[0].confidence
            return result
        
        # 多结果融合
        synthesized = {
            "success": True,
            "query": query,
            "intent": intent.value,
            "agent_results": {},
            "synthesis": {},
            "confidence": 0.0
        }
        
        # 收集各Agent结果
        for result in successful_results:
            synthesized["agent_results"][result.task_id] = {
                "agent_type": result.agent_type.value,
                "result": result.result,
                "confidence": result.confidence
            }
        
        # 生成综合回答
        synthesized["synthesis"] = await self._generate_synthesis(query, successful_results)
        synthesized["confidence"] = sum(r.confidence for r in successful_results) / len(successful_results)
        
        return synthesized
    
    async def _generate_synthesis(self, query: str, results: List[AgentResult]) -> Dict:
        """生成综合回答"""
        synthesis = {
            "summary": "",
            "key_points": [],
            "recommendations": [],
            "data_insights": {}
        }
        
        # 从各结果中提取关键信息
        for result in results:
            if result.agent_type == AgentType.DATA_QUERY:
                synthesis["data_insights"] = result.result.get("data", {})
            elif result.agent_type == AgentType.ANALYSIS:
                synthesis["key_points"].extend(result.result.get("insights", []))
            elif result.agent_type == AgentType.ADVISORY:
                synthesis["recommendations"].extend(result.result.get("recommendations", []))
        
        # 生成总结
        if synthesis["data_insights"]:
            synthesis["summary"] = f"基于当前数据分析，{query}"
        
        return synthesis

# 全局Agent管理器实例
agent_manager = AgentManager()
