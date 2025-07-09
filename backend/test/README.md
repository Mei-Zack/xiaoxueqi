# 血糖监测与预警功能测试

本目录包含用于测试血糖监测与预警功能的脚本。

## 测试脚本说明

### 1. test_glucose_monitor.py

测试血糖监测与预警功能的主要API端点，包括：

- 获取设备数据
- 导入设备数据
- 分析血糖数据
- 分析血糖趋势
- 注册/取消注册设备
- 获取支持的设备列表
- 直接导入血糖数据

### 2. test_glucose_mock_data.py

生成模拟血糖数据并进行可视化分析，功能包括：

- 生成不同类型糖尿病患者的模拟血糖数据
- 保存模拟数据到JSON文件
- 分析血糖数据（平均值、最大值、最小值、标准差等）
- 可视化血糖数据（生成图表）

### 3. test_diet_suggestions.py

测试基于血糖数据的饮食建议API，包括：

- 测试不同场景下的饮食建议（高血糖、低血糖、稳定血糖）
- 测试不同用户偏好的饮食建议（低碳饮食、均衡饮食、地中海饮食等）
- 测试快速饮食建议API

## 运行测试

### 前提条件

1. 确保后端服务已启动
2. 安装必要的依赖：

   ```bash
   pip install requests matplotlib numpy
   ```

### 运行测试脚本

1. **测试血糖监测API**

   ```bash
   cd backend
   python -m test.test_glucose_monitor
   ```

2. **生成模拟血糖数据**

   ```bash
   cd backend
   python -m test.test_glucose_mock_data
   ```

   运行后将生成：
   - `mock_glucose_data.json`：模拟血糖数据文件
   - `mock_glucose_visualization.png`：血糖数据可视化图表

3. **测试饮食建议API**

   ```bash
   cd backend
   python -m test.test_diet_suggestions
   ```

### 注意事项

- 测试脚本默认使用 `admin@example.com` / `admin123` 账号登录
- 测试脚本默认连接到 `http://localhost:8000/api/v1`
- 如果需要修改这些设置，请编辑相应测试脚本中的配置部分

## 自定义测试

每个测试脚本都提供了运行特定测试的功能，可以通过修改脚本中的 `if __name__ == "__main__"` 部分来选择运行哪些测试。

例如，要只运行特定的饮食建议测试：

```python
if __name__ == "__main__":
    # run_all_tests()  # 注释掉运行所有测试
    run_specific_test()  # 取消注释运行特定测试
```

## 扩展测试

如果需要添加新的测试，可以遵循以下步骤：

1. 在相应的测试脚本中添加新的测试函数
2. 在 `run_all_tests()` 函数中调用新添加的测试函数
3. 或者创建新的测试脚本，遵循类似的结构
