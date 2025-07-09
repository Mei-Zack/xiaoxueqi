import requests
import json

# 基础配置
BASE_URL = "http://localhost:8000/api/v1"

def get_auth_token():
    """获取认证令牌"""
    # 尝试几种常见的认证端点路径
    auth_endpoints = [
        "/auth/token",
        "/auth/login",
        "/login/access-token",
        "/users/token",
        "/token"
    ]
    
    data = {
        "username": "admin@example.com",
        "password": "admin123"
    }
    
    for endpoint in auth_endpoints:
        url = f"{BASE_URL}{endpoint}"
        print(f"尝试认证端点: {url}")
        
        try:
            response = requests.post(url, json=data)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                if "access_token" in token_data:
                    print(f"认证令牌: {token_data.get('access_token')}")
                    return token_data.get('access_token')
                else:
                    print(f"响应中没有access_token字段: {token_data}")
            else:
                print(f"获取令牌失败: {response.text}")
        except Exception as e:
            print(f"请求异常: {str(e)}")
    
    print("所有认证端点都失败了")
    return None

if __name__ == "__main__":
    get_auth_token() 