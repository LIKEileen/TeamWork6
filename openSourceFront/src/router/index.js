import { createRouter, createWebHistory } from 'vue-router'
// import { useUserStore } from '@/store/user'

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
    component: RegisterPage,
    meta: { title: '注册账号 - 会易' },
  },
  {
    path: '/bind-phone',
    name: 'BindPhone',
    component: BindPhone,
    meta: { title: '绑定手机号 - 会易' },
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
        redirect: 'dashboard/board',
      },
      {
        path: 'board',
        name: 'Board',
        component: Board,
        meta: { title: '别人啥时候有事' },
      },
      {
        path: 'schedule',
        name: 'Schedule',
        component: Schedule,
        meta: { title: '咱啥时候有事' },
      },
      {
        path: 'create',
        name: 'CreateMeeting',
        component: CreateMeeting,
        meta: { title: '建个会议喵~' },
      },
      {
        path: 'org',
        name: 'MyOrganization',
        component: MyOrganization,
        meta: { title: '俺嘞人脉圈' },
      },
      {
        path: 'settings',
        name: 'Settings',
        component: Settings,
        meta: { title: '设置一下吧~' },
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

router.afterEach((to) => {
  // 优先取路由 meta.title，没有则用默认标题
  console.log()
  document.title = to.meta.title || 'Ciallo～ (∠・ω< )⌒★';
});

// router.beforeEach((to, from, next) => {
//   if (to.meta.title) {
//   document.title = to.meta.title;
//   }
//   next();
//   });

export default router
