# 糖尿病智能健康助理产品需求文档(PRD)

## 1. 项目概述

### 1.1 项目背景

糖尿病作为全球高发慢性疾病，患者需要长期进行血糖监测、饮食管理、药物调整和健康咨询。传统管理方式存在患者依从性低、个性化不足、医疗资源紧张等问题。本项目旨在开发一个基于大模型的智能健康助理，提供全方位的糖尿病管理服务。

### 1.2 项目目标

- 提高患者自我管理能力和依从性
- 提供个性化的健康建议和干预
- 减轻医疗资源压力
- 提升患者生活质量

### 1.3 技术栈

- 前端：Vue 3 + Element Plus + Vite + TypeScript
- 后端：Python + FastAPI
- 数据库：MySQL
- 本地大模型：DeepSeek-Lite-7B（适合 6G 显存部署）
- 向量数据库：Chroma（存储 RAG 知识库）

## 2. 功能模块详细设计

### 2.1 用户管理模块

#### 2.1.1 用户注册/登录

- 支持手机号、邮箱注册/登录
- 短信/邮箱验证码功能
- JWT token 认证机制
- 密码加密存储

#### 2.1.2 个人信息管理

- 基础信息：姓名、年龄、性别、身高、体重
- 疾病信息：糖尿病类型（1 型/2 型）、确诊时间
- 风险因素：高血压、吸烟史、家族遗传史
- 头像上传与编辑功能

#### 2.1.3 健康风险评估

- 基于 ADA（美国糖尿病协会）风险评分系统
- 可视化风险评估结果
- 提供针对性风险干预建议

### 2.2 健康数据管理模块

#### 2.2.1 个人健康卡

- 基础健康指标：BMI、血压、血脂、糖化血红蛋白
- 数据可视化展示
- 历史趋势图表

#### 2.2.2 个人病例管理

- 就诊记录：医院、科室、医生、诊断结果
- 用药历史：药品名称、剂量、频次、服用时间
- 并发症记录：眼底病变、肾病、神经病变等
- 检查报告上传功能（支持 PDF、图片格式）

#### 2.2.3 血糖数据管理

- 手动录入：空腹、餐后、睡前血糖值
- 设备同步：预留血糖仪 API 接口
- 血糖日志：时间、数值、状态（正常/偏高/偏低）
- 数据导出功能（CSV、PDF 格式）

#### 2.2.4 饮食记录

- 拍照识别食物（调用图像识别 API）
- 手动搜索食物数据库
- 记录食物种类、分量、热量、碳水化合物
- 每日营养摄入统计

### 2.3 预测与分析模块

#### 2.3.1 糖尿病风险预测

- 基于机器学习模型（随机森林/XGBoost）
- 输入：生活习惯、家族史、BMI 等指标
- 输出：患病风险概率、风险等级

#### 2.3.2 血糖趋势预测

- 基于 LSTM 时间序列模型
- 输入：历史血糖数据、饮食记录、运动记录
- 输出：未来 24 小时血糖趋势曲线
- 模型定期重训练（每周/每月）

#### 2.3.3 异常血糖预警

- 设置个性化血糖目标范围
- 实时监测血糖数据
- 当预测血糖超出范围时推送预警
- 预警级别：轻度、中度、严重

### 2.4 糖尿病医疗智能体

#### 2.4.1 智能问答系统

- 基于 DeepSeek-Lite-7B 大模型
- RAG 技术结合个人健康卡数据
- 支持自然语言交互
- 问答内容：
  - 糖尿病基础知识
  - 医学术语解释
  - 个性化健康建议
  - 药物使用指导

#### 2.4.2 饮食计划生成

- 基于个人血糖数据、饮食偏好生成
- 考虑因素：热量需求、碳水限制、口味偏好
- 输出：一日三餐食谱推荐
- 食物替代建议功能

#### 2.4.3 血糖管理建议

- 运动方案推荐（类型、强度、时长）
- 用药提醒（时间、剂量）
- 生活方式调整建议
- 定期健康报告生成

### 2.5 糖尿病护理百科

#### 2.5.1 知识库管理

- 糖尿病基础知识（病因、症状、并发症）
- 饮食指南（升糖指数表、食物营养成分）
- 运动建议（适合糖尿病患者的运动方式）
- 常见问题解答

#### 2.5.2 社区互动（可选）

- 经验分享功能
- 话题讨论区
- 内容审核机制
- 点赞、收藏、评论功能

## 3. 数据库设计

### 3.1 用户表(users)

- id: int (主键)
- username: varchar(50)
- email: varchar(100)
- phone: varchar(20)
- password_hash: varchar(255)
- created_at: datetime
- updated_at: datetime

### 3.2 用户信息表(user_profiles)

- id: int (主键)
- user_id: int (外键)
- age: int
- gender: enum('male', 'female', 'other')
- height: float
- weight: float
- diabetes_type: enum('type1', 'type2', 'other')
- diagnosis_date: date
- hypertension: boolean
- smoking_history: boolean
- family_history: boolean
- avatar_url: varchar(255)

### 3.3 健康数据表(health_records)

- id: int (主键)
- user_id: int (外键)
- record_date: date
- bmi: float
- blood_pressure_systolic: int
- blood_pressure_diastolic: int
- cholesterol: float
- hba1c: float
- created_at: datetime
- updated_at: datetime

### 3.4 血糖记录表(glucose_records)

- id: int (主键)
- user_id: int (外键)
- record_time: datetime
- glucose_value: float
- measurement_type: enum('fasting', 'post_meal', 'before_sleep', 'other')
- notes: text
- created_at: datetime

### 3.5 饮食记录表(diet_records)

- id: int (主键)
- user_id: int (外键)
- meal_time: datetime
- meal_type: enum('breakfast', 'lunch', 'dinner', 'snack')
- food_items: json
- total_calories: float
- total_carbs: float
- image_url: varchar(255)
- notes: text

### 3.6 医疗记录表(medical_records)

- id: int (主键)
- user_id: int (外键)
- visit_date: date
- hospital: varchar(100)
- doctor: varchar(50)
- diagnosis: text
- prescription: text
- report_url: varchar(255)

### 3.7 知识库表(knowledge_base)

- id: int (主键)
- category: enum('basic', 'diet', 'exercise', 'medication', 'complication')
- title: varchar(255)
- content: text
- tags: json
- created_at: datetime
- updated_at: datetime

## 4. API 设计

### 4.1 用户管理 API

- POST /api/users/register - 用户注册
- POST /api/users/login - 用户登录
- GET /api/users/profile - 获取用户信息
- PUT /api/users/profile - 更新用户信息
- POST /api/users/risk-assessment - 健康风险评估

### 4.2 健康数据 API

- GET /api/health/summary - 获取健康数据摘要
- POST /api/health/records - 添加健康记录
- GET /api/health/records - 获取健康记录列表
- GET /api/health/records/{id} - 获取单条健康记录
- PUT /api/health/records/{id} - 更新健康记录

### 4.3 血糖管理 API

- POST /api/glucose/records - 添加血糖记录
- GET /api/glucose/records - 获取血糖记录列表
- GET /api/glucose/statistics - 获取血糖统计数据
- GET /api/glucose/prediction - 获取血糖预测数据
- POST /api/glucose/alert-settings - 设置血糖预警阈值

### 4.4 饮食管理 API

- POST /api/diet/records - 添加饮食记录
- GET /api/diet/records - 获取饮食记录列表
- POST /api/diet/image-recognition - 食物图像识别
- GET /api/diet/recommendations - 获取饮食建议

### 4.5 智能助手 API

- POST /api/assistant/chat - 智能问答接口
- GET /api/assistant/diet-plan - 获取饮食计划
- GET /api/assistant/exercise-plan - 获取运动计划
- GET /api/assistant/medication-reminder - 获取用药提醒

### 4.6 知识库 API

- GET /api/knowledge - 获取知识库列表
- GET /api/knowledge/{id} - 获取知识详情
- GET /api/knowledge/search - 搜索知识库

## 5. 本地大模型部署方案

### 5.1 推荐模型：DeepSeek-Lite-7B

- 适合 6G 显存部署（通过量化）
- 优秀的中文理解和生成能力
- 支持 4-bit 量化降低显存占用
- 支持 LoRA 微调适应医疗领域

### 5.2 部署步骤

1. 环境准备：Python 3.8+, CUDA 11.7+, PyTorch 2.0+
2. 模型下载：从 HuggingFace 获取 DeepSeek-Lite-7B 模型
3. 量化处理：使用 GPTQ 或 AWQ 进行 4-bit 量化以减少显存占用
4. FastAPI 集成：封装推理接口
5. RAG 系统构建：
   - 知识库文档收集与处理
   - 向量化存储（使用 Chroma DB）
   - 检索增强生成流程实现

### 5.3 模型优化

- 领域知识微调（糖尿病医疗知识）
- 提示词工程优化
- 上下文长度优化
- 推理速度优化

## 6. 前端页面设计

### 6.1 页面结构

- 登录/注册页
- 个人主页/仪表盘
- 健康数据管理页
- 血糖记录与分析页
- 饮食记录与建议页
- 智能助手聊天页
- 知识库浏览页
- 个人设置页

### 6.2 UI 组件库

- Element Plus（适配 Vue 3）
- ECharts（数据可视化）
- VueUse（常用工具函数）

### 6.3 响应式设计

- 移动端优先设计
- 适配平板与桌面端
- 暗黑模式支持

## 7. 项目实施计划

### 7.1 开发阶段

1. 需求分析与设计（1 周）
2. 数据库设计与搭建（1 周）
3. 后端 API 开发（3 周）
4. 大模型部署与调优（2 周）
5. 前端开发（3 周）
6. 系统集成与测试（2 周）
7. 优化与修复（1 周）

### 7.2 测试计划

- 单元测试：后端 API 功能测试
- 集成测试：前后端交互测试
- 性能测试：大模型响应速度测试
- 用户测试：邀请糖尿病患者进行实际使用测试

### 7.3 部署方案

- 开发环境：Docker 容器化部署
- 生产环境：服务器配置建议
  - CPU: 8 核以上
  - RAM: 16GB 以上
  - GPU: NVIDIA 显卡，6GB 显存以上
  - 存储: SSD 100GB 以上

## 8. 风险评估与应对策略

### 8.1 技术风险

- 大模型部署难度：提前测试不同量化方案
- 数据安全风险：实施严格的数据加密和访问控制
- 系统性能风险：进行负载测试和性能优化

### 8.2 业务风险

- 医疗建议准确性：明确免责声明，不替代专业医疗建议
- 用户隐私保护：严格遵守数据保护法规
- 用户接受度：进行用户体验研究，优化交互设计

## 9. 项目扩展计划

### 9.1 功能扩展

- 医患沟通模块：连接患者与医生
- 可穿戴设备集成：支持更多血糖监测设备
- 多语言支持：扩展国际化能力

### 9.2 技术升级

- 模型升级：随着硬件条件改善，升级到更大参数模型
- 算法优化：持续改进血糖预测算法
- 移动应用开发：基于现有系统开发原生移动应用

## 10. 附录

### 10.1 参考资料

- 美国糖尿病协会(ADA)指南
- 中国糖尿病防治指南
- DeepSeek-Lite 模型文档

### 10.2 术语表

- RAG: Retrieval-Augmented Generation，检索增强生成
- LSTM: Long Short-Term Memory，长短期记忆网络
- HbA1c: 糖化血红蛋白，反映近 3 个月血糖控制情况
