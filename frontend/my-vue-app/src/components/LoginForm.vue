<template>
  <div class="login-container">
    <form @submit.prevent="login">
      <h2>用户登录</h2>
      
      <!-- 为了保持与注册组件的结构一致，这里移除了最外层的 <div> -->
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
      <p v-if="success" class="success">登录成功</p>
      
      <router-link to="/register">没有账号?</router-link>
    </form>
  </div>
</template>

<script>
import axios from 'axios';
import router from '@/router';
export default {
  name: "用户-登录",
  data() {
    return {
      form:{
      username: '',
      password: ''
      },
      errorMessage: null,
      success: false
    };
  },
  methods: {
    async login() {
      this.errorMessage = null;
      this.success = false;
      const LOGIN_API_URL='http://127.0.0.1:8000/api/users/login/';
      try {
        const response = await axios.post(LOGIN_API_URL, this.form);
        console.log('登录成功响应:', response.data);
        const { access_token, refresh_token } = response.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        
        console.log('登录成功，Token 已存储！');
        this.success = true;
        this.form = {
            username: '',
            password: ''
        };
        
      router.push('/personalpage');

      } catch(err) {
        console.error('登录失败:', err.response);
        let errorMsg = "登录失败，请检查网络或服务器。";
        if (err.response && err.response.data) {
            const errors = err.response.data;
            // 尝试提取 Django Rest Framework (DRF) 的错误信息
            if (errors.detail) {
                errorMsg = `登录失败: ${errors.detail}`;
            } else {
                for (const key in errors) {
                    // 只显示第一个字段的第一个错误
                    errorMsg = `登录失败: ${errors[key][0]}`;
                    break;
                }
            }
        }
        this.errorMessage = errorMsg;
      }
    }
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