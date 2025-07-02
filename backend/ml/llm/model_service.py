import os
from typing import List, Dict, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import HuggingFacePipeline
from langchain.schema import Document
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.llm = None
        self.vector_store = None
        self.embeddings = None
        self.is_initialized = False
        self.system_prompt = """你是一个专业的糖尿病健康助理，名为"小雪琪"。你的任务是帮助糖尿病患者管理他们的健康，提供专业、准确、有用的建议。
请记住以下几点：
1. 提供科学、准确的医学建议，但不要替代专业医生的诊断
2. 保持友好、耐心和同理心
3. 回答要简洁明了，针对问题给出具体建议
4. 如果不确定或不了解某个问题，请诚实地表明你不知道，而不是提供可能不准确的信息
5. 避免使用过于专业的医学术语，用通俗易懂的语言解释复杂概念
6. 鼓励用户定期监测血糖，保持健康饮食和适当运动
7. 不要提供处方药物的具体剂量建议，这应由医生决定

现在，请根据用户的问题，提供专业、有帮助的回答。"""

    async def initialize(self):
        """
        初始化大模型和向量数据库
        """
        if self.is_initialized:
            return

        try:
            logger.info("正在初始化大模型...")
            
            # 配置量化参数
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=settings.MODEL_QUANTIZATION == "int4",
                load_in_8bit=settings.MODEL_QUANTIZATION == "int8",
                bnb_4bit_compute_dtype=torch.float16 if settings.MODEL_QUANTIZATION == "int4" else None
            )
            
            # 加载模型和分词器
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.MODEL_PATH,
                trust_remote_code=True
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                settings.MODEL_PATH,
                trust_remote_code=True,
                torch_dtype=torch.float16,
                device_map=settings.MODEL_DEVICE,
                quantization_config=quantization_config
            )
            
            # 创建LangChain Pipeline
            from langchain.llms import HuggingFacePipeline
            from transformers import pipeline
            
            pipe = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1,
                do_sample=True
            )
            
            self.llm = HuggingFacePipeline(pipeline=pipe)
            
            # 初始化向量嵌入
            self.embeddings = HuggingFaceEmbeddings(
                model_name="shibing624/text2vec-base-chinese"
            )
            
            # 如果向量数据库目录存在，加载它
            if os.path.exists(settings.VECTOR_DB_PATH):
                self.vector_store = FAISS.load_local(
                    settings.VECTOR_DB_PATH,
                    self.embeddings
                )
                logger.info(f"已加载向量数据库: {settings.VECTOR_DB_PATH}")
            else:
                logger.info("向量数据库不存在，将在首次添加文档时创建")
            
            self.is_initialized = True
            logger.info("大模型初始化完成")
            
        except Exception as e:
            logger.error(f"初始化大模型失败: {str(e)}")
            raise

    async def generate_response(self, user_message: str, chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        生成对用户消息的回复
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # 构建提示
            if chat_history:
                conversation = ""
                for msg in chat_history[-5:]:  # 只使用最近的5条消息
                    role = "用户" if msg["role"] == "user" else "助手"
                    conversation += f"{role}: {msg['content']}\n"
                conversation += f"用户: {user_message}\n助手: "
                
                prompt = f"{self.system_prompt}\n\n{conversation}"
            else:
                prompt = f"{self.system_prompt}\n\n用户: {user_message}\n助手: "
            
            # 使用RAG增强回复
            relevant_docs = []
            if self.vector_store:
                try:
                    relevant_docs = self.vector_store.similarity_search(user_message, k=3)
                    if relevant_docs:
                        context = "\n".join([doc.page_content for doc in relevant_docs])
                        prompt = f"{self.system_prompt}\n\n相关知识：\n{context}\n\n用户: {user_message}\n助手: "
                except Exception as e:
                    logger.error(f"获取相关文档失败: {str(e)}")
            
            # 生成回复
            response = self.llm.predict(prompt)
            
            # 清理回复
            if "助手:" in response:
                response = response.split("助手:", 1)[1].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"生成回复失败: {str(e)}")
            return "抱歉，我遇到了一些技术问题，无法回答您的问题。请稍后再试。"

    async def add_documents_to_knowledge_base(self, documents: List[Document]) -> bool:
        """
        将文档添加到知识库
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # 分割文档
            text_splitter = CharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                separator="\n"
            )
            
            split_docs = text_splitter.split_documents(documents)
            
            # 创建或更新向量存储
            if self.vector_store:
                self.vector_store.add_documents(split_docs)
            else:
                self.vector_store = FAISS.from_documents(
                    split_docs,
                    self.embeddings
                )
            
            # 保存向量存储
            os.makedirs(os.path.dirname(settings.VECTOR_DB_PATH), exist_ok=True)
            self.vector_store.save_local(settings.VECTOR_DB_PATH)
            
            logger.info(f"已将{len(split_docs)}个文档片段添加到知识库")
            return True
            
        except Exception as e:
            logger.error(f"添加文档到知识库失败: {str(e)}")
            return False


# 单例模式
llm_service = LLMService() 