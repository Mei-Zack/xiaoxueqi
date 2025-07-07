<template>
  <div class="glucose-record-container">
    <el-card class="glucose-record-card">
      <template #header>
        <div class="card-header">
          <h2>记录血糖</h2>
        </div>
      </template>
      
      <el-form
        ref="glucoseFormRef"
        :model="glucoseForm"
        label-width="100px"
        @submit.prevent="submitGlucoseRecord"
      >
        <el-form-item label="血糖值" prop="value">
          <el-input-number
            v-model="glucoseForm.value"
            :min="1"
            :max="30"
            :precision="1"
            :step="0.1"
            controls-position="right"
            style="width: 100%"
          />
          <span class="unit-label">mmol/L</span>
        </el-form-item>
        
        <el-form-item label="测量时间" prop="measured_at">
          <el-date-picker
            v-model="glucoseForm.measured_at"
            type="datetime"
            placeholder="选择日期时间"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="测量类型" prop="measurement_time">
          <el-select
            v-model="glucoseForm.measurement_time"
            placeholder="请选择测量类型"
            style="width: 100%"
          >
            <el-option label="早餐前" value="BEFORE_BREAKFAST" />
            <el-option label="早餐后" value="AFTER_BREAKFAST" />
            <el-option label="午餐前" value="BEFORE_LUNCH" />
            <el-option label="午餐后" value="AFTER_LUNCH" />
            <el-option label="晚餐前" value="BEFORE_DINNER" />
            <el-option label="晚餐后" value="AFTER_DINNER" />
            <el-option label="睡前" value="BEFORE_SLEEP" />
            <el-option label="半夜" value="MIDNIGHT" />
            <el-option label="其他" value="OTHER" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="测量方法" prop="measurement_method">
          <el-select
            v-model="glucoseForm.measurement_method"
            placeholder="请选择测量方法"
            style="width: 100%"
          >
            <el-option label="指尖采血" value="FINGER_STICK" />
            <el-option label="连续监测" value="CONTINUOUS_MONITOR" />
            <el-option label="实验室检验" value="LAB_TEST" />
            <el-option label="其他" value="OTHER" />
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
          <el-button type="primary" native-type="submit" :loading="submitting">保存记录</el-button>
          <el-button @click="resetForm">重置</el-button>
          <el-button @click="goBack">返回</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage } from "element-plus";
import dayjs from "dayjs";
import { useRouter } from "vue-router";
import { glucoseApi } from "../api/index";
import { useUserStore } from "../stores/user";

const router = useRouter();
const glucoseFormRef = ref();
const submitting = ref(false);
const userStore = useUserStore();

// 初始化表单数据
const glucoseForm = reactive({
  value: 5.6,
  measured_at: dayjs().format("YYYY-MM-DD HH:mm:ss"),
  measurement_time: "BEFORE_BREAKFAST",
  measurement_method: "FINGER_STICK",
  notes: ""
});

// 提交表单
const submitGlucoseRecord = async () => {
  submitting.value = true;
  try {
    // 检查用户ID是否存在
    if (!userStore.user || !userStore.user.id) {
      ElMessage.error('用户未登录或用户ID不存在');
      submitting.value = false;
      return;
    }
    
    console.log('发送的血糖数据:', {
      user_id: userStore.user.id,
      value: glucoseForm.value,
      measured_at: glucoseForm.measured_at,
      measurement_time: glucoseForm.measurement_time,
      measurement_method: glucoseForm.measurement_method,
      notes: glucoseForm.notes
    });
    
    const response = await glucoseApi.addGlucoseRecord({
      user_id: userStore.user.id,
      value: glucoseForm.value,
      measured_at: glucoseForm.measured_at,
      measurement_time: glucoseForm.measurement_time,
      measurement_method: glucoseForm.measurement_method,
      notes: glucoseForm.notes
    });
    
    console.log('保存血糖记录响应:', response);
    
    // 检查血糖值是否异常
    const highThreshold = 7.8; // 高血糖阈值
    const lowThreshold = 3.9; // 低血糖阈值
    
    if (glucoseForm.value > highThreshold) {
      ElMessage.warning({
        message: `检测到高血糖值 ${glucoseForm.value} mmol/L，请注意控制饮食和监测血糖`,
        duration: 5000
      });
    } else if (glucoseForm.value < lowThreshold) {
      ElMessage.warning({
        message: `检测到低血糖值 ${glucoseForm.value} mmol/L，请及时补充碳水化合物`,
        duration: 5000
      });
    }
    
    ElMessage.success("血糖记录保存成功");
    resetForm();
    
    // 可选：保存后返回仪表盘
    // router.push("/dashboard");
  } catch (error) {
    console.error("保存血糖记录失败", error);
    
    // 提供更详细的错误信息
    if (error.response) {
      console.error('错误响应数据:', error.response.data);
      
      // 显示详细的验证错误信息
      if (error.response.data && error.response.data.detail) {
        let errorMsg = '数据验证失败: ';
        
        if (Array.isArray(error.response.data.detail)) {
          errorMsg += error.response.data.detail.map(err => `${err.loc.join('.')}:${err.msg}`).join('; ');
        } else {
          errorMsg += error.response.data.detail;
        }
        
        ElMessage.error(errorMsg);
        return;
      }
    }
    
    ElMessage.error("保存血糖记录失败");
  } finally {
    submitting.value = false;
  }
};

// 重置表单
const resetForm = () => {
  if (glucoseFormRef.value) {
    glucoseFormRef.value.resetFields();
  }
  
  // 重置为当前时间
  glucoseForm.measured_at = dayjs().format("YYYY-MM-DD HH:mm:ss");
};

// 返回上一页
const goBack = () => {
  router.back();
};

// 组件挂载时设置当前时间
onMounted(() => {
  glucoseForm.measured_at = dayjs().format("YYYY-MM-DD HH:mm:ss");
});
</script>

<style scoped>
.glucose-record-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.glucose-record-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #409eff;
}

.unit-label {
  margin-left: 8px;
  color: #606266;
}

@media (max-width: 768px) {
  .glucose-record-container {
    padding: 10px;
  }
}
</style> 