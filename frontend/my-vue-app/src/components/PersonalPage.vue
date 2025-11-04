<template>
  <div class="personal-page">
    <h2>个人信息中心</h2>
    
    <div v-if="loading" class="loading-state">
      <p>正在加载用户信息...</p>
      <p style="color: gray;">Token 状态: {{ tokenState?.value }}</p>
    </div>
    
    <div v-else-if="userInfo.username">
      <div class="info-card">
        
        <div class="avatar-container">
          <img :src="userInfo.account_avatar" alt="用户头像" class="user-avatar">
        </div>
        
        <p><strong>用户名 :</strong> {{ userInfo.username }}</p>
        <p><strong>账户ID :</strong> {{ userInfo.account_id }}</p>
      </div>
    </div>
    
    <div v-else class="error-state">
      <p style="color: red;">获取用户信息失败。</p>
      <p v-if="errorMessage">{{ errorMessage }}</p>
      <button @click="fetchUserInfo">重新加载</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
// 导入拦截器及其状态（如果需要显示状态）
import { setupAxiosInterceptor, tokenStatus } from '@/utils/AxiosInterceptor.js';

// 初始化拦截器
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
  try {
    const response = await axios.get(API_URL);
   console.log('得到的用户信息:', response.data);

    userInfo.value = response.data;
    
  } catch (error) {
    console.error('获取用户信息失败:', error);
    if (error.response && error.response.data && error.response.data.detail) {
        errorMessage.value = `服务器错误: ${error.response.data.detail}`;
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
  // 组件加载完成后，调用获取用户信息的方法
  fetchUserInfo();
});
</script>

<style scoped>
.personal-page {
  max-width: 600px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #e0e0e0; /* 柔和的边框 */
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); /* 增加轻微阴影 */
}

/* --- 🌟 头像美化样式 🌟 --- */

.avatar-container {
  /* 确保头像容器居中 */
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 25px; /* 与下方信息保持距离 */
  margin-top: 10px;
}

.user-avatar {
  /* 尺寸控制 */
  width: 100px; /* 统一尺寸 */
  height: 100px; 
  object-fit: cover; /* 确保图片不变形 */
  
  /* 形状美化：圆形 */
  border-radius: 50%; 
  
  /* 边框美化 */
  border: 4px solid #42b983; /* 绿色边框突出显示 */
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.3); /* 柔和的外发光 */
  
  /* 动画效果 (可选，让加载更柔和) */
  transition: transform 0.3s ease-in-out;
}

.user-avatar:hover {
    transform: scale(1.05); /* 鼠标悬停时轻微放大 */
}

/* --- 信息卡片样式优化 --- */
.info-card {
  margin-top: 20px;
  padding: 20px;
  background-color: #ffffff; /* 白色背景更清爽 */
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  text-align: left;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.info-card p {
    margin: 10px 0;
    font-size: 1.1em;
    color: #333;
    /* 确保 strong 标签内的文本对齐 */
    display: flex;
    justify-content: space-between;
}

.info-card strong {
    min-width: 100px; /* 确保标签对齐 */
    color: #555;
    font-weight: 600;
}

.loading-state, .error-state {
  margin-top: 30px;
  font-size: 1.1em;
}

.error-state button {
    margin-top: 10px;
    padding: 8px 15px;
    background-color: #ff6b6b;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}
</style>