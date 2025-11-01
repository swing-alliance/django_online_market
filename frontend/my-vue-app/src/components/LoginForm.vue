<template>
  <div class="login-container">
    <h2>用户登录</h2>
    <form @submit.prevent="login">
      <div class="form-group">
        <label for="username">用户名:</label>
        <input type="text" id="username" v-model="form.username" required>
      </div>
      <div class="form-group">
        <label for="password">密码:</label>
        <input type="password" id="password" v-model="form.password" required>
      </div>
      <button type="submit">登录</button>
    </form>
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    <p v-if="success" class=" success-massage">登录成功</p>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  name: "用户-登录",
  data() {
    return {
      form:{
      username: '',
      password: ''
      },

    errorMessage: ''
    };
  },
  methods: {
    async login() {
      this.errorMessage = null;
      this.success= false;
      const LOGIN_API_URL='http://127.0.0.1:8000/api/users/login/';
      try {
        const response = await axios.post(LOGIN_API_URL, this.form);
        console.log('登录成功响应:', response.data);
        this.success = true;
        this.form = {
            username: '',
            password: ''
        };
      }catch(err) {
        console.error('登录失败:', err.response);
        if (err.response && err.response.data) {
            const errors = err.response.data;
            let errorMessage = "登录失败：";
            for (const key in errors) {
                errorMessage += `${key}: ${errors[key][0]} `;
                break; 
            }
            this.errorMessage = errorMessage;
        }
      }

    }

  }

};
</script>

<style scoped>
.login-container {
  max-width: 300px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
  text-align: center;
}
.form-group {
  margin-bottom: 15px;
  text-align: left;
}
label {
  display: block;
  margin-bottom: 5px;
}
input[type="text"], input[type="password"] {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}
button {
  padding: 10px 15px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
button:hover {
  background-color: #368a6d;
}
.error-message {
  color: red;
  margin-top: 10px;
}
</style>