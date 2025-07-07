#!/usr/bin/env python
"""
查询数据库中的用户
"""

import sys
import os
import logging
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models import User

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def check_users():
    """检查数据库中的用户"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"数据库中共有 {len(users)} 个用户:")
        
        for user in users:
            user_info = {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "hashed_password": user.hashed_password[:10] + "..." if user.hashed_password else None
            }
            print(json.dumps(user_info, ensure_ascii=False, indent=2))
            print("-" * 40)
    except Exception as e:
        print(f"查询用户失败: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("🔍 正在查询数据库用户...")
    check_users() 