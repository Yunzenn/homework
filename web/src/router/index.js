import { createRouter, createWebHistory } from 'vue-router'
import SimpleLayout from '@/layout/SimpleLayout.vue'
import SimpleDashboard from '@/views/SimpleDashboard.vue'
import SimpleRecords from '@/views/SimpleRecords.vue'
import SimpleQuery from '@/views/SimpleQuery.vue'
import ApiTest from '@/views/ApiTest.vue'
import TestForm from '@/views/TestForm.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: SimpleLayout,
      children: [
        {
          path: '',
          redirect: '/dashboard'
        },
        {
          path: '/dashboard',
          name: 'Dashboard',
          component: SimpleDashboard,
          meta: { title: '仪表盘' }
        },
        {
          path: '/records',
          name: 'Records',
          component: SimpleRecords,
          meta: { title: '数据管理' }
        },
        {
          path: '/query',
          name: 'Query',
          component: SimpleQuery,
          meta: { title: '高级查询' }
        },
        {
          path: '/test-form',
          name: 'TestForm',
          component: TestForm,
          meta: { title: '测试表单' }
        },
        {
          path: '/api-test',
          name: 'ApiTest',
          component: ApiTest,
          meta: { title: 'API测试' }
        },
        {
          path: '/alerts',
          name: 'Alerts',
          component: () => import('@/views/SimpleDashboard.vue'),
          meta: { title: '报警监控' }
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

export default router
