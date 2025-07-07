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
import { ref, computed, onMounted, watch, nextTick, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { Plus, ChatLineRound, Clock, CircleCheck, Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { glucoseApi, healthApi, dietApi, knowledgeApi, apiClient } from '../api'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'

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

// 从API获取血糖数据
const fetchGlucoseData = async () => {
  try {
    loading.value = true
    console.log('开始获取血糖数据...')
    const response = await glucoseApi.getGlucoseRecords()
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

// 导入血糖数据
const importGlucoseData = async () => {
  if (!glucoseForm.value.value || !glucoseForm.value.measurement_time) {
    ElMessage.warning('请填写完整的血糖数据')
    return
  }
  
  importing.value = true
  try {
    const response = await apiClient.post('/api/v1/glucose', {
      value: glucoseForm.value.value,
      measured_at: dayjs().format('YYYY-MM-DDTHH:mm:00Z'),
      measurement_time: glucoseForm.value.measurement_time,
      notes: '从仪表盘快速添加'
    })
    
    ElMessage.success(response.data.message || '血糖数据保存成功')
    
    // 重置表单
    glucoseForm.value.value = 5.6
    
    // 刷新血糖数据
    await fetchGlucoseData()
    
    // 分析血糖数据
    await analyzeGlucoseData()
  } catch (error) {
    console.error('保存血糖数据失败', error)
    ElMessage.error('保存血糖数据失败')
  } finally {
    importing.value = false
  }
}

// 分析血糖数据并检查异常
const analyzeGlucoseData = async () => {
  try {
    const response = await apiClient.post('/api/v1/glucose-monitor/analyze', {
      hours: 24 // 分析最近24小时的数据
    })
    
    const result = response.data
    
    // 如果有警报，添加到警报列表
    if (result.has_alerts && result.alerts && result.alerts.length > 0) {
      // 清空旧的警报
      glucoseAlerts.value = []
      
      // 添加新警报
      result.alerts.forEach((alert: any) => {
        let title = ''
        let message = ''
        let type: 'warning' | 'error' = 'warning'
        
        if (alert.type === 'low_glucose') {
          title = '低血糖警报'
          message = `检测到血糖值 ${alert.value} mmol/L，低于正常范围 ${alert.threshold} mmol/L`
          type = alert.severity === 'high' ? 'error' : 'warning'
        } else if (alert.type === 'high_glucose') {
          title = '高血糖警报'
          message = `检测到血糖值 ${alert.value} mmol/L，高于正常范围 ${alert.threshold} mmol/L`
          type = alert.severity === 'high' ? 'error' : 'warning'
        } else if (alert.type === 'rapid_rise') {
          title = '血糖快速上升警报'
          message = `检测到血糖快速上升 ${alert.value.toFixed(1)} mmol/L/小时`
          type = 'warning'
        } else if (alert.type === 'rapid_drop') {
          title = '血糖快速下降警报'
          message = `检测到血糖快速下降 ${alert.value.toFixed(1)} mmol/L/小时`
          type = 'error'
        }
        
        glucoseAlerts.value.push({
          title,
          message,
          type
        })
      })
    }
    
    return result
  } catch (error) {
    console.error('分析血糖数据失败', error)
    return null
  }
}

// 移除警报
const removeAlert = (index: number) => {
  glucoseAlerts.value.splice(index, 1)
}

onMounted(async () => {
  console.log('DashboardView组件挂载')
  try {
    // 获取血糖数据
    const result = await fetchGlucoseData()
    
    // 分析血糖数据
    await analyzeGlucoseData()
    
    // 确保DOM已经渲染完成
    await nextTick()
    console.log('DOM已更新，准备初始化图表')
    
    // 延迟一点时间确保DOM完全渲染
    setTimeout(() => {
      if (glucoseChartRef.value && hasGlucoseData.value) {
        // 强制设置容器尺寸
        glucoseChartRef.value.style.height = '300px'
        glucoseChartRef.value.style.width = '100%'
        
        console.log('组件挂载时初始化图表')
        initGlucoseChart()
      } else {
        console.error('组件挂载时图表容器不存在或无数据')
      }
    }, 200)
    
    // 加载完成
    loading.value = false
    
    // 获取其他数据（可以添加实际API调用）
    // await fetchHealthMetrics()
    // await fetchDietRecords()
  } catch (error) {
    console.error('获取仪表盘数据失败', error)
  } finally {
    loading.value = false
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