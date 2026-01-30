<template>
  <div id="app">
    <nav class="global-nav">
      <router-link to="/">首页</router-link>
      <router-link to="/notification" class="notification-link">
        通知
        <span v-if="pendingCount > 0" class="notification-badge">{{ pendingCount }}</span>
      </router-link>
      <router-link to="/friendslist">好友</router-link>
      <router-link to="/personalpage">个人</router-link>
      <router-link to="/test">测试</router-link>
      <router-link to="/test_ws">测试ws</router-link>
    </nav>

    <main class="main-content">
      <router-view />
    </main>

    </div>
</template>

<script setup>
import router from '@/router'
import { ref, onMounted, onUnmounted, watch } from 'vue';  // ← 加上 watch
import emitter from '@/utils/eventBus.js';
import wsService from '@/utils/websoketservice.js';
const pendingCount = ref(0);

const handlePendingUpdate = (count) => {
  pendingCount.value = parseInt(count) || 0;
  console.log('未读数更新:', pendingCount.value);
};

// 关键代码：监听路由变化，进入通知页就清零
watch(
  () => router.currentRoute.value.path,
  (newPath) => {
    if (newPath === '/notification' || newPath.startsWith('/notification')) {
      if (pendingCount.value > 0) {
        pendingCount.value = 0;
        // 同时通过 eventBus 通知其他组件（可选，推荐）
        emitter.emit('pending-update', 0);
        // 如果你后端需要“标记为已读”，这里也可以发请求或 ws 消息
        // wsService.send({ type: 'mark_all_read' });
      }
    }
  },
  { immediate: true } // 首次加载也在 /notification 时也清零
);

onMounted(() => {
  if (!wsService.isConnected()){
    wsService.connect();
  }
      
  emitter.on('pending-update', handlePendingUpdate);
  emitter.on('login-requested', wsService.connect);
  emitter.on('logout-requested', wsService.disconnect);
});

onUnmounted(() => {
  emitter.off('pending-update', handlePendingUpdate);
  emitter.off('login-requested', wsService.connect);
  emitter.off('logout-requested', wsService.disconnect);
});

const refresh_token = localStorage.getItem('refresh_token');
if (!refresh_token) {
  router.push('/login');
}
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow: hidden; /* 关键：禁止浏览器级别的滚动条 */
}


#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  /* 删掉或者改为 auto */
  min-height: auto; 
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
  background: #3e576f; /* 悬停时稍微变亮/变暗 */
}

.global-nav a.router-link-active {
  background: #516683;
}

.main-content {
  flex: none; 
  /* 改固定高度为自动高度 */
  height: auto; 
  width: 100%;
  
  /* 既然不要上下拉，确保没有多余的外边距 */
  margin: 0;
  padding: 0;
  
  /* 保持 overflow: hidden 以防止内部意外溢出 */
  overflow: hidden; 
}


/* 通知红点样式 */
.notification-link {
  position: relative;
  display: inline-block;
}

.notification-badge {
  /* 调整定位，使其更靠近右上角 */
  position: absolute;
  top: -6px; /* 向上移动，减少负值 */
  right: -8px; /* 向右移动，减少负值 */
  
  background: #e74c3c;
  color: white;
  
  /* 缩小字体 */
  font-size: 10px; 
  font-weight: bold;
  
  /* 缩小尺寸，确保单行显示 */
  min-width: 16px; 
  height: 16px; /* 减小高度 */
  line-height: 16px; /* 减小行高以保持垂直居中 */
  
  border-radius: 50%;
  text-align: center;
  padding: 0 3px; /* 减小水平内边距 */
  box-shadow: 0 1px 2px rgba(0,0,0,0.2); /* 减小阴影深度 */
  white-space: nowrap;
  
  /* 确保徽章本身在动画光环之上 */
  z-index: 10; 
}

/* 脉冲动画光环 */
.notification-badge::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: #e74c3c;
  border-radius: 50%; /* 修正：使用 50% 确保是圆形 */
  /* 确保光环在徽章之下 */
  z-index: -1; 
  animation: pulse 2s infinite;
}


</style>