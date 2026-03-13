#!/usr/bin/env python3
"""
AI服务启动脚本
启动本地LLM服务或检查API连接
"""

import os
import sys
import time
import requests
import subprocess
import logging
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent / 'src'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIServiceManager:
    """AI服务管理器"""
    
    def __init__(self):
        self.local_llm_url = 'http://localhost:8000/v1'
        self.health_check_url = f'{self.local_llm_url}/models'
        self.process = None
    
    def check_local_llm(self) -> bool:
        """检查本地LLM是否运行"""
        try:
            response = requests.get(self.health_check_url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_ollama(self) -> bool:
        """启动Ollama服务"""
        try:
            logger.info("正在启动Ollama服务...")
            
            # 检查Ollama是否已安装
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("Ollama未安装，请先安装Ollama")
                logger.info("安装命令: curl -fsSL https://ollama.ai/install.sh | sh")
                return False
            
            # 启动Ollama服务
            self.process = subprocess.Popen(['ollama', 'serve'])
            
            # 等待服务启动
            for i in range(30):  # 最多等待30秒
                time.sleep(1)
                if self.check_local_llm():
                    logger.info("Ollama服务启动成功")
                    return True
                logger.info(f"等待Ollama服务启动... ({i+1}/30)")
            
            logger.error("Ollama服务启动超时")
            return False
            
        except Exception as e:
            logger.error(f"启动Ollama失败: {str(e)}")
            return False
    
    def pull_model(self, model_name: str = 'llama2') -> bool:
        """拉取模型"""
        try:
            logger.info(f"正在拉取模型: {model_name}")
            
            result = subprocess.run(['ollama', 'pull', model_name], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"模型 {model_name} 拉取成功")
                return True
            else:
                logger.error(f"模型 {model_name} 拉取失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"拉取模型失败: {str(e)}")
            return False
    
    def test_model(self, model_name: str = 'llama2') -> bool:
        """测试模型"""
        try:
            logger.info(f"正在测试模型: {model_name}")
            
            data = {
                "model": model_name,
                "prompt": "Hello, how are you?",
                "stream": False
            }
            
            response = requests.post(
                f'{self.local_llm_url}/generate',
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"模型测试成功: {result.get('response', '')[:50]}...")
                return True
            else:
                logger.error(f"模型测试失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"测试模型失败: {str(e)}")
            return False
    
    def start_lm_studio(self) -> bool:
        """启动LM Studio服务"""
        try:
            logger.info("正在启动LM Studio...")
            
            # 检查LM Studio是否在运行
            if self.check_local_llm():
                logger.info("LM Studio已在运行")
                return True
            
            logger.info("请手动启动LM Studio并加载模型")
            logger.info("启动后访问: http://localhost:1234")
            return False
            
        except Exception as e:
            logger.error(f"启动LM Studio失败: {str(e)}")
            return False
    
    def check_openai_api(self) -> bool:
        """检查OpenAI API连接"""
        try:
            from django.conf import settings
            
            api_key = getattr(settings, 'OPENAI_API_KEY', None)
            if not api_key:
                logger.warning("未配置OpenAI API密钥")
                return False
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                'https://api.openai.com/v1/models',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("OpenAI API连接正常")
                return True
            else:
                logger.error(f"OpenAI API连接失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"检查OpenAI API失败: {str(e)}")
            return False
    
    def check_claude_api(self) -> bool:
        """检查Claude API连接"""
        try:
            from django.conf import settings
            
            api_key = getattr(settings, 'CLAUDE_API_KEY', None)
            if not api_key:
                logger.warning("未配置Claude API密钥")
                return False
            
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json={
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "test"}]
                },
                timeout=10
            )
            
            if response.status_code in [200, 400]:  # 400可能是参数错误，但说明API可用
                logger.info("Claude API连接正常")
                return True
            else:
                logger.error(f"Claude API连接失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"检查Claude API失败: {str(e)}")
            return False
    
    def start_service(self, service_type: str = 'auto') -> bool:
        """启动AI服务"""
        logger.info(f"正在启动AI服务: {service_type}")
        
        if service_type == 'auto':
            # 自动选择最佳服务
            if self.check_local_llm():
                logger.info("本地LLM服务已运行")
                return True
            
            if self.check_openai_api():
                logger.info("使用OpenAI API")
                return True
            
            if self.check_claude_api():
                logger.info("使用Claude API")
                return True
            
            # 尝试启动本地服务
            logger.info("尝试启动本地LLM服务...")
            
            # 尝试Ollama
            if self.start_ollama():
                if self.pull_model('llama2'):
                    if self.test_model('llama2'):
                        return True
            
            # 尝试LM Studio
            if self.start_lm_studio():
                return True
            
            logger.error("无法启动任何AI服务")
            return False
        
        elif service_type == 'ollama':
            return self.start_ollama()
        
        elif service_type == 'lm_studio':
            return self.start_lm_studio()
        
        elif service_type == 'openai':
            return self.check_openai_api()
        
        elif service_type == 'claude':
            return self.check_claude_api()
        
        else:
            logger.error(f"未知的服务类型: {service_type}")
            return False
    
    def stop_service(self):
        """停止服务"""
        if self.process:
            logger.info("正在停止AI服务...")
            self.process.terminate()
            self.process.wait()
            logger.info("AI服务已停止")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI服务管理器')
    parser.add_argument('--service', choices=['auto', 'ollama', 'lm_studio', 'openai', 'claude'],
                       default='auto', help='服务类型')
    parser.add_argument('--check-only', action='store_true', help='仅检查服务状态')
    parser.add_argument('--model', default='llama2', help='模型名称')
    
    args = parser.parse_args()
    
    manager = AIServiceManager()
    
    try:
        if args.check_only:
            # 仅检查服务状态
            logger.info("检查AI服务状态...")
            
            services = {
                '本地LLM': manager.check_local_llm(),
                'OpenAI API': manager.check_openai_api(),
                'Claude API': manager.check_claude_api()
            }
            
            available_services = [name for name, available in services.items() if available]
            
            if available_services:
                logger.info(f"可用服务: {', '.join(available_services)}")
            else:
                logger.warning("没有可用的AI服务")
                logger.info("请启动本地LLM服务或配置API密钥")
        
        else:
            # 启动服务
            success = manager.start_service(args.service)
            
            if success:
                logger.info("AI服务启动成功")
                
                if args.service in ['ollama', 'auto'] and manager.check_local_llm():
                    logger.info(f"本地LLM服务地址: {manager.local_llm_url}")
                    logger.info("可以使用以下命令测试:")
                    logger.info(f"curl -X POST {manager.local_llm_url}/chat/completions \\")
                    logger.info('  -H "Content-Type: application/json" \\')
                    logger.info('  -d \'{"model":"llama2","messages":[{"role":"user","content":"Hello"}]}\'')
                
                # 保持服务运行
                try:
                    while True:
                        time.sleep(60)
                        if not manager.check_local_llm():
                            logger.warning("本地LLM服务断开连接")
                            break
                except KeyboardInterrupt:
                    logger.info("收到停止信号")
            else:
                logger.error("AI服务启动失败")
                sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("收到停止信号")
    finally:
        manager.stop_service()

if __name__ == '__main__':
    main()
