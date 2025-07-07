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
          
          <!-- 健康指标卡片 -->
          <el-col :xs="24" :sm="12">
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
          
          <!-- 饮食记录卡片 -->
          <el-col :xs="24" :sm="12">
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
import { Plus, ChatLineRound, Clock, CircleCheck, Refresh, ChatLineSquare } from '@element-plus/icons-vue'
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
        min: 3.5,
        max: 10.5,
        interval: 1,
        axisLine: { lineStyle: { color: '#666' } }
      },
      series: [
        {
          name: '空腹血糖',
          type: 'line',
          data: fastingData,
          connectNulls: true,
          symbol: 'circle',
          symbolSize: 6,
          itemStyle: {
            color: '#409eff'
          },
          lineStyle: {
            width: 2
          },
          markArea: {
            itemStyle: {
              color: 'rgba(103, 194, 58, 0.1)'
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
          data: afterMealData,
          connectNulls: true,
          symbol: 'circle',
          symbolSize: 6,
          itemStyle: {
            color: '#ff9f43'
          },
          lineStyle: {
            width: 2
          },
          markArea: {
            itemStyle: {
              color: 'rgba(103, 194, 58, 0.1)'
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
.dashboard-container {
  padding: 20px;
}

.el-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-card {
  background: linear-gradient(135deg, #409eff, #67c23a);
  color: white;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-text h2 {
  margin: 0;
  font-size: 1.8rem;
}

.welcome-text p {
  margin: 8px 0 0;
  opacity: 0.8;
}

.welcome-actions {
  display: flex;
  gap: 10px;
}

.chart-container {
  height: 300px;
  width: 100%;
  margin: 10px 0;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.chart {
  width: 100%;
  height: 100%;
  min-height: 300px;
}

.metrics-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.metric-item {
  text-align: center;
  padding: 10px;
}

.metric-label {
  color: var(--text-color-secondary);
  font-size: 0.9rem;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 1.4rem;
  font-weight: bold;
  color: var(--text-color);
}

.diet-list {
  margin-bottom: 10px;
}

.diet-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
}

.diet-item:last-child {
  border-bottom: none;
}

.diet-time {
  font-size: 0.9rem;
  color: var(--text-color-secondary);
  width: 30%;
}

.diet-name {
  flex: 1;
}

.diet-calories {
  color: var(--text-color-secondary);
}

.reminder-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reminder-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.reminder-icon {
  margin-right: 12px;
  font-size: 1.2rem;
  color: var(--warning-color);
}

.reminder-icon.done {
  color: var(--success-color);
}

.reminder-content {
  flex: 1;
}

.reminder-text {
  font-weight: 500;
}

.reminder-time {
  font-size: 0.8rem;
  color: var(--text-color-secondary);
}

.knowledge-item {
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}

.knowledge-item:last-child {
  border-bottom: none;
}

.knowledge-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.knowledge-desc {
  font-size: 0.9rem;
  color: var(--text-color-secondary);
  margin-bottom: 8px;
}

.card-footer {
  margin-top: 12px;
  text-align: center;
}

.empty-data {
  padding: 20px 0;
}

.loading-container {
  padding: 20px 0;
}

.glucose-card {
  margin-bottom: 20px;
}

.quick-import {
  padding: 10px;
}

.quick-import h4 {
  margin-bottom: 10px;
  color: #409eff;
  font-weight: 500;
}

.quick-import .el-form {
  margin-bottom: 10px;
}

.glucose-alerts {
  margin-bottom: 15px;
}

.glucose-alerts .el-alert {
  margin-bottom: 8px;
}

.glucose-alerts .el-alert:last-child {
  margin-bottom: 0;
}

/* 智能分析相关样式 */
.glucose-analysis {
  margin-top: 10px;
}

.analysis-summary {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.summary-item {
  text-align: center;
  flex: 1;
  padding: 8px 0;
  border-radius: 4px;
}

.summary-value {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
}

.summary-label {
  font-size: 12px;
  color: #606266;
}

.normal-value { background-color: rgba(103, 194, 58, 0.1); color: #67c23a; }
.high-value { background-color: rgba(245, 108, 108, 0.1); color: #f56c6c; }
.low-value { background-color: rgba(230, 162, 60, 0.1); color: #e6a23c; }

.good-range { background-color: rgba(103, 194, 58, 0.1); color: #67c23a; }
.average-range { background-color: rgba(230, 162, 60, 0.1); color: #e6a23c; }
.poor-range { background-color: rgba(245, 108, 108, 0.1); color: #f56c6c; }

.stable-std { background-color: rgba(103, 194, 58, 0.1); color: #67c23a; }
.moderate-std { background-color: rgba(230, 162, 60, 0.1); color: #e6a23c; }
.unstable-std { background-color: rgba(245, 108, 108, 0.1); color: #f56c6c; }

.advice-preview {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 12px;
  margin-bottom: 10px;
}

.advice-title {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  color: #409eff;
  font-weight: 500;
}

.advice-title .el-icon {
  margin-right: 6px;
}

.advice-content {
  font-size: 13px;
  line-height: 1.5;
  color: #606266;
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

@media (max-width: 768px) {
  .welcome-content {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .metrics-container {
    grid-template-columns: 1fr;
  }
}
</style> 