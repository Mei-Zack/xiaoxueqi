<template>
  <div class="assistant-container">
    <div class="chat-header">
      <h2>智能健康助理</h2>
      <div class="chat-actions">
        <el-dropdown v-if="availableModels.length > 0" @command="selectModel" style="margin-right: 10px;">
          <el-button type="primary" plain size="small">
            {{ selectedModel || '选择模型' }}
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-for="model in availableModels"
                :key="model.name"
                :command="model.name"
              >
                {{ model.name }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button type="danger" plain size="small" @click="clearHistory">
          清空对话
        </el-button>
      </div>
    </div>
    
    <div class="chat-body" ref="chatBodyRef">
      <div v-if="loading && messages.length === 0" class="loading-container">
        <el-skeleton :rows="3" animated />
      </div>
      
      <template v-else>
        <div v-if="messages.length === 0" class="welcome-message">
          <div class="welcome-icon">
            <el-icon :size="48"><ChatLineRound /></el-icon>
          </div>
          <h3>您好，我是小雪琪</h3>
          <p>您的糖尿病智能健康助理，有任何健康问题都可以问我。</p>
          <div class="suggestion-chips">
            <el-button
              v-for="(suggestion, index) in suggestions"
              :key="index"
              size="small"
              @click="sendMessage(suggestion)"
            >
              {{ suggestion }}
            </el-button>
          </div>
          <div class="model-status" v-if="modelStatus">
            <el-tag :type="modelStatus === 'active' ? 'success' : 'danger'">
              {{ modelStatus === 'active' ? 'Ollama已连接' : 'Ollama未连接' }}
            </el-tag>
          </div>
        </div>
        
        <div v-for="(message, index) in messages" :key="index" class="message-container" :class="{ 'user-message': message.role === 'user', 'assistant-message': message.role === 'assistant' }">
          <div class="message-avatar">
            <el-avatar v-if="message.role === 'user'" :size="36" :src="userAvatar">{{ userInitial }}</el-avatar>
            <el-avatar v-else :size="36" src="/assistant-avatar.png">小雪琪</el-avatar>
          </div>
          <div class="message-content">
            <div class="message-text" v-html="formatMessage(message.content)"></div>
            <div v-if="message.metadata?.sources && message.metadata.sources.length > 0" class="message-sources">
              <div class="sources-title">参考资料：</div>
              <div v-for="(source, idx) in message.metadata.sources" :key="idx" class="source-item">
                <el-link type="primary" @click="showSourceDetail(source)">{{ source.title }}</el-link>
              </div>
            </div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>
      </template>
      
      <div v-if="loading" class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>
    
    <div class="chat-input">
      <el-input
        v-model="userInput"
        type="textarea"
        :rows="2"
        placeholder="请输入您的问题..."
        resize="none"
        @keydown.enter.prevent="handleEnterKey"
      />
      <div class="send-options">
        <el-checkbox v-model="useOllama" @change="handleOllamaToggle">使用Ollama</el-checkbox>
        <el-button
          type="primary"
          :disabled="!userInput.trim() || loading"
          @click="sendMessage()"
        >
          发送
        </el-button>
      </div>
    </div>

    <!-- 知识源详情对话框 -->
    <el-dialog
      v-model="sourceDialogVisible"
      title="参考资料详情"
      width="60%"
      :before-close="handleCloseSourceDialog"
    >
      <div v-if="selectedSource">
        <h3>{{ selectedSource.title }}</h3>
        <div class="source-content">{{ selectedSource.content }}</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ChatLineRound, ArrowDown } from '@element-plus/icons-vue'
import { assistantApi, ollamaApi } from '../api'
import { useUserStore } from '../stores/user'
import dayjs from 'dayjs'
import { marked } from 'marked'

const userStore = useUserStore()
const chatBodyRef = ref<HTMLElement | null>(null)
const messages = ref<any[]>([])
const userInput = ref('')
const loading = ref(false)
const currentConversationId = ref<string | null>(null)
const userAvatar = ref(userStore.user.avatar || '')
const userInitial = computed(() => {
  return userStore.user.name ? userStore.user.name.charAt(0).toUpperCase() : 'U'
})

// Ollama相关
const useOllama = ref(false)
const modelStatus = ref<'active' | 'inactive' | null>(null)
const availableModels = ref<any[]>([])
const selectedModel = ref<string>('')
const ollamaConversation = ref<Array<{role: string, content: string}>>([])

// 系统提示词
const systemPrompt = `你是一个专业的糖尿病健康助理，名为"小雪琪"。你的任务是帮助用户管理糖尿病，提供健康建议，解答相关问题。
请遵循以下原则：
1. 提供准确、科学的糖尿病相关信息和建议
2. 根据用户的具体情况提供个性化建议
3. 使用友好、专业的语气，避免医学术语过于专业化
4. 不要假装你是医生，重要医疗决策应建议用户咨询专业医生
5. 回答要简洁明了，突出重点
6. 用中文回答用户的问题`

// 知识源详情相关
const sourceDialogVisible = ref(false)
const selectedSource = ref<any>(null)

const suggestions = [
  '什么是糖尿病?',
  '如何控制血糖?',
  '糖尿病患者的饮食建议',
  '运动对血糖的影响',
  '低血糖的处理方法'
]

onMounted(async () => {
  loading.value = true
  try {
    // 检查Ollama服务状态
    checkOllamaStatus()
    
    // 获取历史消息
    const response = await assistantApi.getConversationHistory()
    messages.value = response.data
    
    // 如果有消息，设置当前对话ID
    if (response.data && response.data.length > 0) {
      currentConversationId.value = response.data[0].conversation_id
    }
    
    scrollToBottom()
  } catch (error) {
    console.error('获取聊天历史失败', error)
    ElMessage.error('获取聊天历史失败')
  } finally {
    loading.value = false
  }
})

// 检查Ollama服务状态
const checkOllamaStatus = async () => {
  try {
    const healthResponse = await ollamaApi.checkHealth()
    if (healthResponse.data && healthResponse.data.status === 'ok') {
      modelStatus.value = 'active'
      // 加载可用模型
      const modelsResponse = await ollamaApi.listModels()
      if (modelsResponse.data && modelsResponse.data.models) {
        availableModels.value = modelsResponse.data.models
        if (availableModels.value.length > 0) {
          selectedModel.value = availableModels.value[0].name
        }
      }
    } else {
      modelStatus.value = 'inactive'
    }
  } catch (error) {
    console.error('Ollama服务检查失败', error)
    modelStatus.value = 'inactive'
  }
}

const handleOllamaToggle = (val: boolean) => {
  if (val && modelStatus.value !== 'active') {
    ElMessage.warning('Ollama服务未连接，请检查后端服务是否正常运行')
    useOllama.value = false
    return
  }
  
  if (val) {
    // 清空当前Ollama对话历史
    ollamaConversation.value = []
    
    // 如果有现有消息，将其添加到Ollama对话历史中
    if (messages.value.length > 0) {
      messages.value.forEach(msg => {
        ollamaConversation.value.push({
          role: msg.role,
          content: msg.content
        })
      })
    }
  }
}

const selectModel = (modelName: string) => {
  selectedModel.value = modelName
  ElMessage.success(`已选择模型: ${modelName}`)
}

const handleEnterKey = (e: KeyboardEvent) => {
  if (e.shiftKey) return
  sendMessage()
}

const sendMessage = async (text?: string) => {
  const messageText = text || userInput.value.trim()
  if (!messageText || loading.value) return
  
  // 添加用户消息到界面
  const userMessage = {
    id: 'temp-' + Date.now(),
    role: 'user',
    content: messageText,
    timestamp: new Date().toISOString()
  }
  
  messages.value.push(userMessage)
  
  // 更新Ollama对话历史
  if (useOllama.value) {
    ollamaConversation.value.push({
      role: 'user',
      content: messageText
    })
  }
  
  userInput.value = ''
  scrollToBottom()
  
  loading.value = true
  try {
    if (useOllama.value) {
      // 使用Ollama API
      console.log('Ollama请求参数:', {
        messages: ollamaConversation.value,
        model: selectedModel.value,
        system: systemPrompt
      });
      
      const response = await ollamaApi.chat(
        ollamaConversation.value,
        selectedModel.value,
        systemPrompt,  // 添加系统提示词
        0.7,  // 设置温度参数
        2000  // 最大生成token数
      );
      
      console.log('Ollama API响应:', response.data);
      
      // 处理Ollama API的返回格式，支持两种可能的格式
      if (response.data) {
        let content = '';
        let role = 'assistant';
        
        // 检查response.data.message格式
        if (response.data.message && typeof response.data.message === 'object') {
          // 格式1: {message: {role: 'assistant', content: '...'}}
          content = response.data.message.content;
          role = response.data.message.role;
        } 
        // 检查是否直接返回了role和content字段
        else if (response.data.role && response.data.content) {
          // 格式2: {role: 'assistant', content: '...'}
          content = response.data.content;
          role = response.data.role;
        }
        // 检查是否只返回了response字段
        else if (response.data.response) {
          // 格式3: {response: '...'}
          content = response.data.response;
        } else {
          throw new Error('无法解析Ollama响应格式');
        }
        
        // 添加助手回复到界面
        const assistantMessage = {
          id: 'ollama-' + Date.now(),
          role: 'assistant',
          content: content,
          timestamp: new Date().toISOString(),
          metadata: { model: selectedModel.value }
        }
        
        messages.value.push(assistantMessage)
        
        // 更新Ollama对话历史
        ollamaConversation.value.push({
          role: 'assistant',
          content: content
        })
      } else {
        throw new Error('Ollama响应为空')
      }
    } else {
      // 使用原有的智能助手API
      const response = await assistantApi.sendMessage(messageText, currentConversationId.value || undefined)
      
      // 保存当前对话ID
      if (response.data.conversation_id) {
        currentConversationId.value = response.data.conversation_id
      }
      
      // 添加助手回复到界面
      messages.value.push({
        id: response.data.message_id,
        role: 'assistant',
        content: response.data.message,
        timestamp: new Date().toISOString(),
        metadata: response.data.sources ? { sources: response.data.sources } : undefined
      })
    }
    
    scrollToBottom()
  }   catch (error) {
    console.error('发送消息失败', error)
    
    // 获取错误信息
    let errorMsg = '发送消息失败，请稍后再试';
    if (error.response && error.response.data) {
      errorMsg = `错误: ${error.response.data.detail || error.response.data.message || '未知错误'}`;
    } else if (error.message) {
      errorMsg = `错误: ${error.message}`;
    }
    
    ElMessage.error(errorMsg);
    
    // 在界面上显示错误消息
    messages.value.push({
      id: 'error-' + Date.now(),
      role: 'assistant',
      content: `抱歉，我遇到了一些问题，无法回答您的问题。${errorMsg}`,
      timestamp: new Date().toISOString()
    })
  } finally {
    loading.value = false
  }
}

const clearHistory = () => {
  ElMessageBox.confirm('确定要清空所有对话历史吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      if (!useOllama.value) {
        await assistantApi.clearConversation()
      }
      messages.value = []
      ollamaConversation.value = []
      currentConversationId.value = null
      ElMessage.success('对话历史已清空')
    } catch (error) {
      console.error('清空对话历史失败', error)
      ElMessage.error('清空对话历史失败')
    }
  }).catch(() => {})
}

const formatMessage = (text: string) => {
  // 尝试将文本作为Markdown渲染
  try {
    return marked(text)
  } catch (e) {
    // 如果Markdown渲染失败，退回到简单的HTML转换
    return text.replace(/\n/g, '<br>')
  }
}

const formatTime = (timestamp: string) => {
  return dayjs(timestamp).format('HH:mm')
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatBodyRef.value) {
      chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
    }
  })
}

const showSourceDetail = (source: any) => {
  selectedSource.value = source
  sourceDialogVisible.value = true
}

const handleCloseSourceDialog = () => {
  sourceDialogVisible.value = false
  selectedSource.value = null
}
</script>

<style scoped>
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 定义主题色变量 */
:root {
  --metric-color: #2ecc71; /* 绿色 */
  --diet-suggestion-color: #e67e22; /* 橙色 */
  --diet-record-color: #f1c40f; /* 黄色 */
  --glucose-monitor-color: #3498db; /* 蓝色 */
  --reminder-color: #9b59b6; /* 紫色 */
  --knowledge-color: #34495e; /* 深蓝灰色 */
  --primary-color: #0072ff; /* 基础蓝色 */
  --primary-color-light: #eaf5ff; /* 基础蓝色浅色版 */
  --background-color: #f0f4f8; /* 整体背景色 */
  --text-color-primary: #2c3e50; /* 主要文本颜色 */
  --text-color-secondary: #576b81; /* 次要文本颜色 */
  --border-color: #eef2f7; /* 边框颜色 */
}

.assistant-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--background-color); /* 与DashboardView保持一致 */
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif; /* 与DashboardView保持一致 */
  padding: 24px; /* 与DashboardView的容器padding一致 */
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--border-color); /* 使用主题边框色 */
  background-color: white;
  border-radius: 16px 16px 0 0; /* 圆角与卡片保持一致 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.03); /* 浅阴影 */
  margin-bottom: 16px;
}

.chat-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--primary-color); /* 使用主题蓝色 */
  font-weight: 600;
}

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: white; /* 聊天背景为白色 */
  border-radius: 16px; /* 圆角与卡片保持一致 */
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.05); /* 浅阴影 */
  margin-bottom: 16px;
}

.welcome-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  height: 100%;
  color: #303133;
  animation: fadeIn 0.8s ease-in-out;
}

.welcome-icon {
  margin-bottom: 20px;
}

.welcome-message h3 {
  margin: 0 0 8px 0;
  font-size: 1.5rem;
  color: var(--text-color-primary); /* 使用主要文本颜色 */
}

.welcome-message p {
  margin: 0 0 24px 0;
  color: var(--text-color-secondary); /* 使用次要文本颜色 */
}

.model-status {
  margin-top: 20px;
}

.suggestion-chips {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  max-width: 600px;
}

.suggestion-chips .el-button {
  border-radius: 20px; /* 圆角 */
  font-weight: 600;
  background-color: var(--primary-color-light); /* 浅蓝色背景 */
  color: var(--primary-color); /* 蓝色文字 */
  border: none;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.suggestion-chips .el-button:hover {
  background-color: var(--primary-color);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.message-container {
  display: flex;
  margin-bottom: 16px;
  gap: 12px;
  align-items: flex-start; /* 消息顶部对齐 */
}

.user-message {
  flex-direction: row-reverse;
  justify-content: flex-end; /* 用户消息靠右 */
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  padding: 12px;
  border-radius: 16px; /* 圆角与Dashboard卡片一致 */
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.05); /* 阴影与Dashboard卡片一致 */
  max-width: 70%;
  animation: fadeInUp 0.5s ease-in-out forwards; /* 添加动画 */
  opacity: 0; /* 初始透明 */
  position: relative; /* 为animation-delay提供上下文 */
}

.message-container:nth-child(even) .message-content { animation-delay: 0.1s; } /* 错落动画 */
.message-container:nth-child(odd) .message-content { animation-delay: 0.2s; } /* 错落动画 */

.user-message .message-content {
  background-color: var(--primary-color-light); /* 浅蓝色背景 */
  color: var(--text-color-primary); /* 主要文本颜色 */
  margin-left: auto; /* 用户消息靠右 */
}

.assistant-message .message-content {
  background-color: white; /* 助手消息白色背景 */
  color: var(--text-color-primary); /* 主要文本颜色 */
  margin-right: auto; /* 助手消息靠左 */
  border: 1px solid var(--border-color); /* 浅边框 */
}

.message-text {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6; /* 更好的阅读体验 */
  color: var(--text-color-primary);
}

.message-time {
  margin-top: 6px;
  font-size: 0.75rem;
  color: var(--text-color-secondary);
  text-align: right;
}

.chat-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background-color: white;
  border-top: 1px solid var(--border-color);
  border-radius: 0 0 16px 16px; /* 底部圆角 */
  box-shadow: 0 -4px 8px rgba(0, 0, 0, 0.03); /* 浅阴影 */
}

.chat-input .el-textarea__inner {
  border-radius: 8px; /* 输入框圆角 */
  border: 1px solid var(--border-color);
  padding: 8px 12px;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.chat-input .el-textarea__inner:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(0, 114, 255, 0.2);
}

.send-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.send-options .el-checkbox {
  color: var(--text-color-secondary);
}

.send-options .el-button {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
  border-radius: 8px; /* 按钮圆角 */
  font-weight: 600;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.send-options .el-button:hover {
  background-color: #0056b3;
  border-color: #0056b3;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px;
  margin-bottom: 16px;
  width: fit-content;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.05);
}

.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--primary-color); /* 使用主题色 */
  animation: typing-animation 1.4s infinite ease-in-out;
}

@keyframes typing-animation {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.6;
  }
  30% {
    transform: translateY(-6px);
    opacity: 1;
  }
}

.loading-container {
  padding: 20px;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.05);
  margin-bottom: 16px;
}

.message-sources {
  margin-top: 10px;
  font-size: 0.9em;
  border-top: 1px solid var(--border-color); /* 使用主题边框色 */
  padding-top: 8px;
}

.sources-title {
  font-weight: bold;
  margin-bottom: 4px;
  color: var(--text-color-primary);
}

.source-item {
  margin-bottom: 4px;
}

.source-item .el-link {
  color: var(--primary-color);
  font-size: 0.85em;
  transition: color 0.2s;
}

.source-item .el-link:hover {
  color: #0056b3;
}

.source-content {
  margin-top: 10px;
  padding: 10px;
  background-color: var(--background-color); /* 使用背景色 */
  border-radius: 8px; /* 圆角 */
  max-height: 400px;
  overflow-y: auto;
  white-space: pre-wrap;
  border: 1px solid var(--border-color);
  color: var(--text-color-primary);
}

:deep(.message-text) {
  line-height: 1.6;
}

:deep(.message-text p) {
  margin: 0.5em 0;
}

:deep(.message-text ul, .message-text ol) {
  padding-left: 20px;
}

:deep(.message-text code) {
  background-color: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: monospace;
  color: #c7254e;
}

:deep(.message-text pre) {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

:deep(.message-text strong) {
  color: var(--primary-color); /* 加粗文本使用主题色 */
}

/* 调整对话框样式 */
.el-dialog {
  border-radius: 16px;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

:deep(.el-dialog__header) {
  background-color: var(--background-color);
  border-bottom: 1px solid var(--border-color);
  border-radius: 16px 16px 0 0;
  padding: 16px 20px;
}

:deep(.el-dialog__title) {
  color: var(--text-color-primary);
  font-weight: 600;
  font-size: 1.1rem;
}

:deep(.el-dialog__body) {
  padding: 20px;
  color: var(--text-color-primary);
}

/* Element Plus 组件样式覆盖 */

/* Dropdown 按钮 */
.chat-actions .el-dropdown .el-button {
  border-radius: 20px; /* 按钮圆角 */
  font-weight: 600;
  padding: 8px 15px;
  transition: all 0.2s ease;
}

.chat-actions .el-dropdown .el-button--primary.is-plain {
  background-color: var(--primary-color-light);
  color: var(--primary-color);
  border-color: var(--primary-color-light);
}

.chat-actions .el-dropdown .el-button--primary.is-plain:hover {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Dropdown 菜单 */
:deep(.el-dropdown-menu) {
  border-radius: 12px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1); 
  border: 1px solid var(--border-color);
  padding: 8px;
}

:deep(.el-dropdown-menu__item) {
  border-radius: 8px;
  padding: 8px 12px;
  color: var(--text-color-primary);
}

:deep(.el-dropdown-menu__item:hover) {
  background-color: var(--primary-color-light);
  color: var(--primary-color);
}

/* Checkbox */
.send-options .el-checkbox__input.is-checked .el-checkbox__inner {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

.send-options .el-checkbox__label {
  color: var(--text-color-secondary);
}

/* Tag */
.model-status .el-tag {
  border-radius: 16px; /* 大圆角 */
  font-weight: 500;
  padding: 0 12px;
  height: 32px;
  line-height: 30px;
}

.model-status .el-tag--success {
  background-color: rgba(46, 204, 113, 0.15); /* 绿色浅色背景 */
  border-color: rgba(46, 204, 113, 0.3); /* 绿色边框 */
  color: #27ae60; /* 深绿色文本 */
}

.model-status .el-tag--danger {
  background-color: rgba(231, 76, 60, 0.15); /* 红色浅色背景 */
  border-color: rgba(231, 76, 60, 0.3); /* 红色边框 */
  color: #c0392b; /* 深红色文本 */
}

/* 移除原有的变量定义，现在从:root获取 */
/*
:root {
  --background-color: #f0f4f8;
  --primary-color: #409EFF;
  --primary-color-light: #ecf5ff;
  --text-color-primary: #303133;
  --text-color-secondary: #909399;
  --border-color: #dcdfe6;
}
*/
</style>