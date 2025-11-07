<template>
  <div class="page-wrapper">
    <div class="personal-page">
      <h2 class="title">个人信息中心</h2>

      <!-- --------------------- 加载状态 --------------------- -->
      <div v-if="loading" class="loading-state">
        <div class="loader-spinner"></div>
        <p>正在加载用户信息...</p>
        <p class="token-status">Token 状态: {{ tokenState?.value }}</p>
      </div>
      <div v-else-if="userInfo.username" class="info-card-wrapper">
        <div class="info-card">
          <div class="avatar-container">
            <img 
              :src="userInfo.account_avatar || 'https://placehold.co/100x100/42b983/ffffff?text=U'" 
              alt="用户头像" 
              class="user-avatar"
              @error="userInfo.account_avatar = 'https://placehold.co/100x100/42b983/ffffff?text=U'"
            >
          </div>
          <div class="user-details">
            <p><strong>用户名</strong> <span class="info-value">{{ userInfo.username }}</span></p>
            <p><strong>账户ID</strong> <span class="info-value">{{ userInfo.account_id }}</span></p>
          </div>

          <!-- 退出按钮 -->
          <button @click="simplelogout" class="logout-button">
            退出登录
          </button>
        </div>
      </div>

      <!-- --------------------- 错误状态 --------------------- -->
      <div v-else class="error-state">
        <p class="error-message">😔 {{ errorMessage || '获取用户信息失败。' }}</p>
        <router-link to="/login" class="link-button">
          转到登录
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
// 假设 '@/utils/istokenexit.js' 中导出了 simplelogout
import authService from '@/utils/istokenexit.js';
const { simplelogout } = authService;
// 假设 '@/utils/AxiosInterceptor.js' 存在
import { setupAxiosInterceptor, tokenStatus } from '@/utils/AxiosInterceptor.js';

// 初始化 Axios 拦截器
setupAxiosInterceptor();

const userInfo = ref({});
const loading = ref(true);
const errorMessage = ref('');
const tokenState = tokenStatus; 

const API_URL = 'http://127.0.0.1:8000/api/users/fetch_user_info/';

const fetchUserInfo = async () => {
  loading.value = true;
  errorMessage.value = '';
  userInfo.value = {};
  
  // 检查是否有 Token，如果没有直接跳转到登录页（简单处理，更严谨在路由守卫）
  if (!localStorage.getItem('access_token')) {
     loading.value = false;
     errorMessage.value = '请先登录。';
     return;
  }

  try {
    const response = await axios.get(API_URL);
    console.log('得到的用户信息:', response.data);

    // 假设后端返回的数据结构直接可用
    userInfo.value = response.data;
    
  } catch (error) {
    console.error('获取用户信息失败:', error);
    if (error.response && error.response.status === 401) {
        // 如果是 401 错误，等待拦截器刷新，或者提示用户登录
        errorMessage.value = '认证失败或已过期，请重新登录。';
    } else if (error.message) {
        errorMessage.value = `网络/请求错误: ${error.message}`;
    } else {
        errorMessage.value = '发生未知错误。';
    }
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchUserInfo();
});
</script>

<style scoped>
/* ------------------- 布局和容器美化 ------------------- */
.page-wrapper {
  /* 使用 flexbox 使内容在 App.vue 的 main-content 容器中垂直居中 */
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px); /* 减去导航栏和页脚的高度 */
  background-color: #f7f9fc; /* 浅灰色背景 */
}

.personal-page {
  width: 100%;
  max-width: 450px; /* 略微缩小卡片宽度，更精致 */
  padding: 30px;
  background-color: #ffffff; 
  border-radius: 18px; /* 增加圆角 */
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); /* 更深邃的阴影 */
  border: 1px solid #e9ecef; /* 非常浅的边框 */
  transition: all 0.3s ease;
}

.title {
    font-size: 1.8rem;
    color: #2c3e50;
    margin-bottom: 30px;
    font-weight: 700;
}

/* --- 🌟 头像美化样式 🌟 --- */
.avatar-container {
  display: flex;
  justify-content: center;
  margin-bottom: 30px; 
}

.user-avatar {
  width: 120px; /* 增大头像 */
  height: 120px; 
  object-fit: cover;
  border-radius: 50%; 
  border: 5px solid #42b883; /* 绿色边框 */
  box-shadow: 0 0 0 4px rgba(66, 184, 131, 0.4), 0 5px 15px rgba(0, 0, 0, 0.1); 
  transition: transform 0.3s ease-in-out;
}

.user-avatar:hover {
    transform: scale(1.05) rotate(1deg);
}


/* --- 信息卡片样式优化 (基于您之前提供的样式) --- */
.info-card {
    /* 容器是个人主页本身，这里不需要额外的 info-card */
    /* 只是为了保持代码结构清晰 */
    text-align: left;
}

.user-details {
    padding: 15px 0;
    border-top: 1px solid #f0f0f0;
    border-bottom: 1px solid #f0f0f0;
    margin-bottom: 30px;
}

.user-details p {
    margin: 15px 0;
    font-size: 1.05em;
    color: #34495e;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.user-details strong {
    min-width: 120px; 
    color: #7f8c8d; /* 灰色标签 */
    font-weight: 600;
}

.info-value {
    color: #2c3e50;
    font-weight: 500;
}


/* --- 退出按钮美化 --- */
.logout-button {
    width: 100%;
    padding: 12px;
    background-color: #e74c3c; /* 醒目的红色 */
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 1.1em;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.1s;
    box-shadow: 0 4px 10px rgba(231, 76, 60, 0.3);
}

.logout-button:hover {
    background-color: #c0392b;
    transform: translateY(-1px);
}

/* --- 状态显示美化 --- */
.loading-state, .error-state {
  margin-top: 30px;
  padding: 20px;
  background-color: #ecf0f1;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.token-status {
    font-size: 0.9em;
    color: #95a5a6;
    margin-top: 5px;
}

.error-message {
    color: #e74c3c;
    font-weight: 600;
    margin-bottom: 15px;
}

.link-button {
    display: inline-block;
    padding: 10px 20px;
    background-color: #3498db;
    color: white;
    text-decoration: none;
    border-radius: 6px;
    transition: background-color 0.3s;
}

.link-button:hover {
    background-color: #2980b9;
}

.loader-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #42b883;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>