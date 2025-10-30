<!-- src/App.vue - 正确的写法 -->
<template>
  <div id="app">
    <!-- 全局导航 -->
    <nav class="global-nav">
      <router-link to="/">首页</router-link>
      <router-link to="/hello">HelloWorld</router-link>
      <router-link to="/register">注册</router-link>
      <router-link to="/login">登录</router-link>
    </nav>

    <!-- 主要内容区域 - 只显示当前路由对应的组件 -->
    <main class="main-content">
      <router-view />
    </main>

    <!-- 全局页脚 -->
    <footer class="global-footer">
      <p>&copy; 2024 我的应用</p>
    </footer>
  </div>
</template>

<script setup>
// App.vue 只管理全局布局，不导入具体页面组件
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
}

.global-nav a.router-link-active {
  background: #42b883;
}

.main-content {
  flex: 1;
  padding: 2rem;
}

.global-footer {
  background: #f8f9fa;
  padding: 1rem;
  text-align: center;
  border-top: 1px solid #dee2e6;
}
</style>