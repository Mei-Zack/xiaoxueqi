import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import router from '../router'
import { ElMessage } from 'element-plus'
import { userApi, apiClient } from '../api'

// 内置测试账号
const BUILT_IN_ACCOUNTS = [
  {
    username: 'test@example.com',
    password: 'test123',
    userData: {
      id: 1,
      username: 'test',
      email: 'test@example.com',
      name: '测试用户',
      is_active: true,
      is_admin: true
    }
  }
]

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const user = ref<any>(JSON.parse(localStorage.getItem('user') || '{}'))
  const useLocalAuth = ref(false) // 恢复为false，始终使用后端API
  
  // 计算属性
  const isAuthenticated = computed(() => {
    // 检查token和user.id是否都存在
    return !!token.value && !!user.value.id
  })
  const userFullName = computed(() => user.value?.name || '用户')
  
  // 方法
  async function login(email: string, password: string) {
    try {
      // 添加内置账号支持（仅用于开发和测试）
      if (useLocalAuth.value && (
          (email === 'admin@example.com' && password === 'admin') ||
          (email === 'test@example.com' && password === 'test123')
      )) {
        // 使用内置账号登录
        const mockToken = `mock_token_${Date.now()}`
        token.value = mockToken
        localStorage.setItem('token', mockToken)
        
        const userData = email === 'admin@example.com' ? {
          id: 'admin-id',
          email: 'admin@example.com',
          name: '系统管理员',
          is_active: true,
          is_superuser: true
        } : {
          id: 'test-id',
          email: 'test@example.com',
          name: '测试用户',
          is_active: true,
          is_superuser: false
        }
        
        user.value = userData
        localStorage.setItem('user', JSON.stringify(userData))
        
        console.log('登录成功，用户信息:', userData)
        ElMessage.success('登录成功')
        
        // 如果有重定向，则导航到重定向页面
        const redirectPath = router.currentRoute.value.query.redirect as string
        router.push(redirectPath || '/dashboard')
        
        return true
      }
      
      // 如果不是内置账号或本地认证禁用，尝试调用后端API登录
      const response = await userApi.login(email, password)
      
      const data = response.data
      token.value = data.access_token
      localStorage.setItem('token', data.access_token)
      
      // 存储用户基本信息
      const userId = data.user_id || data.id
      localStorage.setItem('user_id', userId)
      localStorage.setItem('email', email)
      
      // 直接构造用户对象并保存，确保有id字段
      const userObj = {
        id: userId,
        email: email,
        name: data.name || '用户' + email.split('@')[0],
        is_active: true
      }
      
      user.value = userObj
      localStorage.setItem('user', JSON.stringify(userObj))
      
      console.log('登录成功，用户信息:', userObj)
      ElMessage.success('登录成功')
      
      // 如果有重定向，则导航到重定向页面
      const redirectPath = router.currentRoute.value.query.redirect as string
      router.push(redirectPath || '/dashboard')
      
      return true
    } catch (error: any) {
      console.error('登录失败:', error)
      ElMessage.error(error.response?.data?.detail || '登录失败：用户名或密码错误')
      return false
    }
  }
  
  async function register(userData: any) {
    try {
      if (useLocalAuth.value) {
        // 本地模拟注册成功
        ElMessage.success('注册成功，请登录')
        router.push('/login')
        return true
      }
      
      await userApi.register(userData)
      ElMessage.success('注册成功，请登录')
      router.push('/login')
      return true
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '注册失败')
      return false
    }
  }
  
  async function fetchUserProfile() {
    try {
      // 如果没有token，直接返回
      if (!token.value) {
        return null
      }
      
      // 使用登录时返回的基本信息，不立即请求详细资料
      const basicUserInfo = {
        id: user.value.id || localStorage.getItem('user_id'),
        email: user.value.email || localStorage.getItem('email'),
        name: user.value.name || '用户' + (localStorage.getItem('email') || '').split('@')[0],
        is_active: true
      }
      
      // 确保有用户ID
      if (!basicUserInfo.id) {
        // 如果没有用户ID，清除token并返回null
        token.value = ''
        user.value = {}
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        return null
      }
      
      user.value = basicUserInfo
      localStorage.setItem('user', JSON.stringify(basicUserInfo))
      
      return user.value
    } catch (error) {
      console.error('获取用户信息失败', error)
      return null
    }
  }
  
  function logout() {
    token.value = ''
    user.value = {}
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('user_id')
    localStorage.removeItem('email')
    router.push('/login')
    ElMessage.success('已退出登录')
  }
  
  async function updateProfile(userData: any) {
    try {
      if (useLocalAuth.value) {
        // 本地模拟更新成功
        user.value = { ...user.value, ...userData }
        localStorage.setItem('user', JSON.stringify(user.value))
        ElMessage.success('个人信息更新成功（本地模式）')
        return true
      }
      
      const response = await userApi.updateProfile(userData)
      
      user.value = { ...user.value, ...response.data }
      localStorage.setItem('user', JSON.stringify(user.value))
      ElMessage.success('个人信息更新成功')
      return true
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '更新失败')
      return false
    }
  }
  
  // 切换认证模式
  function toggleAuthMode(useLocal: boolean) {
    useLocalAuth.value = useLocal
    return useLocalAuth.value
  }
  
  // 初始化函数，确保用户数据一致性
  function initialize() {
    // 如果有token但没有完整的用户信息，尝试获取
    if (token.value && (!user.value || !user.value.id)) {
      fetchUserProfile()
    }
  }
  
  // 设置全局axios默认值
  axios.defaults.baseURL = 'http://localhost:8000'
  axios.interceptors.request.use(config => {
    if (token.value) {
      config.headers.Authorization = `Bearer ${token.value}`
    }
    return config
  })
  
  // 自动初始化
  initialize()
  
  // 为apiClient设置拦截器
  apiClient.interceptors.response.use(
    response => response,
    error => {
      if (error.response?.status === 401) {
        console.error('认证失败，自动登出', error)
        logout()
      }
      return Promise.reject(error)
    }
  )
  
  return {
    token,
    user,
    isAuthenticated,
    userFullName,
    useLocalAuth,
    login,
    register,
    fetchUserProfile,
    logout,
    updateProfile,
    toggleAuthMode,
    initialize
  }
}) 