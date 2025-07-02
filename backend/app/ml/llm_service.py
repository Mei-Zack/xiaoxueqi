from typing import List, Dict, Any, Tuple, Optional
import os
import json
from datetime import datetime
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from app.core.config import settings
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMService:
    """大模型服务类，负责模型加载、推理和知识库管理"""
    
    def __init__(self):
        """初始化大模型服务"""
        self.model = None
        self.tokenizer = None
        self.embedding_model = None
        self.vector_db = None
        self.knowledge_collection = None
        
        # 不再初始化向量数据库，将在需要时初始化
        # self._init_vector_db()
        
        # 懒加载模型，首次使用时才加载
        logger.info("LLM服务初始化完成，模型将在首次使用时加载")
    
    def _init_vector_db(self):
        """初始化向量数据库"""
        try:
            # 确保向量数据库目录存在
            os.makedirs(settings.VECTOR_STORE_DIR, exist_ok=True)
            
            # 初始化ChromaDB客户端
            self.vector_db = chromadb.PersistentClient(path=settings.VECTOR_STORE_DIR)
            
            # 尝试加载embedding模型 - 使用更短的超时
            try:
                # 设置更短的超时时间
                import urllib.request
                import socket
                socket.setdefaulttimeout(5)  # 减少到5秒超时
                
                # 创建一个简单的嵌入函数，暂不加载模型
                # 仅在实际需要时再加载SentenceTransformer模型
                self.embedding_model = None
                
                # 获取知识库集合，但不立即设置embedding_function
                try:
                    self.knowledge_collection = self.vector_db.get_collection(name="diabetes_knowledge")
                    logger.info(f"已加载知识库集合，包含 {self.knowledge_collection.count()} 条记录")
                except Exception:
                    try:
                        # 创建集合但暂不设置embedding_function
                        self.knowledge_collection = self.vector_db.create_collection(name="diabetes_knowledge")
                        logger.info("已创建新的知识库集合")
                    except Exception as e:
                        logger.error(f"创建知识库集合失败: {str(e)}")
                        self.knowledge_collection = None
            
            except Exception as e:
                logger.error(f"初始化知识库失败: {str(e)}")
                self.embedding_model = None
                self.knowledge_collection = None
        
        except Exception as e:
            logger.error(f"初始化向量数据库失败: {str(e)}")
            self.vector_db = None
            self.knowledge_collection = None
    
    def _load_model(self):
        """加载大模型"""
        if self.model is not None:
            return
        
        try:
            logger.info(f"正在加载模型: {settings.MODEL_PATH}")
            
            # 加载分词器
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.MODEL_PATH, 
                trust_remote_code=True
            )
            
            # 根据量化设置加载模型
            if settings.MODEL_QUANTIZATION == "int4":
                self.model = AutoModelForCausalLM.from_pretrained(
                    settings.MODEL_PATH,
                    torch_dtype=torch.float16,
                    device_map=settings.MODEL_DEVICE,
                    trust_remote_code=True,
                    load_in_4bit=True
                )
            elif settings.MODEL_QUANTIZATION == "int8":
                self.model = AutoModelForCausalLM.from_pretrained(
                    settings.MODEL_PATH,
                    torch_dtype=torch.float16,
                    device_map=settings.MODEL_DEVICE,
                    trust_remote_code=True,
                    load_in_8bit=True
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    settings.MODEL_PATH,
                    torch_dtype=torch.float16,
                    device_map=settings.MODEL_DEVICE,
                    trust_remote_code=True
                )
            
            logger.info("模型加载完成")
        
        except Exception as e:
            logger.error(f"加载模型失败: {str(e)}")
            raise RuntimeError(f"加载模型失败: {str(e)}")
    
    def generate_response(
        self, 
        user_message: str, 
        user_context: Dict[str, Any] = None,
        knowledge_sources: List[Dict[str, Any]] = None,
        history: List[Dict[str, str]] = None
    ) -> Tuple[str, Optional[List[Dict[str, Any]]]]:
        """生成回复"""
        try:
            # 检查是否可以加载模型
            can_use_model = True
            try:
                # 懒加载模型
                if self.model is None:
                    self._load_model()
            except Exception as e:
                logger.error(f"加载模型失败: {str(e)}")
                can_use_model = False
            
            # 如果无法加载模型，返回默认回复
            if not can_use_model:
                default_response = "很抱歉，智能助手目前无法使用。请稍后再试或联系管理员。"
                return default_response, None
            
            # 构建系统提示词
            system_prompt = self._build_system_prompt(user_context, knowledge_sources)
            
            # 构建对话历史
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加历史消息
            if history:
                messages.extend(history)
            
            # 添加当前用户消息
            messages.append({"role": "user", "content": user_message})
            
            # 转换为模型输入格式
            prompt = self.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            # 生成回复
            inputs = self.tokenizer(prompt, return_tensors="pt").to(settings.MODEL_DEVICE)
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=1024,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1,
                do_sample=True
            )
            
            # 解码回复
            response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
            
            # 返回回复和知识源
            return response.strip(), knowledge_sources
        
        except Exception as e:
            logger.error(f"生成回复失败: {str(e)}")
            default_response = "很抱歉，我在处理您的问题时遇到了一些技术问题。请稍后再试或以不同方式提问。"
            return default_response, None
    
    def _build_system_prompt(
        self, 
        user_context: Dict[str, Any] = None,
        knowledge_sources: List[Dict[str, Any]] = None
    ) -> str:
        """构建系统提示词"""
        # 基础系统提示词
        system_prompt = """你是一个专业的糖尿病健康助理，名为"糖管家"。你的任务是帮助用户管理糖尿病，提供健康建议，解答相关问题。
请遵循以下原则：
1. 提供准确、科学的糖尿病相关信息和建议
2. 根据用户的具体情况（如血糖水平、糖尿病类型等）提供个性化建议
3. 使用友好、专业的语气，避免医学术语过于专业化
4. 不要假装你是医生，重要医疗决策应建议用户咨询专业医生
5. 回答要简洁明了，突出重点
"""
        
        # 添加用户上下文
        if user_context:
            user_info = []
            if user_context.get("name"):
                user_info.append(f"姓名: {user_context['name']}")
            if user_context.get("gender"):
                user_info.append(f"性别: {user_context['gender']}")
            if user_context.get("age"):
                user_info.append(f"年龄: {user_context['age']}岁")
            if user_context.get("diabetes_type"):
                user_info.append(f"糖尿病类型: {user_context['diabetes_type']}")
            if user_context.get("height") and user_context.get("weight"):
                height_m = user_context["height"] / 100
                bmi = round(user_context["weight"] / (height_m * height_m), 1)
                user_info.append(f"身高: {user_context['height']}cm, 体重: {user_context['weight']}kg, BMI: {bmi}")
            if user_context.get("target_glucose_min") and user_context.get("target_glucose_max"):
                user_info.append(f"目标血糖范围: {user_context['target_glucose_min']}-{user_context['target_glucose_max']} mmol/L")
            
            if user_info:
                system_prompt += "\n\n用户信息：\n" + "\n".join(user_info)
        
        # 添加知识库内容
        if knowledge_sources and len(knowledge_sources) > 0:
            system_prompt += "\n\n相关知识：\n"
            for i, source in enumerate(knowledge_sources, 1):
                system_prompt += f"{i}. {source['title']}\n{source['content']}\n\n"
        
        return system_prompt
    
    def search_knowledge_base(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """搜索知识库"""
        try:
            # 检查是否已初始化向量数据库，未初始化则先返回空结果
            # 避免在每次搜索时都尝试初始化，减少不必要的延迟
            if not self.knowledge_collection:
                logger.warning("知识库未初始化，暂不支持知识检索")
                return []
            
            # 搜索知识库
            results = self.knowledge_collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            # 处理结果
            sources = []
            if results and len(results["ids"]) > 0 and len(results["ids"][0]) > 0:
                for i in range(len(results["ids"][0])):
                    source = {
                        "id": results["ids"][0][i],
                        "title": results["metadatas"][0][i].get("title", "未知标题"),
                        "content": results["documents"][0][i],
                        "score": float(results["distances"][0][i]) if "distances" in results else 0.0
                    }
                    sources.append(source)
            
            return sources
        
        except Exception as e:
            logger.error(f"搜索知识库失败: {str(e)}")
            return []
    
    def add_to_knowledge_base(self, doc_id: str, title: str, content: str) -> bool:
        """添加文档到知识库"""
        if not self.knowledge_collection:
            logger.warning("知识库未初始化，无法添加文档")
            return False
        
        try:
            # 添加文档
            self.knowledge_collection.add(
                ids=[doc_id],
                documents=[content],
                metadatas=[{"title": title, "updated_at": datetime.now().isoformat()}]
            )
            logger.info(f"已添加文档到知识库: {title}")
            return True
        
        except Exception as e:
            logger.error(f"添加文档到知识库失败: {str(e)}")
            return False
    
    def update_knowledge_base(self, doc_id: str, title: str, content: str) -> bool:
        """更新知识库中的文档"""
        if not self.knowledge_collection:
            logger.warning("知识库未初始化，无法更新文档")
            return False
        
        try:
            # 更新文档
            self.knowledge_collection.update(
                ids=[doc_id],
                documents=[content],
                metadatas=[{"title": title, "updated_at": datetime.now().isoformat()}]
            )
            logger.info(f"已更新知识库文档: {title}")
            return True
        
        except Exception as e:
            logger.error(f"更新知识库文档失败: {str(e)}")
            return False
    
    def delete_from_knowledge_base(self, doc_id: str) -> bool:
        """从知识库中删除文档"""
        if not self.knowledge_collection:
            logger.warning("知识库未初始化，无法删除文档")
            return False
        
        try:
            # 删除文档
            self.knowledge_collection.delete(ids=[doc_id])
            logger.info(f"已从知识库删除文档: {doc_id}")
            return True
        
        except Exception as e:
            logger.error(f"从知识库删除文档失败: {str(e)}")
            return False

# 创建一个全局的LLMService实例
llm_service = LLMService() 