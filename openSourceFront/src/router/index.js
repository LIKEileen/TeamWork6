import { createRouter, createWebHistory } from 'vue-router'

// 页面模块导入
import LoginPage from '@/pages/LoginPage.vue'
import RegisterPage from '@/pages/RegisterPage.vue'
import BindPhone from '@/pages/BindPhone.vue'
import Dashboard from '@/pages/Dashboard.vue'

import Board from '@/pages/Board.vue'
import Schedule from '@/pages/Schedule.vue'
import CreateMeeting from '@/pages/CreateMeeting.vue'
import MyOrganization from '@/pages/MyOrganization.vue'
import Settings from '@/pages/Settings.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterPage
  },
  {
    path: '/bind-phone',
    name: 'BindPhone',
    component: BindPhone
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/pages/ForgotPassword.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    children: [
      {
        path: '',
        redirect: 'dashboard/board'
      },
      {
        path: 'board',
        name: 'Board',
        component: Board
      },
      {
        path: 'schedule',
        name: 'Schedule',
        component: Schedule
      },
      {
        path: 'create',
        name: 'CreateMeeting',
        component: CreateMeeting
      },
      {
        path: 'org',
        name: 'MyOrganization',
        component: MyOrganization
      },
      {
        path: 'settings',
        name: 'Settings',
        component: Settings
      }
    ]
  },
//   {
//     path: '/:pathMatch(.*)*',
//     redirect: '/login'
//   }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
