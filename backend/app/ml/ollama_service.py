import httpx
import json
import logging
from typing import Dict, List, Optional, Union, Any, Generator
import ollama

logger = logging.getLogger(__name__)

class OllamaService:
    """Ollama服务接口，用于与本地运行的Ollama服务进行交互"""
    
    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "deepseek-r1:7b", lazy_connect: bool = True):
        """
        初始化Ollama服务
        
        Args:
            base_url: Ollama服务的基础URL
            default_model: 默认使用的模型名称
            lazy_connect: 是否延迟连接（仅在首次调用时连接）
        """
        self.base_url = base_url
        self.default_model = default_model
        self.client = None
        self.available = False
        self.initialized = False
        
        # 如果不是延迟连接，则立即初始化
        if not lazy_connect:
            self._initialize_client()
        else:
            logger.info(f"OllamaService配置完成，将在首次使用时尝试连接: {base_url}")
    
    def _initialize_client(self):
        """初始化客户端连接"""
        if self.initialized:
            return
            
        self.initialized = True
        # 尝试初始化客户端
        try:
            self.client = ollama.Client(host=self.base_url)
            # 测试连接
            try:
                self.client.list()
                self.available = True
                logger.info(f"OllamaService初始化成功，基础URL: {self.base_url}, 默认模型: {self.default_model}")
            except Exception as e:
                logger.warning(f"Ollama服务连接测试失败: {str(e)}，服务可能不可用")
        except Exception as e:
            logger.error(f"OllamaService初始化失败: {str(e)}")
            
    
    async def generate(self, prompt: str, model: Optional[str] = None, 
                      system: Optional[str] = None, temperature: float = 0.7,
                      max_tokens: int = 2000) -> Dict[str, Any]:
        """
        生成文本响应
        
        Args:
            prompt: 用户输入的提示词
            model: 使用的模型名称，如果为None则使用默认模型
            system: 系统提示词
            temperature: 温度参数，控制生成的随机性
            max_tokens: 最大生成的token数量
            
        Returns:
            包含生成文本的字典
        """
        # 延迟初始化
        if not self.initialized:
            self._initialize_client()
            
        # 检查服务是否可用
        if not self.available or self.client is None:
            return self._create_error_response("Ollama服务不可用，请确保Ollama已启动")
        
        try:
            model_name = model or self.default_model
            logger.info(f"使用模型 {model_name} 生成回复，提示词: {prompt[:50]}...")
            
            # 构建请求参数
            params = {
                "model": model_name,
                "prompt": prompt,
                # 注意: ollama Python客户端不支持temperature参数
                # "temperature": temperature,
                # "max_tokens": max_tokens,
            }
            
            if system:
                params["system"] = system
                
            # 调用Ollama API
            response = self.client.generate(**params)
            
            return {
                "response": response["response"],
                "model": model_name,
                "total_duration": response.get("total_duration", 0),
                "prompt_eval_count": response.get("prompt_eval_count", 0),
                "eval_count": response.get("eval_count", 0)
            }
            
        except Exception as e:
            logger.error(f"Ollama生成失败: {str(e)}")
            return self._create_error_response(f"Ollama生成失败: {str(e)}")
    
    async def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None,
                  system: Optional[str] = None, temperature: float = 0.7,
                  max_tokens: int = 2000) -> Dict[str, Any]:
        """
        聊天接口，支持多轮对话
        
        Args:
            messages: 对话历史，格式为[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            model: 使用的模型名称，如果为None则使用默认模型
            system: 系统提示词
            temperature: 温度参数，控制生成的随机性
            max_tokens: 最大生成的token数量
            
        Returns:
            包含生成文本的字典
        """
        # 延迟初始化
        if not self.initialized:
            self._initialize_client()
            
        # 检查服务是否可用
        if not self.available or self.client is None:
            return self._create_error_response("Ollama服务不可用，请确保Ollama已启动")
        
        try:
            model_name = model or self.default_model
            logger.info(f"使用模型 {model_name} 进行聊天，消息数量: {len(messages)}")
            
            # 处理系统提示词
            chat_messages = messages.copy()
            if system:
                # 如果提供了系统提示词，将其添加到消息列表开头
                logger.info(f"添加系统提示词: {system[:50]}...")
                system_message = {"role": "system", "content": system}
                chat_messages.insert(0, system_message)
            
            # 构建请求参数
            params = {
                "model": model_name,
                "messages": chat_messages,
                # 注意: ollama Python客户端不支持temperature参数
                # "temperature": temperature,
                # "max_tokens": max_tokens,
            }
            
            # 调用Ollama API
            response = self.client.chat(**params)
            
            return {
                "message": response["message"],
                "model": model_name,
                "total_duration": response.get("total_duration", 0),
                "prompt_eval_count": response.get("prompt_eval_count", 0),
                "eval_count": response.get("eval_count", 0)
            }
            
        except Exception as e:
            logger.error(f"Ollama聊天失败: {str(e)}")
            return self._create_error_response(f"Ollama聊天失败: {str(e)}")
    
    async def stream_generate(self, prompt: str, model: Optional[str] = None,
                             system: Optional[str] = None, temperature: float = 0.7,
                             max_tokens: int = 2000) -> Generator[Dict[str, Any], None, None]:
        """
        流式生成文本响应
        
        Args:
            prompt: 用户输入的提示词
            model: 使用的模型名称，如果为None则使用默认模型
            system: 系统提示词
            temperature: 温度参数，控制生成的随机性
            max_tokens: 最大生成的token数量
            
        Returns:
            生成文本的流
        """
        # 延迟初始化
        if not self.initialized:
            self._initialize_client()
            
        # 检查服务是否可用
        if not self.available or self.client is None:
            yield {"response": "Ollama服务不可用，请确保Ollama已启动", "done": True, "error": True}
            return
        
        try:
            model_name = model or self.default_model
            logger.info(f"使用模型 {model_name} 流式生成回复，提示词: {prompt[:50]}...")
            
            # 构建请求参数
            params = {
                "model": model_name,
                "prompt": prompt,
                # 注意: ollama Python客户端不支持temperature参数
                # "temperature": temperature,
                # "max_tokens": max_tokens,
                "stream": True
            }
            
            if system:
                params["system"] = system
                
            # 调用Ollama API
            for chunk in self.client.generate(**params):
                yield chunk
                
        except Exception as e:
            logger.error(f"Ollama流式生成失败: {str(e)}")
            yield {"response": f"Ollama流式生成失败: {str(e)}", "done": True, "error": True}
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """
        获取可用的模型列表
        
        Returns:
            模型列表
        """
        # 延迟初始化
        if not self.initialized:
            self._initialize_client()
            
        # 检查服务是否可用
        if not self.available or self.client is None:
            return []
        
        try:
            models = self.client.list()
            return models["models"]
        except Exception as e:
            logger.error(f"获取模型列表失败: {str(e)}")
            return []
    
    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        获取模型信息
        
        Args:
            model_name: 模型名称
            
        Returns:
            模型信息
        """
        # 延迟初始化
        if not self.initialized:
            self._initialize_client()
            
        # 检查服务是否可用
        if not self.available or self.client is None:
            return {"error": "Ollama服务不可用，请确保Ollama已启动"}
        
        try:
            model_info = self.client.show(model_name)
            return model_info
        except Exception as e:
            logger.error(f"获取模型信息失败: {str(e)}")
            return {"error": f"获取模型信息失败: {str(e)}"}
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """创建统一的错误响应"""
        return {
            "response": error_message,
            "model": self.default_model,
            "error": True
        }

# 创建Ollama服务实例
ollama_service = OllamaService() 