## 糖尿病助手项目API服务总结

### 主要API路由结构

该项目使用FastAPI框架构建，主API入口在backend/main.py中定义，所有API路由前缀为/api/v1。主要路由包括：

1. 用户管理 /api/v1/users

- 注册新用户: POST /register

- 用户登录: POST /login

- 健康风险评估: POST /risk-assessment

1. 健康记录 /api/v1/health

- 创建健康记录: POST /

- 获取健康记录: GET /

- 获取单条健康记录: GET /{record_id}

- 更新健康记录: PUT /{record_id}

- 删除健康记录: DELETE /{record_id}

1. 血糖记录 /api/v1/glucose

- 创建血糖记录: POST /

- 获取血糖记录列表: GET /

- 获取血糖统计数据: GET /statistics

- 获取最近血糖记录: GET /recent

- 获取单条血糖记录: GET /{record_id}

- 更新血糖记录: PUT /{record_id}

- 删除血糖记录: DELETE /{record_id}

1. 饮食记录 /api/v1/diet

- 创建饮食记录: POST /

- 获取饮食记录列表: GET /

- 获取最近饮食记录: GET /recent

- 获取饮食统计数据: GET /statistics

- 获取单条饮食记录: GET /{record_id}

- 上传食物图片: POST /upload-image

1. 智能助手 /api/v1/assistant

- 聊天接口: POST /chat

- 获取聊天历史: GET /history

- 清空聊天历史: DELETE /history

- 创建对话: POST /conversations

- 获取对话列表: GET /conversations

- 获取单个对话: GET /conversations/{conversation_id}

- 更新对话: PUT /conversations/{conversation_id}

- 删除对话: DELETE /conversations/{conversation_id}

- 创建消息: POST /messages

- 获取对话消息: GET /conversations/{conversation_id}/messages

1. 知识库 /api/v1/knowledge

- 创建知识库条目: POST /

- 获取知识库条目列表: GET /

- 获取单个知识库条目: GET /{entry_id}

- 更新知识库条目: PUT /{entry_id}

- 删除知识库条目: DELETE /{entry_id}

1. 大模型服务 /api/v1/ollama

- 获取可用模型列表: GET /models

- 获取模型信息: GET /models/{model_name}

- 生成文本(GET方法): GET /generate

- 生成文本(POST方法): POST /generate

- 检查服务健康状态: GET /health