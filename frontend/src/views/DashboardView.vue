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
                  <el-radio-group v-model="glucosePeriod" size="small">
                    <el-radio-button value="week">周</el-radio-button>
                    <el-radio-button value="month">月</el-radio-button>
                  </el-radio-group>
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
                <div ref="glucoseChartRef" class="chart"></div>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { Plus, ChatLineRound, Clock, CircleCheck } from '@element-plus/icons-vue'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { glucoseApi, healthApi, dietApi, knowledgeApi } from '../api'
import dayjs from 'dayjs'

// 注册ECharts组件
echarts.use([LineChart, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer])

const router = useRouter()
const userStore = useUserStore()

const loading = ref(true)
const glucosePeriod = ref('week')
const glucoseChartRef = ref<HTMLElement | null>(null)
const glucoseChart = ref<echarts.ECharts | null>(null)

const userName = computed(() => userStore.userFullName)
const currentDate = computed(() => dayjs().format('YYYY年MM月DD日'))

// 模拟数据
const healthMetrics = ref({
  weight: '68.5',
  bloodPressure: '120/80',
  bmi: '22.5',
  steps: '6,842'
})

const hasGlucoseData = ref(true)
const hasDietData = ref(true)

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

onMounted(async () => {
  try {
    // 这里应该调用API获取实际数据
    // await fetchDashboardData()
    
    // 初始化血糖趋势图
    initGlucoseChart()
  } catch (error) {
    console.error('获取仪表盘数据失败', error)
  } finally {
    loading.value = false
  }
})

const initGlucoseChart = () => {
  if (glucoseChartRef.value) {
    glucoseChart.value = echarts.init(glucoseChartRef.value)
    
    // 模拟数据
    const dates = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    const fastingData = [5.6, 5.8, 5.5, 6.1, 5.9, 5.7, 5.6]
    const afterMealData = [7.8, 8.2, 7.5, 8.5, 8.0, 7.9, 7.7]
    
    const option = {
      tooltip: {
        trigger: 'axis'
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
        min: 4,
        max: 10,
        interval: 1
      },
      series: [
        {
          name: '空腹血糖',
          type: 'line',
          data: fastingData,
          markArea: {
            itemStyle: {
              color: 'rgba(0, 255, 0, 0.1)'
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
          markArea: {
            itemStyle: {
              color: 'rgba(0, 255, 0, 0.1)'
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
    
    glucoseChart.value.setOption(option)
    
    // 监听窗口大小变化，调整图表大小
    window.addEventListener('resize', () => {
      glucoseChart.value?.resize()
    })
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
  router.push('/glucose')
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
}

.chart {
  width: 100%;
  height: 100%;
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