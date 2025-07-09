<template>
  <div class="diet-advice-container">
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>
    <div v-else-if="error" class="error-container">
      <el-alert
        :title="error"
        type="error"
        show-icon
        :closable="false"
      />
      <el-button size="small" type="primary" @click="fetchAdvice" class="mt-3">
        重试
      </el-button>
    </div>
    <div v-else-if="!advice" class="empty-container">
      <el-empty description="暂无饮食建议">
        <template #description>
          <p>需要至少2天的饮食记录和血糖数据才能生成建议</p>
        </template>
        <el-button size="small" type="primary" @click="fetchAdvice">
          获取饮食建议
        </el-button>
      </el-empty>
    </div>
    <div v-else class="advice-content">
      <div class="advice-header">
        <div class="advice-title">
          <el-icon><Bowl /></el-icon>
          <span>个性化饮食建议</span>
        </div>
        <div class="advice-meta">
          <el-tooltip content="基于您最近的饮食记录和血糖数据生成">
            <el-tag size="small" type="info">AI生成</el-tag>
          </el-tooltip>
          <el-tooltip :content="generatedAt">
            <span class="advice-time">{{ formattedTime }}</span>
          </el-tooltip>
        </div>
      </div>
      
      <div class="advice-body">
        <div v-if="showFullContent" class="full-content">
          <p v-for="(paragraph, index) in adviceParagraphs" :key="index" class="advice-paragraph">
            {{ paragraph }}
          </p>
        </div>
        <div v-else class="preview-content">
          {{ previewContent }}
        </div>
      </div>
      
      <div class="advice-footer">
        <el-button 
          v-if="!showFullContent" 
          type="primary" 
          text 
          @click="showFullContent = true"
        >
          查看完整建议
        </el-button>
        <el-button 
          v-else 
          type="primary" 
          text 
          @click="showFullContent = false"
        >
          收起
        </el-button>
        <el-button type="primary" text @click="refreshAdvice">
          <el-icon><Refresh /></el-icon> 刷新建议
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Bowl, Refresh } from '@element-plus/icons-vue'
import { apiClient, ollamaApi } from '../api'
import dayjs from 'dayjs'

// 组件状态
const loading = ref(false)
const error = ref('')
const advice = ref('')
const generatedAt = ref('')
const showFullContent = ref(false)

// 计算属性
const adviceParagraphs = computed(() => {
  return advice.value.split('\n').filter(p => p.trim() !== '')
})

const previewContent = computed(() => {
  // 截取前100个字符作为预览
  const maxLength = 100
  if (advice.value.length <= maxLength) {
    return advice.value
  }
  return advice.value.substring(0, maxLength) + '...'
})

const formattedTime = computed(() => {
  if (!generatedAt.value) return ''
  return dayjs(generatedAt.value).format('MM-DD HH:mm')
})

// 方法
const fetchAdvice = async () => {
  try {
    loading.value = true
    error.value = ''
    
    // 调用API获取饮食建议
    const response = await ollamaApi.getDietAdvice({
      days: 2, // 获取最近2天的饮食记录
      temperature: 0.7
    })
    
    if (response.data && response.data.advice) {
      advice.value = response.data.advice
      generatedAt.value = response.data.based_on.generated_at
      showFullContent.value = false // 默认显示预览
    } else {
      error.value = '获取饮食建议失败，请稍后再试'
    }
  } catch (err) {
    console.error('获取饮食建议失败:', err)
    error.value = '获取饮食建议失败，请确保有足够的饮食和血糖记录'
  } finally {
    loading.value = false
  }
}

const refreshAdvice = async () => {
  await fetchAdvice()
  ElMessage.success('饮食建议已更新')
}

// 组件挂载时获取建议
onMounted(() => {
  fetchAdvice()
})
</script>

<style scoped>
.diet-advice-container {
  width: 100%;
  margin-bottom: 20px;
}

.loading-container, .error-container, .empty-container {
  padding: 20px 0;
  text-align: center;
}

.mt-3 {
  margin-top: 12px;
}

.advice-content {
  display: flex;
  flex-direction: column;
}

.advice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.advice-title {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 500;
  color: var(--el-color-primary);
}

.advice-title .el-icon {
  margin-right: 8px;
}

.advice-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.advice-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.advice-body {
  background-color: var(--el-fill-color-light);
  border-radius: 4px;
  padding: 12px;
  margin-bottom: 12px;
}

.full-content {
  max-height: 300px;
  overflow-y: auto;
}

.advice-paragraph {
  margin-bottom: 8px;
  line-height: 1.6;
}

.advice-paragraph:last-child {
  margin-bottom: 0;
}

.preview-content {
  line-height: 1.6;
  color: var(--el-text-color-regular);
}

.advice-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 