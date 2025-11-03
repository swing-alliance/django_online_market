<template>
  <div class="personal-page">
    <h2>个人信息中心</h2>
    
    <div v-if="loading" class="loading-state">
      <p>正在加载用户信息...</p>
      <p style="color: gray;">Token 状态: {{ tokenState.value }}</p>
    </div>
    
    <div v-else-if="userInfo.username">
      <div class="info-card">
        <p><strong>用户名 (Username):</strong> {{ userInfo.username }}</p>
        <p><strong>账户ID (Account ID):</strong> {{ userInfo.account_id }}</p>
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
   

    userInfo.value = response.data;
    
  } catch (error) {
    console.error('获取用户信息失败:', error);
    
    // 如果是 Axios 错误且有响应体
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
  border: 1px solid #ddd;
  border-radius: 8px;
  text-align: center;
}
.info-card {
  margin-top: 20px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 6px;
  text-align: left;
}
.loading-state, .error-state {
  margin-top: 20px;
}
</style>