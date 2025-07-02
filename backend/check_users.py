#!/usr/bin/env python
"""
查询数据库中的用户
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models import User

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def check_users():
    """查询数据库中的所有用户"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        
        if not users:
            logger.info("⚠️ 数据库中没有用户")
            return
        
        logger.info(f"✅ 找到 {len(users)} 个用户:")
        
        for user in users:
            logger.info(f"  - ID: {user.id}")
            logger.info(f"    Email: {user.email}")
            logger.info(f"    Name: {user.name}")
            logger.info(f"    Is Admin: {user.is_superuser}")
            logger.info(f"    Is Active: {user.is_active}")
            logger.info(f"    Created At: {user.created_at}")
            logger.info("---")
    
    except Exception as e:
        logger.error(f"❌ 查询用户失败: {e}")
    
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("🔍 正在查询数据库用户...")
    check_users() 