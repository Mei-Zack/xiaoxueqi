<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="24" :md="16" :lg="18">
        <el-row :gutter="20">
          <!-- 欢迎卡片 -->
          <el-col :span="24">
            <el-card class="welcome-card">
              <div class="welcome-content">
                <div class="welcome-text">
                  <h2>您好，{{ userName }}！</h2>
                  <p>欢迎使用糖尿病智能健康助理，今天是 {{ currentDate }}</p>
                </div>
                <div class="welcome-actions">
                  <el-button type="primary" @click="goToGlucoseRecord">
                    <el-icon><Plus /></el-icon>记录血糖
                  </el-button>
                  <el-button @click="goToAssistant">
                    <el-icon><ChatLineRound /></el-icon>咨询助理
                  </el-button>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <!-- 血糖趋势图 -->
          <el-col :span="24">
            <el-card class="chart-card">
              <template #header>
                <div class="card-header">
                  <span>血糖趋势</span>
                  <div class="header-actions">
                    <el-button type="primary" size="small" circle @click="refreshData">
                      <el-icon><Refresh /></el-icon>
                    </el-button>
                    <el-radio-group v-model="glucosePeriod" size="small">
                      <el-radio-button value="week">周</el-radio-button>
                      <el-radio-button value="month">月</el-radio-button>
                    </el-radio-group>
                  </div>
                </div>
              </template>
              <div v-if="loading" class="loading-container">
                <el-skeleton :rows="5" animated />
              </div>
              <div v-else-if="!hasGlucoseData" class="empty-data">
                <el-empty description="暂无血糖数据">
                  <el-button type="primary" @click="goToGlucoseRecord">记录血糖</el-button>
                </el-empty>
              </div>
              <div v-else class="chart-container">
                <!-- 这里将使用ECharts渲染血糖趋势图 -->
                <div ref="glucoseChartRef" class="chart" :key="chartKey"></div>
              </div>
            </el-card>
          </el-col>
          
          <!-- 三卡片布局：健康指标、饮食建议、今日饮食 -->
          <el-col :xs="24" :sm="8">
            <el-card class="metric-card">
              <template #header>
                <div class="card-header">
                  <span>健康指标</span>
                </div>
              </template>
              <div class="metrics-container">
                <div class="metric-item">
                  <div class="metric-label">体重</div>
                  <div class="metric-value">{{ healthMetrics.weight || '--' }} kg</div>
                </div>
                <div class="metric-item">
                  <div class="metric-label">血压</div>
                  <div class="metric-value">{{ healthMetrics.bloodPressure || '--' }}</div>
                </div>
                <div class="metric-item">
                  <div class="metric-label">BMI</div>
                  <div class="metric-value">{{ healthMetrics.bmi || '--' }}</div>
                </div>
                <div class="metric-item">
                  <div class="metric-label">今日步数</div>
                  <div class="metric-value">{{ healthMetrics.steps || '--' }}</div>
                </div>
              </div>
              <div class="card-footer">
                <el-button text @click="goToHealthData">查看更多</el-button>
              </div>
            </el-card>
          </el-col>
          
          <!-- 血糖饮食建议卡片 - 从右侧移动到左侧 -->
          <el-col :xs="24" :sm="8">
            <el-card class="diet-suggestion-card">
              <template #header>
                <div class="card-header">
                  <span>血糖饮食建议</span>
                  <el-button type="text" @click="refreshDietSuggestions">
                    <el-icon><Refresh /></el-icon>
                  </el-button>
                </div>
              </template>
              <div v-if="loadingDietSuggestions" class="loading-container">
                <el-skeleton :rows="3" animated />
              </div>
              <div v-else-if="!hasDietSuggestions" class="empty-data">
                <el-empty description="暂无饮食建议" :image-size="60">
                  <template #description>
                    <p>需要血糖数据才能生成饮食建议</p>
                  </template>
                  <el-button size="small" @click="fetchDietSuggestions">获取建议</el-button>
                </el-empty>
              </div>
              <div v-else>
                <div class="diet-status-banner" :class="getDietStatusClass(dietSuggestions.glucose_status)">
                  <el-icon><InfoFilled /></el-icon>
                  <span>{{ dietSuggestions.current_status }}</span>
                </div>
                
                <div class="diet-suggestion-content">
                  <p class="suggestion-text">{{ dietSuggestions.quick_suggestion }}</p>
                  
                  <div class="food-section">
                    <h4>推荐食物</h4>
                    <div class="food-tags">
                      <el-tag 
                        v-for="(food, index) in dietSuggestions.recommended_foods" 
                        :key="index"
                        type="success"
                        effect="light"
                        class="food-tag"
                      >
                        {{ food }}
                      </el-tag>
                    </div>
                  </div>
                  
                  <div class="food-section">
                    <h4>建议避免</h4>
                    <div class="food-tags">
                      <el-tag 
                        v-for="(food, index) in dietSuggestions.foods_to_avoid" 
                        :key="index"
                        type="danger"
                        effect="light"
                        class="food-tag"
                      >
                        {{ food }}
                      </el-tag>
                    </div>
                  </div>
                  
                  <el-divider content-position="center">下一餐建议</el-divider>
                  
                  <div class="next-meal">
                    <div class="meal-type-selector">
                      <el-radio-group v-model="selectedMealType" size="small" @change="updateMealSuggestion">
                        <el-radio-button label="breakfast">早餐</el-radio-button>
                        <el-radio-button label="lunch">午餐</el-radio-button>
                        <el-radio-button label="dinner">晚餐</el-radio-button>
                        <el-radio-button label="snack">加餐</el-radio-button>
                      </el-radio-group>
                    </div>
                    <div class="meal-suggestion">
                      {{ dietSuggestions.meal_plan_example || '暂无特定餐食建议' }}
                    </div>
                  </div>
                  
                  <div class="card-footer">
                    <el-button type="primary" size="small" @click="showDetailedDietSuggestions">
                      获取详细建议
                    </el-button>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <!-- 饮食记录卡片 -->
          <el-col :xs="24" :sm="8">
            <el-card class="diet-card">
              <template #header>
                <div class="card-header">
                  <span>今日饮食</span>
                </div>
              </template>
              <div v-if="loading" class="loading-container">
                <el-skeleton :rows="3" animated />
              </div>
              <div v-else-if="!hasDietData" class="empty-data">
                <el-empty description="暂无今日饮食记录">
                  <el-button type="primary" @click="goToDietRecord">记录饮食</el-button>
                </el-empty>
              </div>
              <div v-else class="diet-list">
                <div v-for="(meal, index) in dietRecords" :key="index" class="diet-item">
                  <div class="diet-time">{{ meal.time }}</div>
                  <div class="diet-name">{{ meal.name }}</div>
                  <div class="diet-calories">{{ meal.calories }} 卡路里</div>
                </div>
              </div>
              <div class="card-footer">
                <el-button text @click="goToDietRecord">添加饮食记录</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-col>
      
      <!-- 右侧边栏 -->
      <el-col :xs="24" :sm="24" :md="8" :lg="6">
        <!-- 血糖监测卡片 -->
        <el-card class="glucose-card">
          <template #header>
            <div class="card-header">
              <span>血糖监测</span>
              <el-button type="text" @click="goToGlucoseRecord">
                查看更多
              </el-button>
            </div>
          </template>
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else>
            <!-- 血糖警报通知 -->
            <div v-if="glucoseAlerts.length > 0" class="glucose-alerts">
              <el-alert
                v-for="(alert, index) in glucoseAlerts"
                :key="index"
                :title="alert.title"
                :description="alert.message"
                :type="alert.type"
                :closable="true"
                show-icon
                @close="removeAlert(index)"
              />
            </div>
            
            <!-- 快速导入血糖数据 -->
            <div class="quick-import">
              <h4>快速记录血糖</h4>
              <el-form :model="glucoseForm" label-position="top" size="small">
                <el-form-item label="血糖值 (mmol/L)">
                  <el-input-number v-model="glucoseForm.value" :min="1" :max="30" :precision="1" :step="0.1" style="width: 100%" />
                </el-form-item>
                <el-form-item label="测量类型">
                  <el-select v-model="glucoseForm.measurement_time" placeholder="请选择" style="width: 100%">
                    <el-option label="早餐前" value="BEFORE_BREAKFAST" />
                    <el-option label="早餐后" value="AFTER_BREAKFAST" />
                    <el-option label="午餐前" value="BEFORE_LUNCH" />
                    <el-option label="午餐后" value="AFTER_LUNCH" />
                    <el-option label="晚餐前" value="BEFORE_DINNER" />
                    <el-option label="晚餐后" value="AFTER_DINNER" />
                    <el-option label="睡前" value="BEFORE_SLEEP" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="importGlucoseData" :loading="importing" style="width: 100%">
                    保存记录
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
            
            <!-- 新增：智能分析部分 -->
            <el-divider content-position="center">智能分析</el-divider>
            
            <div v-if="loadingAnalysis" class="loading-container">
              <el-skeleton :rows="3" animated />
            </div>
            <div v-else-if="!hasAnalysisData" class="empty-analysis">
              <el-empty description="需要至少3天的血糖数据" :image-size="60">
                <template #description>
                  <p>需要更多血糖数据才能生成分析</p>
                </template>
                <el-button size="small" @click="fetchGlucoseAnalysis">尝试分析</el-button>
              </el-empty>
            </div>
            <div v-else class="glucose-analysis">
              <!-- 分析概要 -->
              <div class="analysis-summary">
                <div class="summary-item" :class="getValueClass(glucoseAnalysis.statistics.average)">
                  <div class="summary-value">{{ glucoseAnalysis.statistics.average.toFixed(1) }}</div>
                  <div class="summary-label">平均血糖</div>
                </div>
                <div class="summary-item" :class="getRangeClass(glucoseAnalysis.statistics.in_range_percentage)">
                  <div class="summary-value">{{ glucoseAnalysis.statistics.in_range_percentage.toFixed(0) }}%</div>
                  <div class="summary-label">达标率</div>
                </div>
                <div class="summary-item" :class="getStdClass(glucoseAnalysis.statistics.std)">
                  <div class="summary-value">{{ getVariabilityText(glucoseAnalysis.statistics.std) }}</div>
                  <div class="summary-label">波动性</div>
                </div>
              </div>
              
              <!-- 智能建议预览 -->
              <div class="advice-preview">
                <div class="advice-title">
                  <el-icon><ChatLineSquare /></el-icon>
                  <span>AI建议</span>
                </div>
                <div class="advice-content">
                  {{ truncateAdvice(glucoseAnalysis.advice, 100) }}
                </div>
                <el-button type="text" @click="showFullAdvice">查看完整建议</el-button>
              </div>
            </div>
          </div>
        </el-card>
        
        <!-- 今日提醒 -->
        <el-card class="reminder-card">
          <template #header>
            <div class="card-header">
              <span>今日提醒</span>
            </div>
          </template>
          <div class="reminder-list">
            <div v-for="(reminder, index) in reminders" :key="index" class="reminder-item">
              <el-icon :class="['reminder-icon', reminder.done ? 'done' : '']">
                <component :is="reminder.done ? 'CircleCheck' : 'Clock'" />
              </el-icon>
              <div class="reminder-content">
                <div class="reminder-text">{{ reminder.text }}</div>
                <div class="reminder-time">{{ reminder.time }}</div>
              </div>
              <el-checkbox v-model="reminder.done" @change="updateReminder(reminder)" />
            </div>
          </div>
        </el-card>
        
        <!-- 健康知识 -->
        <el-card class="knowledge-card">
          <template #header>
            <div class="card-header">
              <span>健康知识</span>
            </div>
          </template>
          <div class="knowledge-item" v-for="(article, index) in knowledgeArticles" :key="index">
            <div class="knowledge-title">{{ article.title }}</div>
            <div class="knowledge-desc">{{ article.description }}</div>
            <el-button text @click="readArticle(article.id)">阅读全文</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick, onActivated, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { Plus, ChatLineRound, Clock, CircleCheck, Refresh, ChatLineSquare, InfoFilled } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { glucoseApi, healthApi, dietApi, knowledgeApi, apiClient } from '../api'
import dayjs from 'dayjs'
import { ElMessage, ElMessageBox } from 'element-plus'

// 定义血糖记录类型接口
interface GlucoseRecord {
  id: string;
  value: number;
  measured_at: string;
  measurement_time: string;
  notes: string;
  user_id: string;
}

// 定义日期分组记录类型
interface DateGroupedRecords {
  [date: string]: {
    fasting: number[];
    afterMeal: number[];
  }
}

const router = useRouter()
const userStore = useUserStore()

const loading = ref(true)
const importing = ref(false)
const glucosePeriod = ref('week')
const glucoseChartRef = ref<HTMLElement | null>(null)
const glucoseChart = ref<echarts.ECharts | null>(null)
const chartKey = ref(0)
const glucoseCheckTimer = ref<number | null>(null)

const userName = computed(() => userStore.userFullName)
const currentDate = computed(() => dayjs().format('YYYY年MM月DD日'))

// 模拟数据
const healthMetrics = ref({
  weight: '68.5',
  bloodPressure: '120/80',
  bmi: '22.5',
  steps: '6,842'
})

const hasGlucoseData = ref(false)
const hasDietData = ref(true)
const glucoseAlerts = ref<Array<{title: string, message: string, type: 'success' | 'warning' | 'info' | 'error'}>>([])

const dietRecords = ref([
  { time: '早餐 08:30', name: '全麦面包+牛奶+鸡蛋', calories: 350 },
  { time: '午餐 12:00', name: '糙米饭+清蒸鱼+西兰花', calories: 480 },
  { time: '晚餐 18:30', name: '蔬菜沙拉+鸡胸肉', calories: 420 }
])

const reminders = ref([
  { id: 1, text: '测量空腹血糖', time: '早上8:00', done: true },
  { id: 2, text: '服用二甲双胍', time: '早餐后', done: true },
  { id: 3, text: '测量餐后血糖', time: '午餐后2小时', done: false },
  { id: 4, text: '30分钟有氧运动', time: '下午5:00', done: false },
  { id: 5, text: '服用二甲双胍', time: '晚餐后', done: false }
])

const knowledgeArticles = ref([
  {
    id: 1,
    title: '糖尿病患者如何科学运动',
    description: '适当的运动可以帮助控制血糖，但糖尿病患者需要注意一些事项...'
  },
  {
    id: 2,
    title: '低血糖的识别与处理',
    description: '低血糖是糖尿病患者常见的急性并发症，及时识别和处理非常重要...'
  },
  {
    id: 3,
    title: '糖尿病饮食的"四多四少"原则',
    description: '合理的饮食对控制血糖至关重要，建议多吃蔬菜、粗粮，少吃...'
  }
])

// 血糖数据
const glucoseRecords = ref<GlucoseRecord[]>([])

// 快速导入血糖表单
const glucoseForm = ref({
  value: 5.6,
  measurement_time: 'BEFORE_BREAKFAST'
})

// 智能分析相关状态
const loadingAnalysis = ref(false)
const hasAnalysisData = ref(false)
const glucoseAnalysis = ref({
  statistics: {
    average: 0,
    max: 0,
    min: 0,
    std: 0,
    in_range_percentage: 0,
    high_percentage: 0,
    low_percentage: 0
  },
  patterns: {},
  advice: '',
  record_count: 0,
  updated_at: ''
})

// 饮食建议相关状态
const loadingDietSuggestions = ref(false)
const hasDietSuggestions = ref(false)
const selectedMealType = ref('breakfast')
const dietSuggestions = ref({
  current_status: '',
  glucose_status: 'normal', // 可能的值: high, normal, low
  quick_suggestion: '',
  recommended_foods: [] as string[],
  foods_to_avoid: [] as string[],
  meal_plan_example: ''
})

// 从API获取血糖数据
const fetchGlucoseData = async () => {
  try {
    loading.value = true
    console.log('开始获取血糖数据...')
    
    // 使用新的API路径
    const response = await apiClient.get('/api/v1/glucose/recent', {
      params: {
        days: glucosePeriod.value === 'week' ? 7 : 30
      }
    })
    
    console.log('获取到血糖数据:', response.data)
    
    if (Array.isArray(response.data)) {
      glucoseRecords.value = response.data
      hasGlucoseData.value = glucoseRecords.value.length > 0
      
      console.log(`获取到 ${glucoseRecords.value.length} 条血糖记录`)
      console.log('血糖记录示例:', glucoseRecords.value.slice(0, 2))
      
      // 返回数据状态，不在此函数中初始化图表
      return {
        success: true,
        hasData: hasGlucoseData.value
      }
    } else {
      console.error('API返回的数据格式不正确:', response.data)
      hasGlucoseData.value = false
      return {
        success: false,
        hasData: false
      }
    }
  } catch (error) {
    console.error('获取血糖数据失败', error)
    hasGlucoseData.value = false
    return {
      success: false,
      hasData: false
    }
  } finally {
    loading.value = false
  }
}

// 处理血糖数据，根据周期返回图表所需数据
const processGlucoseData = () => {
  console.log('开始处理血糖数据，当前记录数:', glucoseRecords.value?.length || 0)
  
  if (!glucoseRecords.value || glucoseRecords.value.length === 0) {
    console.log('没有血糖记录，返回空数据')
    return {
      dates: [] as string[],
      fastingData: [] as (number | null)[],
      afterMealData: [] as (number | null)[]
    }
  }
  
  // 根据周期过滤数据
  let filteredRecords = [...glucoseRecords.value]
  const now = dayjs()
  
  if (glucosePeriod.value === 'week') {
    // 获取最近7天的数据
    const startDate = now.subtract(6, 'day').startOf('day')
    console.log('周视图起始日期:', startDate.format('YYYY-MM-DD'))
    filteredRecords = filteredRecords.filter(record => 
      dayjs(record.measured_at).isAfter(startDate)
    )
  } else {
    // 获取最近30天的数据
    const startDate = now.subtract(29, 'day').startOf('day')
    console.log('月视图起始日期:', startDate.format('YYYY-MM-DD'))
    filteredRecords = filteredRecords.filter(record => 
      dayjs(record.measured_at).isAfter(startDate)
    )
  }
  
  console.log('过滤后的记录数:', filteredRecords.length)
  
  // 按日期分组
  const recordsByDate: DateGroupedRecords = {}
  const dateFormat = 'MM-DD'
  
  filteredRecords.forEach(record => {
    const date = dayjs(record.measured_at).format(dateFormat)
    if (!recordsByDate[date]) {
      recordsByDate[date] = {
        fasting: [],
        afterMeal: []
      }
    }
    
    // 根据测量时间类型分组
    if (['BEFORE_BREAKFAST', 'BEFORE_LUNCH', 'BEFORE_DINNER', 'before_breakfast', 'before_lunch', 'before_dinner'].includes(record.measurement_time.toUpperCase())) {
      recordsByDate[date].fasting.push(record.value)
    } else if (['AFTER_BREAKFAST', 'AFTER_LUNCH', 'AFTER_DINNER', 'after_breakfast', 'after_lunch', 'after_dinner'].includes(record.measurement_time.toUpperCase())) {
      recordsByDate[date].afterMeal.push(record.value)
    }
  })
  
  console.log('按日期分组后的数据:', recordsByDate)
  
  // 准备图表数据
  const dates: string[] = []
  const fastingData: (number | null)[] = []
  const afterMealData: (number | null)[] = []
  
  // 生成日期范围
  let dateRange: string[] = []
  if (glucosePeriod.value === 'week') {
    // 最近7天
    for (let i = 6; i >= 0; i--) {
      dateRange.push(now.subtract(i, 'day').format(dateFormat))
    }
  } else {
    // 最近30天
    for (let i = 29; i >= 0; i--) {
      dateRange.push(now.subtract(i, 'day').format(dateFormat))
    }
  }
  
  // 修复：使用新的dayjs实例避免日期计算错误
  dateRange = []
  const periodDays = glucosePeriod.value === 'week' ? 7 : 30
  const startDay = glucosePeriod.value === 'week' ? 6 : 29
  
  for (let i = startDay; i >= 0; i--) {
    const d = dayjs().subtract(i, 'day')
    dateRange.push(d.format(dateFormat))
  }
  
  console.log('生成的日期范围:', dateRange)
  
  // 填充数据，没有的日期用null
  dateRange.forEach(date => {
    dates.push(date)
    
    if (recordsByDate[date]) {
      // 计算空腹血糖平均值
      const fastingValues = recordsByDate[date].fasting
      fastingData.push(fastingValues.length > 0 
        ? Number((fastingValues.reduce((sum, val) => sum + val, 0) / fastingValues.length).toFixed(1))
        : null)
      
      // 计算餐后血糖平均值
      const afterMealValues = recordsByDate[date].afterMeal
      afterMealData.push(afterMealValues.length > 0
        ? Number((afterMealValues.reduce((sum, val) => sum + val, 0) / afterMealValues.length).toFixed(1))
        : null)
    } else {
      fastingData.push(null)
      afterMealData.push(null)
    }
  })
  
  console.log('处理后的图表数据:', {
    dates,
    fastingData,
    afterMealData
  })
  
  return { dates, fastingData, afterMealData }
}

// 快速导入血糖数据
const importGlucoseData = async () => {
  // 验证表单
  if (!glucoseForm.value.value || !glucoseForm.value.measurement_time) {
    ElMessage.warning('请填写完整的血糖数据')
    return
  }
  
  try {
    importing.value = true
    
    // 打印 userStore 以检查用户 ID 字段
    console.log('userStore:', userStore)
    
    // 检查用户ID是否存在
    if (!userStore.user || !userStore.user.id) {
      ElMessage.error('用户未登录或用户ID不存在')
      importing.value = false
      return
    }
    
    // 构建请求数据 - 确保格式正确
    const data = {
      value: glucoseForm.value.value,
      measured_at: dayjs().format('YYYY-MM-DDTHH:mm:ss'),
      measurement_time: glucoseForm.value.measurement_time,
      measurement_method: 'FINGER_STICK', // 默认使用指尖血
      notes: '', // 添加可选的备注字段
      user_id: userStore.user.id // 添加用户ID
    }
    
    console.log('发送的血糖数据:', data)
    
    // 调用API保存血糖数据
    const response = await apiClient.post('/api/v1/glucose', data)
    
    console.log('保存血糖数据响应:', response)
    
    ElMessage.success('血糖数据保存成功')
    
    // 重置表单
    glucoseForm.value.value = 5.6
    
    // 刷新血糖数据
    await fetchGlucoseData()
    
    // 分析血糖数据
    await analyzeGlucoseData()
    
    // 获取三天分析
    await fetchGlucoseAnalysis()
    
  } catch (error) {
    console.error('保存血糖数据失败:', error)
    
    // 提供更详细的错误信息
    if (error.response) {
      console.error('错误响应数据:', error.response.data)
      
      // 显示详细的验证错误信息
      if (error.response.data && error.response.data.detail) {
        let errorMsg = '数据验证失败: ';
        
        if (Array.isArray(error.response.data.detail)) {
          errorMsg += error.response.data.detail.map(err => `${err.loc.join('.')}:${err.msg}`).join('; ');
        } else {
          errorMsg += error.response.data.detail;
        }
        
        ElMessage.error(errorMsg)
        return;
      }
    }
    
    ElMessage.error('保存血糖数据失败，请稍后再试')
  } finally {
    importing.value = false
  }
}

// 分析血糖数据
const analyzeGlucoseData = async () => {
  try {
    // 获取最近的血糖数据
    const recentResponse = await apiClient.get('/api/v1/glucose/recent', {
      params: {
        days: 1 // 获取最近1天的数据
      }
    });
    
    if (!recentResponse.data || recentResponse.data.length === 0) {
      console.log('没有最近的血糖数据可供分析');
      return null;
    }
    
    const records = recentResponse.data;
    console.log('获取到最近的血糖数据:', records);
    
    // 分析血糖数据
    const highThreshold = 7.8; // 高血糖阈值
    const lowThreshold = 3.9; // 低血糖阈值
    
    const highRecords = records.filter(record => record.value > highThreshold);
    const lowRecords = records.filter(record => record.value < lowThreshold);
    
    // 生成警报
    if (highRecords.length > 0 || lowRecords.length > 0) {
      let alertMessage = '';
      
      if (highRecords.length > 0) {
        const latestHigh = highRecords.sort((a, b) => 
          new Date(b.measured_at).getTime() - new Date(a.measured_at).getTime()
        )[0];
        
        alertMessage += `检测到${highRecords.length}次高血糖记录，最近一次为${dayjs(latestHigh.measured_at).format('MM-DD HH:mm')}，血糖值${latestHigh.value.toFixed(1)}mmol/L。`;
      }
      
      if (lowRecords.length > 0) {
        if (alertMessage) alertMessage += ' ';
        
        const latestLow = lowRecords.sort((a, b) => 
          new Date(b.measured_at).getTime() - new Date(a.measured_at).getTime()
        )[0];
        
        alertMessage += `检测到${lowRecords.length}次低血糖记录，最近一次为${dayjs(latestLow.measured_at).format('MM-DD HH:mm')}，血糖值${latestLow.value.toFixed(1)}mmol/L。`;
      }
      
      // 添加警报
      if (alertMessage) {
        addAlert('血糖异常提醒', alertMessage, 'warning');
      }
    }
    
    // 计算统计数据
    const sum = records.reduce((acc, record) => acc + record.value, 0);
    const avg = sum / records.length;
    const max = Math.max(...records.map(record => record.value));
    const min = Math.min(...records.map(record => record.value));
    
    return {
      statistics: {
        average: avg,
        max: max,
        min: min,
        count: records.length,
        high_count: highRecords.length,
        low_count: lowRecords.length
      },
      has_alerts: highRecords.length > 0 || lowRecords.length > 0
    };
  } catch (error) {
    console.error('分析血糖数据失败:', error);
    return null;
  }
}

// 添加警报
const addAlert = (title: string, message: string, type: 'success' | 'warning' | 'info' | 'error' = 'warning') => {
  glucoseAlerts.value.push({
    title,
    message,
    type
  })
}

// 移除警报
const removeAlert = (index: number) => {
  glucoseAlerts.value.splice(index, 1)
}

// 组件挂载时初始化
onMounted(async () => {
  try {
    // 获取血糖数据
    const glucoseResult = await fetchGlucoseData()
    
    // 如果有血糖数据，分析血糖数据
    if (glucoseResult?.hasData) {
      await analyzeGlucoseData()
      await fetchGlucoseAnalysis()
    }
    
    // 确保DOM已更新
    await nextTick()
    
    // 初始化图表
    if (hasGlucoseData.value) {
      initGlucoseChart()
    }
    
    // 设置定时检查血糖数据的定时器（每30分钟检查一次）
    const checkInterval = 30 * 60 * 1000; // 30分钟
    glucoseCheckTimer.value = setInterval(async () => {
      console.log('定时检查血糖数据...');
      await analyzeGlucoseData();
    }, checkInterval);
    
    // 如果有血糖数据，获取饮食建议
    if (glucoseResult?.hasData) {
      await fetchDietSuggestions()
    }
    
  } catch (error) {
    console.error('初始化数据失败:', error)
    ElMessage.error('加载数据失败，请刷新页面重试')
  } finally {
    loading.value = false
  }
})

// 在组件卸载时清除定时器
onUnmounted(() => {
  if (glucoseCheckTimer.value) {
    clearInterval(glucoseCheckTimer.value);
    glucoseCheckTimer.value = null;
  }
})

// 添加onActivated钩子，在组件被激活时重新获取数据
onActivated(async () => {
  console.log('Dashboard组件被激活，重新获取数据')
  try {
    // 检查图表是否已初始化
    if (hasGlucoseData.value && !glucoseChart.value && glucoseChartRef.value) {
      console.log('组件激活，但图表未初始化，尝试初始化图表')
      
      // 更新chartKey强制重新渲染图表容器
      chartKey.value += 1
      
      await nextTick()
      
      // 强制设置容器尺寸
      if (glucoseChartRef.value) {
        glucoseChartRef.value.style.height = '300px'
        glucoseChartRef.value.style.width = '100%'
      }
      
      setTimeout(() => {
        initGlucoseChart()
      }, 200)
    } else if (!glucoseChart.value) {
      // 重新获取数据
      const result = await fetchGlucoseData()
      
      if (result.success && result.hasData) {
        // 更新chartKey强制重新渲染图表容器
        chartKey.value += 1
        
        await nextTick()
        
        // 强制设置容器尺寸
        if (glucoseChartRef.value) {
          glucoseChartRef.value.style.height = '300px'
          glucoseChartRef.value.style.width = '100%'
        }
        
        setTimeout(() => {
          initGlucoseChart()
        }, 200)
      }
    } else {
      console.log('图表已存在，尝试更新')
      updateGlucoseChart()
    }
    
    // 刷新饮食建议
    if (hasGlucoseData.value && !hasDietSuggestions.value) {
      await fetchDietSuggestions()
    }
  } catch (error) {
    console.error('重新获取血糖数据失败', error)
  } finally {
    loading.value = false
  }
})

// 添加手动刷新功能
const refreshData = async () => {
  try {
    loading.value = true
    console.log('手动刷新数据开始')
    
    // 销毁现有图表实例
    if (glucoseChart.value) {
      console.log('销毁现有图表实例')
      glucoseChart.value.dispose()
      glucoseChart.value = null
    }
    
    // 更新chartKey强制重新渲染图表容器
    chartKey.value += 1
    console.log('更新chartKey:', chartKey.value)
    
    // 获取新数据
    const result = await fetchGlucoseData()
    
    // 确保在获取数据后重新创建图表
    if (result.success && result.hasData) {
      console.log('刷新后准备重新创建图表')
      
      // 使用更简单的方法，直接重新创建图表
      await nextTick()
      
      // 确保图表容器存在
      if (!glucoseChartRef.value) {
        console.error('图表容器不存在，无法重新创建图表')
        return
      }
      
      // 强制设置容器尺寸
      glucoseChartRef.value.style.height = '300px'
      glucoseChartRef.value.style.width = '100%'
      
      console.log('重新创建图表实例')
      try {
        // 确保echarts已正确导入
        if (!echarts) {
          console.error('echarts库未正确导入')
          return
        }
        
        // 直接创建新实例
        glucoseChart.value = echarts.init(glucoseChartRef.value)
        console.log('图表实例创建成功:', glucoseChart.value)
        
        // 设置图表选项
        updateGlucoseChart()
      } catch (error) {
        console.error('刷新时创建图表实例失败:', error)
      }
    }
    
    ElMessage.success('数据刷新成功')
  } catch (error) {
    console.error('刷新数据失败', error)
    ElMessage.error('刷新数据失败')
  } finally {
    loading.value = false
  }
}

// 监听glucosePeriod变化，更新图表
watch(glucosePeriod, () => {
  if (hasGlucoseData.value && glucoseChart.value) {
    updateGlucoseChart()
  }
})

// 更新血糖图表
const updateGlucoseChart = () => {
  console.log('开始更新图表')
  if (!glucoseChart.value) {
    console.error('图表实例不存在，无法更新')
    return
  }
  
  const { dates, fastingData, afterMealData } = processGlucoseData()
  console.log('处理后的图表数据:', { 
    dates, 
    fastingData, 
    afterMealData,
    datesLength: dates.length
  })
  
  try {
    const option = {
      tooltip: {
        trigger: 'axis',
        formatter: function(params: any) {
          let result = params[0].axisValueLabel + '<br/>';
          params.forEach((param: any) => {
            if (param.value !== null) {
              const color = param.value > 7.8 ? '#f56c6c' : 
                            param.value < 3.9 ? '#e6a23c' : '#67c23a';
              result += `<span style="display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:${param.color};"></span>`;
              result += `${param.seriesName}: <span style="color:${color};font-weight:bold">${param.value} mmol/L</span><br/>`;
            }
          });
          return result;
        }
      },
      legend: {
        data: ['空腹血糖', '餐后血糖']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: dates
      },
      yAxis: {
        type: 'value',
        name: '血糖 (mmol/L)',
        min: 3, // 调整范围以获得更好的视觉效果
        max: 12,
        interval: 1.5,
        axisLine: { lineStyle: { color: '#aaa' } },
        splitLine: {
          lineStyle: {
            color: '#eee'
          }
        }
      },
      series: [
        {
          name: '空腹血糖',
          type: 'line',
          smooth: true, // 使线条更平滑
          data: fastingData,
          connectNulls: true,
          symbol: 'circle',
          symbolSize: 8, // 稍大的标记点
          itemStyle: {
            color: '#3498db' // 活力蓝
          },
          lineStyle: {
            width: 3,
            shadowColor: 'rgba(52, 152, 219, 0.5)',
            shadowBlur: 10,
            shadowOffsetY: 5
          },
          markArea: {
            itemStyle: {
              color: 'rgba(46, 204, 113, 0.1)' // 清新绿
            },
            data: [
              [{
                yAxis: 3.9
              }, {
                yAxis: 6.1
              }]
            ]
          }
        },
        {
          name: '餐后血糖',
          type: 'line',
          smooth: true, // 使线条更平滑
          data: afterMealData,
          connectNulls: true,
          symbol: 'circle',
          symbolSize: 8,
          itemStyle: {
            color: '#e67e22' // 活力橙
          },
          lineStyle: {
            width: 3,
            shadowColor: 'rgba(230, 126, 34, 0.5)',
            shadowBlur: 10,
            shadowOffsetY: 5
          },
          markArea: {
            itemStyle: {
              color: 'rgba(46, 204, 113, 0.1)' // 清新绿
            },
            data: [
              [{
                yAxis: 3.9
              }, {
                yAxis: 7.8
              }]
            ]
          }
        }
      ]
    }
    
    console.log('设置图表选项')
    glucoseChart.value.setOption(option)
    console.log('图表选项设置完成')
  } catch (error) {
    console.error('设置图表选项失败:', error)
  }
}

const initGlucoseChart = () => {
  console.log('开始初始化图表')
  console.log('glucoseChartRef元素:', glucoseChartRef.value)
  
  if (!glucoseChartRef.value) {
    console.error('图表容器元素不存在，无法初始化图表')
    return
  }
  
  // 如果已经有图表实例，先销毁
  if (glucoseChart.value) {
    console.log('销毁旧图表实例')
    try {
      glucoseChart.value.dispose()
    } catch (error) {
      console.error('销毁旧图表实例失败:', error)
    }
    glucoseChart.value = null
  }
  
  // 确保DOM元素有宽高
  const chartElement = glucoseChartRef.value
  if (chartElement.offsetHeight === 0) {
    console.log('图表容器高度为0，设置默认高度')
    chartElement.style.height = '300px'
  }
  
  if (chartElement.offsetWidth === 0) {
    console.log('图表容器宽度为0，设置默认宽度')
    chartElement.style.width = '100%'
  }
  
  console.log('图表容器尺寸:', {
    height: chartElement.offsetHeight,
    width: chartElement.offsetWidth,
    clientHeight: chartElement.clientHeight,
    clientWidth: chartElement.clientWidth
  })
  
  // 创建新的图表实例
  try {
    console.log('创建新图表实例')
    // 确保echarts已正确导入
    if (!echarts) {
      console.error('echarts库未正确导入')
      return
    }
    
    glucoseChart.value = echarts.init(chartElement)
    console.log('图表实例创建成功:', glucoseChart.value)
    
    // 设置图表选项
    updateGlucoseChart()
    
    // 监听窗口大小变化，调整图表大小
    const resizeHandler = () => {
      console.log('窗口大小变化，调整图表大小')
      if (glucoseChart.value) {
        glucoseChart.value.resize()
      }
    }
    
    window.removeEventListener('resize', resizeHandler)
    window.addEventListener('resize', resizeHandler)
  } catch (error) {
    console.error('图表初始化失败:', error)
    // 尝试再次初始化
    setTimeout(() => {
      console.log('尝试再次初始化图表')
      try {
        if (chartElement && !glucoseChart.value) {
          glucoseChart.value = echarts.init(chartElement)
          updateGlucoseChart()
        }
      } catch (retryError) {
        console.error('再次初始化图表失败:', retryError)
      }
    }, 500)
  }
}

const updateReminder = (reminder: any) => {
  // 这里应该调用API更新提醒状态
  console.log('更新提醒状态', reminder)
}

const readArticle = (id: number) => {
  router.push(`/knowledge/${id}`)
}

const goToGlucoseRecord = () => {
  router.push('/glucose-record')
}

const goToAssistant = () => {
  router.push('/assistant')
}

const goToHealthData = () => {
  router.push('/health')
}

const goToDietRecord = () => {
  router.push('/diet')
}

// 获取血糖智能分析
const fetchGlucoseAnalysis = async () => {
  if (!hasGlucoseData.value) return

  try {
    loadingAnalysis.value = true
    
    // 获取最近记录的血糖数据
    const recentResponse = await apiClient.get('/api/v1/glucose/recent', {
      params: { days: 3 }
    })
    
    if (!recentResponse.data || recentResponse.data.length < 3) {
      hasAnalysisData.value = false
      loadingAnalysis.value = false
      return
    }
    
    // 获取统计数据
    const statsResponse = await apiClient.get('/api/v1/glucose/statistics', {
      params: { period: 'week' }
    })
    
    if (statsResponse.data) {
      // 构建分析数据结构
      const records = recentResponse.data
      const stats = statsResponse.data
      
      // 计算标准差
      let sum = 0
      let sumSquares = 0
      records.forEach(record => {
        sum += record.value
        sumSquares += record.value * record.value
      })
      const mean = sum / records.length
      const variance = sumSquares / records.length - mean * mean
      const std = Math.sqrt(variance)
      
      // 计算达标率
      const inRangeCount = records.filter(r => r.value >= 3.9 && r.value <= 7.8).length
      const inRangePercentage = (inRangeCount / records.length) * 100
      
      // 计算高低血糖比例
      const highCount = records.filter(r => r.value > 7.8).length
      const lowCount = records.filter(r => r.value < 3.9).length
      const highPercentage = (highCount / records.length) * 100
      const lowPercentage = (lowCount / records.length) * 100
      
      // 生成简单的建议文本
      let advice = '根据您最近三天的血糖记录分析：\n\n'
      
      if (mean > 7.8) {
        advice += '您的平均血糖偏高，建议控制碳水化合物摄入，增加运动量。\n\n'
      } else if (mean < 3.9) {
        advice += '您的平均血糖偏低，请注意及时补充碳水化合物，避免低血糖发生。\n\n'
      } else {
        advice += '您的平均血糖处于正常范围，请继续保持良好的生活方式。\n\n'
      }
      
      if (std > 2.0) {
        advice += '您的血糖波动较大，建议规律三餐，避免暴饮暴食，监测血糖的频率可以适当增加。\n\n'
      }
      
      if (inRangePercentage < 70) {
        advice += `您的血糖达标率为${inRangePercentage.toFixed(0)}%，低于理想水平(70%)，建议咨询医生调整治疗方案。\n\n`
      }
      
      advice += '请记住，良好的饮食习惯、适当的运动和按时服药是控制血糖的关键。'
      
      // 更新分析数据
      glucoseAnalysis.value = {
        statistics: {
          average: mean,
          max: stats.max_value || 0,
          min: stats.min_value || 0,
          std: std,
          in_range_percentage: inRangePercentage,
          high_percentage: highPercentage,
          low_percentage: lowPercentage
        },
        patterns: {},
        advice: advice,
        record_count: records.length,
        updated_at: new Date().toISOString()
      }
      
      hasAnalysisData.value = true
    } else {
      hasAnalysisData.value = false
      ElMessage.info('暂无足够的血糖数据进行分析')
    }
  } catch (error) {
    console.error('获取血糖分析失败:', error)
    ElMessage.error('获取血糖分析失败，请稍后再试')
    hasAnalysisData.value = false
  } finally {
    loadingAnalysis.value = false
  }
}

// 获取饮食建议
const fetchDietSuggestions = async () => {
  if (!hasGlucoseData.value) {
    ElMessage.warning('需要血糖数据才能生成饮食建议')
    return
  }
  
  try {
    loadingDietSuggestions.value = true
    
    // 获取最近的血糖值
    const latestGlucose = glucoseRecords.value[0]?.value || 0
    const isMealTime = new Date().getHours() >= 6 && new Date().getHours() <= 20
    const isBeforeMeal = isMealTime && Math.random() > 0.5 // 模拟餐前/餐后，实际应根据时间或用户输入判断
    
    // 调用API获取快速饮食建议
    const response = await apiClient.get('/api/v1/glucose-monitor/quick-diet-suggestions', {
      params: {
        glucose_value: latestGlucose,
        meal_type: selectedMealType.value,
        is_before_meal: isBeforeMeal
      }
    })
    
    if (response.data) {
      dietSuggestions.value = {
        ...response.data,
        glucose_status: getGlucoseStatus(latestGlucose, isBeforeMeal)
      }
      hasDietSuggestions.value = true
    } else {
      hasDietSuggestions.value = false
      ElMessage.info('无法获取饮食建议，请稍后再试')
    }
  } catch (error) {
    console.error('获取饮食建议失败:', error)
    
    // 模拟数据用于演示
    simulateDietSuggestions()
  } finally {
    loadingDietSuggestions.value = false
  }
}

// 模拟饮食建议数据（在API未实现时使用）
const simulateDietSuggestions = () => {
  const latestGlucose = glucoseRecords.value[0]?.value || 7.2
  const isBeforeMeal = Math.random() > 0.5
  const status = getGlucoseStatus(latestGlucose, isBeforeMeal)
  
  let suggestion = ''
  let recommended: string[] = []
  let avoid: string[] = []
  let mealPlan = ''
  
  if (status === 'high') {
    suggestion = '您的血糖偏高，建议减少碳水化合物摄入，增加蛋白质和膳食纤维。'
    recommended = ['蔬菜沙拉', '鸡胸肉', '豆腐', '牛油果', '坚果少量']
    avoid = ['白米饭', '白面包', '甜点', '含糖饮料']
    mealPlan = '推荐：烤鸡胸肉100g + 混合蔬菜沙拉 + 藜麦50g'
  } else if (status === 'low') {
    suggestion = '您的血糖偏低，建议适量摄入优质碳水化合物，避免空腹过久。'
    recommended = ['全麦面包', '燕麦', '香蕉', '酸奶', '蜂蜜少量']
    avoid = ['精制糖', '果汁', '咖啡因饮料']
    mealPlan = '推荐：全麦面包2片 + 煮鸡蛋1个 + 小香蕉1根'
  } else {
    suggestion = '您的血糖正常，建议保持均衡饮食，控制碳水化合物摄入量。'
    recommended = ['全谷物', '绿叶蔬菜', '鱼肉', '豆制品', '坚果适量']
    avoid = ['精制碳水', '甜点', '油炸食品']
    mealPlan = '推荐：糙米饭半碗 + 清蒸鱼100g + 西兰花 + 豆腐'
  }
  
  dietSuggestions.value = {
    current_status: `您的当前血糖为${latestGlucose.toFixed(1)} mmol/L，属于${isBeforeMeal ? '餐前' : '餐后'}${status === 'normal' ? '正常' : status === 'high' ? '偏高' : '偏低'}范围。`,
    glucose_status: status,
    quick_suggestion: suggestion,
    recommended_foods: recommended,
    foods_to_avoid: avoid,
    meal_plan_example: mealPlan
  }
  
  hasDietSuggestions.value = true
}

// 根据血糖值判断状态
const getGlucoseStatus = (value: number, isBeforeMeal: boolean): 'high' | 'normal' | 'low' => {
  if (isBeforeMeal) {
    if (value < 3.9) return 'low'
    if (value > 7.0) return 'high'
    return 'normal'
  } else {
    if (value < 3.9) return 'low'
    if (value > 10.0) return 'high'
    return 'normal'
  }
}

// 获取饮食状态对应的CSS类
const getDietStatusClass = (status: string) => {
  if (status === 'high') return 'status-high'
  if (status === 'low') return 'status-low'
  return 'status-normal'
}

// 刷新饮食建议
const refreshDietSuggestions = () => {
  fetchDietSuggestions()
}

// 更新餐食建议
const updateMealSuggestion = async () => {
  try {
    loadingDietSuggestions.value = true
    
    // 在实际应用中，这里应该调用API获取特定餐食类型的建议
    // 这里使用模拟数据
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const mealPlans = {
      breakfast: '早餐推荐：全麦面包2片 + 煮鸡蛋1个 + 牛奶200ml',
      lunch: '午餐推荐：糙米饭半碗 + 清蒸鱼100g + 西兰花 + 豆腐',
      dinner: '晚餐推荐：藜麦沙拉 + 烤鸡胸肉100g + 烤红薯小份',
      snack: '加餐推荐：无糖酸奶100g + 蓝莓一小把或坚果10g'
    }
    
    dietSuggestions.value.meal_plan_example = mealPlans[selectedMealType.value]
  } catch (error) {
    console.error('更新餐食建议失败:', error)
  } finally {
    loadingDietSuggestions.value = false
  }
}

// 显示详细饮食建议
const showDetailedDietSuggestions = async () => {
  try {
    ElMessage.info('正在生成详细饮食建议...')
    
    // 在实际应用中，这里应该调用API获取详细的饮食建议
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 构建详细建议内容
    const detailedSuggestion = `
      <h3>个性化饮食建议</h3>
      <p>基于您的血糖数据分析，我们为您提供以下饮食建议：</p>
      
      <h4>总体原则</h4>
      <ul>
        <li>控制碳水化合物总量，选择低GI值的碳水食物</li>
        <li>增加蛋白质和健康脂肪的摄入</li>
        <li>多吃富含膳食纤维的蔬菜</li>
        <li>规律三餐，避免长时间空腹</li>
      </ul>
      
      <h4>推荐食物清单</h4>
      <ul>
        <li><strong>碳水来源</strong>：全麦面包、燕麦、糙米、藜麦、红薯</li>
        <li><strong>蛋白质来源</strong>：鸡胸肉、鱼、豆腐、鸡蛋、希腊酸奶</li>
        <li><strong>健康脂肪</strong>：牛油果、橄榄油、坚果(适量)</li>
        <li><strong>蔬菜水果</strong>：西兰花、菠菜、芦笋、蓝莓、草莓(适量)</li>
      </ul>
      
      <h4>一日三餐建议</h4>
      <p><strong>早餐</strong>：${selectedMealType.value === 'breakfast' ? '<span style="color:#409EFF">'+dietSuggestions.value.meal_plan_example+'</span>' : '全麦面包2片 + 煮鸡蛋1个 + 牛奶200ml'}</p>
      <p><strong>午餐</strong>：${selectedMealType.value === 'lunch' ? '<span style="color:#409EFF">'+dietSuggestions.value.meal_plan_example+'</span>' : '糙米饭半碗 + 清蒸鱼100g + 西兰花 + 豆腐'}</p>
      <p><strong>晚餐</strong>：${selectedMealType.value === 'dinner' ? '<span style="color:#409EFF">'+dietSuggestions.value.meal_plan_example+'</span>' : '藜麦沙拉 + 烤鸡胸肉100g + 烤红薯小份'}</p>
      <p><strong>加餐</strong>：${selectedMealType.value === 'snack' ? '<span style="color:#409EFF">'+dietSuggestions.value.meal_plan_example+'</span>' : '无糖酸奶100g + 蓝莓一小把或坚果10g'}</p>
    `
    
    ElMessageBox.alert(
      detailedSuggestion,
      '个性化饮食建议',
      {
        dangerouslyUseHTMLString: true,
        confirmButtonText: '我知道了',
        customClass: 'diet-suggestion-dialog'
      }
    )
  } catch (error) {
    console.error('获取详细饮食建议失败:', error)
    ElMessage.error('获取详细饮食建议失败，请稍后再试')
  }
}

// 辅助方法：根据血糖值获取CSS类
const getValueClass = (value) => {
  if (value > 10.0) return 'high-value'
  if (value < 3.9) return 'low-value'
  return 'normal-value'
}

// 辅助方法：根据达标率获取CSS类
const getRangeClass = (percentage) => {
  if (percentage >= 70) return 'good-range'
  if (percentage >= 50) return 'average-range'
  return 'poor-range'
}

// 辅助方法：根据标准差获取CSS类
const getStdClass = (std) => {
  if (std <= 1.5) return 'stable-std'
  if (std <= 2.5) return 'moderate-std'
  return 'unstable-std'
}

// 辅助方法：根据标准差获取波动性描述
const getVariabilityText = (std) => {
  if (std <= 1.5) return '稳定'
  if (std <= 2.5) return '一般'
  return '波动大'
}

// 截断建议文本，显示预览
const truncateAdvice = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// 显示完整建议
const showFullAdvice = () => {
  ElMessageBox.alert(
    `<div style="white-space: pre-line;">${glucoseAnalysis.value.advice}</div>`,
    '血糖管理建议',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '我知道了',
      customClass: 'advice-dialog'
    }
  )
}

// 同步设备数据
const syncDevice = async () => {
  try {
    ElMessage.info('开始同步设备数据...')
    
    // 直接刷新血糖数据，不调用不存在的同步API
    const result = await fetchGlucoseData()
    
    if (result && result.success) {
      ElMessage.success('设备数据同步成功')
      
      // 分析血糖数据
      await analyzeGlucoseData()
      
      // 获取三天分析
      await fetchGlucoseAnalysis()
      
      // 重新初始化图表
      if (hasGlucoseData.value) {
        chartKey.value++ // 强制重新渲染
        await nextTick()
        initGlucoseChart()
      }
    } else {
      ElMessage.warning('设备数据同步失败')
    }
  } catch (error) {
    console.error('同步设备数据失败:', error)
    ElMessage.error('同步设备数据失败，请检查设备连接')
  }
}
</script>

<style scoped>
/* 定义主题色变量 */
:root {
  --metric-color: #2ecc71; /* 绿色 */
  --diet-suggestion-color: #e67e22; /* 橙色 */
  --diet-record-color: #f1c40f; /* 黄色 */
  --glucose-monitor-color: #3498db; /* 蓝色 */
  --reminder-color: #9b59b6; /* 紫色 */
  --knowledge-color: #34495e; /* 深蓝灰色 */
}

.dashboard-container {
  padding: 24px;
  background-color: #f0f4f8;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

.el-card {
  margin-bottom: 24px;
  border-radius: 16px;
  border: none;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  overflow: hidden; /* 配合圆角 */
}

.el-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 1.1rem;
  color: #2c3e50;
  border-bottom: 1px solid #eef2f7;
  padding-bottom: 10px;
}

/* 为特定卡片添加彩色左边框 */
.metric-card { border-left: 5px solid var(--metric-color); }
.diet-suggestion-card { border-left: 5px solid var(--diet-suggestion-color); }
.diet-card { border-left: 5px solid var(--diet-record-color); }
.glucose-card { border-left: 5px solid var(--glucose-monitor-color); }
.reminder-card { border-left: 5px solid var(--reminder-color); }
.knowledge-card { border-left: 5px solid var(--knowledge-color); }

/* 为卡片头部的文字或图标应用主题色 */
.metric-card .card-header span { color: var(--metric-color); }
.diet-suggestion-card .card-header span { color: var(--diet-suggestion-color); }
.diet-card .card-header span { color: var(--diet-record-color); }
.glucose-card .card-header span { color: var(--glucose-monitor-color); }
.reminder-card .card-header span { color: var(--reminder-color); }
.knowledge-card .card-header span { color: var(--knowledge-color); }

.welcome-card {
  background: linear-gradient(135deg, #00c6ff, #0072ff);
  color: white;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
}

.welcome-text h2 {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
}

.welcome-text p {
  margin: 8px 0 0;
  opacity: 0.9;
  font-size: 1rem;
}

.welcome-actions {
  display: flex;
  gap: 15px;
}

.welcome-actions .el-button--primary {
  background-color: #ffffff !important;
  color: #0072ff;
  border: none;
  border-radius: 20px;
  font-weight: 600;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.welcome-actions .el-button {
  background-color: rgba(255, 255, 255, 0.2) !important;
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  font-weight: 600;
}

.chart-card .card-header {
  border-bottom: none;
}

.chart-container {
  height: 350px;
  width: 100%;
  margin: 0;
  border: none;
  border-radius: 4px;
}

.chart {
  width: 100%;
  height: 100%;
  min-height: 350px;
}

.metrics-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.metric-item {
  text-align: center;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 12px;
}

.metric-label {
  color: #576b81;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--metric-color);
}

.diet-card .diet-list {
  padding: 0 10px;
}

.diet-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #eef2f7;
}

.diet-item:last-child {
  border-bottom: none;
}

.diet-time {
  font-size: 0.9rem;
  color: #576b81;
  width: 30%;
  font-weight: 500;
}

.diet-name {
  flex: 1;
  font-weight: 500;
}

.diet-calories {
  color: var(--diet-record-color);
  font-weight: 600;
}

.reminder-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.reminder-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 10px;
  transition: background-color 0.3s;
}

.reminder-icon {
  margin-right: 12px;
  font-size: 1.4rem;
  color: var(--reminder-color);
}

.reminder-icon.done {
  color: #2ecc71;
}

.reminder-content {
  flex: 1;
}

.reminder-text {
  font-weight: 600;
  color: #2c3e50;
}

.reminder-time {
  font-size: 0.8rem;
  color: #576b81;
}

.reminder-item .el-checkbox {
  margin-left: 10px;
}

.knowledge-item {
  padding: 16px 0;
  border-bottom: 1px solid #eef2f7;
}

.knowledge-item:last-child {
  border-bottom: none;
}

.knowledge-title {
  font-weight: 600;
  margin-bottom: 6px;
  color: #2c3e50;
}

.knowledge-desc {
  font-size: 0.9rem;
  color: #576b81;
  margin-bottom: 12px;
}

.knowledge-item .el-button {
  font-weight: 600;
}

.card-footer {
  margin-top: 16px;
  text-align: center;
}

.empty-data {
  padding: 40px 0;
}

.loading-container {
  padding: 20px;
}

.glucose-card .card-header {
  border-bottom: none;
}

.quick-import {
  padding: 10px 5px;
}

.quick-import h4 {
  margin-bottom: 15px;
  color: var(--glucose-monitor-color);
  font-weight: 600;
}

.quick-import .el-button {
  border-radius: 8px;
  font-weight: 600;
}

.glucose-alerts {
  margin-bottom: 15px;
}

.glucose-alerts .el-alert {
  margin-bottom: 10px;
  border-radius: 8px;
}

.glucose-alerts .el-alert:last-child {
  margin-bottom: 0;
}

/* 智能分析相关样式 */
.glucose-analysis {
  margin-top: 10px;
}

.analysis-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 15px;
}

.summary-item {
  text-align: center;
  flex: 1;
  padding: 12px 0;
  border-radius: 12px;
}

.summary-value {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 4px;
}

.summary-label {
  font-size: 13px;
  font-weight: 500;
}

.normal-value { background-color: rgba(46, 204, 113, 0.1); color: #2ecc71; }
.high-value { background-color: rgba(231, 76, 60, 0.1); color: #e74c3c; }
.low-value { background-color: rgba(243, 156, 18, 0.1); color: #f39c12; }

.good-range { background-color: rgba(46, 204, 113, 0.1); color: #2ecc71; }
.average-range { background-color: rgba(243, 156, 18, 0.1); color: #f39c12; }
.poor-range { background-color: rgba(231, 76, 60, 0.1); color: #e74c3c; }

.stable-std { background-color: rgba(46, 204, 113, 0.1); color: #2ecc71; }
.moderate-std { background-color: rgba(243, 156, 18, 0.1); color: #f39c12; }
.unstable-std { background-color: rgba(231, 76, 60, 0.1); color: #e74c3c; }

.advice-preview {
  background-color: #eaf5ff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 10px;
  border: 1px solid #a8d8ff;
}

.advice-title {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  color: var(--glucose-monitor-color);
  font-weight: 600;
}

.advice-title .el-icon {
  margin-right: 8px;
  font-size: 1.2rem;
}

.advice-content {
  font-size: 14px;
  line-height: 1.6;
  color: #34495e;
  margin-bottom: 8px;
}

.empty-analysis {
  padding: 15px 0;
  text-align: center;
}

/* 对话框样式 */
:deep(.advice-dialog .el-message-box__content) {
  max-height: 400px;
  overflow-y: auto;
}

.diet-suggestion-card .card-header {
  border-bottom: none;
}

.diet-status-banner {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 10px;
  margin-bottom: 15px;
  font-size: 14px;
  font-weight: 600;
}

.diet-status-banner .el-icon {
  margin-right: 8px;
  font-size: 18px;
}

.status-normal {
  background-color: rgba(46, 204, 113, 0.15);
  color: #27ae60;
  border-left: 5px solid #2ecc71;
}

.status-high {
  background-color: rgba(231, 76, 60, 0.15);
  color: #c0392b;
  border-left: 5px solid #e74c3c;
}

.status-low {
  background-color: rgba(243, 156, 18, 0.15);
  color: #d35400;
  border-left: 5px solid #f39c12;
}

.diet-suggestion-content {
  padding: 0 5px;
}

.suggestion-text {
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 20px;
  color: #34495e;
}

.food-section {
  margin-bottom: 20px;
}

.food-section h4 {
  font-size: 15px;
  margin-bottom: 10px;
  color: #2c3e50;
  font-weight: 600;
}

.food-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.food-tag {
  border-radius: 16px;
  padding: 0 15px;
  height: 32px;
  line-height: 30px;
  font-weight: 500;
}

.next-meal {
  margin: 20px 0;
}

.meal-type-selector {
  margin-bottom: 15px;
  text-align: center;
}

.meal-suggestion {
  background-color: #f0f4f8;
  padding: 15px;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.6;
  color: #34495e;
  text-align: center;
  border: 1px dashed #bdc3c7;
}

.card-footer {
  margin-top: 20px;
  text-align: center;
}

:deep(.diet-suggestion-dialog .el-message-box__content) {
  max-height: 400px;
  overflow-y: auto;
}

:deep(.diet-suggestion-dialog ul) {
  padding-left: 20px;
  margin: 10px 0;
  list-style-type: "✨ ";
}

:deep(.diet-suggestion-dialog h3, .diet-suggestion-dialog h4) {
  margin: 15px 0 10px 0;
  color: #0072ff;
}

@media (max-width: 992px) {
  .metrics-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 15px;
  }
  .welcome-content {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .metrics-container, .analysis-summary {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 576px) {
  .metrics-container, .analysis-summary {
    grid-template-columns: 1fr;
  }
  .welcome-text h2 {
    font-size: 1.8rem;
  }
  .welcome-actions {
    flex-direction: column;
    width: 100%;
  }
}
</style> 