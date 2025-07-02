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
.assistant-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--background-color);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  background-color: white;
}

.chat-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--primary-color);
}

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.welcome-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px 20px;
}

.welcome-icon {
  margin-bottom: 16px;
  color: var(--primary-color);
}

.welcome-message h3 {
  margin: 0 0 8px 0;
  font-size: 1.5rem;
}

.welcome-message p {
  margin: 0 0 24px 0;
  color: var(--text-color-secondary);
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

.message-container {
  display: flex;
  margin-bottom: 16px;
  gap: 12px;
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  background-color: white;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  max-width: 70%;
}

.user-message .message-content {
  background-color: var(--primary-color-light);
}

.message-text {
  white-space: pre-wrap;
  word-break: break-word;
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
}

.send-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px;
  margin-bottom: 16px;
  width: fit-content;
}

.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--text-color-secondary);
  animation: typing-animation 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(1) {
  animation-delay: 0s;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.4s;
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
}

.message-sources {
  margin-top: 10px;
  font-size: 0.9em;
  border-top: 1px solid #eee;
  padding-top: 8px;
}

.sources-title {
  font-weight: bold;
  margin-bottom: 4px;
}

.source-item {
  margin-bottom: 4px;
}

.source-content {
  margin-top: 10px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
  max-height: 400px;
  overflow-y: auto;
  white-space: pre-wrap;
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
}

:deep(.message-text pre) {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>