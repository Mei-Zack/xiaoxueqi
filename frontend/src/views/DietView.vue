<template>
  <div class="diet-container">
    <h1>饮食记录管理</h1>
    
    <el-card class="diet-card">
      <template #header>
        <div class="card-header">
          <span>添加饮食记录</span>
        </div>
      </template>
      
      <el-form :model="dietForm" :rules="rules" ref="dietFormRef" label-width="120px">
        <el-form-item label="日期时间" prop="dateTime">
          <el-date-picker
            v-model="dietForm.dateTime"
            type="datetime"
            placeholder="选择日期时间"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        
        <el-form-item label="餐食类型" prop="mealType">
          <el-select v-model="dietForm.mealType" placeholder="请选择餐食类型">
            <el-option label="早餐" value="breakfast" />
            <el-option label="午餐" value="lunch" />
            <el-option label="晚餐" value="dinner" />
            <el-option label="加餐" value="snack" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="食物名称" prop="foodName">
          <el-input v-model="dietForm.foodName" placeholder="请输入食物名称" />
        </el-form-item>
        
        <el-form-item label="食物分类" prop="foodCategory">
          <el-select v-model="dietForm.foodCategory" placeholder="请选择食物分类">
            <el-option
              v-for="item in foodCategories"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="食用量(g)" prop="amount">
          <el-input-number v-model="dietForm.amount" :min="0" :precision="1" :step="10" />
        </el-form-item>
        
        <el-form-item label="碳水化合物(g)" prop="carbs">
          <el-input-number v-model="dietForm.carbs" :min="0" :precision="1" :step="0.5" />
        </el-form-item>
        
        <el-form-item label="蛋白质(g)" prop="protein">
          <el-input-number v-model="dietForm.protein" :min="0" :precision="1" :step="0.5" />
        </el-form-item>
        
        <el-form-item label="脂肪(g)" prop="fat">
          <el-input-number v-model="dietForm.fat" :min="0" :precision="1" :step="0.5" />
        </el-form-item>
        
        <el-form-item label="热量(kcal)" prop="calories">
          <el-input-number v-model="dietForm.calories" :min="0" :precision="0" :step="10" />
        </el-form-item>
        
        <el-form-item label="备注" prop="note">
          <el-input v-model="dietForm.note" type="textarea" :rows="2" placeholder="添加备注信息" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="loading">保存</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="diet-card">
      <template #header>
        <div class="card-header">
          <span>饮食记录列表</span>
          <div class="header-actions">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              @change="handleDateRangeChange"
            />
            <el-select v-model="filterMealType" placeholder="餐食类型" clearable @change="handleFilterChange">
              <el-option label="早餐" value="breakfast" />
              <el-option label="午餐" value="lunch" />
              <el-option label="晚餐" value="dinner" />
              <el-option label="加餐" value="snack" />
            </el-select>
          </div>
        </div>
      </template>
      
      <el-table :data="dietRecords" style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="dateTime" label="日期时间" width="150" />
        <el-table-column prop="mealType" label="餐食类型" width="100">
          <template #default="scope">
            {{ getMealTypeName(scope.row.mealType) }}
          </template>
        </el-table-column>
        <el-table-column prop="foodName" label="食物名称" width="150" />
        <el-table-column prop="foodCategory" label="食物分类" width="100">
          <template #default="scope">
            {{ getFoodCategoryName(scope.row.foodCategory) }}
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="食用量(g)" width="100" />
        <el-table-column prop="carbs" label="碳水(g)" width="90" />
        <el-table-column prop="protein" label="蛋白质(g)" width="90" />
        <el-table-column prop="fat" label="脂肪(g)" width="90" />
        <el-table-column prop="calories" label="热量(kcal)" width="100" />
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
    
    <el-dialog v-model="dialogVisible" title="编辑饮食记录" width="500px">
      <el-form :model="editForm" :rules="rules" ref="editFormRef" label-width="120px">
        <el-form-item label="日期时间" prop="dateTime">
          <el-date-picker
            v-model="editForm.dateTime"
            type="datetime"
            placeholder="选择日期时间"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        
        <el-form-item label="餐食类型" prop="mealType">
          <el-select v-model="editForm.mealType" placeholder="请选择餐食类型">
            <el-option label="早餐" value="breakfast" />
            <el-option label="午餐" value="lunch" />
            <el-option label="晚餐" value="dinner" />
            <el-option label="加餐" value="snack" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="食物名称" prop="foodName">
          <el-input v-model="editForm.foodName" placeholder="请输入食物名称" />
        </el-form-item>
        
        <el-form-item label="食物分类" prop="foodCategory">
          <el-select v-model="editForm.foodCategory" placeholder="请选择食物分类">
            <el-option
              v-for="item in foodCategories"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="食用量(g)" prop="amount">
          <el-input-number v-model="editForm.amount" :min="0" :precision="1" :step="10" />
        </el-form-item>
        
        <el-form-item label="碳水化合物(g)" prop="carbs">
          <el-input-number v-model="editForm.carbs" :min="0" :precision="1" :step="0.5" />
        </el-form-item>
        
        <el-form-item label="蛋白质(g)" prop="protein">
          <el-input-number v-model="editForm.protein" :min="0" :precision="1" :step="0.5" />
        </el-form-item>
        
        <el-form-item label="脂肪(g)" prop="fat">
          <el-input-number v-model="editForm.fat" :min="0" :precision="1" :step="0.5" />
        </el-form-item>
        
        <el-form-item label="热量(kcal)" prop="calories">
          <el-input-number v-model="editForm.calories" :min="0" :precision="0" :step="10" />
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
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { format } from 'date-fns'
import { dietApi } from '~/api'
import { useUserStore } from '~/stores/user'

const userStore = useUserStore()
const user = computed(() => userStore.user)

// 表单数据
const dietForm = reactive({
  dateTime: format(new Date(), 'yyyy-MM-dd HH:mm:ss'),
  mealType: '',
  foodName: '',
  foodCategory: '',
  amount: 100,
  carbs: 0,
  protein: 0,
  fat: 0,
  calories: 0,
  note: ''
})

// 食物分类
const foodCategories = [
  { value: 'grain', label: '谷物类' },
  { value: 'protein', label: '蛋白质类' },
  { value: 'vegetable', label: '蔬菜类' },
  { value: 'fruit', label: '水果类' },
  { value: 'dairy', label: '奶制品' },
  { value: 'fat', label: '油脂类' },
  { value: 'sweet', label: '甜食' },
  { value: 'beverage', label: '饮料' },
  { value: 'other', label: '其他' }
]

// 表单验证规则
const rules = {
  dateTime: [
    { required: true, message: '请选择日期时间', trigger: 'change' }
  ],
  mealType: [
    { required: true, message: '请选择餐食类型', trigger: 'change' }
  ],
  foodName: [
    { required: true, message: '请输入食物名称', trigger: 'blur' }
  ],
  foodCategory: [
    { required: true, message: '请选择食物分类', trigger: 'change' }
  ],
  amount: [
    { required: true, message: '请输入食物食用量', trigger: 'blur' }
  ],
  carbs: [
    { required: true, message: '请输入碳水化合物含量', trigger: 'blur' }
  ],
  protein: [
    { required: true, message: '请输入蛋白质含量', trigger: 'blur' }
  ],
  fat: [
    { required: true, message: '请输入脂肪含量', trigger: 'blur' }
  ],
  calories: [
    { required: true, message: '请输入热量', trigger: 'blur' }
  ]
}

// 表单引用
const dietFormRef = ref(null)
const editFormRef = ref(null)

// 加载状态
const loading = ref(false)
const tableLoading = ref(false)
const updateLoading = ref(false)

// 分页数据
const currentPage = ref(1)
const pageSize = ref(10)
const totalRecords = ref(0)

// 饮食记录数据
const dietRecords = ref([])

// 日期范围筛选
const dateRange = ref([])
const filterMealType = ref('')

// 编辑对话框
const dialogVisible = ref(false)
const editForm = reactive({
  id: null,
  dateTime: '',
  mealType: '',
  foodName: '',
  foodCategory: '',
  amount: 0,
  carbs: 0,
  protein: 0,
  fat: 0,
  calories: 0,
  note: ''
})

// 获取餐食类型名称
const getMealTypeName = (type) => {
  const mealTypes = {
    breakfast: '早餐',
    lunch: '午餐',
    dinner: '晚餐',
    snack: '加餐'
  }
  return mealTypes[type] || type
}

// 获取食物分类名称
const getFoodCategoryName = (type) => {
  const category = foodCategories.find(c => c.value === type)
  return category ? category.label : type
}

// 获取饮食记录数据
const fetchDietRecords = async () => {
  try {
    tableLoading.value = true
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      start_date: dateRange.value?.[0] ? format(dateRange.value[0], 'yyyy-MM-dd HH:mm:ss') : undefined,
      end_date: dateRange.value?.[1] ? format(dateRange.value[1], 'yyyy-MM-dd HH:mm:ss') : undefined,
      meal_type: filterMealType.value || undefined
    }
    
    const response = await dietApi.getDietRecords(params)

    // 后端返回的数据结构是 DietRecord[], food_items 在里面
    // 为了表格方便展示，这里做一个扁平化处理，假设每个记录只有一个食物
    dietRecords.value = response.data.data.map(record => {
      const foodItem = record.food_items?.[0] || {}
      return {
        id: record.id,
        dateTime: format(new Date(record.meal_time), 'yyyy-MM-dd HH:mm:ss'),
        mealType: record.meal_type,
        note: record.notes,
        foodName: foodItem.name,
        foodCategory: foodItem.category,
        amount: foodItem.amount,
        carbs: foodItem.carbs,
        protein: foodItem.protein,
        fat: foodItem.fat,
        calories: foodItem.calories,
      }
    })
    
    totalRecords.value = response.data.total
    
  } catch (error) {
    console.error('获取饮食记录失败:', error)
    if (error.message && error.message.includes('Network Error')) {
      ElMessage.error('网络错误，可能是CORS跨域问题，请检查后端服务是否正常运行')
    } else {
      ElMessage.error('获取饮食记录失败: ' + (error.response?.data?.detail || error.message))
    }
  } finally {
    tableLoading.value = false
  }
}

// 提交表单
const submitForm = async () => {
  if (!dietFormRef.value) return
  
  await dietFormRef.value.validate(async (valid) => {
    if (valid) {
      if (!user.value?.id) {
        ElMessage.error('无法获取用户信息，请重新登录')
        return
      }

      try {
        loading.value = true
        
        const payload = {
          user_id: user.value.id,
          meal_type: dietForm.mealType,
          meal_time: dietForm.dateTime,
          notes: dietForm.note,
          total_carbs: dietForm.carbs,
          total_calories: dietForm.calories,
          food_items: [
            {
              name: dietForm.foodName,
              category: dietForm.foodCategory,
              amount: dietForm.amount,
              carbs: dietForm.carbs,
              protein: dietForm.protein,
              fat: dietForm.fat,
              calories: dietForm.calories
            }
          ]
        }
        
        await dietApi.addDietRecord(payload)
        
        ElMessage.success('饮食记录保存成功')
        resetForm()
        fetchDietRecords()
      } catch (error) {
        console.error('保存饮食记录失败:', error)
        ElMessage.error('保存饮食记录失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        loading.value = false
      }
    }
  })
}

// 重置表单
const resetForm = () => {
  if (dietFormRef.value) {
    dietFormRef.value.resetFields()
    dietForm.dateTime = format(new Date(), 'yyyy-MM-dd HH:mm:ss')
  }
}

// 编辑记录
const editRecord = (row) => {
  Object.assign(editForm, row)
  dialogVisible.value = true
}

// 更新记录
const updateRecord = async () => {
  if (!editFormRef.value) return
  
  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        updateLoading.value = true
        
        const payload = {
          meal_type: editForm.mealType,
          meal_time: editForm.dateTime,
          notes: editForm.note,
          total_carbs: editForm.carbs,
          total_calories: editForm.calories,
          food_items: [
            {
              name: editForm.foodName,
              category: editForm.foodCategory,
              amount: editForm.amount,
              carbs: editForm.carbs,
              protein: editForm.protein,
              fat: editForm.fat,
              calories: editForm.calories
            }
          ]
        }
        
        await dietApi.updateDietRecord(editForm.id, payload)
        
        ElMessage.success('饮食记录更新成功')
        dialogVisible.value = false
        fetchDietRecords()
      } catch (error) {
        console.error('更新饮食记录失败:', error)
        if (error.response?.status === 404) {
          ElMessage.error('记录不存在，可能已被删除')
        } else {
          ElMessage.error('更新饮食记录失败: ' + (error.response?.data?.detail || error.message))
        }
      } finally {
        updateLoading.value = false
      }
    }
  })
}

// 删除记录
const deleteRecord = (row) => {
  ElMessageBox.confirm('确定要删除这条饮食记录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await dietApi.deleteDietRecord(row.id)
      ElMessage.success('饮食记录删除成功')
      fetchDietRecords()
    } catch (error) {
      console.error('删除饮食记录失败:', error)
      if (error.response?.status === 404) {
        ElMessage.error('记录不存在，可能已被删除')
        // 刷新列表
        fetchDietRecords()
      } else {
        ElMessage.error('删除饮食记录失败: ' + (error.response?.data?.detail || error.message))
      }
    }
  }).catch(() => {})
}

// 处理分页变化
const handlePageChange = (page) => {
  currentPage.value = page
  fetchDietRecords()
}

// 处理日期范围变化
const handleDateRangeChange = () => {
  currentPage.value = 1
  fetchDietRecords()
}

// 处理筛选条件变化
const handleFilterChange = () => {
  currentPage.value = 1
  fetchDietRecords()
}

// 组件挂载时获取数据
onMounted(() => {
  fetchDietRecords()
})
</script>

<style scoped>
.diet-container {
  padding: 20px;
}

.diet-card {
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

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style> 