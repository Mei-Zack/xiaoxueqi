import requests
import json
import os
import sys
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 基础配置
BASE_URL = "http://localhost:8000/api/v1"
TOKEN = None  # 将在运行时获取

def get_auth_token():
    """获取认证令牌"""
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": "admin@example.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            url, 
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"登录失败: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"获取令牌时发生错误: {str(e)}")
        return None

def print_response(response, title=None):
    """格式化打印响应"""
    if title:
        print(f"\n===== {title} =====")
    print(f"状态码: {response.status_code}")
    try:
        print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except:
        print(f"响应内容: {response.text}")
    return response.json() if response.status_code < 400 else None

# 1. 测试饮食建议API
def test_diet_suggestions(glucose_data, user_preferences, meal_type):
    """测试饮食建议API"""
    url = f"{BASE_URL}/glucose-monitor/diet-suggestions"
    
    data = {
        "glucose_data": glucose_data,
        "user_preferences": user_preferences,
        "meal_type": meal_type
    }
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, json=data)
    return print_response(response, f"饮食建议 ({meal_type})")

# 2. 测试快速饮食建议API
def test_quick_diet_suggestions(glucose_value, meal_type, is_before_meal):
    """测试快速饮食建议API"""
    url = f"{BASE_URL}/glucose-monitor/quick-diet-suggestions"
    
    params = {
        "glucose_value": glucose_value,
        "meal_type": meal_type,
        "is_before_meal": str(is_before_meal).lower()
    }
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers, params=params)
    return print_response(response, f"快速饮食建议 ({meal_type}, {'餐前' if is_before_meal else '餐后'})")

# 测试不同场景的饮食建议
def test_diet_suggestions_scenarios():
    """测试不同场景下的饮食建议"""
    # 场景1: 高血糖情况
    high_glucose_data = {
        "recent_average": 10.5,
        "fasting_average": 8.5,
        "after_meal_average": 12.1,
        "has_high_glucose": True,
        "has_low_glucose": False,
        "glucose_variability": "high"
    }
    
    # 场景2: 低血糖情况
    low_glucose_data = {
        "recent_average": 3.8,
        "fasting_average": 4.0,
        "after_meal_average": 5.1,
        "has_high_glucose": False,
        "has_low_glucose": True,
        "glucose_variability": "medium"
    }
    
    # 场景3: 稳定血糖情况
    stable_glucose_data = {
        "recent_average": 6.2,
        "fasting_average": 5.8,
        "after_meal_average": 7.0,
        "has_high_glucose": False,
        "has_low_glucose": False,
        "glucose_variability": "low"
    }
    
    # 用户偏好1: 低碳饮食，有坚果过敏
    user_preferences_1 = {
        "diet_type": "low_carb",
        "allergies": ["nuts"],
        "favorite_foods": ["vegetables", "fish"]
    }
    
    # 用户偏好2: 均衡饮食，无过敏
    user_preferences_2 = {
        "diet_type": "balanced",
        "allergies": [],
        "favorite_foods": ["fruits", "rice", "chicken"]
    }
    
    # 用户偏好3: 地中海饮食，乳制品过敏
    user_preferences_3 = {
        "diet_type": "mediterranean",
        "allergies": ["dairy"],
        "favorite_foods": ["vegetables", "whole grains", "olive oil"]
    }
    
    # 测试高血糖场景 + 低碳饮食
    print("\n--- 高血糖场景 + 低碳饮食 ---")
    for meal_type in ["breakfast", "lunch", "dinner", "snack"]:
        test_diet_suggestions(high_glucose_data, user_preferences_1, meal_type)
    
    # 测试低血糖场景 + 均衡饮食
    print("\n--- 低血糖场景 + 均衡饮食 ---")
    for meal_type in ["breakfast", "lunch", "dinner", "snack"]:
        test_diet_suggestions(low_glucose_data, user_preferences_2, meal_type)
    
    # 测试稳定血糖场景 + 地中海饮食
    print("\n--- 稳定血糖场景 + 地中海饮食 ---")
    for meal_type in ["breakfast", "lunch", "dinner", "snack"]:
        test_diet_suggestions(stable_glucose_data, user_preferences_3, meal_type)

# 测试快速饮食建议
def test_quick_diet_suggestions_scenarios():
    """测试不同场景下的快速饮食建议"""
    # 测试不同血糖值
    glucose_values = [3.5, 5.5, 8.5, 12.0]
    meal_types = ["breakfast", "lunch", "dinner", "snack"]
    is_before_meal_options = [True, False]
    
    for glucose_value in glucose_values:
        glucose_status = "低血糖" if glucose_value < 3.9 else "正常血糖" if glucose_value < 7.8 else "高血糖"
        print(f"\n--- {glucose_status} ({glucose_value} mmol/L) ---")
        
        for meal_type in meal_types:
            for is_before_meal in is_before_meal_options:
                test_quick_diet_suggestions(glucose_value, meal_type, is_before_meal)

# 运行所有测试
def run_all_tests():
    global TOKEN
    TOKEN = get_auth_token()
    
    if not TOKEN:
        print("无法获取认证令牌，测试终止")
        return
    
    print("开始测试血糖监测饮食建议API...\n")
    
    # 测试不同场景下的饮食建议
    test_diet_suggestions_scenarios()
    
    # 测试不同场景下的快速饮食建议
    test_quick_diet_suggestions_scenarios()
    
    print("\n所有测试完成!")

# 运行特定测试
def run_specific_test():
    global TOKEN
    TOKEN = get_auth_token()
    
    if not TOKEN:
        print("无法获取认证令牌，测试终止")
        return
    
    # 例如，只测试特定场景
    glucose_data = {
        "recent_average": 7.5,
        "fasting_average": 6.8,
        "after_meal_average": 8.2,
        "has_high_glucose": False,
        "has_low_glucose": False,
        "glucose_variability": "medium"
    }
    
    user_preferences = {
        "diet_type": "low_carb",
        "allergies": ["gluten"],
        "favorite_foods": ["eggs", "avocado", "berries"]
    }
    
    test_diet_suggestions(glucose_data, user_preferences, "breakfast")

if __name__ == "__main__":
    # 运行所有测试
    run_all_tests()
    
    # 或者运行特定测试
    # run_specific_test() 