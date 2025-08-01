<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <!-- 全局顶部导航栏 -->
      <div v-if="isAuthenticated" class="global-header">
        <div class="logo">糖尿病健康助理</div>
        <div class="header-actions">
          <span class="welcome-text">欢迎，{{ userFullName }}</span>
          <el-button type="danger" size="small" @click="handleLogout">退出登录</el-button>
        </div>
      </div>
      
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>

      <!-- Stagewise工具栏 (仅在开发环境中显示) -->
      <client-only v-if="isDevelopment">
        <stagewise-toolbar :config="stagwiseConfig" />
      </client-only>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { ElConfigProvider, ElMessageBox } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { useUserStore } from './stores/user'
import { computed, ref } from 'vue'
import { StagewiseToolbar } from '@stagewise/toolbar-vue'
import VuePlugin from '@stagewise-plugins/vue'
import ClientOnly from './components/ClientOnly.vue'

const userStore = useUserStore()
const isAuthenticated = computed(() => userStore.isAuthenticated)
const userFullName = computed(() => userStore.userFullName)

// 检测是否为开发环境
// @ts-ignore - Vite特定的环境变量
const isDevelopment = process.env.NODE_ENV !== 'production'

// Stagewise配置
const stagwiseConfig = {
  plugins: [VuePlugin]
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout()
  }).catch(() => {})
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.global-header {
  background-color: #304156;
  color: white;
  padding: 0 20px;
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12);
}

.logo {
  font-size: 18px;
  font-weight: bold;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.welcome-text {
  font-size: 14px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style> 