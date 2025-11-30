import { createRouter, createWebHistory } from 'vue-router'
// 导入你的目标组件
const routes = [
  {
    path: '/',
    name: 'mainpage',
    component: () => import('../components/MainPage.vue')
  },

  {
    path: '/register',
    name: 'register',
    component: () => import('../components/RegisterForm.vue')
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../components/LoginForm.vue')
  },
  {
    path:'/personalpage',
    name:'personalpage',
    component: () => import('../components/PersonalPage.vue')
  },
  {
    path:'/friendslist',
    name:'friendslist',
    component: () => import('../components/FriendsPage.vue')
  },
  {
    path:'/notification',
    name:'notification',
    component: () => import('../components/NotifyPage.vue')
  },
  {
    path:'/test',
    name:'test',
    component: () => import('../components/ProtectedTest.vue')
  },
  {
    path:'/test_ws',
    name:'test_ws',
    component: () => import('../components/WsStatusTes.vue')
  }
  

  
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router