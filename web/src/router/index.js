import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import SimpleLayout from '@/layout/SimpleLayout.vue'
import Dashboard from '@/views/Dashboard.vue'
import Records from '@/views/Records.vue'
import SimpleQuery from '@/views/SimpleQuery.vue'
import BatchInput from '@/views/BatchInput.vue'
import DataAnalysis from '@/views/DataAnalysis.vue'
import Alerts from '@/views/Alerts.vue'
import AIChat from '@/views/AIChat.vue'
import EnhancedAnimatedLogin from '@/views/login/EnhancedAnimatedLogin.vue'
import Register from '@/views/login/Register.vue'
import ForgotPassword from '@/views/login/ForgotPassword.vue'
import ResetPassword from '@/views/login/ResetPassword.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/enhanced-login',
      name: 'EnhancedAnimatedLogin',
      component: EnhancedAnimatedLogin,
      meta: { title: '增强动画登录', requiresAuth: false }
    },
    {
      path: '/register',
      name: 'Register',
      component: Register,
      meta: { title: '注册', requiresAuth: false }
    },
    {
      path: '/forgot-password',
      name: 'ForgotPassword',
      component: ForgotPassword,
      meta: { title: '忘记密码', requiresAuth: false }
    },
    {
      path: '/reset-password',
      name: 'ResetPassword',
      component: ResetPassword,
      meta: { title: '重置密码', requiresAuth: false }
    },
    {
      path: '/',
      component: SimpleLayout,
      children: [
        {
          path: '/',
          redirect: '/dashboard'
        },
        {
          path: '/dashboard',
          name: 'Dashboard',
          component: Dashboard,
          meta: { title: '主界面', requiresAuth: true }
        },
        {
          path: '/records',
          name: 'Records',
          component: Records,
          meta: { title: '数据查看', requiresAuth: true }
        },
        {
          path: '/batch-input',
          name: 'BatchInput',
          component: BatchInput,
          meta: { title: '数据录入', requiresAuth: true }
        },
        {
          path: '/batch-input/:id',
          name: 'BatchInputEdit',
          component: BatchInput,
          meta: { title: '编辑记录', requiresAuth: true }
        },
        {
          path: '/query',
          name: 'Query',
          component: SimpleQuery,
          meta: { title: '高级查询', requiresAuth: true }
        },
        {
          path: '/analysis',
          name: 'DataAnalysis',
          component: DataAnalysis,
          meta: { title: '数据分析', requiresAuth: true }
        },
        {
          path: '/alerts',
          name: 'Alerts',
          component: Alerts,
          meta: { title: '报警监控', requiresAuth: true }
        },
        {
          path: '/ai-chat',
          name: 'AIChat',
          component: AIChat,
          meta: { title: 'AI智能助手', requiresAuth: true }
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/404.vue')
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 初始化认证状态
  authStore.initializeAuth()
  
  // 检查是否需要认证
  const requiresAuth = to.meta.requiresAuth !== false
  
  // 如果访问根路径且未登录，直接跳转到登录页
  if (to.path === '/' && !authStore.isAuthenticated) {
    next('/enhanced-login')
    return
  }
  
  if (requiresAuth && !authStore.isAuthenticated) {
    // 需要认证但未登录，跳转到登录页
    next({
      path: '/enhanced-login',
      query: { redirect: to.fullPath }
    })
  } else if (!requiresAuth && authStore.isAuthenticated && to.path !== '/') {
    // 不需要认证但已登录（且不是根路径），跳转到主界面
    next('/dashboard')
  } else if (to.path === '/enhanced-login' && authStore.isAuthenticated) {
    // 已登录用户访问登录页，跳转到主界面
    next('/dashboard')
  } else {
    // 正常访问
    next()
  }
})

export default router
