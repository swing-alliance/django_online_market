<template>
  <div class="login-container">
    <form @submit.prevent="login">
      <h2>用户登录</h2>
      
      <div class="form-group">
        <label for="username">用户名:</label>
        <input type="text" id="username" v-model="form.username" required>
      </div>
      
      <div class="form-group">
        <label for="password">密码:</label>
        <input type="password" id="password" v-model="form.password" required>
      </div>
      
      <button type="submit">登录</button>
      
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      <p v-if="success" class="success">登录成功,即将跳转</p>
      
      <router-link to="/register">没有账号?</router-link>
    </form>
  </div>
</template>

<script setup>
import axios from 'axios';
import { ref } from 'vue';
import router from '../router';
import emitter from '@/utils/eventBus';

// 如果你的后端需要跨域携带 Cookie，请确保配置了 withCredentials
// 例如: axios.defaults.withCredentials = true;

const form = ref({
  username: '',
  password: '',
});

const errorMessage = ref('');
const success = ref(false);

const login = async () => {
  errorMessage.value = '';
  success.value = false;
  try {
    const response = await axios.post('/api/users/login/', {
      username: form.value.username,
      password: form.value.password,
    }, {
      withCredentials: true 
    });

    const { access_token, refresh_token } = response.data;
    

    // --- 业务逻辑继续 ---
    
    if (access_token && refresh_token) {
      success.value = true;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('username', form.value.username || '');
      console.log('Token 存储成功。');

    } else {
      errorMessage.value = '登录成功，但未收到认证令牌。';
    }
    setTimeout(() => {
      router.push('/PersonalPage');
    }, 1000);

  } catch (error) {
    success.value = false;
    if (axios.isAxiosError(error)) {
      errorMessage.value = error.response?.data?.message || '登录失败，请检查用户名和密码。';
    } else {
      errorMessage.value = '发生了一个未知错误。';
    }
    console.error('Login Error:', error);
  }
  finally {
    emitter.emit('login-requested');
  }
};
</script>

<style scoped>
/* 样式与注册组件完全保持一致，实现水平和垂直居中 */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh; /* 确保占据整个视口高度 */
  width: 100%;
  margin: 0;
  padding: 20px;
  box-sizing: border-box;
  /* 使用与注册页面相同的渐变背景 */
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
}

form {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
  box-sizing: border-box;
  text-align: center; /* 确保 router-link 居中 */
}

h2 {
  text-align: center;
  margin-bottom: 20px;
  font-size: 24px;
  color: #333;
}

/* 确保输入组内部标签和输入框靠左对齐 */
.form-group {
    margin-bottom: 15px;
    text-align: left; /* 覆盖 form 的 text-align: center */
}

label {
  font-size: 14px;
  /* font-style:"微软雅黑"; 浏览器可能不支持，建议删除或使用 font-family */
  color: #555;
  display: block;
  margin-bottom: 5px;
}

input {
  width: 100%;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-sizing: border-box;
  outline: none;
  transition: all 0.3s;
}

input:focus {
  border-color: #007bff;
  box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
}

button {
  width: 100%;
  padding: 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 20px; /* 增加按钮上方的间距 */
}

button:hover {
  background-color: #0056b3;
}

p, a {
  font-size: 14px;
  text-align: center;
  display: block; /* 让 router-link 独占一行 */
  margin: 10px 0;
}

/* 链接样式 */
.router-link {
    color: #007bff;
    text-decoration: none;
    transition: color 0.3s;
}
.router-link:hover {
    text-decoration: underline;
}

/* 消息样式 */
.error {
  color: #ff4d4f;
}

.success {
  color: #52c41a;
}
</style>