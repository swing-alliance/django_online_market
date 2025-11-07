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
  }

  
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router