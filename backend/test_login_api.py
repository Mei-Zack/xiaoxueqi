#!/usr/bin/env python
"""
测试登录API并打印详细错误信息
"""

import requests
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# API基本URL
BASE_URL = "http://localhost:8000/api/v1"

def test_login_api(email, password):
    """测试登录API"""
    login_url = f"{BASE_URL}/users/login"
    
    # 注意：登录API使用的是表单数据格式，不是JSON
    # 基于FastAPI的OAuth2PasswordRequestForm
    data = {
        "username": email,  # OAuth2使用username字段
        "password": password
    }
    
    logger.info(f"🔍 正在测试登录API: {login_url}")
    logger.info(f"📧 用户名: {email}")
    logger.info(f"🔑 密码: {'*' * len(password)}")
    
    try:
        # 发送登录请求
        response = requests.post(
            login_url,
            data=data,  # 使用表单数据而不是JSON
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        
        # 打印响应状态码
        logger.info(f"📊 响应状态码: {response.status_code}")
        
        # 尝试解析JSON响应
        try:
            json_response = response.json()
            logger.info(f"📄 响应内容: {json.dumps(json_response, indent=2, ensure_ascii=False)}")
        except Exception as e:
            logger.error(f"❌ 无法解析JSON响应: {e}")
            logger.info(f"📝 原始响应内容: {response.text}")
        
        # 检查响应状态
        if response.ok:
            logger.info("✅ 登录成功!")
            return True, response
        else:
            logger.error(f"❌ 登录失败: {response.reason}")
            return False, response
            
    except requests.RequestException as e:
        logger.error(f"❌ 请求异常: {e}")
        return False, None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("使用方法: python test_login_api.py <email> <password>")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    success, response = test_login_api(email, password)
    
    if success:
        logger.info("✅ API测试成功!")
    else:
        logger.error("❌ API测试失败!") 