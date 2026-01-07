import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { title: '仪表盘' }
  },
  {
    path: '/chats',
    name: 'Chats',
    component: () => import('../views/Chats.vue'),
    meta: { title: '群聊管理' }
  },
  {
    path: '/rules',
    name: 'Rules',
    component: () => import('../views/Rules.vue'),
    meta: { title: '规则配置' }
  },
  {
    path: '/whitelist',
    name: 'Whitelist',
    component: () => import('../views/Whitelist.vue'),
    meta: { title: '白名单管理' }
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: () => import('../views/Analytics.vue'),
    meta: { title: '数据分析' }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/History.vue'),
    meta: { title: '执行历史' }
  },
  {
    path: '/rpa',
    name: 'RPAControl',
    component: () => import('../views/RPAControl.vue'),
    meta: { title: 'RPA 控制' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 企业微信活跃度管理` : '企业微信活跃度管理'
  next()
})

export default router
