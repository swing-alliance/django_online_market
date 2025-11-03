import { createRouter, createWebHistory } from 'vue-router'
// 导入你的目标组件
import HelloWorld from '../components/HiPage.vue' // 假设它在 components 目录下
const routes = [
  {
    path: '/hello',
    name: 'helloworld',
    component: HelloWorld
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
  {path: '/test_auth',
  name: 'test_auth',
  component: () => import('../components/ProtectedTest.vue')
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