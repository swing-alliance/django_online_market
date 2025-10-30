<template>
  <div class="register-container">
    <form @submit.prevent="registerUser">
      <h2>用户注册</h2>
      <div>
        <label for="username">用户名:</label>
        <input type="text" id="username" v-model="form.username" required>
      </div>
      <div>
        <label for="email">邮箱:</label>
        <input type="email" id="email" v-model="form.email" required>
      </div>
      <div>
        <label for="password">密码:</label>
        <input type="password" id="password" v-model="form.password" required>
      </div>
      <div>
        <label for="password_confirm">确认密码:</label>
        <input type="password" id="password_confirm" v-model="form.password_confirm" required>
      </div>
      <button type="submit">注册</button>
      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">注册成功！</p>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      // 这里的字段名必须和你的 Django Serializer 的字段名一致
      form: {
        username: '',
        email: '',
        password: '',
        password_confirm: ''
      },
      error: null,
      success: false
    };
  },
  methods: {
    async registerUser() {
      this.error = null;
      this.success = false;

      // ⚠️ 替换成你的后端注册 API 路径
      const API_URL = 'http://127.0.0.1:8000/api/users/register/'; 
      
      try {
        const response = await axios.post(API_URL, this.form);
        console.log('注册成功响应:', response.data);
        this.success = true;
        this.$emit('register-success', this.form.username);
        // 清空表单
        this.form = {
            username: '',
            email: '',
            password: '',
            password_confirm: ''
        };
        // 可以在这里执行页面跳转
        // this.$router.push('/login'); 
      } catch (err) {
        console.error('注册失败:', err.response);
        // 处理后端返回的错误信息
        if (err.response && err.response.data) {
            // 简单地显示所有字段的第一个错误信息
            const errors = err.response.data;
            let errorMessage = "注册失败：";
            for (const key in errors) {
                errorMessage += `${key}: ${errors[key][0]} `;
                break; // 只显示第一个错误
            }
            this.error = errorMessage;
        } else {
            this.error = "注册失败，请检查网络或服务器。";
        }
      }
    }
  }
};
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  width: 100%;
  margin: 0;
  padding: 20px; /* 添加一些内边距，防止在小屏幕上贴边 */
  box-sizing: border-box;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* 可选：添加背景渐变 */
}

form {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
  box-sizing: border-box;
}

h2 {
  text-align: center;
  margin-bottom: 20px;
  font-size: 24px;
  color: #333;
}

div {
  margin-bottom: 15px;
}

label {
  font-size: 14px;
  font-style:"微软雅黑";
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
  margin-top: 10px;
}

button:hover {
  background-color: #0056b3;
}

p {
  font-size: 14px;
  text-align: center;
  margin: 10px 0;
}

.error {
  color: red;
}

.success {
  color: green;
}
</style>