<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h2>糖尿病智能健康助理</h2>
        <p>登录您的账号</p>
      </div>
      
      <el-alert
        title="管理员账号信息"
        type="info"
        description="您可以使用以下账号进行登录：邮箱：admin@example.com，密码：admin123"
        :closable="false"
        class="test-account-alert"
      />
      
      <el-form
        ref="loginForm"
        :model="loginData"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="loginData.email"
            placeholder="请输入邮箱"
            type="email"
            prefix-icon="el-icon-message"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginData.password"
            placeholder="请输入密码"
            type="password"
            prefix-icon="el-icon-lock"
            show-password
          />
        </el-form-item>
        
        <div class="login-options">
          <el-checkbox v-model="loginData.remember">记住我</el-checkbox>
          <el-link underline="hover" type="primary">忘记密码?</el-link>
        </div>
        
        <el-button
          type="primary"
          native-type="submit"
          :loading="loading"
          class="login-button"
        >
          登录
        </el-button>
        
        <div class="register-link">
          还没有账号? <router-link to="/register">立即注册</router-link>
        </div>
        
        <div class="test-account-tip">
          <el-button text type="primary" @click="fillAdminAccount">
            填入管理员账号
          </el-button>
          <el-button text type="primary" @click="fillTestAccount">
            填入测试账号
          </el-button>
        </div>

        <div v-if="debugMode" class="debug-actions">
          <h4>调试选项</h4>
          <el-button size="small" type="warning" @click="checkAuth">
            检查认证状态
          </el-button>
          <el-button size="small" type="warning" @click="clearAuth">
            清除认证信息
          </el-button>
          <el-button size="small" type="warning" @click="goToDashboard">
            直接前往仪表盘
          </el-button>
        </div>
        
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()
const loading = ref(false)
const debugMode = ref(true) // 启用调试模式，方便排查问题

const loginData = reactive({
  email: '',
  password: '',
  remember: false
})

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 4, message: '密码长度不能少于4个字符', trigger: 'blur' }
  ]
}

const loginForm = ref()

onMounted(() => {
  // 如果用户已登录，直接跳转到首页或重定向页面
  console.log('登录页面加载，认证状态:', userStore.isAuthenticated)
  if (userStore.isAuthenticated) {
    const redirectPath = route.query.redirect as string
    router.push(redirectPath || '/dashboard')
  }
})

const handleLogin = async () => {
  if (!loginForm.value) return
  
  await loginForm.value.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true
      try {
        console.log('尝试登录:', loginData.email)
        const success = await userStore.login(loginData.email, loginData.password)
        if (!success) {
          ElMessage.error('登录失败，请检查您的邮箱和密码')
        } else {
          console.log('登录成功，用户信息:', userStore.user)
        }
      } catch (error) {
        console.error('登录失败', error)
        ElMessage.error('登录失败，请检查您的邮箱和密码')
      } finally {
        loading.value = false
      }
    } else {
      ElMessage.warning('请填写正确的登录信息')
      return false
    }
  })
}

// 填入管理员账号
const fillAdminAccount = () => {
  loginData.email = 'admin@example.com'
  loginData.password = 'admin123'
}

// 填入测试账号
const fillTestAccount = () => {
  loginData.email = 'test@example.com'
  loginData.password = 'test123'
}

// 调试功能：检查认证状态
const checkAuth = () => {
  console.log('当前认证状态:', {
    isAuthenticated: userStore.isAuthenticated,
    token: userStore.token ? '已设置' : '未设置',
    user: userStore.user
  })
  ElMessage.info(`认证状态: ${userStore.isAuthenticated ? '已登录' : '未登录'}`)
}

// 调试功能：清除认证信息
const clearAuth = () => {
  userStore.logout()
  ElMessage.success('已清除认证信息')
}

// 调试功能：直接前往仪表盘
const goToDashboard = () => {
  router.push('/dashboard')
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--background-color);
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-header h2 {
  font-size: 1.8rem;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.login-header p {
  color: var(--text-color-secondary);
  font-size: 1rem;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.login-button {
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
  margin-bottom: 1rem;
}

.register-link {
  text-align: center;
  font-size: 0.9rem;
  color: var(--text-color-secondary);
  margin-bottom: 1rem;
}

.register-link a {
  color: var(--primary-color);
  text-decoration: none;
}

.test-account-alert {
  margin-bottom: 1.5rem;
}

.test-account-tip {
  margin-top: 0.5rem;
  text-align: center;
}

.debug-actions {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px dashed #ddd;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.debug-actions h4 {
  color: #666;
  margin-bottom: 0.5rem;
  text-align: center;
}
</style> 