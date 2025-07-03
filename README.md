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

# 首次部署指南

如何部署糖尿病智能健康助理系统。请按照以下步骤一步一步操作。

## 第一部分：准备工作

### 1. 下载必要软件

在开始前，我们需要下载并安装几个软件。这些软件都是免费的，请按照以下链接下载：

#### 1.1 安装 Python

Python 是运行后端服务的必要软件。

- 访问 [Python 官网](https://www.python.org/downloads/)
- 点击"Download Python 3.10.x"按钮（x 是版本号，选择最新的即可）
- 下载完成后，双击安装文件
- **重要**：在安装过程中，勾选"Add Python to PATH"选项
- 点击"Install Now"完成安装

![Python安装示意图](https://example.com/python_install.png)
（请注意：实际使用时，可以添加真实的截图链接或说明）

#### 1.2 安装 Node.js

Node.js 是运行前端服务的必要软件。

- 访问 [Node.js 官网](https://nodejs.org/)
- 下载"LTS"（长期支持版）版本
- 下载完成后，双击安装文件
- 按照安装向导完成安装，全部使用默认选项即可

#### 1.3 安装 MySQL（可选，使用 SQLite 可跳过）

如果你想使用 MySQL 数据库，需要安装 MySQL：

- 访问 [MySQL 官网](https://dev.mysql.com/downloads/installer/)
- 下载"MySQL Installer"
- 运行安装程序，选择"Server only"或"Custom"安装
- 设置 root 用户密码（请记住这个密码，后面需要用到）
- 完成安装

#### 1.4 安装 Navicat Premium（数据库管理工具）

Navicat Premium 是一款强大的数据库管理工具，可以帮助你更方便地管理 MySQL 数据库。

- 访问 [Navicat Premium 下载页面](https://www.uy5.net/navicat-premium/)
- 下载"Navicat Premium 17.0.8 (x64) 中文版.zip"或"Navicat Premium 17.0.8 (x64) 英语版.zip"
- 下载完成后，解压缩文件
- 按照以下步骤进行安装和激活：
  1. 运行解压后的安装文件，进行安装（记住安装位置，默认为`C:\Program Files\PremiumSoft\Navicat Premium 17`）
  2. 安装完成后，先不要运行软件
  3. 进入解压目录中的"crack"文件夹
  4. 如果之前安装过 Navicat，运行"无限试用 Navicat.bat"删除注册表
  5. 将"winmm.dll"文件复制到 Navicat 的安装目录中
  6. 运行 Navicat Premium，如果没有提示试用，表示激活成功

#### 1.5 安装 Visual Studio Code（推荐的代码编辑器）

Visual Studio Code (VSCode) 是一款免费、功能强大的代码编辑器，非常适合用来查看和编辑项目代码。

- 访问 [Visual Studio Code 官网](https://code.visualstudio.com/)
- 点击"Download for Windows"（或你的操作系统对应的版本）
- 下载完成后，运行安装程序
- 按照安装向导完成安装，建议勾选"Add to PATH"选项

#### 1.6 安装 Ollama（用于本地运行 AI 模型）

Ollama 让你可以在自己的电脑上运行 AI 大模型。

- 访问 [Ollama 官网](https://ollama.ai/download)
- 根据你的操作系统（Windows/Mac/Linux）下载对应版本
- 安装完成后，Ollama 会在后台运行

## 第二部分：获取项目代码

### 2.1 下载项目代码

有两种方式可以获取项目代码：

**方式一：直接下载压缩包**

- 访问项目网站或获取项目压缩包
- 解压到你喜欢的位置，如 `C:\Projects\diabetes-assistant` 或 `D:\diabetes-assistant`
- 记住这个位置，后续步骤会用到

**方式二：使用 Git 克隆**

- 安装 [Git](https://git-scm.com/downloads)
- 打开命令提示符（在 Windows 搜索栏中输入"cmd"并打开）
- 输入以下命令：
  ```
  git clone https://github.com/username/diabetes-assistant.git
  cd diabetes-assistant
  ```

## 第三部分：配置后端

### 3.1 创建虚拟环境

虚拟环境可以避免不同项目之间的依赖冲突。

1. 打开命令提示符（在 Windows 搜索栏中输入"cmd"并打开）
2. 导航到项目的后端目录：

   ```
   cd 路径\到\项目\diabetes-assistant\backend
   ```

   例如：`cd C:\Projects\diabetes-assistant\backend`

3. 创建虚拟环境：

   ```
   python -m venv venv
   ```

4. 激活虚拟环境：

   - Windows 系统：
     ```
     venv\Scripts\activate
     ```
   - Mac/Linux 系统：
     ```
     source venv/bin/activate
     ```

   激活成功后，命令行前面会出现 `(venv)` 字样

### 3.2 安装后端依赖

在激活的虚拟环境中，安装项目所需的所有库：

```
pip install -r requirements.txt
```

这个过程可能需要几分钟时间，请耐心等待。如果出现错误，可能是网络问题，请重试几次。

### 3.3 配置环境变量

1. 在后端目录下创建一个名为 `.env` 的文件（注意文件名前面有一个点）

   **Windows 创建 .env 文件的方法**：

   - 打开记事本
   - 写入以下内容
   - 保存时，文件名输入 `.env`（包括引号），保存类型选择"所有文件"

2. 在 `.env` 文件中添加以下内容：

   ```
   # 数据库配置（使用 SQLite，最简单的方式）
   DATABASE_URL=sqlite:///diabetes_assistant.db

   # 大模型配置
   MODEL_PROVIDER=ollama
   MODEL_NAME=deepseek-r1:7b
   MODEL_DEVICE=cpu

   # 调试模式
   DEBUG=True
   ```

   如果你安装了 MySQL 并想使用它，可以替换为：

   ```
   DATABASE_URL=mysql+pymysql://root:你的MySQL密码@localhost/diabetes_assistant
   ```

### 3.4 初始化数据库

1. 如果你选择使用 MySQL，需要先创建数据库：

   - 打开命令提示符
   - 输入：`mysql -u root -p`
   - 输入你的 MySQL 密码
   - 在 MySQL 命令行中执行：
     ```sql
     CREATE DATABASE diabetes_assistant CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
     exit;
     ```

2. 初始化数据库表和数据：

   - 确保你在后端目录，并且虚拟环境已激活（命令行前面有 `(venv)` 字样）
   - 运行：
     ```
     python setup_dev.py --sample-data
     ```

   这个命令会创建所有必要的数据库表，并添加一些示例数据。

### 3.5 下载 AI 模型

如果你想使用本地 AI 模型，需要通过 Ollama 下载模型：

1. 确保 Ollama 已安装并运行
2. 打开命令提示符，运行：

   ```
<<<<<<< HEAD
   ollama pull deepseek-r1:7b
=======
   ollama run deepseek-r1:1.5b
>>>>>>> 8f592862b6056589a6c30f0453ee467b7493343b
   ```

   这将下载大约 4GB 的模型文件，取决于你的网络速度，可能需要一段时间。

## 第四部分：配置前端

### 4.1 安装前端依赖

1. 打开一个新的命令提示符窗口
2. 导航到项目的前端目录：

   ```
   cd 路径\到\项目\diabetes-assistant\frontend
   ```

   例如：`cd C:\Projects\diabetes-assistant\frontend`

3. 安装依赖：

   ```
   npm install
   ```

   这个过程可能需要几分钟时间。

### 4.2 配置前端环境变量

1. 在前端目录下创建一个名为 `.env.local` 的文件
2. 在文件中添加以下内容：
   ```
   VITE_API_URL=http://localhost:8000
   ```

## 第五部分：启动系统

### 5.1 启动后端服务

1. 确保你在后端目录，并且虚拟环境已激活
2. 运行：
   ```
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
3. 看到类似以下输出表示成功：
   ```
   INFO:     Started server process [12345]
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
   ```
4. 保持这个窗口开着，不要关闭

### 5.2 启动前端服务

1. 打开一个新的命令提示符窗口
2. 导航到前端目录
3. 运行：
   ```
   npm run dev
   ```
4. 看到类似以下输出表示成功：

   ```
   VITE v4.x.x ready in xxx ms

   ➜  Local:   http://localhost:5173/
   ➜  Network: http://192.168.x.x:5173/
   ```

5. 同样保持这个窗口开着，不要关闭

### 5.3 访问系统

1. 打开你的浏览器（推荐使用 Chrome、Edge 或 Firefox 的最新版本）
2. 访问：http://localhost:5173
3. 你应该能看到系统的登录页面
4. 使用以下默认账户登录：
   - 邮箱：admin@diabetes-assistant.com
   - 密码：diabetes2024

## 第六部分：使用 Navicat Premium 管理数据库

Navicat Premium 是一款功能强大的数据库管理工具，可以帮助你方便地查看和管理数据库。以下是使用 Navicat Premium 连接项目数据库的步骤：

### 6.1 连接 MySQL 数据库

如果你使用的是 MySQL 数据库：

1. 打开 Navicat Premium
2. 点击左上角的"连接"按钮，选择"MySQL"
3. 在弹出的窗口中填写以下信息：
   - 连接名：自定义一个名称，如"糖尿病助理"
   - 主机：localhost（本地主机）
   - 端口：3306（MySQL 默认端口）
   - 用户名：root（或你设置的其他用户名）
   - 密码：你在安装 MySQL 时设置的密码
4. 点击"测试连接"确保连接成功
5. 点击"确定"保存连接
6. 在左侧连接列表中，双击你刚创建的连接
7. 展开连接后，你应该能看到"diabetes_assistant"数据库
8. 展开该数据库，你可以看到所有表格

### 6.2 连接 SQLite 数据库

如果你使用的是 SQLite 数据库：

1. 打开 Navicat Premium
2. 点击左上角的"连接"按钮，选择"SQLite"
3. 在弹出的窗口中填写以下信息：
   - 连接名：自定义一个名称，如"糖尿病助理 SQLite"
   - 数据库文件：点击"浏览"，找到项目目录中的"diabetes_assistant.db"文件
     （通常位于项目的根目录或 backend 目录）
4. 点击"确定"保存连接
5. 在左侧连接列表中，双击你刚创建的连接
6. 你应该能看到所有表格

### 6.3 查看和编辑数据

1. 在表格列表中，双击任意表格（如"users"表）查看其内容
2. 你可以直接在表格视图中编辑数据：
   - 双击某个单元格进行编辑
   - 点击工具栏中的"保存"按钮保存更改
3. 你也可以执行 SQL 查询：
   - 点击工具栏中的"查询"按钮
   - 在查询编辑器中输入 SQL 语句，如：`SELECT * FROM users;`
   - 点击"运行"按钮执行查询

### 6.4 数据库备份

1. 右键点击数据库名称
2. 选择"转储 SQL 文件" > "结构和数据"
3. 选择保存位置，点击"保存"
4. 这将创建一个包含所有数据的 SQL 文件，可用于备份或迁移

## 第七部分：使用 Visual Studio Code 查看和编辑项目代码

Visual Studio Code (VSCode) 是一款功能强大的代码编辑器，可以帮助你查看和编辑项目代码。以下是使用 VSCode 的基本步骤：

### 7.1 打开项目

1. 打开 Visual Studio Code
2. 点击"文件" > "打开文件夹"
3. 导航到项目根目录（例如：`C:\Projects\diabetes-assistant`）
4. 点击"选择文件夹"

### 7.2 安装推荐扩展

为了更好地开发和查看代码，需要安装一些 VSCode 扩展。下面分为必装插件和推荐插件两类：

#### 7.2.1 必装插件

这些插件是使用项目的必要组件，请确保安装：

1. **Python**（Microsoft 官方）
   - 提供 Python 语言支持、调试、智能提示等功能
   - 对后端 Python 代码编辑必不可少
2. **Vue Language Features (Volar)**
   - Vue 3 项目专用插件，提供语法高亮、智能提示等功能
   - 前端 Vue 代码开发必备（如使用 Vue 2，则安装 Vetur）
3. **ESLint**

   - JavaScript 和 TypeScript 代码检查工具
   - 帮助按照项目的代码规范编写代码

4. **SQLite Viewer**
   - 直接在 VSCode 中查看和操作 SQLite 数据库文件
   - 方便在不打开 Navicat 的情况下快速查看 SQLite 数据

#### 7.2.2 推荐插件

这些插件可以提升开发体验，建议安装：

1. **Prettier**

   - 代码格式化工具，保持代码风格统一
   - 自动调整代码格式，提高可读性

2. **HTML CSS Support**

   - 提供 HTML 和 CSS 的智能提示
   - 对编辑前端代码有帮助

3. **GitLens**

   - Git 增强功能，可以查看每行代码的提交历史、作者等信息
   - 帮助理解代码的变更历史

4. **Auto Rename Tag**

   - 自动重命名 HTML/XML 配对的标签
   - 编辑 Vue 模板时非常有用

5. **REST Client**

   - 直接在 VSCode 中测试 API 请求
   - 方便测试后端接口

6. **YAML**
   - YAML 文件支持，提供语法高亮和验证
   - 编辑配置文件时有用

#### 7.2.3 查看已安装的插件

要检查您是否已安装所需的插件，可以按照以下步骤操作：

1. 打开 VSCode
2. 点击左侧边栏的扩展图标（或按 Ctrl+Shift+X）
3. 在扩展面板上方，可以看到"已安装"选项，点击它即可查看所有已安装的插件
4. 如果列表中没有某个必要的插件，在搜索框中输入插件名称进行安装

### 7.3 配置 Python 解释器

1. 按 Ctrl+Shift+P 打开命令面板
2. 输入"Python: Select Interpreter"并选择
3. 选择项目虚拟环境（通常显示为 ./venv 或 ./backend/venv）

### 7.4 浏览项目结构

VSCode 左侧的文件浏览器可以帮助你浏览整个项目结构：

- `backend/` 目录包含所有后端代码
  - `app/` 包含主要的应用代码
  - `main.py` 是后端的入口文件
- `frontend/` 目录包含所有前端代码
  - `src/` 包含主要的源代码
  - `src/views/` 包含所有页面组件

### 7.5 编辑代码

1. 在文件浏览器中点击任何文件以打开
2. 编辑文件内容
3. 使用 Ctrl+S 保存更改
4. 如果你修改了后端代码，由于启动时使用了 `--reload` 参数，服务会自动重启
5. 如果你修改了前端代码，页面会自动刷新以反映更改

### 7.6 使用终端

VSCode 内置了终端，可以直接在编辑器中运行命令：

1. 点击顶部菜单的"终端" > "新建终端"（或按 Ctrl+`)
2. 在终端中，你可以运行前面提到的所有命令

## 第八部分：常见问题解决

### 8.1 后端启动问题

#### 问题：找不到模块或库

- **症状**：启动时出现 `ImportError: No module named xxx`
- **解决方法**：确保你已激活虚拟环境，并运行 `pip install -r requirements.txt`

#### 问题：依赖版本冲突

- **症状**：出现 `ImportError: cannot import name 'cached_download' from 'huggingface_hub'`
- **解决方法**：运行以下命令安装兼容版本：
  ```
  pip install huggingface-hub==0.13.3
  pip install transformers==4.26.0
  pip install tokenizers==0.13.2
  pip install sentence-transformers==2.2.2
  ```

#### 问题：数据库连接错误

- **症状**：出现 `OperationalError: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server")`
- **解决方法**：
  1. 确保 MySQL 服务已启动
  2. 检查 `.env` 文件中的数据库连接信息是否正确
  3. 或者切换到 SQLite：修改 `.env` 文件中的 `DATABASE_URL=sqlite:///diabetes_assistant.db`

#### 问题：端口被占用

- **症状**：出现 `OSError: [Errno 48] Address already in use`
- **解决方法**：
  1. 关闭可能占用 8000 端口的其他程序
  2. 或者使用不同的端口：`python -m uvicorn main:app --reload --port 8001`
  3. 如果使用不同的端口，记得同时修改前端的 `.env.local` 文件中的 API 地址

### 8.2 前端启动问题

#### 问题：Node.js 版本过低

- **症状**：启动时出现与 Node.js 版本相关的错误
- **解决方法**：下载并安装最新的 Node.js LTS 版本

#### 问题：依赖安装失败

- **症状**：`npm install` 命令出现错误
- **解决方法**：
  1. 删除 `node_modules` 文件夹和 `package-lock.json` 文件
  2. 重新运行 `npm install`
  3. 如果仍然失败，尝试使用 `npm install --legacy-peer-deps`

#### 问题：前端无法连接后端

- **症状**：登录或其他操作失败，控制台显示网络错误
- **解决方法**：
  1. 确保后端服务正在运行
  2. 检查前端的 `.env.local` 文件中的 API 地址是否正确
  3. 如果后端使用了不同的端口，相应更新前端配置

### 8.3 Ollama 模型问题

#### 问题：模型下载失败

- **症状**：`ollama pull` 命令失败或中断
- **解决方法**：
  1. 检查网络连接
  2. 重新运行 `ollama pull deepseek-r1:7b`
  3. 如果仍然失败，可以尝试下载较小的模型：`ollama pull tinyllama`

#### 问题：Ollama 服务未运行

- **症状**：系统提示无法连接到 Ollama 服务
- **解决方法**：
  1. 检查 Ollama 是否已安装
  2. Windows: 在任务管理器中查找 Ollama 进程，如果没有，重新安装
  3. Mac/Linux: 运行 `ollama serve` 启动服务

#### 问题：内存不足

- **症状**：使用 AI 功能时系统变慢或崩溃
- **解决方法**：
  1. 关闭其他内存占用大的程序
  2. 尝试使用较小的模型：修改 `.env` 文件中的 `MODEL_NAME=tinyllama`
  3. 确保 `MODEL_DEVICE=cpu` 设置已添加到 `.env` 文件中

### 8.4 Navicat Premium 问题

#### 问题：连接数据库失败

- **症状**：尝试连接 MySQL 数据库时出现错误
- **解决方法**：
  1. 确保 MySQL 服务正在运行
  2. 验证用户名和密码是否正确
  3. 检查主机名和端口是否正确（默认为 localhost:3306）

#### 问题：找不到 SQLite 数据库文件

- **症状**：无法找到或打开 SQLite 数据库文件
- **解决方法**：
  1. 确认数据库文件的位置（通常在项目根目录或 backend 目录）
  2. 确保文件存在且未被锁定（可能需要关闭其他正在使用该文件的程序）

#### 问题：激活问题

- **症状**：Navicat Premium 显示试用期限或需要激活
- **解决方法**：
  1. 确保正确完成了激活步骤
  2. 重新运行"无限试用 Navicat.bat"脚本
  3. 确保"winmm.dll"文件已正确复制到安装目录

## 第九部分：系统使用指南

### 9.1 用户管理

- **注册新用户**：点击登录页面的"注册"按钮
- **登录**：使用邮箱和密码登录
- **修改个人信息**：登录后，点击右上角用户头像，选择"设置"

### 9.2 血糖管理

- **添加血糖记录**：在"血糖管理"页面，点击"添加记录"按钮
- **查看血糖趋势**：在"血糖管理"页面，可以查看血糖变化图表
- **设置目标**：在"设置"页面，可以设置血糖目标范围

### 9.3 饮食管理

- **记录饮食**：在"饮食管理"页面，点击"添加饮食记录"
- **查看营养分析**：系统会自动分析记录的食物营养成分
- **获取饮食建议**：基于血糖和饮食记录，系统会提供个性化建议

### 9.4 智能助理

- **咨询健康问题**：在"智能助理"页面，直接输入问题
- **查看历史对话**：所有与助理的对话都会保存，可以随时查看
- **清除对话历史**：如果需要，可以点击"清除历史"按钮

## 第十部分：其他资源

### 10.1 项目文档

- **主项目文档**：位于项目根目录的 `README.md`
- **后端文档**：位于 `backend/README.md`
- **前端文档**：位于 `frontend/README.md`
- **产品需求文档**：位于 `docx/prd.md`
- **需求分析与设计**：位于 `docx/需求分析与设计.md`

### 10.2 寻求帮助

如果你在使用过程中遇到任何问题，可以：

1. 查看本文档的常见问题解决部分
2. 查看详细的项目文档
3. 联系项目维护者寻求支持

---

希望本指南能帮助你顺利部署和使用糖尿病智能健康助理系统！如有任何问题或建议，欢迎反馈。

## 贡献

欢迎提交 Issue 和 Pull Request，一起完善这个项目。

## 许可证

MIT
