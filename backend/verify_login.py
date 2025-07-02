#!/usr/bin/env python
"""
验证用户登录凭据
"""

import sys
import os
import logging
from passlib.context import CryptContext

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models import User
from app.core.security import verify_password

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def verify_user_credentials(email, password):
    """验证用户登录凭据"""
    db = SessionLocal()
    try:
        # 查询用户
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            logger.error(f"❌ 用户不存在: {email}")
            return False
        
        logger.info(f"✅ 找到用户: {user.email}")
        logger.info(f"用户ID: {user.id}")
        logger.info(f"用户名: {user.name}")
        logger.info(f"是否激活: {user.is_active}")
        logger.info(f"是否管理员: {user.is_superuser}")
        
        # 验证密码
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_match = pwd_context.verify(password, user.hashed_password)
        
        if password_match:
            logger.info(f"✅ 密码验证成功!")
            return True
        else:
            logger.error(f"❌ 密码不匹配")
            return False
    
    except Exception as e:
        logger.error(f"❌ 验证凭据时出错: {e}")
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使用方法: python verify_login.py <email> <password>")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    logger.info(f"🔍 正在验证用户凭据: {email}")
    result = verify_user_credentials(email, password)
    
    if result:
        logger.info("✅ 验证成功! 用户凭据有效")
    else:
        logger.error("❌ 验证失败! 用户凭据无效") 