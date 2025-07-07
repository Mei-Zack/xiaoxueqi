from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)

# 创建数据库引擎
try:
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False} if settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite") else {}
    )
    logger.info(f"已连接到数据库: {settings.SQLALCHEMY_DATABASE_URI}")
except Exception as e:
    logger.error(f"数据库连接失败: {str(e)}")
    # 如果主数据库连接失败，使用SQLite作为备用
    logger.info(f"使用备用数据库: {settings.SQLALCHEMY_DATABASE_URI_FALLBACK}")
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URI_FALLBACK,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False}
    )

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# 依赖函数，用于获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()  # 发生错误时回滚
        logger.error(f"数据库会话错误: {str(e)}")
        raise
    finally:
        db.close() 