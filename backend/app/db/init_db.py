import logging
from sqlalchemy.orm import Session

from app.db.base_class import Base
from app.db.session import engine
from app.core.config import settings
from app.db import models  # 导入所有模型以确保它们被注册

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db() -> None:
    """初始化数据库，创建所有表"""
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("✅ 数据库表创建成功")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise


def reset_db() -> None:
    """重置数据库，删除所有表并重新创建"""
    try:
        # 删除所有表
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ 数据库表删除成功")
        
        # 重新创建所有表
        init_db()
    except Exception as e:
        logger.error(f"❌ 数据库重置失败: {e}")
        raise 