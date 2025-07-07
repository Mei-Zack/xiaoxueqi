import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

// 路由懒加载
const LoginView = () => import('../views/LoginView.vue')
const RegisterView = () => import('../views/RegisterView.vue')
const DashboardView = () => import('../views/DashboardView.vue')
const HealthView = () => import('../views/HealthView.vue')
const GlucoseView = () => import('../views/GlucoseView.vue')
const DietView = () => import('../views/DietView.vue')
const AssistantView = () => import('../views/AssistantView.vue')
const KnowledgeView = () => import('../views/KnowledgeView.vue')
const SettingsView = () => import('../views/SettingsView.vue')
const NotFoundView = () => import('../views/NotFoundView.vue')
const GlucoseRecordView = () => import('../views/GlucoseRecordView.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { requiresAuth: false }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/health',
      name: 'health',
      component: HealthView,
      meta: { requiresAuth: true }
    },
    {
      path: '/glucose',
      name: 'glucose',
      component: GlucoseView,
      meta: { requiresAuth: true }
    },
    {
      path: '/diet',
      name: 'diet',
      component: DietView,
      meta: { requiresAuth: true }
    },
    {
      path: '/assistant',
      name: 'assistant',
      component: AssistantView,
      meta: { requiresAuth: true }
    },
    {
      path: '/knowledge',
      name: 'knowledge',
      component: KnowledgeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/glucose-record',
      name: 'glucose-record',
      component: GlucoseRecordView,
      meta: { requiresAuth: true }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundView
    }
  ]
})

// 全局导航守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.meta.requiresAuth !== false
  
  console.log('路由导航:', {
    from: from.path,
    to: to.path,
    requiresAuth,
    isAuthenticated: userStore.isAuthenticated,
    token: !!userStore.token,
    userId: userStore.user?.id
  })

  // 如果不需要认证，直接通过
  if (!requiresAuth) {
    next()
    return
  }
  
  // 如果需要认证但用户未登录
  if (!userStore.isAuthenticated) {
    console.log('需要认证但用户未登录，重定向到登录页')
    next({ 
      name: 'login', 
      query: { redirect: to.fullPath },
      replace: true 
    })
    return
  }
  
  // 如果用户已登录，允许访问
  next()
})

export default router 