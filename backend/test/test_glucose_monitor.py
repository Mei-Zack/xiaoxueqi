import requests
import json
import os
import sys
from datetime import datetime, timedelta
import unittest
import time

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 基础配置
BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjIxNjg5MzAsInN1YiI6ImU2NzI2YTc2LTM2MjQtNGRjYi1hZDlkLThlYThmZjRiMDEwYSJ9.SbVrDlLcCwp1AtVCQhm9HnJJq9i8gFxwTGqvazfgDtY"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

class GlucoseMonitorAPITest(unittest.TestCase):
    """血糖监测API测试类"""
    
    @classmethod
    def setUpClass(cls):
        """在所有测试之前运行，确认API服务器可用"""
        print("\n===== 检查API服务器是否可用 =====")
        max_retries = 3
        retry_delay = 2
        
        for i in range(max_retries):
            try:
                # 尝试访问健康检查端点
                response = requests.get(f"{BASE_URL.split('/api/v1')[0]}/health")
                if response.status_code == 200:
                    print("API服务器可用")
                    return
                else:
                    print(f"API服务器返回状态码: {response.status_code}")
            except requests.exceptions.ConnectionError:
                print(f"无法连接到API服务器，尝试 {i+1}/{max_retries}")
            
            if i < max_retries - 1:
                print(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
        
        print("警告: API服务器可能不可用，测试可能会失败")
    
    def setUp(self):
        """测试前的准备工作"""
        # 生成模拟数据
        self.mock_data = self.generate_mock_glucose_data(hours=24)
    
    def print_response_info(self, response):
        """打印响应信息，帮助调试"""
        print(f"状态码: {response.status_code}")
        try:
            print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except:
            print(f"响应内容: {response.text}")
    
    def generate_mock_glucose_data(self, hours=24, interval_minutes=15):
        """生成模拟血糖数据"""
        import random
        data = []
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        current_time = start_time
        
        # 定义一些血糖测量时间类型
        measurement_times = [
            "BEFORE_BREAKFAST", "AFTER_BREAKFAST",
            "BEFORE_LUNCH", "AFTER_LUNCH",
            "BEFORE_DINNER", "AFTER_DINNER",
            "BEDTIME", "NIGHT", "FASTING"
        ]
        
        while current_time <= end_time:
            # 生成5.0-10.0之间的随机血糖值，模拟一些波动
            base_value = 7.0
            variation = random.uniform(-2.0, 3.0)
            # 添加时间相关的波动，模拟餐后血糖升高
            hour = current_time.hour
            if 7 <= hour <= 9 or 12 <= hour <= 14 or 18 <= hour <= 20:
                variation += 1.5  # 餐后血糖升高
            
            value = round(base_value + variation, 1)
            
            # 确定测量时间类型
            if 6 <= hour < 8:
                measurement_time = "BEFORE_BREAKFAST"
            elif 8 <= hour < 10:
                measurement_time = "AFTER_BREAKFAST"
            elif 11 <= hour < 13:
                measurement_time = "BEFORE_LUNCH"
            elif 13 <= hour < 15:
                measurement_time = "AFTER_LUNCH"
            elif 17 <= hour < 19:
                measurement_time = "BEFORE_DINNER"
            elif 19 <= hour < 21:
                measurement_time = "AFTER_DINNER"
            elif 22 <= hour < 24:
                measurement_time = "BEDTIME"
            elif 0 <= hour < 6:
                measurement_time = "NIGHT"
            else:
                measurement_time = random.choice(measurement_times)
            
            data.append({
                "measured_at": current_time.isoformat(),
                "value": value,
                "measurement_time": measurement_time
            })
            
            current_time += timedelta(minutes=interval_minutes)
        
        return data
    
    def test_0_health_check(self):
        """测试API服务器健康状态"""
        print("\n===== 测试API服务器健康状态 =====")
        try:
            # 尝试访问用户信息端点，这通常需要认证
            response = requests.get(f"{BASE_URL}/users/me", headers=HEADERS)
            self.print_response_info(response)
            
            # 检查状态码
            if response.status_code == 404:
                print("警告: API端点不存在，请检查BASE_URL配置")
            elif response.status_code == 401:
                print("警告: 认证令牌可能已过期，请更新TOKEN变量")
            elif response.status_code == 200:
                print("API认证正常")
            
            # 不要断言状态码，因为我们只是想检查API是否响应
            self.assertIn(response.status_code, [200, 401, 404], "API服务器应该返回响应")
        except requests.exceptions.ConnectionError:
            self.fail("无法连接到API服务器，请确保服务器已启动")
    
    def test_1_get_supported_devices(self):
        """测试获取支持的设备列表"""
        print("\n===== 测试获取支持的设备列表 =====")
        url = f"{BASE_URL}/glucose-monitor/supported-devices"
        
        response = requests.get(url, headers=HEADERS)
        self.print_response_info(response)
        
        # 断言响应状态码为200
        self.assertEqual(response.status_code, 200)
        
        # 断言响应包含devices字段
        response_json = response.json()
        self.assertIn("devices", response_json)
        
        # 断言devices是一个列表
        self.assertIsInstance(response_json["devices"], list)
        
        # 打印支持的设备列表
        print(f"支持的设备: {response_json['devices']}")
        return response_json["devices"]
    
    def test_2_import_glucose_data(self):
        """测试直接导入血糖数据"""
        print("\n===== 测试直接导入血糖数据 =====")
        url = f"{BASE_URL}/glucose-monitor/devices/import"
        
        data = {
            "device_id": "mock_device_001",
            "data": self.mock_data[:10]  # 只导入前10条数据，避免数据过多
        }
        
        response = requests.post(url, headers=HEADERS, json=data)
        self.print_response_info(response)
        
        # 断言响应状态码为200
        self.assertEqual(response.status_code, 200)
        
        # 断言响应包含status字段，且值为success
        response_json = response.json()
        self.assertIn("status", response_json)
        self.assertEqual(response_json["status"], "success")
        
        # 断言响应包含imported_count字段，且值大于0
        self.assertIn("imported_count", response_json)
        self.assertGreater(response_json["imported_count"], 0)
        
        print(f"导入结果: {response_json}")
        return response_json
    
    def test_3_analyze_glucose(self):
        """测试分析血糖数据"""
        print("\n===== 测试分析血糖数据 =====")
        url = f"{BASE_URL}/glucose-monitor/analyze"
        
        data = {
            "hours": 24
        }
        
        response = requests.post(url, headers=HEADERS, json=data)
        self.print_response_info(response)
        
        # 断言响应状态码为200
        self.assertEqual(response.status_code, 200)
        
        # 断言响应包含status字段
        response_json = response.json()
        self.assertIn("status", response_json)
        
        # 如果有数据，断言包含statistics字段
        if "message" not in response_json:
            self.assertIn("statistics", response_json)
            self.assertIn("average", response_json["statistics"])
            self.assertIn("max", response_json["statistics"])
            self.assertIn("min", response_json["statistics"])
        
        print(f"分析结果: {json.dumps(response_json, indent=2)}")
        return response_json
    
    def test_4_analyze_glucose_trend(self):
        """测试分析血糖趋势"""
        print("\n===== 测试分析血糖趋势 =====")
        url = f"{BASE_URL}/glucose-monitor/analyze-trend"
        
        data = {
            "days": 3
        }
        
        response = requests.post(url, headers=HEADERS, json=data)
        self.print_response_info(response)
        
        # 断言响应状态码为200
        self.assertEqual(response.status_code, 200)
        
        # 断言响应包含status字段
        response_json = response.json()
        self.assertIn("status", response_json)
        
        # 如果有数据，断言包含statistics字段
        if response_json.get("has_data", False):
            self.assertIn("statistics", response_json)
            self.assertIn("patterns", response_json)
            self.assertIn("advice", response_json)
        
        print(f"趋势分析结果: {json.dumps(response_json, indent=2) if len(str(response_json)) < 500 else '(结果太长，省略显示)'}")
        return response_json
    
    def test_5_register_device(self):
        """测试注册设备"""
        print("\n===== 测试注册设备 =====")
        url = f"{BASE_URL}/glucose-monitor/register-device"
        
        data = {
            "device_type": "freestyle_libre",
            "params": {
                "db_path": "/path/to/trident.realm",
                "encryption_key": "your-encryption-key"
            },
            "enable_auto_sync": True
        }
        
        response = requests.post(url, headers=HEADERS, json=data)
        self.print_response_info(response)
        
        # 断言响应状态码为200
        self.assertEqual(response.status_code, 200)
        
        # 断言响应包含status字段，且值为success
        response_json = response.json()
        self.assertIn("status", response_json)
        self.assertEqual(response_json["status"], "success")
        
        # 断言响应包含auto_sync字段
        self.assertIn("auto_sync", response_json)
        
        print(f"注册结果: {response_json}")
        return response_json
    
    def test_6_unregister_device(self):
        """测试取消注册设备"""
        print("\n===== 测试取消注册设备 =====")
        url = f"{BASE_URL}/glucose-monitor/unregister-device"
        
        response = requests.post(url, headers=HEADERS)
        self.print_response_info(response)
        
        # 断言响应状态码为200
        self.assertEqual(response.status_code, 200)
        
        # 断言响应包含status字段，且值为success
        response_json = response.json()
        self.assertIn("status", response_json)
        self.assertEqual(response_json["status"], "success")
        
        print(f"取消注册结果: {response_json}")
        return response_json

if __name__ == "__main__":
    # 运行测试
    # unittest.main(verbosity=2) 
    
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description="血糖监测API测试")
    parser.add_argument("--test", "-t", help="要运行的测试名称，例如 test_1_get_supported_devices")
    parser.add_argument("--all", "-a", action="store_true", help="运行所有测试")
    args = parser.parse_args()
    
    # 根据参数运行测试
    if args.test:
        # 运行单个测试
        suite = unittest.TestSuite()
        suite.addTest(GlucoseMonitorAPITest(args.test))
        unittest.TextTestRunner(verbosity=2).run(suite)
    else:
        # 运行所有测试
        unittest.main(verbosity=2) 