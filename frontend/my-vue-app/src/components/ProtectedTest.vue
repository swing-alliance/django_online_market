<template>
  <div id="simple-auth-tester">
    <header :class="{ 'success-header': isSuccess, 'failure-header': !isSuccess && !isLoading }">
      <h1 v-if="isLoading">正在验证认证信息...</h1>
      <h1 v-else-if="isSuccess">
        🎉 认证成功 (HTTP {{ statusCode }})
      </h1>
      <h1 v-else>
        ❌ 认证失败 (HTTP {{ statusCode }})
      </h1>
    </header>

    <main>
      <h2>API Endpoint: <code>http://127.0.0.1:8000/api/users/test_auth</code></h2>
      
      <div class="info-box">
        <p><strong>状态:</strong> {{ statusMessage }}</p>
        <p><strong>Access Token 状态:</strong> {{ tokenStatus }}</p>
      </div>

      <p v-if="!isSuccess && !isLoading" class="error-detail">
        {{ errorMessage }}
      </p>

      <button @click="testApi" :disabled="isLoading">
        重新测试认证
      </button>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import  setupAxiosInterceptor from '../utils/AxiosInterceptor';
// --- 状态变量 ---
const isSuccess = ref(false);
const isLoading = ref(true);
const statusCode = ref('---');
const errorMessage = ref('未能通过认证，请检查 Token 是否有效或已过期。');
const tokenStatus = ref('');
const statusMessage = ref('等待请求发送...');

const API_URL = 'http://127.0.0.1:8000/api/users/test_auth';



// --- API 测试函数 ---

const testApi = async () => {
  isLoading.value = true;
  isSuccess.value = false;
  statusCode.value = '---';
  statusMessage.value = '发送请求中...';
  errorMessage.value = '';
  setupAxiosInterceptor();

  try {
    const response = await axios.get(API_URL);
    isSuccess.value = true;
    statusCode.value = response.status;
    statusMessage.value = 'API 成功响应。';
  } catch (error) {
    isSuccess.value = false;
    
    if (error.response) {
      statusCode.value = error.response.status;
      if (error.response.status === 401) {
        errorMessage.value = `401 认证失败。原因：${error.response.data.detail || 'Access Token 无效或已过期。'}`;
      } else if (error.response.status === 403) {
        errorMessage.value = '403 权限不足。';
      } else {
        errorMessage.value = `API 返回错误：HTTP ${error.response.status}`;
      }
      statusMessage.value = 'API 响应失败。';
      
    } else if (error.request) {
      statusCode.value = '网络';
      errorMessage.value = '网络请求失败，请检查 CORS 配置或后端服务器是否运行在 :8000 端口。';
      statusMessage.value = '请求无响应。';
    } else {
      statusCode.value = 'JS';
      errorMessage.value = '客户端错误：' + error.message;
      statusMessage.value = '客户端请求构建失败。';
    }

  } finally {
    isLoading.value = false;
  }
};

// 5. 组件挂载后立即进行认证测试
onMounted(() => {
  testApi();
});
</script>

<style scoped>
#simple-auth-tester {
  max-width: 600px;
  margin: 50px auto;
  padding: 0;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  overflow: hidden;
}

header {
  padding: 30px 20px;
  text-align: center;
  color: white;
  transition: background-color 0.5s;
}

.success-header {
  background-color: #2ecc71; /* 绿色 */
}

.failure-header {
  background-color: #e74c3c; /* 红色 */
}

h1 {
  margin: 0;
  font-size: 2em;
}

main {
  padding: 20px;
}

h2 {
  color: #34495e;
  font-size: 1.1em;
  border-bottom: 1px solid #bdc3c7;
  padding-bottom: 10px;
  margin-top: 0;
}

.info-box {
  background-color: #f4f7f9;
  padding: 15px;
  border-radius: 5px;
  border-left: 4px solid #3498db;
  margin-bottom: 20px;
}

.error-detail {
  color: #c0392b;
  background-color: #fceae9;
  padding: 10px;
  border: 1px dashed #e74c3c;
  border-radius: 4px;
}

button {
  display: block;
  width: 100%;
  padding: 12px;
  margin-top: 20px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

button:hover:not(:disabled) {
  background-color: #2980b9;
}

button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}
</style>