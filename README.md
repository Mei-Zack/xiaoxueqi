# 糖尿病智能健康助理

基于大模型的糖尿病智能健康助理系统，帮助糖尿病患者进行血糖监测、饮食管理、健康咨询等全方位健康管理。

## 项目概述

本项目旨在利用人工智能技术，特别是大语言模型，为糖尿病患者提供个性化的健康管理服务。系统集成了血糖监测、饮食管理、健康知识库和智能问答等功能，通过大模型提供智能化的健康建议和咨询服务。

### 核心功能

- **用户管理**：注册、登录、个人信息管理
- **血糖监测**：记录、分析、预警
- **饮食管理**：饮食记录、营养分析、饮食建议
- **健康数据**：体重、血压、运动等健康指标记录与分析
- **智能助理**：基于大模型的健康咨询与建议
- **知识库**：糖尿病相关知识、文章、健康指南

## 技术架构

### 前端

- **框架**：Vue 3 + TypeScript
- **UI 库**：Element Plus
- **状态管理**：Pinia
- **路由**：Vue Router
- **HTTP 客户端**：Axios
- **图表**：ECharts, Chart.js

### 后端

- **框架**：FastAPI
- **数据库**：MySQL
- **ORM**：SQLAlchemy
- **认证**：JWT
- **迁移**：Alembic
- **大模型集成**：Ollama、Hugging Face Transformers
- **向量检索**：ChromaDB

## 项目结构

```
xiaoxueqi/
├── backend/                # 后端代码
│   ├── app/                # 应用代码
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── db/             # 数据库
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── ml/                 # 机器学习相关
│   │   ├── llm/            # 大语言模型
│   │   └── prediction/     # 预测模型
│   ├── tests/              # 测试
│   ├── main.py             # 入口文件
│   └── requirements.txt    # 依赖
├── frontend/               # 前端代码
│   ├── src/                # 源代码
│   │   ├── api/            # API请求
│   │   ├── assets/         # 静态资源
│   │   ├── components/     # 组件
│   │   ├── composables/    # 组合式函数
│   │   ├── layouts/        # 布局
│   │   ├── router/         # 路由
│   │   ├── stores/         # 状态管理
│   │   ├── types/          # 类型定义
│   │   ├── utils/          # 工具函数
│   │   └── views/          # 页面
│   ├── index.html          # HTML入口
│   └── package.json        # 依赖
└── docx/                   # 文档
    ├── prd.md              # 产品需求文档
    └── 需求分析与设计.md   # 需求分析与设计文档
```

## 首次部署指南

首次部署项目需要进行以下步骤：

### 1. 系统需求

- Python 3.8+
- Node.js 16+
- MySQL 5.7+ 或 SQLite3（作为备用）
- Ollama（如需使用本地大模型）

### 2. 环境变量配置

在 `backend` 目录下创建 `.env` 文件，根据需求配置以下环境变量：

文件路径：`backend/.env` (需要新建)

```bash
# 数据库连接配置
DATABASE_URL=mysql+pymysql://用户名:密码@主机地址/数据库名
# 例如：DATABASE_URL=mysql+pymysql://root:password@localhost/diabetes_assistant

# 大模型配置
MODEL_PROVIDER=ollama  # 模型提供者：local, ollama, openai 等
MODEL_NAME=deepseek-r1:7b  # 使用的Ollama模型名称

# 调试模式
DEBUG=True  # 开发环境设置为 True，生产环境设置为 False
```

### 3. 数据库初始化

#### 3.1 创建 MySQL 数据库

如果使用 MySQL 作为数据库，需要先创建数据库：

```bash
mysql -u root -p
```

在 MySQL 命令行中执行：

```sql
CREATE DATABASE diabetes_assistant CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 3.2 数据库配置

修改 `backend/app/core/config.py` 文件中的 `SQLALCHEMY_DATABASE_URI` 配置：

文件路径：`backend/app/core/config.py`

```python
SQLALCHEMY_DATABASE_URI: Optional[str] = os.getenv(
    "DATABASE_URL",
    # 默认配置，根据实际情况修改
    "mysql+pymysql://用户名:密码@主机地址/数据库名"
)
```

#### 3.3 初始化数据库表和数据

文件路径：`backend/init_db.py`

```bash
cd backend
python init_db.py
```

执行后会创建所有数据表并添加一个默认的超级管理员账户：

- 邮箱：admin@example.com
- 密码：admin123

### 4. Ollama 大模型部署

本项目支持使用 Ollama 部署本地大模型，步骤如下：

#### 4.1 安装 Ollama

根据您的操作系统，从 [Ollama 官网](https://ollama.ai/download) 下载并安装 Ollama。

#### 4.2 下载并运行模型

```bash
# 下载并运行deepseek-r1模型（推荐）
ollama pull deepseek-r1:7b
```

也可以使用其他支持的模型：

```bash
# 其他可选模型
ollama pull llama3:8b      # Meta的Llama 3
ollama pull qwen2:7b       # 阿里云通义千问2
ollama pull yi:34b         # 01.AI的Yi模型
```

#### 4.3 配置后端使用 Ollama

确保在 `.env` 文件中配置了正确的模型提供者和模型名称：

```bash
MODEL_PROVIDER=ollama
MODEL_NAME=deepseek-r1:7b  # 使用的Ollama模型名称
```

### 5. 安装与启动后端

主要文件：`backend/main.py`，`backend/requirements.txt`

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 依赖版本兼容性问题处理

如果遇到依赖版本冲突，可以尝试以下解决方案：

```bash
# 确保安装兼容版本的huggingface-hub和transformers
pip install huggingface-hub==0.13.3
pip install transformers==4.26.0
pip install tokenizers==0.13.2
pip install sentence-transformers==2.2.2

# 如果遇到CUDA相关错误，可以强制使用CPU
# 在.env文件中添加：MODEL_DEVICE=cpu
```

如果启动时出现以下错误：

```
ImportError: cannot import name 'cached_download' from 'huggingface_hub'
```

请确保使用上述兼容版本的依赖，特别是`huggingface-hub`和`sentence-transformers`的版本。

#### 启动后端服务

```bash
# 运行开发服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. 安装与启动前端

主要文件：`frontend/package.json`，`frontend/vite.config.js`

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev
```

### 7. 访问系统

完成以上步骤后，可以通过以下地址访问系统：

- 后端 API 文档：http://localhost:8000/docs
- 前端应用：http://localhost:5173

### 8. 常见问题排查

#### 数据库连接问题

涉及文件：`backend/app/db/session.py`

如果无法连接到 MySQL 数据库，系统会自动切换到 SQLite 作为备用：

```
数据库连接失败: ...
使用备用数据库: sqlite:///diabetes_assistant.db
```

#### 模型加载问题

涉及文件：`backend/app/ml/llm_service.py` 和 `backend/app/ml/ollama_service.py`

如果使用 Ollama 模式时遇到问题，请检查：

1. Ollama 服务是否正在运行（默认端口 11434）
2. 是否已正确下载所需的模型
3. `.env` 文件中的 `MODEL_PROVIDER` 是否设置为 `ollama`
4. `.env` 文件中的 `MODEL_NAME` 是否与已下载的模型名称一致

可以通过访问 `http://localhost:8000/api/v1/ollama/models` 检查可用的 Ollama 模型。

#### 前端连接后端问题

如果前端无法连接后端，请检查：

1. 后端服务是否正在运行
2. CORS 配置是否正确（在 `backend/main.py` 中）
3. 前端 API 基础 URL 是否正确（在 `frontend/src/api/index.ts` 中）

#### 数据验证错误

如果在使用 API 时出现数据验证错误，特别是涉及 `message_metadata` 字段，可能是由于 Pydantic 模型与数据库模型之间的字段不匹配。请检查 `app/models` 目录下的相关模型定义。

## 安装与运行（简化版）

### 后端

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
uvicorn main:app --reload
```

### 前端

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev
```

## Ollama 模型部署与使用

本项目支持使用 Ollama 快速部署和使用大语言模型。

### 安装 Ollama

从 [Ollama 官网](https://ollama.ai/download) 下载并安装 Ollama。

### 下载并使用模型

```bash
# 下载模型
ollama pull deepseek-r1:7b

# 启动Ollama服务
# 默认情况下，安装后Ollama会自动运行为系统服务

# 检查Ollama状态
ollama ps

# 测试模型
ollama run deepseek-r1:7b "你好，请介绍一下糖尿病的基本知识"
```

### 配置项目使用 Ollama

在 `.env` 文件中添加：

```
MODEL_PROVIDER=ollama
MODEL_NAME=deepseek-r1:7b
```

## 贡献

欢迎提交 Issue 和 Pull Request，一起完善这个项目。

## 许可证

MIT
