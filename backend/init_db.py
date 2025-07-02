import logging
from sqlalchemy.orm import Session
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.init_db import init_db, reset_db
from app.db.session import SessionLocal
from app.models.user import UserCreate
from app.services.user import create_superuser
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    """初始化数据库"""
    db = SessionLocal()
    try:
        # 初始化数据库表
        init_db()
        
        # 创建超级管理员
        create_admin(db)
        
        logger.info("✅ 数据库初始化完成")
    finally:
        db.close()


def reset() -> None:
    """重置数据库"""
    db = SessionLocal()
    try:
        # 重置数据库表
        reset_db()
        
        # 创建超级管理员
        create_admin(db)
        
        logger.info("✅ 数据库重置完成")
    finally:
        db.close()


def create_admin(db: Session) -> None:
    """创建超级管理员账户"""
    try:
        # 创建超级管理员
        admin = UserCreate(
            email="admin@example.com",
            name="系统管理员",
            password="admin123",
            is_active=True,
            is_superuser=True
        )
        
        create_superuser(db, admin)
        logger.info("✅ 超级管理员账户创建成功")
    except Exception as e:
        logger.error(f"❌ 创建超级管理员账户失败: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "reset":
            logger.info("🔄 正在重置数据库...")
            reset()
        else:
            logger.info("⚠️ 未知命令，使用方法: python init_db.py [reset]")
    else:
        logger.info("🚀 正在初始化数据库...")
        init() 