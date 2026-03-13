"""
AI模型接口
支持多种AI模型接入方式：API调用、本地模型、OpenAI等
"""

import json
import requests
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """模型类型"""
    OPENAI_API = "openai_api"
    LOCAL_LLM = "local_llm"
    CLAUDE_API = "claude_api"
    GEMINI_API = "gemini_api"
    CUSTOM_API = "custom_api"

@dataclass
class ModelConfig:
    """模型配置"""
    model_type: ModelType
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    model_name: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 30
    custom_headers: Optional[Dict] = None

class BaseModelInterface(ABC):
    """AI模型基础接口"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model_type = config.model_type
    
    @abstractmethod
    async def generate_text(self, prompt: str, context: Dict = None) -> str:
        """生成文本"""
        pass
    
    @abstractmethod
    async def generate_structured(self, prompt: str, schema: Dict) -> Dict:
        """生成结构化数据"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查模型是否可用"""
        pass

class OpenAIModel(BaseModelInterface):
    """OpenAI API模型"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.model_name = config.model_name or "gpt-3.5-turbo"
        self.base_url = config.api_url or "https://api.openai.com/v1"
    
    async def generate_text(self, prompt: str, context: Dict = None) -> str:
        """使用OpenAI API生成文本"""
        try:
            messages = []
            
            # 添加系统提示
            if context and 'system_prompt' in context:
                messages.append({"role": "system", "content": context['system_prompt']})
            
            # 添加用户提示
            messages.append({"role": "user", "content": prompt})
            
            # 添加上下文
            if context and 'context_data' in context:
                messages.append({
                    "role": "system", 
                    "content": f"上下文信息：\n{json.dumps(context['context_data'], ensure_ascii=False, indent=2)}"
                })
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model_name,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"OpenAI API错误: {response.status_code} - {response.text}")
                return f"API调用失败: {response.status_code}"
                
        except Exception as e:
            logger.error(f"OpenAI模型调用异常: {str(e)}")
            return f"模型调用异常: {str(e)}"
    
    async def generate_structured(self, prompt: str, schema: Dict) -> Dict:
        """生成结构化数据"""
        structured_prompt = f"""
请根据以下要求生成JSON格式的数据：

要求：
{prompt}

JSON格式要求：
{json.dumps(schema, ensure_ascii=False, indent=2)}

请直接返回JSON数据，不要包含其他说明文字：
"""
        
        response = await self.generate_text(structured_prompt)
        
        try:
            # 尝试解析JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # 如果解析失败，返回原始文本
            return {"error": "JSON解析失败", "raw_response": response}
    
    def is_available(self) -> bool:
        """检查OpenAI API是否可用"""
        if not self.api_key:
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
        except:
            return False

class LocalLLMModel(BaseModelInterface):
    """本地大语言模型"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.api_url = config.api_url or "http://localhost:8000/v1"
        self.model_name = config.model_name or "local-model"
    
    async def generate_text(self, prompt: str, context: Dict = None) -> str:
        """使用本地LLM生成文本"""
        try:
            messages = []
            
            # 添加系统提示
            if context and 'system_prompt' in context:
                messages.append({"role": "system", "content": context['system_prompt']})
            
            # 添加用户提示
            messages.append({"role": "user", "content": prompt})
            
            # 添加上下文
            if context and 'context_data' in context:
                messages.append({
                    "role": "system", 
                    "content": f"上下文信息：\n{json.dumps(context['context_data'], ensure_ascii=False, indent=2)}"
                })
            
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.config.custom_headers:
                headers.update(self.config.custom_headers)
            
            data = {
                "model": self.model_name,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens
            }
            
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"本地LLM API错误: {response.status_code} - {response.text}")
                return f"本地模型调用失败: {response.status_code}"
                
        except Exception as e:
            logger.error(f"本地LLM调用异常: {str(e)}")
            return f"本地模型调用异常: {str(e)}"
    
    async def generate_structured(self, prompt: str, schema: Dict) -> Dict:
        """生成结构化数据"""
        structured_prompt = f"""
请根据以下要求生成JSON格式的数据：

要求：
{prompt}

JSON格式要求：
{json.dumps(schema, ensure_ascii=False, indent=2)}

请直接返回JSON数据，不要包含其他说明文字：
"""
        
        response = await self.generate_text(structured_prompt)
        
        try:
            # 尝试解析JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # 如果解析失败，返回原始文本
            return {"error": "JSON解析失败", "raw_response": response}
    
    def is_available(self) -> bool:
        """检查本地LLM是否可用"""
        try:
            response = requests.get(f"{self.api_url}/models", timeout=10)
            return response.status_code == 200
        except:
            return False

class ClaudeModel(BaseModelInterface):
    """Claude API模型"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.model_name = config.model_name or "claude-3-sonnet-20240229"
        self.base_url = config.api_url or "https://api.anthropic.com/v1"
    
    async def generate_text(self, prompt: str, context: Dict = None) -> str:
        """使用Claude API生成文本"""
        try:
            # 构建消息
            message_content = prompt
            
            if context and 'context_data' in context:
                message_content += f"\n\n上下文信息：\n{json.dumps(context['context_data'], ensure_ascii=False, indent=2)}"
            
            if context and 'system_prompt' in context:
                system_prompt = context['system_prompt']
            else:
                system_prompt = "你是一个专业的水质监控分析助手。"
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": self.model_name,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": message_content}
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=data,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["content"][0]["text"]
            else:
                logger.error(f"Claude API错误: {response.status_code} - {response.text}")
                return f"Claude API调用失败: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Claude模型调用异常: {str(e)}")
            return f"Claude模型调用异常: {str(e)}"
    
    async def generate_structured(self, prompt: str, schema: Dict) -> Dict:
        """生成结构化数据"""
        structured_prompt = f"""
请根据以下要求生成JSON格式的数据：

要求：
{prompt}

JSON格式要求：
{json.dumps(schema, ensure_ascii=False, indent=2)}

请直接返回JSON数据，不要包含其他说明文字：
"""
        
        response = await self.generate_text(structured_prompt)
        
        try:
            # 尝试解析JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # 如果解析失败，返回原始文本
            return {"error": "JSON解析失败", "raw_response": response}
    
    def is_available(self) -> bool:
        """检查Claude API是否可用"""
        if not self.api_key:
            return False
        
        try:
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                json={
                    "model": self.model_name,
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "test"}]
                },
                timeout=10
            )
            
            return response.status_code in [200, 400]  # 400可能是参数错误，但说明API可用
        except:
            return False

class ModelFactory:
    """模型工厂类"""
    
    @staticmethod
    def create_model(config: ModelConfig) -> BaseModelInterface:
        """根据配置创建模型实例"""
        if config.model_type == ModelType.OPENAI_API:
            return OpenAIModel(config)
        elif config.model_type == ModelType.LOCAL_LLM:
            return LocalLLMModel(config)
        elif config.model_type == ModelType.CLAUDE_API:
            return ClaudeModel(config)
        else:
            raise ValueError(f"不支持的模型类型: {config.model_type}")
    
    @staticmethod
    def create_from_settings(settings: Dict) -> BaseModelInterface:
        """从设置创建模型"""
        model_type_str = settings.get('MODEL_TYPE', 'local_llm')
        model_type = ModelType(model_type_str)
        
        config = ModelConfig(
            model_type=model_type,
            api_key=settings.get('API_KEY'),
            api_url=settings.get('API_URL'),
            model_name=settings.get('MODEL_NAME'),
            temperature=settings.get('TEMPERATURE', 0.7),
            max_tokens=settings.get('MAX_TOKENS', 2000),
            timeout=settings.get('TIMEOUT', 30),
            custom_headers=settings.get('CUSTOM_HEADERS')
        )
        
        return ModelFactory.create_model(config)
