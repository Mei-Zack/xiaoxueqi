<template>
  <div class="settings-container">
    <h1>账户设置</h1>
    
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>个人资料</span>
        </div>
      </template>
      
      <el-form :model="profileForm" :rules="profileRules" ref="profileFormRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="profileForm.username" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item label="姓名" prop="fullName">
          <el-input v-model="profileForm.fullName" placeholder="请输入姓名" />
        </el-form-item>
        
        <el-form-item label="手机号码" prop="phone">
          <el-input v-model="profileForm.phone" placeholder="请输入手机号码" />
        </el-form-item>
        
        <el-form-item label="出生日期" prop="birthDate">
          <el-date-picker
            v-model="profileForm.birthDate"
            type="date"
            placeholder="选择出生日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="profileForm.gender">
            <el-radio label="male">男</el-radio>
            <el-radio label="female">女</el-radio>
            <el-radio label="other">其他</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="updateProfile" :loading="profileLoading">保存个人资料</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>修改密码</span>
        </div>
      </template>
      
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
        <el-form-item label="当前密码" prop="currentPassword">
          <el-input v-model="passwordForm.currentPassword" type="password" placeholder="请输入当前密码" show-password />
        </el-form-item>
        
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" show-password />
        </el-form-item>
        
        <el-form-item label="确认新密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="updatePassword" :loading="passwordLoading">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>通知设置</span>
        </div>
      </template>
      
      <el-form :model="notificationForm" ref="notificationFormRef" label-width="100px">
        <el-form-item label="邮件通知">
          <el-switch v-model="notificationForm.emailEnabled" />
        </el-form-item>
        
        <el-form-item label="血糖提醒">
          <el-switch v-model="notificationForm.glucoseReminder" />
        </el-form-item>
        
        <el-form-item label="药物提醒">
          <el-switch v-model="notificationForm.medicationReminder" />
        </el-form-item>
        
        <el-form-item label="健康报告">
          <el-switch v-model="notificationForm.healthReport" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="updateNotificationSettings" :loading="notificationLoading">保存通知设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="settings-card danger-zone">
      <template #header>
        <div class="card-header">
          <span>危险操作</span>
        </div>
      </template>
      
      <div class="danger-actions">
        <div class="danger-action">
          <div class="danger-info">
            <h4>退出登录</h4>
            <p>退出当前账号的登录状态</p>
          </div>
          <el-button type="danger" @click="handleLogout">退出登录</el-button>
        </div>
        
        <div class="danger-action">
          <div class="danger-info">
            <h4>删除账户</h4>
            <p>删除您的账户将永久删除您的所有数据，此操作无法撤销。</p>
          </div>
          <el-button type="danger" @click="showDeleteAccountDialog">删除账户</el-button>
        </div>
      </div>
    </el-card>
    
    <!-- 删除账户确认对话框 -->
    <el-dialog
      v-model="deleteAccountDialogVisible"
      title="删除账户"
      width="500px"
    >
      <div class="delete-account-warning">
        <el-alert
          title="此操作将永久删除您的账户和所有相关数据，无法恢复！"
          type="error"
          :closable="false"
          show-icon
        />
      </div>
      
      <el-form :model="deleteAccountForm" :rules="deleteAccountRules" ref="deleteAccountFormRef" label-width="100px">
        <el-form-item label="密码" prop="password">
          <el-input v-model="deleteAccountForm.password" type="password" placeholder="请输入密码确认" show-password />
        </el-form-item>
        
        <el-form-item label="确认" prop="confirm">
          <el-checkbox v-model="deleteAccountForm.confirm">我确认要删除我的账户</el-checkbox>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="deleteAccountDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="deleteAccount" :loading="deleteAccountLoading">确认删除</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

// 表单引用
const profileFormRef = ref(null)
const passwordFormRef = ref(null)
const notificationFormRef = ref(null)
const deleteAccountFormRef = ref(null)

// 加载状态
const profileLoading = ref(false)
const passwordLoading = ref(false)
const notificationLoading = ref(false)
const deleteAccountLoading = ref(false)

// 个人资料表单
const profileForm = reactive({
  username: '',
  email: '',
  fullName: '',
  phone: '',
  birthDate: '',
  gender: ''
})

// 个人资料验证规则
const profileRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ]
}

// 密码表单
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 验证密码一致性
const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入新密码'))
  } else if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

// 密码验证规则
const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为 6 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 通知设置表单
const notificationForm = reactive({
  emailEnabled: true,
  glucoseReminder: true,
  medicationReminder: true,
  healthReport: true
})

// 删除账户对话框
const deleteAccountDialogVisible = ref(false)

// 删除账户表单
const deleteAccountForm = reactive({
  password: '',
  confirm: false
})

// 删除账户验证规则
const deleteAccountRules = {
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ],
  confirm: [
    { required: true, message: '请确认删除账户', trigger: 'change' },
    { type: 'boolean', enum: [true], message: '请确认删除账户', trigger: 'change' }
  ]
}

// 获取用户资料
const fetchUserProfile = async () => {
  try {
    // 这里应该调用后端API获取用户资料
    // const userData = await api.getUserProfile()
    
    // 模拟数据
    setTimeout(() => {
      const userData = {
        username: 'user123',
        email: 'user@example.com',
        fullName: '张三',
        phone: '13800138000',
        birthDate: '1990-01-01',
        gender: 'male'
      }
      
      // 填充表单
      Object.keys(profileForm).forEach(key => {
        if (userData[key] !== undefined) {
          profileForm[key] = userData[key]
        }
      })
    }, 300)
    
  } catch (error) {
    console.error('获取用户资料失败:', error)
    ElMessage.error('获取用户资料失败')
  }
}

// 获取通知设置
const fetchNotificationSettings = async () => {
  try {
    // 这里应该调用后端API获取通知设置
    // const settings = await api.getNotificationSettings()
    
    // 模拟数据
    setTimeout(() => {
      const settings = {
        emailEnabled: true,
        glucoseReminder: true,
        medicationReminder: false,
        healthReport: true
      }
      
      // 填充表单
      Object.keys(notificationForm).forEach(key => {
        if (settings[key] !== undefined) {
          notificationForm[key] = settings[key]
        }
      })
    }, 300)
    
  } catch (error) {
    console.error('获取通知设置失败:', error)
    ElMessage.error('获取通知设置失败')
  }
}

// 更新个人资料
const updateProfile = async () => {
  if (!profileFormRef.value) return
  
  await profileFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        profileLoading.value = true
        
        // 这里应该调用后端API更新个人资料
        // await api.updateUserProfile(profileForm)
        
        // 模拟更新成功
        setTimeout(() => {
          ElMessage.success('个人资料更新成功')
          profileLoading.value = false
        }, 500)
        
      } catch (error) {
        console.error('更新个人资料失败:', error)
        ElMessage.error('更新个人资料失败')
        profileLoading.value = false
      }
    }
  })
}

// 更新密码
const updatePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        passwordLoading.value = true
        
        // 这里应该调用后端API更新密码
        // await api.updatePassword(passwordForm)
        
        // 模拟更新成功
        setTimeout(() => {
          ElMessage.success('密码修改成功')
          passwordFormRef.value.resetFields()
          passwordLoading.value = false
        }, 500)
        
      } catch (error) {
        console.error('修改密码失败:', error)
        ElMessage.error('修改密码失败')
        passwordLoading.value = false
      }
    }
  })
}

// 更新通知设置
const updateNotificationSettings = async () => {
  try {
    notificationLoading.value = true
    
    // 这里应该调用后端API更新通知设置
    // await api.updateNotificationSettings(notificationForm)
    
    // 模拟更新成功
    setTimeout(() => {
      ElMessage.success('通知设置更新成功')
      notificationLoading.value = false
    }, 500)
    
  } catch (error) {
    console.error('更新通知设置失败:', error)
    ElMessage.error('更新通知设置失败')
    notificationLoading.value = false
  }
}

// 显示删除账户对话框
const showDeleteAccountDialog = () => {
  deleteAccountDialogVisible.value = true
  deleteAccountForm.password = ''
  deleteAccountForm.confirm = false
}

// 删除账户
const deleteAccount = async () => {
  if (!deleteAccountFormRef.value) return
  
  await deleteAccountFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        deleteAccountLoading.value = true
        
        // 这里应该调用后端API删除账户
        // await api.deleteAccount(deleteAccountForm.password)
        
        // 模拟删除成功
        setTimeout(() => {
          ElMessage.success('账户已删除')
          userStore.logout()
          router.push('/login')
        }, 1000)
        
      } catch (error) {
        console.error('删除账户失败:', error)
        ElMessage.error('删除账户失败，请确认密码是否正确')
        deleteAccountLoading.value = false
      }
    }
  })
}

// 退出登录
const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout()
  }).catch(() => {})
}

// 组件挂载时获取数据
onMounted(() => {
  fetchUserProfile()
  fetchNotificationSettings()
})
</script>

<style scoped>
.settings-container {
  padding: 20px;
}

.settings-card {
  margin-bottom: 20px;
}

.danger-zone {
  border: 1px solid #f56c6c;
}

.danger-zone .el-card__header {
  background-color: #fef0f0;
}

.danger-actions {
  padding: 10px 0;
}

.danger-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}

.danger-action:last-child {
  border-bottom: none;
}

.danger-info h4 {
  margin: 0 0 5px;
  color: #f56c6c;
}

.danger-info p {
  margin: 0;
  font-size: 14px;
  color: #606266;
}

.delete-account-warning {
  margin-bottom: 20px;
}
</style> 