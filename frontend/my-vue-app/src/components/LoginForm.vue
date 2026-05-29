<template>
  <div class="login-container">
    <div class="bg-circle circle1"></div>
    <div class="bg-circle circle2"></div>

    <form @submit.prevent="login" class="login-form">
      <h2>用户登录</h2>

      <div class="form-group">
        <label>用户名</label>
        <input
          type="text"
          v-model="form.username"
          placeholder="请输入用户名"
          required
        />
      </div>

      <div class="form-group">
        <label>密码</label>
        <input
          type="password"
          v-model="form.password"
          placeholder="请输入密码"
          required
        />
      </div>

      <div class="form-group captcha-box">
        <label>验证码</label>

        <div class="captcha-row">
          <input
            type="text"
            v-model="userInputCaptcha"
            placeholder="输入验证码"
            required
          />

          <canvas
            ref="canvasRef"
            width="100"
            height="40"
            @click="drawCaptcha"
            title="点击刷新验证码"
          ></canvas>
        </div>
      </div>

      <button type="submit" :disabled="success">
        {{ success ? "登录中..." : "登录" }}
      </button>

      <p v-if="errorMessage" class="error">
        {{ errorMessage }}
      </p>

      <p v-if="success" class="success">登录成功，即将跳转...</p>

      <div class="footer-links">
        <router-link to="/register"> 没有账号？点击注册 </router-link>
      </div>
    </form>
  </div>
</template>

<script setup>
import emitter from "@/utils/eventBus";
import axios from "axios";
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const form = ref({
  username: "",
  password: "",
});

const errorMessage = ref("");
const success = ref(false);

// 验证码
const canvasRef = ref(null);
const captchaCode = ref("");
const userInputCaptcha = ref("");

const drawCaptcha = () => {
  const canvas = canvasRef.value;

  if (!canvas) return;

  const ctx = canvas.getContext("2d");

  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";

  let code = "";

  // 清空
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // 背景
  ctx.fillStyle = "#f4f9ff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // 字符
  for (let i = 0; i < 4; i++) {
    const char = chars[Math.floor(Math.random() * chars.length)];

    code += char;

    ctx.font = "bold 24px Arial";

    ctx.fillStyle = `rgb(
      ${Math.random() * 120},
      ${Math.random() * 120},
      ${Math.random() * 200}
    )`;

    const x = 12 + i * 20;
    const y = 28;

    const angle = (Math.random() - 0.5) * 0.4;

    ctx.save();

    ctx.translate(x, y);
    ctx.rotate(angle);

    ctx.fillText(char, 0, 0);

    ctx.restore();
  }

  // 干扰线
  for (let i = 0; i < 4; i++) {
    ctx.beginPath();

    ctx.strokeStyle = `rgba(
      ${Math.random() * 255},
      ${Math.random() * 255},
      ${Math.random() * 255},
      0.5
    )`;

    ctx.moveTo(Math.random() * canvas.width, Math.random() * canvas.height);

    ctx.lineTo(Math.random() * canvas.width, Math.random() * canvas.height);

    ctx.stroke();
  }

  // 干扰点
  for (let i = 0; i < 25; i++) {
    ctx.fillStyle = "#ccc";

    ctx.beginPath();

    ctx.arc(
      Math.random() * canvas.width,
      Math.random() * canvas.height,
      1,
      0,
      Math.PI * 2,
    );

    ctx.fill();
  }

  captchaCode.value = code;
};

onMounted(() => {
  drawCaptcha();
});

const login = async () => {
  // 验证码校验
  if (userInputCaptcha.value.toUpperCase() !== captchaCode.value) {
    errorMessage.value = "验证码错误，请重试";

    userInputCaptcha.value = "";

    drawCaptcha();

    return;
  }

  errorMessage.value = "";

  try {
    const response = await axios.post(
      "/api/users/login/",
      {
        username: form.value.username,
        password: form.value.password,
      },
      {
        withCredentials: true,
      },
    );

    const { access_token, refresh_token, user_id } = response.data;

    if (access_token) {
      success.value = true;

      localStorage.setItem("access_token", access_token);

      localStorage.setItem("refresh_token", refresh_token);

      localStorage.setItem("username", form.value.username);

      localStorage.setItem("user_id", user_id);

      emitter.emit("login-requested");

      setTimeout(() => {
        router.push("/PersonalPage");
      }, 1000);
    }
  } catch (error) {
    console.error("Login Error:", error);

    errorMessage.value = "登录失败，请检查账号或密码";

    drawCaptcha();
  }
};
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.login-container {
  position: relative;
  width: 100%;
  min-height: 100vh;

  display: flex;
  justify-content: center;
  align-items: center;

  overflow: hidden;

  background: linear-gradient(135deg, #e8f4ff 0%, #f5fbff 50%, #dcefff 100%);
}

/* 背景装饰圆 */
.bg-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(10px);
}

.circle1 {
  width: 260px;
  height: 260px;

  background: rgba(100, 181, 246, 0.2);

  top: -60px;
  left: -60px;
}

.circle2 {
  width: 320px;
  height: 320px;

  background: rgba(144, 202, 249, 0.18);

  bottom: -100px;
  right: -80px;
}

.login-form {
  position: relative;
  z-index: 10;

  width: 360px;

  padding: 35px 30px;

  border-radius: 24px;

  background: rgba(255, 255, 255, 0.88);

  backdrop-filter: blur(10px);

  border: 1px solid rgba(255, 255, 255, 0.6);

  box-shadow: 0 10px 40px rgba(0, 102, 255, 0.08),
    0 4px 12px rgba(0, 0, 0, 0.05);
}

.login-form h2 {
  text-align: center;

  margin-bottom: 28px;

  color: #409eff;

  font-size: 28px;

  font-weight: 700;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;

  margin-bottom: 8px;

  color: #4a5568;

  font-size: 14px;

  font-weight: 600;
}

input {
  width: 100%;

  padding: 12px 14px;

  border-radius: 14px;

  border: 1px solid #dbeafe;

  background: rgba(255, 255, 255, 0.9);

  outline: none;

  transition: all 0.25s ease;

  font-size: 14px;
}

input:focus {
  border-color: #409eff;

  box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.15);

  background: white;
}

.captcha-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

canvas {
  border-radius: 12px;

  border: 1px solid #dbeafe;

  cursor: pointer;

  background: white;

  transition: all 0.2s;
}

canvas:hover {
  transform: scale(1.03);
}

button {
  width: 100%;

  padding: 13px;

  border: none;

  border-radius: 14px;

  background: linear-gradient(135deg, #4facfe, #409eff);

  color: white;

  font-size: 16px;

  font-weight: 600;

  cursor: pointer;

  transition: all 0.25s ease;

  margin-top: 8px;

  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.3);
}

button:hover {
  transform: translateY(-2px);

  box-shadow: 0 10px 20px rgba(64, 158, 255, 0.35);
}

button:active {
  transform: scale(0.98);
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error {
  margin-top: 14px;

  text-align: center;

  color: #ff4d4f;

  font-size: 14px;
}

.success {
  margin-top: 14px;

  text-align: center;

  color: #52c41a;

  font-size: 14px;
}

.footer-links {
  margin-top: 18px;

  text-align: center;
}

.footer-links a {
  color: #409eff;

  text-decoration: none;

  font-size: 14px;

  transition: 0.2s;
}

.footer-links a:hover {
  color: #1677ff;
  text-decoration: underline;
}
</style>
