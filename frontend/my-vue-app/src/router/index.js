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
  }
  
]

const router = createRouter({
  // 使用 HTML5 History 模式（需要服务器支持）
  history: createWebHistory(),
  routes
})

export default router