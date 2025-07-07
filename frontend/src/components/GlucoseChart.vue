<template>
  <div class="glucose-chart-container">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <div class="chart-controls">
        <el-select v-model="selectedPeriod" placeholder="选择时间范围" size="small" @change="fetchData">
          <el-option v-for="item in periodOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </div>
    </div>
    
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="6" animated />
    </div>
    
    <div v-else-if="error" class="error-container">
      <el-empty description="加载数据失败" :image-size="100">
        <template #description>
          <p>{{ error }}</p>
        </template>
        <el-button type="primary" size="small" @click="fetchData">重试</el-button>
      </el-empty>
    </div>
    
    <div v-else-if="!hasData" class="empty-container">
      <el-empty description="暂无血糖数据" :image-size="100">
        <el-button type="primary" size="small" @click="$emit('add-record')">添加记录</el-button>
      </el-empty>
    </div>
    
    <div v-else ref="chartContainer" class="chart-container"></div>
    
    <div v-if="hasData && showStats" class="statistics-container">
      <div class="stat-item">
        <div class="stat-label">平均血糖</div>
        <div class="stat-value">{{ statistics.average }} mmol/L</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">最高值</div>
        <div class="stat-value">{{ statistics.max }} mmol/L</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">最低值</div>
        <div class="stat-value">{{ statistics.min }} mmol/L</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">达标率</div>
        <div class="stat-value">{{ statistics.in_range_percentage }}%</div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch, nextTick } from 'vue';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';
import { useUserStore } from '@/stores/user';
import { fetchGlucoseRecords, fetchGlucoseStatistics } from '@/api/glucose';
import dayjs from 'dayjs';

// 计算数组平均值的辅助函数
const average = (arr: number[]): number | null => {
  if (!arr || arr.length === 0) return null;
  const sum = arr.reduce((a, b) => a + b, 0);
  return Number((sum / arr.length).toFixed(1));
};

export default defineComponent({
  name: 'GlucoseChart',
  props: {
    title: {
      type: String,
      default: '血糖趋势'
    },
    showStats: {
      type: Boolean,
      default: true
    }
  },
  emits: ['add-record'],
  setup(props) {
    const userStore = useUserStore();
    const chartContainer = ref<HTMLElement | null>(null);
    const chart = ref<echarts.ECharts | null>(null);
    const loading = ref(false);
    const error = ref('');
    const hasData = ref(false);
    
    const selectedPeriod = ref('week');
    const periodOptions = [
      { value: 'day', label: '今日' },
      { value: 'week', label: '本周' },
      { value: 'month', label: '本月' },
      { value: 'quarter', label: '三个月' }
    ];
    
    const glucoseData = ref<any[]>([]);
    const statistics = ref({
      average: 0,
      max: 0,
      min: 0,
      count: 0,
      in_range_percentage: 0,
      high_percentage: 0,
      low_percentage: 0
    });
    
    // 目标血糖范围
    const targetMin = ref(3.9);
    const targetMax = ref(7.8);
    
    // 初始化图表
    const initChart = () => {
      if (!chartContainer.value) return;
      
      // 如果图表已经存在，先销毁
      if (chart.value) {
        chart.value.dispose();
      }
      
      // 创建新图表
      chart.value = echarts.init(chartContainer.value);
      
      // 设置图表配置
      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: function(params: any) {
            const data = params[0].data;
            const time = new Date(data[0]).toLocaleString();
            const value = data[1];
            const measurementTime = data[2];
            return `${time}<br/>血糖值: ${value} mmol/L<br/>测量时间: ${measurementTime}`;
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'time',
          boundaryGap: false,
          axisLabel: {
            formatter: function(value: number) {
              const date = new Date(value);
              return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
            }
          }
        },
        yAxis: {
          type: 'value',
          name: '血糖值 (mmol/L)',
          axisLine: { show: true },
          splitLine: { show: true },
          min: function(value: { min: number }) {
            return Math.max(0, Math.floor(value.min) - 1);
          },
          max: function(value: { max: number }) {
            return Math.ceil(value.max) + 1;
          },
          axisLabel: {
            formatter: '{value}'
          }
        },
        series: [
          {
            name: '血糖值',
            type: 'line',
            smooth: true,
            symbol: 'circle',
            symbolSize: 8,
            sampling: 'average',
            itemStyle: {
              color: '#5470c6'
            },
            markArea: {
              silent: true,
              data: [
                [
                  {
                    yAxis: targetMin.value,
                    itemStyle: {
                      color: 'rgba(144, 238, 144, 0.2)'
                    }
                  },
                  {
                    yAxis: targetMax.value
                  }
                ]
              ]
            },
            data: glucoseData.value
          }
        ],
        visualMap: {
          show: false,
          pieces: [
            {
              gt: 0,
              lte: targetMin.value,
              color: '#f56c6c'
            },
            {
              gt: targetMin.value,
              lte: targetMax.value,
              color: '#67c23a'
            },
            {
              gt: targetMax.value,
              color: '#e6a23c'
            }
          ],
          outOfRange: {
            color: '#f56c6c'
          }
        }
      };
      
      // 应用配置
      chart.value.setOption(option);
      
      // 添加响应式调整
      window.addEventListener('resize', () => {
        chart.value?.resize();
      });
    };
    
    // 处理数据，将记录按日期和时间类型分组
    const processData = (records) => {
      // 按日期分组
      const recordsByDate = {};
      
      records.forEach(record => {
        const date = dayjs(record.measured_at).format('YYYY-MM-DD');
        if (!recordsByDate[date]) {
          recordsByDate[date] = [];
        }
        recordsByDate[date].push(record);
      });
      
      // 转换为图表数据
      const chartData = [];
      
      Object.keys(recordsByDate).forEach(date => {
        const dateRecords = recordsByDate[date];
        
        // 按测量类型分组
        const byType = {
          BEFORE_BREAKFAST: [],
          AFTER_BREAKFAST: [],
          BEFORE_LUNCH: [],
          AFTER_LUNCH: [],
          BEFORE_DINNER: [],
          AFTER_DINNER: [],
          BEFORE_SLEEP: []
        };
        
        dateRecords.forEach(record => {
          // 确保measurement_time是大写
          const measurementType = record.measurement_time.toUpperCase();
          if (byType[measurementType]) {
            byType[measurementType].push(record.value);
          }
        });
        
        // 计算每种类型的平均值
        const entry = {
          date: date,
          BEFORE_BREAKFAST: average(byType.BEFORE_BREAKFAST),
          AFTER_BREAKFAST: average(byType.AFTER_BREAKFAST),
          BEFORE_LUNCH: average(byType.BEFORE_LUNCH),
          AFTER_LUNCH: average(byType.AFTER_LUNCH),
          BEFORE_DINNER: average(byType.BEFORE_DINNER),
          AFTER_DINNER: average(byType.AFTER_DINNER),
          BEFORE_SLEEP: average(byType.BEFORE_SLEEP)
        };
        
        chartData.push(entry);
      });
      
      // 按日期排序
      return chartData.sort((a, b) => dayjs(a.date).diff(dayjs(b.date)));
    };
    
    // 创建散点图数据
    const createScatterData = (records) => {
      return records.map(record => ({
        x: new Date(record.measured_at),
        y: record.value,
        type: record.measurement_time.toUpperCase(), // 确保使用大写
        id: record.id
      }));
    };
    
    // 获取数据
    const fetchData = async () => {
      loading.value = true;
      error.value = '';
      
      try {
        // 获取用户目标血糖范围
        if (userStore.user) {
          targetMin.value = userStore.user.target_glucose_min || 3.9;
          targetMax.value = userStore.user.target_glucose_max || 7.8;
        }
        
        // 获取血糖记录
        const period = selectedPeriod.value;
        const response = await fetchGlucoseRecords({ period });
        
        // 处理数据
        glucoseData.value = processData(response.data);
        hasData.value = glucoseData.value.length > 0;
        
        // 获取统计数据
        const statsResponse = await fetchGlucoseStatistics({ period });
        statistics.value = statsResponse.data;
        
        // 更新图表
        nextTick(() => {
          initChart();
        });
      } catch (err: any) {
        error.value = err.message || '加载数据失败';
        ElMessage.error('加载血糖数据失败');
      } finally {
        loading.value = false;
      }
    };
    
    // 监听周期变化
    watch(selectedPeriod, () => {
      fetchData();
    });
    
    // 组件挂载时获取数据
    onMounted(() => {
      fetchData();
    });
    
    return {
      chartContainer,
      loading,
      error,
      hasData,
      selectedPeriod,
      periodOptions,
      statistics,
      fetchData
    };
  }
});
</script>

<style scoped>
.glucose-chart-container {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 16px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.chart-container {
  height: 300px;
  width: 100%;
}

.loading-container,
.error-container,
.empty-container {
  height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.statistics-container {
  margin-top: 16px;
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  border-top: 1px solid #ebeef5;
  padding-top: 16px;
}

.stat-item {
  text-align: center;
  padding: 8px 16px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}
</style> 