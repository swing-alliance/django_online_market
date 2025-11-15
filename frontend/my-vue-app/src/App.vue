<template>
  <div id="app">
    <nav class="global-nav">
      <router-link to="/">首页</router-link>
      <router-link to="/personalpage">个人</router-link>
      <router-link to="/friendslist">好友</router-link>
      <router-link to="/notification">通知</router-link>
      <router-link to="/test">测试</router-link>
    </nav>

    <!-- 主要内容区域 - 只显示当前路由对应的组件 -->
    <main class="main-content">
      <router-view />
    </main>

    <!-- 全局页脚 -->
    <footer class="global-footer">
      <p>&copy; 2025 我的应用</p>
    </footer>
  </div>
</template>

<script setup>
import router from '@/router'
const refresh_token = localStorage.getItem('refresh_token');
if (!refresh_token) {
    router.push('/login');

}

</script>

<style>
#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.global-nav {
  background: #2c3e50;
  padding: 1rem 2rem;
}

.global-nav a {
  color: white;
  text-decoration: none;
  margin-right: 1rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  /* 确保链接有过渡效果，更平滑 */
  transition: background-color 0.3s ease; 
}

/* 核心修复：移除浏览器默认的焦点轮廓线（边框） */
.global-nav a:focus,
.global-nav a:active {
  outline: none; /* 移除点击或聚焦时的默认轮廓 */
  box-shadow: none; /* 移除可能的阴影效果 */
}

/* 添加悬停效果 */
.global-nav a:hover {
  background: #34495e; /* 悬停时稍微变亮/变暗 */
}

.global-nav a.router-link-active {
  background: #42b883;
}

.main-content {
  flex: 1;
}

.global-footer {
  background: #115fac;
  padding: 1rem;
  text-align: center;
  border-top: 1px solid #dee2e6;
  color: white; /* 增加页脚文本颜色 */
}
</style>