<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick, onActivated, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { Plus, ChatLineRound, Clock, CircleCheck, Refresh, ChatLineSquare, InfoFilled, Warning, WarningFilled, Close } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { glucoseApi, healthApi, dietApi, knowledgeApi, apiClient } from '../api'
import dayjs from 'dayjs'
import { ElMessage, ElMessageBox } from 'element-plus'

const detailedAdviceContent = ref('')
const showDetailedAdviceCard = ref(false)

// 新增：用于"查看完整分析"模态框的状态
const fullAnalysisContent = ref('')
const showFullAnalysisCard = ref(false)

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
  risk_level: 'normal', // 新增风险等级: normal, warning, danger
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

// 新增：风险评估状态计算属性
const riskAssessmentStatus = computed(() => {
  const level = glucoseAnalysis.value.risk_level
  if (level === 'danger') {
    return {
      class: 'ai-alert-danger',
      icon: WarningFilled,
      title: 'AI血糖高风险评估'
    }
  }
  if (level === 'warning') {
    return {
      class: 'ai-alert-warning',
      icon: Warning,
      title: 'AI血糖风险预警'
    }
  }
  return {
    class: 'ai-alert-good',
    icon: CircleCheck,
    title: 'AI血糖健康评估'
  }
})

// 从API获取血糖数据
const fetchGlucoseData = async () => {
  try {
    loading.value = true
    console.log('开始获取血糖数据...')

    // 使用新的API函数
    const response = await glucoseApi.getRecentGlucoseRecords(
      glucosePeriod.value === 'week' ? 7 : 30
    )

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
    const recentResponse = await glucoseApi.getRecentGlucoseRecords(1); // 获取最近1天的数据

    if (!recentResponse.data || recentResponse.data.length === 0) {
      console.log('没有最近的血糖数据可供分析');
      return null;
    }

    const records = recentResponse.data;
    console.log('获取到最近的血糖数据:', records);

    // 调用后端分析API获取血糖异常预警
    try {
      const analyzeResponse = await apiClient.post('/api/v1/glucose-monitor/analyze', {
        hours: 24 // 分析最近24小时的数据
      }, {
        timeout: 20000 // 设置20秒超时时间
      });

      // 处理API返回的预警信息
      if (analyzeResponse.data?.has_alerts) {
        // 如果有预警信息并且包含大模型生成的警报消息
        if (analyzeResponse.data.alert_message) {
          // 清除现有的相似警报
          glucoseAlerts.value = glucoseAlerts.value.filter(alert => !alert.title.includes('血糖异常'));

          // 添加新的警报，显示大模型生成的个性化预警信息
          addAlert(
            '血糖异常预警',
            analyzeResponse.data.alert_message,
            analyzeResponse.data.alerts.some(a => a.severity === 'high') ? 'error' : 'warning'
          );
          console.log('添加大模型生成的预警消息:', analyzeResponse.data.alert_message);

          return {
            statistics: analyzeResponse.data.statistics || {
              average: 0,
              max: 0,
              min: 0,
              count: records.length,
              high_count: 0,
              low_count: 0
            },
            has_alerts: true,
            alert_message: analyzeResponse.data.alert_message
          };
        }
      }
    } catch (apiError) {
      console.error('调用血糖分析API失败，回退到本地分析:', apiError);
      // 发生错误时继续使用本地分析
    }

    // 本地分析血糖数据（作为备选方案）
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
    const recentResponse = await glucoseApi.getRecentGlucoseRecords(3)

    if (!recentResponse.data || recentResponse.data.length < 3) {
      hasAnalysisData.value = false
      loadingAnalysis.value = false
      return
    }

    // 使用后端分析API获取血糖异常预警和统计数据
    const analyzeResponse = await apiClient.post('/api/v1/glucose-monitor/analyze', {
      hours: 72 // 分析最近72小时(3天)的数据
    }, {
      timeout: 30000 // 设置30秒超时时间
    })

    // 确定风险等级
    let riskLevel: 'normal' | 'warning' | 'danger' = 'normal'
    if (analyzeResponse.data?.has_alerts && analyzeResponse.data.alerts?.length > 0) {
      if (analyzeResponse.data.alerts.some(a => a.severity === 'high')) {
        riskLevel = 'danger'
      } else {
        riskLevel = 'warning'
      }
    }

    // 如果有预警信息，显示在顶部警报区域
    if (analyzeResponse.data?.has_alerts && analyzeResponse.data?.alert_message) {
      // 清除现有的相似警报
      glucoseAlerts.value = glucoseAlerts.value.filter(alert => !alert.title.includes('血糖异常'))

      // 添加新的警报，显示大模型生成的个性化预警信息
      addAlert(
        '血糖异常预警',
        analyzeResponse.data.alert_message,
        analyzeResponse.data.alerts.some(a => a.severity === 'high') ? 'error' : 'warning'
      )
    }

    // 获取统计数据
    const statsResponse = await glucoseApi.getStatistics('week')

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

      // 优先使用大模型生成的建议
      let advice = ''

      // 判断是否有可用的大模型生成的建议
      if (analyzeResponse.data?.alert_message) {
        // 使用大模型生成的个性化预警建议
        advice = analyzeResponse.data.alert_message
        console.log('使用大模型生成的预警建议:', advice)
      } else {
        // 生成本地建议文本
        advice = '根据您最近三天的血糖记录分析：\n\n'

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
          advice += `您的血糖达标率为${inRangePercentage.toFixed(0)}%，低于理想水平(70%)，建议咨询医生调整治疗方案。\n\n`;
        } else if (riskLevel === 'normal') {
          advice = '您的血糖控制良好，各项指标均在理想范围内。请继续保持当前的健康生活方式，定期监测，预防风险。'
        } else {
          advice += '请记住，良好的饮食习惯、适当的运动和按时服药是控制血糖的关键。'
        }
      }

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
        patterns: {
          fasting_avg: records.filter(r =>
            ['BEFORE_BREAKFAST', 'BEFORE_LUNCH', 'BEFORE_DINNER'].includes(r.measurement_time)
          ).reduce((sum, r) => sum + r.value, 0) /
          Math.max(1, records.filter(r =>
            ['BEFORE_BREAKFAST', 'BEFORE_LUNCH', 'BEFORE_DINNER'].includes(r.measurement_time)
          ).length),
          postprandial_avg: records.filter(r =>
            ['AFTER_BREAKFAST', 'AFTER_LUNCH', 'AFTER_DINNER'].includes(r.measurement_time)
          ).reduce((sum, r) => sum + r.value, 0) /
          Math.max(1, records.filter(r =>
            ['AFTER_BREAKFAST', 'AFTER_LUNCH', 'AFTER_DINNER'].includes(r.measurement_time)
          ).length)
        },
        advice: advice,
        risk_level: riskLevel, // 设置风险等级
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

    // 暂时移除大模型API调用，直接使用模拟数据
    // const latestGlucose = glucoseRecords.value[0]?.value || 0
    // const isMealTime = new Date().getHours() >= 6 && new Date().getHours() <= 20
    // const isBeforeMeal = isMealTime && Math.random() > 0.5

    // 不再调用API，直接使用模拟数据
    // const response = await apiClient.get('/api/v1/glucose-monitor/quick-diet-suggestions', {
    //   params: {
    //     glucose_value: latestGlucose,
    //     meal_type: selectedMealType.value,
    //     is_before_meal: isBeforeMeal
    //   }
    // })

    // 直接使用模拟数据
    await new Promise(resolve => setTimeout(resolve, 500)) // 模拟延迟
    simulateDietSuggestions()

  } catch (error) {
    console.error('获取饮食建议失败:', error)
    // 出错时也使用模拟数据
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

    const response = await apiClient.post('/api/v1/glucose-monitor/analyze-trend', { days: 3 }, {
      timeout: 30000
    })

    if (!response.data || !response.data.advice) {
      throw new Error('无法获取血糖分析和建议')
    }

    const adviceContent = response.data.advice

    let processedAdvice = adviceContent
      .replace(/\n\n/g, '<br><br>')
      .replace(/###\s+(.*?)(\n|$)/g, '<h3>$1</h3>')
      .replace(/####\s+(.*?)(\n|$)/g, '<h4>$1</h4>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')

    detailedAdviceContent.value = `
      <div class="blood-glucose-analysis">
        ${processedAdvice}
      </div>
      <h4 class="additional-meal-suggestions">根据您选择的餐型，我们提供以下建议</h4>
      <p><strong>${selectedMealType.value === 'breakfast' ? '早餐' :
                    selectedMealType.value === 'lunch' ? '午餐' :
                    selectedMealType.value === 'dinner' ? '晚餐' : '加餐'}</strong>：
         <span style="color:#409EFF">${dietSuggestions.value.meal_plan_example}</span>
      </p>
    `
    showDetailedAdviceCard.value = true
  } catch (error) {
    console.error('获取详细饮食建议失败:', error)
    ElMessage.error('获取详细饮食建议失败，请稍后再试')

    fallbackToLocalSuggestions()
  }
}

// 回退到本地静态建议
const fallbackToLocalSuggestions = () => {
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
  detailedAdviceContent.value = detailedSuggestion
  showDetailedAdviceCard.value = true
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
const showFullAdvice = async () => {
  try {
    // 显示加载提示
    ElMessage.info('正在获取最新的血糖风险评估...')

    // 首先调用analyze接口获取预警信息
    const alertResponse = await apiClient.post('/api/v1/glucose-monitor/analyze', {
      hours: 72 // 分析最近72小时的数据
    }, {
      timeout: 30000 // 设置30秒超时时间
    })

    // 然后调用analyze-trend接口获取详细的血糖分析报告
    const trendResponse = await apiClient.post('/api/v1/glucose-monitor/analyze-trend', {
      days: 3
    }, {
      timeout: 30000 // 设置30秒超时时间
    })

    if (!trendResponse.data || !trendResponse.data.advice) {
      throw new Error('无法获取血糖分析和建议')
    }

    // 使用大模型生成的血糖分析报告和建议
    const adviceContent = trendResponse.data.advice
    let dialogTitle = '血糖风险评估与管理建议'

    // 更新当前的建议内容
    glucoseAnalysis.value.advice = adviceContent

    // 如果有预警信息，添加到顶部警报区域
    if (alertResponse.data?.has_alerts && alertResponse.data?.alert_message) {
      // 清除现有的相似警报
      glucoseAlerts.value = glucoseAlerts.value.filter(alert => !alert.title.includes('血糖异常'))

      // 添加新的警报，显示大模型生成的个性化预警信息
      addAlert(
        '血糖异常预警',
        alertResponse.data.alert_message,
        alertResponse.data.alerts.some(a => a.severity === 'high') ? 'error' : 'warning'
      )
    }

    // 将大模型生成的文本处理为HTML格式
    let processedAdvice = adviceContent
      .replace(/\n\n/g, '<br><br>') // 替换双换行为HTML换行
      .replace(/###\s+(.*?)(\n|$)/g, '<h3>$1</h3>') // 处理 ### 标题
      .replace(/####\s+(.*?)(\n|$)/g, '<h4>$1</h4>') // 处理 #### 标题
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // 处理加粗文本

    // 如果有预警信息，在分析报告前添加预警信息
    let contentToShow = ``

    if (alertResponse.data?.has_alerts && alertResponse.data?.alert_message) {
      contentToShow = `
        <div class="glucose-alert-warning">
          <h3>⚠️ 血糖异常预警</h3>
          <p>${alertResponse.data.alert_message}</p>
        </div>
        <div class="blood-glucose-analysis ai-analysis-content">
          ${processedAdvice}
        </div>
      `
    } else {
      contentToShow = `
        <div class="blood-glucose-analysis ai-analysis-content">
          ${processedAdvice}
        </div>
      `
    }

    // ! 移除 ElMessageBox.alert，改为显示自定义模态框
    fullAnalysisContent.value = contentToShow
    showFullAnalysisCard.value = true

  } catch (error) {
    console.error('获取血糖风险评估失败:', error)
    ElMessage.error('获取血糖风险评估失败，请稍后再试')

    // 错误时回退到本地静态建议，并显示在新的模态框中
    const staticAdvice = `
      <h3>血糖管理建议</h3>
      <p>很抱歉，无法获取实时血糖分析。以下是基于通用规则的建议：</p>

      <h4>血糖管理原则</h4>
      <ul>
        <li>保持规律饮食，避免暴饮暴食</li>
        <li>增加体育活动，每天至少30分钟中等强度运动</li>
        <li>按时服药，遵医嘱调整药物剂量</li>
        <li>定期监测血糖，记录变化趋势</li>
        <li>避免过度疲劳和精神压力</li>
      </ul>

      <h4>监测提示</h4>
      <p>建议继续监测并记录您的血糖值，特别是在餐前和餐后2小时的数值，这将有助于更准确地评估您的血糖控制情况。</p>
    `

    fullAnalysisContent.value = `<div class="blood-glucose-analysis ai-analysis-content">${staticAdvice}</div>`
    showFullAnalysisCard.value = true
  }
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
