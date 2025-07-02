# 糖尿病智能健康助理 - 后端服务

这是一个基于 FastAPI 构建的糖尿病智能健康助理后端服务，提供血糖记录管理、饮食管理、健康数据管理以及智能助理等功能。

## 项目结构

```
backend/
  ├── app/                     # 应用代码
  │   ├── api/                 # API接口
  │   │   ├── endpoints/       # 各功能模块的API接口
  │   │   └── deps.py          # API依赖项
  │   ├── core/                # 核心配置
  │   ├── db/                  # 数据库相关
  │   ├── ml/                  # 机器学习模块
  │   ├── models/              # Pydantic模型
  │   ├── services/            # 业务逻辑服务
  │   └── utils/               # 工具函数
  ├── vector_db/               # 向量数据库
  ├── main.py                  # 应用入口
  ├── setup_dev.py             # 开发环境设置脚本
  ├── init_db.py               # 数据库初始化脚本
  └── requirements.txt         # 依赖项
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 设置开发环境

```bash
# 初始化数据库
python setup_dev.py

# 重置数据库（慎用，会删除所有数据）
python setup_dev.py --reset

# 初始化数据库并创建示例数据
python setup_dev.py --sample-data
```

### 3. 启动服务

```bash
# 开发模式启动
python -m uvicorn main:app --reload --port 8000
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 默认账户

- 管理员账户：admin@diabetes-assistant.com / diabetes2024
- 测试用户账户：test@example.com / test123

## API 接口说明

### 用户管理

- POST `/api/v1/users/register` - 注册新用户
- POST `/api/v1/users/login` - 用户登录
- GET `/api/v1/users/profile` - 获取用户信息
- PUT `/api/v1/users/profile` - 更新用户信息

### 血糖管理

- GET `/api/v1/glucose` - 获取血糖记录
- POST `/api/v1/glucose` - 添加血糖记录
- PUT `/api/v1/glucose/{id}` - 更新血糖记录
- DELETE `/api/v1/glucose/{id}` - 删除血糖记录
- GET `/api/v1/glucose/statistics` - 获取血糖统计数据

### 饮食管理

- GET `/api/v1/diet` - 获取饮食记录
- POST `/api/v1/diet` - 添加饮食记录
- PUT `/api/v1/diet/{id}` - 更新饮食记录
- DELETE `/api/v1/diet/{id}` - 删除饮食记录

### 健康数据管理

- GET `/api/v1/health` - 获取健康数据
- POST `/api/v1/health` - 添加健康数据
- PUT `/api/v1/health/{id}` - 更新健康数据
- DELETE `/api/v1/health/{id}` - 删除健康数据

### 智能助理

- POST `/api/v1/assistant/chat` - 与助理对话
- GET `/api/v1/assistant/history` - 获取对话历史
- DELETE `/api/v1/assistant/history` - 清除对话历史

## 开发注意事项

### 环境变量

项目支持通过`.env`文件配置环境变量，主要配置项包括：

- `DATABASE_URL` - 数据库连接字符串
- `SECRET_KEY` - JWT 密钥
- `MODEL_PATH` - 大模型路径
- `MODEL_PRELOAD` - 是否预加载模型
- `DEBUG` - 是否开启调试模式

### 错误处理策略

系统采用了多层次的错误处理策略：

1. 数据库连接失败时，自动切换到 SQLite 备用数据库
2. 大模型加载失败时，提供友好的回退响应
3. 向量数据库初始化失败时，仍然允许系统基本功能运行

### 测试

运行测试：

```bash
pytest
```

## 常见问题排查

1. **数据库连接问题**

   - 运行 `python test_db_connection.py` 检查数据库连接

2. **模型加载问题**

   - 确保模型文件存在于 `MODEL_PATH` 指定的路径
   - 调整 `MODEL_DEVICE` 设置，尝试使用 "cpu" 作为备选

3. **API 请求失败**
   - 检查日志文件了解详细错误信息
   - 验证请求头是否包含有效的认证令牌
