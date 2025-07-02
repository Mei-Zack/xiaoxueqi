# 糖尿病智能健康助理 - 前端

基于Vue 3 + TypeScript的糖尿病智能健康助理系统前端，提供直观、友好的用户界面，帮助糖尿病患者进行健康管理。

## 技术栈

- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP客户端**: Axios
- **图表**: ECharts, Chart.js

## 目录结构

```
frontend/
├── src/                # 源代码
│   ├── api/            # API请求
│   ├── assets/         # 静态资源
│   ├── components/     # 组件
│   ├── composables/    # 组合式函数
│   ├── layouts/        # 布局
│   ├── router/         # 路由
│   ├── stores/         # 状态管理
│   ├── types/          # 类型定义
│   ├── utils/          # 工具函数
│   ├── views/          # 页面
│   ├── App.vue         # 根组件
│   └── main.ts         # 入口文件
├── public/             # 公共资源
├── index.html          # HTML入口
├── tsconfig.json       # TypeScript配置
├── vite.config.ts      # Vite配置
└── package.json        # 依赖
```

## 功能模块

- **用户管理**: 注册、登录、个人信息管理
- **仪表盘**: 健康数据概览、提醒事项
- **血糖管理**: 血糖记录、趋势图表、异常提醒
- **饮食管理**: 饮食记录、营养分析、饮食建议
- **健康数据**: 体重、血压、运动等健康指标记录与分析
- **智能助理**: 基于大模型的健康咨询与建议
- **知识库**: 糖尿病相关知识、文章、健康指南
- **设置**: 个人偏好、通知设置

## 安装

### 1. 安装依赖

```bash
npm install
```

### 2. 配置环境变量

创建`.env.local`文件并配置以下环境变量:

```
VITE_API_URL=http://localhost:8000
```

## 运行

### 开发环境

```bash
npm run dev
```

访问 http://localhost:5173 查看应用。

### 构建生产版本

```bash
npm run build
```

构建后的文件将生成在`dist`目录中。

## 代码规范

### 代码风格检查

```bash
npm run lint
```

### 代码格式化

```bash
npm run format
```

## 测试

```bash
npm run test
```

## 浏览器兼容性

- Chrome (最新版)
- Firefox (最新版)
- Safari (最新版)
- Edge (最新版)
