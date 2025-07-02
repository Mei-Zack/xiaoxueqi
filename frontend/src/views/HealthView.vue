<template>
  <div class="health-container">
    <h1>健康数据管理</h1>
    
    <el-card class="health-card">
      <template #header>
        <div class="card-header">
          <span>添加健康数据</span>
        </div>
      </template>
      
      <el-form :model="healthForm" :rules="rules" ref="healthFormRef" label-width="120px">
        <el-form-item label="测量日期" prop="measureDate">
          <el-date-picker
            v-model="healthForm.measureDate"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <el-form-item label="体重 (kg)" prop="weight">
          <el-input-number v-model="healthForm.weight" :precision="1" :step="0.1" :min="20" :max="200" />
        </el-form-item>
        
        <el-form-item label="血压 (mmHg)" prop="bloodPressure">
          <div class="blood-pressure-input">
            <el-input-number v-model="healthForm.systolicPressure" :min="60" :max="250" placeholder="收缩压" />
            <span class="separator">/</span>
            <el-input-number v-model="healthForm.diastolicPressure" :min="40" :max="150" placeholder="舒张压" />
          </div>
        </el-form-item>
        
        <el-form-item label="心率 (bpm)" prop="heartRate">
          <el-input-number v-model="healthForm.heartRate" :min="30" :max="220" />
        </el-form-item>
        
        <el-form-item label="备注" prop="note">
          <el-input v-model="healthForm.note" type="textarea" :rows="2" placeholder="添加备注信息" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="loading">保存</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="health-card">
      <template #header>
        <div class="card-header">
          <span>健康数据记录</span>
          <div class="header-actions">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              @change="handleDateRangeChange"
            />
          </div>
        </div>
      </template>
      
      <el-table :data="healthRecords" style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="measureDate" label="日期" width="120" />
        <el-table-column prop="weight" label="体重 (kg)" width="100" />
        <el-table-column label="血压 (mmHg)" width="120">
          <template #default="scope">
            {{ scope.row.systolicPressure }}/{{ scope.row.diastolicPressure }}
          </template>
        </el-table-column>
        <el-table-column prop="heartRate" label="心率 (bpm)" width="100" />
        <el-table-column prop="note" label="备注" />
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="editRecord(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteRecord(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="totalRecords"
          :page-size="pageSize"
          :current-page="currentPage"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
    
    <el-dialog v-model="dialogVisible" title="编辑健康数据" width="500px">
      <el-form :model="editForm" :rules="rules" ref="editFormRef" label-width="120px">
        <el-form-item label="测量日期" prop="measureDate">
          <el-date-picker
            v-model="editForm.measureDate"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <el-form-item label="体重 (kg)" prop="weight">
          <el-input-number v-model="editForm.weight" :precision="1" :step="0.1" :min="20" :max="200" />
        </el-form-item>
        
        <el-form-item label="血压 (mmHg)" prop="bloodPressure">
          <div class="blood-pressure-input">
            <el-input-number v-model="editForm.systolicPressure" :min="60" :max="250" placeholder="收缩压" />
            <span class="separator">/</span>
            <el-input-number v-model="editForm.diastolicPressure" :min="40" :max="150" placeholder="舒张压" />
          </div>
        </el-form-item>
        
        <el-form-item label="心率 (bpm)" prop="heartRate">
          <el-input-number v-model="editForm.heartRate" :min="30" :max="220" />
        </el-form-item>
        
        <el-form-item label="备注" prop="note">
          <el-input v-model="editForm.note" type="textarea" :rows="2" placeholder="添加备注信息" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="updateRecord" :loading="updateLoading">确认</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { format } from 'date-fns'
import { healthApi } from '../api/index'
import { useUserStore } from '../stores/user'

// 获取用户store
const userStore = useUserStore()

// 表单数据
const healthForm = reactive({
  measureDate: format(new Date(), 'yyyy-MM-dd'),
  weight: null,
  systolicPressure: null,
  diastolicPressure: null,
  heartRate: null,
  note: '',
  user_id: ''
})

// 表单验证规则
const rules = {
  measureDate: [
    { required: true, message: '请选择测量日期', trigger: 'change' }
  ],
  weight: [
    { required: true, message: '请输入体重', trigger: 'blur' }
  ],
  heartRate: [
    { required: true, message: '请输入心率', trigger: 'blur' }
  ]
}

// 表单引用
const healthFormRef = ref(null)
const editFormRef = ref(null)

// 加载状态
const loading = ref(false)
const tableLoading = ref(false)
const updateLoading = ref(false)

// 分页数据
const currentPage = ref(1)
const pageSize = ref(10)
const totalRecords = ref(0)

// 健康记录数据
const healthRecords = ref([])

// 日期范围筛选
const dateRange = ref([])

// 编辑对话框
const dialogVisible = ref(false)
const editForm = reactive({
  id: null,
  measureDate: '',
  weight: null,
  systolicPressure: null,
  diastolicPressure: null,
  heartRate: null,
  note: '',
  user_id: ''
})

// 获取健康数据记录
const fetchHealthRecords = async () => {
  try {
    tableLoading.value = true
    
    // 调用后端API获取数据
    const params = {
      page: currentPage.value - 1,
      limit: pageSize.value,
      start_date: dateRange.value ? dateRange.value[0] : null,
      end_date: dateRange.value ? dateRange.value[1] : null
    }
    
    const response = await healthApi.getHealthData(params)
    
    if (response.data && Array.isArray(response.data)) {
      // 处理健康记录数据
      healthRecords.value = response.data.map(record => ({
        id: record.id,
        measureDate: format(new Date(record.record_date), 'yyyy-MM-dd'),
        weight: record.weight_records && record.weight_records.length > 0 
          ? record.weight_records[0].weight 
          : null,
        systolicPressure: record.blood_pressure_records && record.blood_pressure_records.length > 0 
          ? record.blood_pressure_records[0].systolic 
          : null,
        diastolicPressure: record.blood_pressure_records && record.blood_pressure_records.length > 0 
          ? record.blood_pressure_records[0].diastolic 
          : null,
        heartRate: record.blood_pressure_records && record.blood_pressure_records.length > 0 
          ? record.blood_pressure_records[0].pulse 
          : null,
        note: record.notes
      }))
      
      totalRecords.value = response.data.length
    } else {
      healthRecords.value = []
      totalRecords.value = 0
    }
    
  } catch (error) {
    console.error('获取健康数据失败:', error)
    ElMessage.error('获取健康数据失败')
  } finally {
    tableLoading.value = false
  }
}

// 提交表单
const submitForm = async () => {
  if (!healthFormRef.value) return
  
  await healthFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        loading.value = true
        
        // 确保表单有用户ID
        if (!healthForm.user_id) {
          healthForm.user_id = userStore.user?.id || ''
        }
        
        // 构建API请求数据
        const requestData = {
          user_id: healthForm.user_id,
          record_date: new Date(healthForm.measureDate),
          notes: healthForm.note,
          weight_records: healthForm.weight ? [{
            user_id: healthForm.user_id,
            weight: healthForm.weight,
            measured_at: new Date(healthForm.measureDate)
          }] : [],
          blood_pressure_records: healthForm.systolicPressure && healthForm.diastolicPressure ? [{
            user_id: healthForm.user_id,
            systolic: healthForm.systolicPressure,
            diastolic: healthForm.diastolicPressure,
            pulse: healthForm.heartRate,
            measured_at: new Date(healthForm.measureDate)
          }] : []
        }
        
        // 调用API创建记录
        await healthApi.addHealthData(requestData)
        
        ElMessage.success('健康数据保存成功')
        resetForm()
        fetchHealthRecords()
        
      } catch (error) {
        console.error('保存健康数据失败:', error)
        ElMessage.error('保存健康数据失败')
      } finally {
        loading.value = false
      }
    }
  })
}

// 重置表单
const resetForm = () => {
  if (healthFormRef.value) {
    healthFormRef.value.resetFields()
    healthForm.measureDate = format(new Date(), 'yyyy-MM-dd')
  }
}

// 编辑记录
const editRecord = (row) => {
  Object.assign(editForm, row)
  editForm.user_id = userStore.user?.id || ''
  dialogVisible.value = true
}

// 更新记录
const updateRecord = async () => {
  if (!editFormRef.value) return
  
  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        updateLoading.value = true
        
        // 构建API请求数据
        const requestData = {
          notes: editForm.note,
          weight_records: editForm.weight ? [{
            user_id: editForm.user_id,
            weight: editForm.weight,
            measured_at: new Date(editForm.measureDate)
          }] : [],
          blood_pressure_records: editForm.systolicPressure && editForm.diastolicPressure ? [{
            user_id: editForm.user_id,
            systolic: editForm.systolicPressure,
            diastolic: editForm.diastolicPressure,
            pulse: editForm.heartRate,
            measured_at: new Date(editForm.measureDate)
          }] : []
        }
        
        // 调用API更新记录
        await healthApi.updateHealthData(editForm.id, requestData)
        
        ElMessage.success('健康数据更新成功')
        dialogVisible.value = false
        fetchHealthRecords()
        
      } catch (error) {
        console.error('更新健康数据失败:', error)
        ElMessage.error('更新健康数据失败')
      } finally {
        updateLoading.value = false
      }
    }
  })
}

// 删除记录
const deleteRecord = (row) => {
  ElMessageBox.confirm('确定要删除这条健康记录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      // 调用API删除记录
      await healthApi.deleteHealthData(row.id)
      
      ElMessage.success('健康数据删除成功')
      fetchHealthRecords()
      
    } catch (error) {
      console.error('删除健康数据失败:', error)
      ElMessage.error('删除健康数据失败')
    }
  }).catch(() => {})
}

// 处理分页变化
const handlePageChange = (page) => {
  currentPage.value = page
  fetchHealthRecords()
}

// 处理日期范围变化
const handleDateRangeChange = () => {
  currentPage.value = 1
  fetchHealthRecords()
}

// 组件挂载时获取数据
onMounted(() => {
  // 设置用户ID
  healthForm.user_id = userStore.user?.id || ''
  fetchHealthRecords()
})
</script>

<style scoped>
.health-container {
  padding: 20px;
}

.health-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.blood-pressure-input {
  display: flex;
  align-items: center;
  gap: 10px;
}

.separator {
  font-weight: bold;
  font-size: 18px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style> 