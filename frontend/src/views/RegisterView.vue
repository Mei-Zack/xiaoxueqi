<template>
  <div class="register-container">
    <div class="background-animation"></div>
    <div class="register-card glass-effect">
      <div class="register-header">
        <h2>创建您的专属健康助理账号</h2>
        <p>仅需几步，即可开启智能健康管理</p>
      </div>

      <el-form
        ref="registerForm"
        :model="registerData"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleRegister"
        class="register-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="registerData.username"
            placeholder="用户名"
            prefix-icon="el-icon-user"
            size="large"
          />
        </el-form-item>
        <el-form-item prop="email">
          <el-input
            v-model="registerData.email"
            placeholder="邮箱"
            type="email"
            prefix-icon="el-icon-message"
            size="large"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="registerData.password"
            type="password"
            placeholder="设置密码"
            show-password
            prefix-icon="el-icon-lock"
            size="large"
          />
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="registerData.confirmPassword"
            type="password"
            placeholder="确认密码"
            show-password
            prefix-icon="el-icon-circle-check"
            size="large"
          />
        </el-form-item>
        <el-button
          type="primary"
          native-type="submit"
          :loading="loading"
          class="register-button"
          size="large"
        >
          {{ loading ? '注册中...' : '立即注册' }}
        </el-button>
        <div class="login-link">
          已有账号？<router-link to="/login">立即登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)

const registerData = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validatePass = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else {
    if (registerData.confirmPassword !== '') {
      registerForm.value.validateField('confirmPassword')
    }
    callback()
  }
}

const validateConfirmPass = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerData.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = reactive({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为 6 个字符', trigger: 'blur' },
    { validator: validatePass, trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPass, trigger: 'blur' }
  ]
})

const registerForm = ref()

const handleRegister = async () => {
  if (!registerForm.value) return;
  await registerForm.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        loading.value = true
        await userStore.register(registerData)
        ElMessage.success('注册成功！即将跳转到登录页面...')
        setTimeout(() => {
          router.push('/login')
        }, 1500)
      } catch (error: any) {
        console.error('注册失败:', error)
        ElMessage.error(error.message || '注册失败，请稍后重试')
      } finally {
        loading.value = false
      }
    }
  });
}
</script>

<style scoped>
@keyframes gradient-animation {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 64px); /* Subtract header height */
  position: relative;
  overflow: hidden;
}

.background-animation {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(-45deg, #161b22, #0d1117, #1a202c, #2d3748);
  background-size: 400% 400%;
  animation: gradient-animation 15s ease infinite;
  z-index: 0;
}

.register-card.glass-effect {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 450px;
  padding: 40px;
  background: rgba(22, 27, 34, 0.7);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  color: #e6edf3;
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-header h2 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.register-header p {
  color: #c9d1d9;
  font-size: 14px;
}

.register-form .el-form-item {
  margin-bottom: 25px;
}

:deep(.el-input__wrapper) {
  background-color: rgba(33, 41, 54, 0.7) !important;
  border: 1px solid #30363d !important;
  border-radius: 8px !important;
  box-shadow: none !important;
}

:deep(.el-input__inner) {
  color: #e6edf3 !important;
}

:deep(.el-input__inner:-webkit-autofill) {
  -webkit-box-shadow: 0 0 0 1000px rgba(33, 41, 54, 0.9) inset !important;
  -webkit-text-fill-color: #e6edf3 !important;
}

:deep(.el-input__prefix .el-icon) {
  color: #8b949e;
}

.register-button {
  width: 100%;
  font-weight: 600;
  border: none;
  background: linear-gradient(to right, #58a6ff, #388bfd);
  transition: all 0.3s ease;
  letter-spacing: 1px;
  margin-top: 10px;
}
.register-button:hover {
  opacity: 0.9;
  box-shadow: 0 0 15px rgba(56, 139, 253, 0.5);
}

.login-link {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #8b949e;
}
.login-link a {
  color: #58a6ff;
  text-decoration: none;
  font-weight: 600;
}
.login-link a:hover {
  text-decoration: underline;
}
</style> 