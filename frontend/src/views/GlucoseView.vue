<template>
  <div class="glucose-container">
    <el-card class="glucose-form-card">
      <template #header>
        <div class="card-header">
          <h3>记录血糖</h3>
        </div>
      </template>
      
      <el-form
        ref="glucoseFormRef"
        :model="glucoseForm"
        label-width="100px"
        @submit.prevent="submitGlucoseRecord"
      >
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12">
            <el-form-item label="血糖值" prop="value">
              <el-input-number
                v-model="glucoseForm.value"
                :min="1"
                :max="30"
                :precision="1"
                :step="0.1"
                controls-position="right"
              />
              <span class="unit-label">mmol/L</span>
            </el-form-item>
          </el-col>
          
          <el-col :xs="24" :sm="12">
            <el-form-item label="测量时间" prop="measured_at">
              <el-date-picker
                v-model="glucoseForm.measured_at"
                type="datetime"
                placeholder="选择日期和时间"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="测量类型" prop="measurement_time">
          <el-select
            v-model="glucoseForm.measurement_time"
            placeholder="请选择测量类型"
          >
            <el-option label="早餐前" value="before_breakfast" />
            <el-option label="早餐后" value="after_breakfast" />
            <el-option label="午餐前" value="before_lunch" />
            <el-option label="午餐后" value="after_lunch" />
            <el-option label="晚餐前" value="before_dinner" />
            <el-option label="晚餐后" value="after_dinner" />
            <el-option label="睡前" value="before_sleep" />
            <el-option label="半夜" value="midnight" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="测量方法" prop="measurement_method">
          <el-select
            v-model="glucoseForm.measurement_method"
            placeholder="请选择测量方法"
          >
            <el-option label="指尖采血" value="finger_stick" />
            <el-option label="连续监测" value="continuous_monitor" />
            <el-option label="实验室检验" value="lab_test" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="备注">
          <el-input
            v-model="glucoseForm.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息（可选）"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="submitting"
            >保存记录</el-button
          >
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="glucose-table-card">
      <template #header>
        <div class="card-header">
          <h3>历史记录</h3>
          <div class="header-actions">
            <el-select v-model="filterType" placeholder="筛选类型" size="small">
              <el-option label="全部" value="" />
              <el-option label="早餐前" value="before_breakfast" />
              <el-option label="早餐后" value="after_breakfast" />
              <el-option label="午餐前" value="before_lunch" />
              <el-option label="午餐后" value="after_lunch" />
              <el-option label="晚餐前" value="before_dinner" />
              <el-option label="晚餐后" value="after_dinner" />
              <el-option label="睡前" value="before_sleep" />
              <el-option label="半夜" value="midnight" />
              <el-option label="其他" value="other" />
            </el-select>
          </div>
        </div>
      </template>
      
      <el-table
        v-loading="loading"
        :data="filteredGlucoseRecords"
        stripe
        style="width: 100%"
      >
        <el-table-column
          prop="measured_at"
          label="测量时间"
          sortable
          width="180"
        >
          <template #default="scope">
            {{ formatDateTime(scope.row.measured_at) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="value" label="血糖值" sortable width="120">
          <template #default="scope">
            <span :class="getGlucoseValueClass(scope.row.value)">
              {{ scope.row.value }} mmol/L
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="measurement_time" label="测量类型" width="120">
          <template #default="scope">
            {{ getMeasurementTimeText(scope.row.measurement_time) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="notes" label="备注" />
        
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button
              size="small"
              type="primary"
              plain
              @click="editRecord(scope.row)"
            >
              编辑
            </el-button>
            <el-button
              size="small"
              type="danger"
              plain
              @click="deleteRecord(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import dayjs from "dayjs";
import { glucoseApi } from "../api/index";
import { useUserStore } from "../stores/user";

// 表单引用
const glucoseFormRef = ref();

// 加载状态
const loading = ref(false);
const submitting = ref(false);

// 筛选
const filterType = ref("");

// 血糖记录表单
const glucoseForm = reactive({
  id: "",
  value: 5.6,
  measured_at: new Date(),
  measurement_time: "before_breakfast",
  measurement_method: "finger_stick",
  notes: "",
  user_id: "",
});

// 血糖记录数据
const glucoseRecords = ref([]);

// 获取用户store
const userStore = useUserStore();

// 根据筛选条件过滤血糖记录
const filteredGlucoseRecords = computed(() => {
  let result = glucoseRecords.value;

  // 按类型筛选
  if (filterType.value) {
    result = result.filter(
      (record) => record.measurement_time === filterType.value
    );
  }

  // 按照时间降序排序
  result = [...result].sort((a, b) => {
    return dayjs(b.measured_at).valueOf() - dayjs(a.measured_at).valueOf();
  });

  return result;
});

onMounted(async () => {
  loading.value = true;
  try {
    // 设置用户ID
    glucoseForm.user_id = userStore.user?.id || "";

    // 从API获取血糖记录
    const response = await glucoseApi.getGlucoseRecords();
    glucoseRecords.value = response.data || [];
  } catch (error) {
    console.error("获取血糖记录失败", error);
    ElMessage.error("获取血糖记录失败");
  } finally {
    loading.value = false;
  }
});

// 提交血糖记录
const submitGlucoseRecord = async () => {
  submitting.value = true;
  try {
    // 确保表单有用户ID
    if (!glucoseForm.user_id) {
      glucoseForm.user_id = userStore.user?.id || "";
    }

    // 如果有ID，则是编辑现有记录
    if (glucoseForm.id) {
      // 调用API更新记录
      await glucoseApi.updateGlucoseRecord(glucoseForm.id, {
        value: glucoseForm.value,
        measurement_time: glucoseForm.measurement_time,
        measurement_method: glucoseForm.measurement_method,
        measured_at: glucoseForm.measured_at,
        notes: glucoseForm.notes,
      });

      ElMessage.success("血糖记录更新成功");
    } else {
      // 调用API添加记录
      await glucoseApi.addGlucoseRecord({
        user_id: glucoseForm.user_id,
        value: glucoseForm.value,
        measurement_time: glucoseForm.measurement_time,
        measurement_method: glucoseForm.measurement_method,
        measured_at: glucoseForm.measured_at,
        notes: glucoseForm.notes,
      });

      ElMessage.success("血糖记录添加成功");
    }

    // 重新获取记录
    const response = await glucoseApi.getGlucoseRecords();
    glucoseRecords.value = response.data || [];
    
    // 重置表单
    resetForm();
  } catch (error) {
    console.error("保存血糖记录失败", error);
    ElMessage.error("保存血糖记录失败");
  } finally {
    submitting.value = false;
  }
};

// 重置表单
const resetForm = () => {
  glucoseForm.id = "";
  glucoseForm.value = 5.6;
  glucoseForm.measured_at = new Date();
  glucoseForm.measurement_time = "before_breakfast";
  glucoseForm.measurement_method = "finger_stick";
  glucoseForm.notes = "";
};

// 编辑记录
const editRecord = (record) => {
  glucoseForm.id = record.id;
  glucoseForm.value = record.value;
  glucoseForm.measured_at = dayjs(record.measured_at).toDate();
  glucoseForm.measurement_time = record.measurement_time;
  glucoseForm.measurement_method = record.measurement_method;
  glucoseForm.notes = record.notes;
  
  // 滚动到表单
  document
    .querySelector(".glucose-form-card")
    ?.scrollIntoView({ behavior: "smooth" });
};

// 删除记录
const deleteRecord = (record) => {
  ElMessageBox.confirm("确定要删除这条血糖记录吗？", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      try {
        // 调用API删除记录
        await glucoseApi.deleteGlucoseRecord(record.id);

        // 重新获取记录列表
        const response = await glucoseApi.getGlucoseRecords();
        glucoseRecords.value = response.data || [];

        ElMessage.success("血糖记录删除成功");
      } catch (error) {
        console.error("删除血糖记录失败", error);
        ElMessage.error("删除血糖记录失败");
      }
    })
    .catch(() => {});
};

// 格式化日期时间
const formatDateTime = (dateStr) => {
  return dayjs(dateStr).format("YYYY-MM-DD HH:mm");
};

// 获取测量类型文本
const getMeasurementTimeText = (type) => {
  const typeMap = {
    before_breakfast: "早餐前",
    after_breakfast: "早餐后",
    before_lunch: "午餐前",
    after_lunch: "午餐后",
    before_dinner: "晚餐前",
    after_dinner: "晚餐后",
    before_sleep: "睡前",
    midnight: "半夜",
    other: "其他",
  };
  return typeMap[type] || type;
};

// 获取血糖值对应的CSS类
const getGlucoseValueClass = (value) => {
  if (value < 3.9) return "glucose-low";
  if (value > 10.0) return "glucose-high";
  return "glucose-normal";
};
</script>

<style scoped>
.glucose-container {
  padding: 20px;
}

.glucose-form-card {
  margin-bottom: 20px;
}

.glucose-table-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
}

.unit-label {
  margin-left: 8px;
  color: #606266;
}

.glucose-high {
  color: #f56c6c;
  font-weight: bold;
}

.glucose-low {
  color: #e6a23c;
  font-weight: bold;
}

.glucose-normal {
  color: #67c23a;
}

.header-actions {
  display: flex;
  gap: 10px;
}
</style> 
