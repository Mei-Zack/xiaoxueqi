import json
import random
from datetime import datetime, timedelta
import os
import sys
import matplotlib.pyplot as plt
import numpy as np

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 生成模拟血糖数据
def generate_mock_glucose_data(days=3, interval_minutes=15):
    """
    生成模拟的血糖数据
    
    参数:
        days (int): 生成多少天的数据
        interval_minutes (int): 数据点之间的时间间隔（分钟）
    
    返回:
        list: 血糖数据列表
    """
    data = []
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    current_time = start_time
    
    # 定义一些血糖测量时间类型
    measurement_times = [
        "BEFORE_BREAKFAST", "AFTER_BREAKFAST",
        "BEFORE_LUNCH", "AFTER_LUNCH",
        "BEFORE_DINNER", "AFTER_DINNER",
        "BEDTIME", "NIGHT", "FASTING"
    ]
    
    # 模拟一些基本的血糖模式
    # 1. 正常人的血糖范围通常在3.9-6.1 mmol/L (空腹)
    # 2. 糖尿病患者的血糖可能更高，尤其是餐后
    # 3. 血糖在一天中有波动，通常餐后升高，然后逐渐下降
    
    # 随机选择一个糖尿病类型，影响基础血糖水平
    diabetes_type = random.choice(["TYPE_1", "TYPE_2", "GESTATIONAL", "NORMAL"])
    
    if diabetes_type == "NORMAL":
        base_glucose = 5.0  # 正常人基础血糖
        variation_range = (-1.0, 1.5)  # 正常波动范围
        meal_effect = 1.0  # 餐后升高幅度
    elif diabetes_type == "TYPE_1":
        base_glucose = 7.0  # 1型糖尿病基础血糖
        variation_range = (-2.5, 4.0)  # 波动更大
        meal_effect = 3.0  # 餐后升高幅度更大
    elif diabetes_type == "TYPE_2":
        base_glucose = 8.0  # 2型糖尿病基础血糖
        variation_range = (-2.0, 3.5)  # 波动较大
        meal_effect = 2.5  # 餐后升高幅度较大
    else:  # GESTATIONAL
        base_glucose = 6.5  # 妊娠糖尿病基础血糖
        variation_range = (-1.5, 2.5)  # 中等波动
        meal_effect = 2.0  # 餐后升高幅度中等
    
    # 添加一些随机事件
    # 1. 偶尔的低血糖事件
    low_glucose_days = random.sample(range(days), k=min(2, days))
    # 2. 偶尔的高血糖事件
    high_glucose_days = random.sample(range(days), k=min(2, days))
    
    day_count = 0
    while current_time <= end_time:
        # 计算当前是第几天（从0开始）
        current_day = (current_time.date() - start_time.date()).days
        
        # 基础血糖值加上随机波动
        variation = random.uniform(*variation_range)
        
        # 添加时间相关的波动，模拟餐后血糖升高
        hour = current_time.hour
        minute = current_time.minute
        
        # 特殊事件：低血糖
        is_low_event = current_day in low_glucose_days and random.random() < 0.1
        # 特殊事件：高血糖
        is_high_event = current_day in high_glucose_days and random.random() < 0.1
        
        # 早餐时间
        if 7 <= hour < 9:
            if hour == 7 and minute < 30:  # 早餐前
                meal_boost = 0
                measurement_time = "BEFORE_BREAKFAST"
            else:  # 早餐后
                meal_boost = meal_effect * (1 - (hour - 7) / 2)  # 效果随时间减弱
                measurement_time = "AFTER_BREAKFAST"
        # 午餐时间
        elif 12 <= hour < 14:
            if hour == 12 and minute < 30:  # 午餐前
                meal_boost = 0
                measurement_time = "BEFORE_LUNCH"
            else:  # 午餐后
                meal_boost = meal_effect * (1 - (hour - 12) / 2)  # 效果随时间减弱
                measurement_time = "AFTER_LUNCH"
        # 晚餐时间
        elif 18 <= hour < 20:
            if hour == 18 and minute < 30:  # 晚餐前
                meal_boost = 0
                measurement_time = "BEFORE_DINNER"
            else:  # 晚餐后
                meal_boost = meal_effect * (1 - (hour - 18) / 2)  # 效果随时间减弱
                measurement_time = "AFTER_DINNER"
        # 睡前
        elif 22 <= hour < 24:
            meal_boost = 0
            measurement_time = "BEDTIME"
        # 夜间
        elif 0 <= hour < 6:
            meal_boost = 0
            measurement_time = "NIGHT"
        # 其他时间
        else:
            meal_boost = 0
            measurement_time = random.choice(measurement_times)
        
        # 计算最终血糖值
        if is_low_event:
            value = round(max(2.5, base_glucose - 2.0 + random.uniform(-0.5, 0.5)), 1)
        elif is_high_event:
            value = round(min(20.0, base_glucose + 6.0 + random.uniform(-1.0, 1.0)), 1)
        else:
            value = round(max(2.8, min(18.0, base_glucose + variation + meal_boost)), 1)
        
        data.append({
            "measured_at": current_time.isoformat(),
            "value": value,
            "measurement_time": measurement_time
        })
        
        current_time += timedelta(minutes=interval_minutes)
    
    print(f"生成了{len(data)}条模拟血糖数据，类型: {diabetes_type}")
    return data

def save_mock_data_to_file(data, filename="mock_glucose_data.json"):
    """保存模拟数据到文件"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"模拟数据已保存到 {filename}")

def visualize_glucose_data(data):
    """可视化血糖数据"""
    timestamps = [datetime.fromisoformat(item["measured_at"]) for item in data]
    values = [item["value"] for item in data]
    measurement_times = [item["measurement_time"] for item in data]
    
    # 创建颜色映射
    color_map = {
        "BEFORE_BREAKFAST": "blue",
        "AFTER_BREAKFAST": "lightblue",
        "BEFORE_LUNCH": "green",
        "AFTER_LUNCH": "lightgreen",
        "BEFORE_DINNER": "red",
        "AFTER_DINNER": "salmon",
        "BEDTIME": "purple",
        "NIGHT": "darkblue",
        "FASTING": "orange"
    }
    
    colors = [color_map.get(mt, "gray") for mt in measurement_times]
    
    plt.figure(figsize=(15, 6))
    
    # 绘制血糖值
    plt.scatter(timestamps, values, c=colors, alpha=0.7)
    plt.plot(timestamps, values, 'k-', alpha=0.3)
    
    # 添加正常范围区域
    plt.axhspan(3.9, 6.1, color='green', alpha=0.1, label='正常空腹血糖范围')
    plt.axhspan(3.9, 7.8, color='blue', alpha=0.1, label='正常餐后血糖范围')
    
    # 添加警戒线
    plt.axhline(y=3.9, color='orange', linestyle='--', label='低血糖警戒线')
    plt.axhline(y=10.0, color='red', linestyle='--', label='高血糖警戒线')
    
    # 设置图表属性
    plt.title('模拟血糖数据')
    plt.xlabel('时间')
    plt.ylabel('血糖值 (mmol/L)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # 添加自定义图例，显示测量时间类型
    import matplotlib.patches as mpatches
    legend_patches = []
    for mt, color in color_map.items():
        patch = mpatches.Patch(color=color, label=mt)
        legend_patches.append(patch)
    plt.legend(handles=legend_patches, loc='upper left', bbox_to_anchor=(1, 1))
    
    plt.tight_layout()
    plt.savefig('mock_glucose_visualization.png')
    plt.show()
    
    print("血糖数据可视化已保存到 mock_glucose_visualization.png")

def analyze_mock_data(data):
    """分析模拟血糖数据"""
    values = [item["value"] for item in data]
    
    # 基本统计
    avg_value = np.mean(values)
    max_value = np.max(values)
    min_value = np.min(values)
    std_value = np.std(values)
    
    # 计算达标率
    target_min = 3.9
    target_max = 7.8
    in_range_count = sum(1 for v in values if target_min <= v <= target_max)
    in_range_percentage = (in_range_count / len(values)) * 100
    
    # 计算高血糖和低血糖比例
    high_count = sum(1 for v in values if v > target_max)
    low_count = sum(1 for v in values if v < target_min)
    high_percentage = (high_count / len(values)) * 100
    low_percentage = (low_count / len(values)) * 100
    
    # 按测量时间分组
    measurement_groups = {}
    for item in data:
        mt = item["measurement_time"]
        if mt not in measurement_groups:
            measurement_groups[mt] = []
        measurement_groups[mt].append(item["value"])
    
    # 计算各组平均值
    group_averages = {mt: np.mean(values) for mt, values in measurement_groups.items()}
    
    # 输出分析结果
    print("\n===== 血糖数据分析 =====")
    print(f"记录总数: {len(data)}")
    print(f"平均血糖: {avg_value:.2f} mmol/L")
    print(f"最高血糖: {max_value:.2f} mmol/L")
    print(f"最低血糖: {min_value:.2f} mmol/L")
    print(f"标准差: {std_value:.2f} mmol/L")
    print(f"目标范围内比例: {in_range_percentage:.2f}%")
    print(f"高于目标范围比例: {high_percentage:.2f}%")
    print(f"低于目标范围比例: {low_percentage:.2f}%")
    
    print("\n各测量时间点平均血糖:")
    for mt, avg in group_averages.items():
        print(f"  {mt}: {avg:.2f} mmol/L")
    
    return {
        "record_count": len(data),
        "average": avg_value,
        "max": max_value,
        "min": min_value,
        "std": std_value,
        "in_range_percentage": in_range_percentage,
        "high_percentage": high_percentage,
        "low_percentage": low_percentage,
        "group_averages": group_averages
    }

if __name__ == "__main__":
    # 生成3天的模拟数据，每15分钟一个数据点
    mock_data = generate_mock_glucose_data(days=3, interval_minutes=15)
    
    # 保存到文件
    save_mock_data_to_file(mock_data)
    
    # 分析数据
    analysis = analyze_mock_data(mock_data)
    
    # 可视化数据
    visualize_glucose_data(mock_data) 