import os
import secrets
from typing import List, Optional, Union, Dict, Any

from pydantic import field_validator, AnyHttpUrl, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS配置
    CORS_ORIGINS: Union[List[str], List[AnyHttpUrl], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost",
        "http://127.0.0.1",
        "*"  # 开发环境临时允许所有来源
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and v != "*":
            return [i.strip() for i in v.split(",")]
        return v
    
    PROJECT_NAME: str = "糖尿病智能健康助理"
    
    # 调试模式
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI: Optional[str] = os.getenv(
        "DATABASE_URL",
        # 默认使用MySQL
        "mysql+pymysql://root:65353804778@localhost/diabetes_assistant"
    )
    
    # 如果MySQL连接失败，使用SQLite作为备用
    SQLALCHEMY_DATABASE_URI_FALLBACK: str = "sqlite:///diabetes_assistant.db"
    
    # 向量数据库设置
    VECTOR_STORE_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "vector_db")
    
    # 大模型配置
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./models/deepseek-lite")
    MODEL_DEVICE: str = os.getenv("MODEL_DEVICE", "cpu")
    MODEL_QUANTIZATION: str = os.getenv("MODEL_QUANTIZATION", "int4")
    MODEL_PRELOAD: bool = False  # 默认不预加载模型
    MODEL_PROVIDER: str = os.getenv("MODEL_PROVIDER", "local")  # 模型提供者：local, ollama, openai等
    MODEL_NAME: str = os.getenv("MODEL_NAME", "deepseek-lite")  # 模型名称
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"  # 允许额外的字段

settings = Settings() 