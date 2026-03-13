"""
增强的AI Agent基类
支持多种模型接入和智能路由
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from .model_interface import ModelFactory, ModelConfig, ModelType, BaseModelInterface

logger = logging.getLogger(__name__)

@dataclass
class AgentResponse:
    """Agent响应数据"""
    success: bool
    data: Any
    confidence: float
    message: str
    execution_time: float
    model_used: str
    error_details: Optional[str] = None

class EnhancedBaseAgent(ABC):
    """增强的AI Agent基类"""
    
    def __init__(self, model_config: ModelConfig = None):
        """
        初始化Agent
        
        Args:
            model_config: 模型配置，如果为None则使用默认配置
        """
        self.model_config = model_config or self._get_default_config()
        self.model = ModelFactory.create_model(self.model_config)
        self.agent_name = self.__class__.__name__
        self.system_prompt = self._get_system_prompt()
        
    def _get_default_config(self) -> ModelConfig:
        """获取默认模型配置"""
        return ModelConfig(
            model_type=ModelType.LOCAL_LLM,
            api_url="http://localhost:8000/v1",
            model_name="local-model",
            temperature=0.7,
            max_tokens=2000,
            timeout=30
        )
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        pass
    
    @abstractmethod
    def _get_response_schema(self) -> Dict:
        """获取响应数据结构"""
        pass
    
    @abstractmethod
    async def _prepare_context(self, parameters: Dict) -> Dict:
        """准备上下文数据"""
        pass
    
    async def process(self, query: str, parameters: Dict = None) -> AgentResponse:
        """
        处理查询请求
        
        Args:
            query: 用户查询
            parameters: 额外参数
            
        Returns:
            Agent响应
        """
        start_time = datetime.now()
        parameters = parameters or {}
        
        try:
            # 检查模型可用性
            if not self.model.is_available():
                return AgentResponse(
                    success=False,
                    data=None,
                    confidence=0.0,
                    message=f"模型不可用: {self.model_config.model_type.value}",
                    execution_time=0.0,
                    model_used=self.model_config.model_type.value,
                    error_details="模型服务未启动或配置错误"
                )
            
            # 准备上下文
            context = await self._prepare_context(parameters)
            context['system_prompt'] = self.system_prompt
            
            # 生成响应
            response_text = await self.model.generate_text(query, context)
            
            # 解析结构化响应
            structured_response = await self._parse_response(response_text)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return AgentResponse(
                success=True,
                data=structured_response,
                confidence=self._calculate_confidence(structured_response),
                message="处理成功",
                execution_time=execution_time,
                model_used=self.model_config.model_type.value
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"{self.agent_name}处理异常: {str(e)}")
            
            return AgentResponse(
                success=False,
                data=None,
                confidence=0.0,
                message=f"处理失败: {str(e)}",
                execution_time=execution_time,
                model_used=self.model_config.model_type.value,
                error_details=str(e)
            )
    
    async def _parse_response(self, response_text: str) -> Dict:
        """解析模型响应"""
        try:
            # 尝试直接解析JSON
            return json.loads(response_text)
        except json.JSONDecodeError:
            # 如果不是JSON格式，包装为结构化数据
            return {
                "text_response": response_text,
                "type": "text",
                "content": response_text
            }
    
    def _calculate_confidence(self, response_data: Dict) -> float:
        """计算响应置信度"""
        # 基础置信度计算逻辑
        if response_data.get("type") == "text":
            return 0.7  # 文本响应的基础置信度
        elif response_data.get("confidence"):
            return float(response_data["confidence"])
        else:
            return 0.8  # 结构化数据的基础置信度
    
    async def process_with_fallback(self, query: str, parameters: Dict = None, 
                                   fallback_configs: List[ModelConfig] = None) -> AgentResponse:
        """
        带降级策略的处理
        
        Args:
            query: 用户查询
            parameters: 额外参数
            fallback_configs: 降级模型配置列表
            
        Returns:
            Agent响应
        """
        # 首先尝试主模型
        response = await self.process(query, parameters)
        
        if response.success:
            return response
        
        # 如果主模型失败，尝试降级模型
        if fallback_configs:
            logger.warning(f"主模型失败，尝试降级模型: {self.model_config.model_type.value}")
            
            for config in fallback_configs:
                try:
                    # 临时更换模型
                    original_config = self.model_config
                    self.model_config = config
                    self.model = ModelFactory.create_model(config)
                    
                    response = await self.process(query, parameters)
                    
                    if response.success:
                        logger.info(f"降级模型成功: {config.model_type.value}")
                        return response
                    
                    # 恢复原始配置
                    self.model_config = original_config
                    self.model = ModelFactory.create_model(original_config)
                    
                except Exception as e:
                    logger.error(f"降级模型 {config.model_type.value} 也失败: {str(e)}")
                    continue
        
        # 所有模型都失败
        return AgentResponse(
            success=False,
            data=None,
            confidence=0.0,
            message="所有模型都不可用",
            execution_time=0.0,
            model_used="none",
            error_details="主模型和所有降级模型都不可用"
        )

class SmartAgentRouter:
    """智能Agent路由器"""
    
    def __init__(self):
        self.model_configs = {}
        self.agent_instances = {}
        self._load_configurations()
    
    def _load_configurations(self):
        """加载模型配置"""
        # 从Django settings加载配置
        from django.conf import settings
        
        # 默认配置
        self.model_configs = {
            'primary': ModelConfig(
                model_type=ModelType.LOCAL_LLM,
                api_url=getattr(settings, 'AI_LOCAL_URL', 'http://localhost:8000/v1'),
                model_name=getattr(settings, 'AI_LOCAL_MODEL', 'local-model'),
                temperature=getattr(settings, 'AI_TEMPERATURE', 0.7),
                max_tokens=getattr(settings, 'AI_MAX_TOKENS', 2000),
                timeout=getattr(settings, 'AI_TIMEOUT', 30)
            ),
            'openai': ModelConfig(
                model_type=ModelType.OPENAI_API,
                api_key=getattr(settings, 'OPENAI_API_KEY', None),
                model_name=getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo'),
                temperature=getattr(settings, 'AI_TEMPERATURE', 0.7),
                max_tokens=getattr(settings, 'AI_MAX_TOKENS', 2000)
            ),
            'claude': ModelConfig(
                model_type=ModelType.CLAUDE_API,
                api_key=getattr(settings, 'CLAUDE_API_KEY', None),
                model_name=getattr(settings, 'CLAUDE_MODEL', 'claude-3-sonnet-20240229'),
                temperature=getattr(settings, 'AI_TEMPERATURE', 0.7),
                max_tokens=getattr(settings, 'AI_MAX_TOKENS', 2000)
            )
        }
    
    def get_best_config(self) -> ModelConfig:
        """获取最佳可用配置"""
        # 按优先级检查模型可用性
        priority_order = ['primary', 'openai', 'claude']
        
        for config_name in priority_order:
            config = self.model_configs[config_name]
            model = ModelFactory.create_model(config)
            
            if model.is_available():
                logger.info(f"使用模型配置: {config_name}")
                return config
        
        # 如果都不可用，返回默认配置
        logger.warning("所有模型都不可用，使用默认配置")
        return self.model_configs['primary']
    
    def get_fallback_configs(self) -> List[ModelConfig]:
        """获取降级配置列表"""
        configs = []
        
        # 排除主配置，获取其他可用配置
        for name, config in self.model_configs.items():
            if name != 'primary':
                model = ModelFactory.create_model(config)
                if model.is_available():
                    configs.append(config)
        
        return configs
