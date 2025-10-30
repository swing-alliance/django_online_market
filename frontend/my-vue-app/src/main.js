import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js' // 导入创建的路由实例

const app = createApp(App)

// 注册路由：使整个应用都具备路由功能
console.log(router)
app.use(router)

app.mount('#app')