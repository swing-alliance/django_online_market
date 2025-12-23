import { createApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia'
import router from './router/index.js' // 导入创建的路由实例
const pinia = createPinia()
const app = createApp(App)

// 注册路由：使整个应用都具备路由功能
app.use(pinia)
app.use(router)

app.mount('#app')