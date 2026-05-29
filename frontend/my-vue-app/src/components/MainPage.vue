<template>
  <div class="social-container">
    <div class="main-content">
      <div class="card announcement-card">
        <div class="announcement-header">
          <i class="ri-notification-3-line"></i>
          <span>系统公告</span>
        </div>
        <p class="announcement-body">
          欢迎来到系统！为了营造健康、绿色的社交环境，请在交流中<strong>保持友善、互相尊重</strong>。让我们共同维护一个文明和谐的社区空间！
        </p>
      </div>

      <div class="card social-main-card">
        <div class="section-header">
          <h2>快捷导航</h2>
        </div>

        <div class="action-grid">
          <button @click="navToCreateForum" class="nav-btn nav-forum-btn">
            <i class="ri-add-circle-line"></i> 创建论坛
          </button>

          <button @click="navToShowForum" class="nav-btn nav-show-forums-btn">
            <i class="ri-compass-line"></i> 探索版块
          </button>

          <button @click="navToAiTest" class="nav-btn nav-ai-btn">
            <i class="ri-robot-line"></i> AI小助手
          </button>

          <button @click="navToCreateGroup" class="nav-btn nav-group-btn">
            <i class="ri-team-line"></i> 发起群聊
          </button>
        </div>

        <div class="divider"></div>

        <div class="friend-management-section">
          <h3>好友管理</h3>
          <div class="input-group">
            <div class="input-wrapper">
              <i class="ri-search-line input-icon"></i>
              <input
                type="text"
                placeholder="输入用户ID或名称..."
                v-model="name_or_id"
                @keyup.enter="sendFriendRequest"
              />
            </div>
            <button
              class="submit-request-btn"
              @click="sendFriendRequest"
              :disabled="!name_or_id.trim() || isLoading"
            >
              <span v-if="!isLoading"
                ><i class="ri-user-add-line"></i> 发送请求</span
              >
              <span v-else
                ><i class="ri-loader-4-line spin"></i> 发送中...</span
              >
            </button>
          </div>

          <transition name="fade">
            <div
              v-if="message"
              class="message-banner"
              :class="isError ? 'error-banner' : 'success-banner'"
            >
              <span>{{ message }}</span>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { setupAxiosInterceptor } from "@/utils/AxiosInterceptor.js";
import axios from "axios";
import { ref } from "vue";
import { useRouter } from "vue-router";

// 初始化拦截器
setupAxiosInterceptor();
const apiUrl = "/api/users/add_friend_request/";

const router = useRouter();

// 响应式变量
const name_or_id = ref("");
const isLoading = ref(false);
const message = ref("");
const isError = ref(false);

// 发送好友请求
const sendFriendRequest = async () => {
  const searchKey = name_or_id.value.trim();
  if (!searchKey) return;

  message.value = "";
  isLoading.value = true;

  try {
    const response = await axios.post(apiUrl, {
      account_id: searchKey.length >= 7 ? searchKey : "",
      account_name: searchKey.length >= 7 ? "" : searchKey,
    });
    message.value = response.data.message || "请求已发送成功";
    isError.value = false;
    name_or_id.value = "";
  } catch (error) {
    isError.value = true;
    message.value =
      error.response?.data?.detail || "发送失败，请检查用户是否存在";
  } finally {
    isLoading.value = false;
  }
};

// 路由跳转
const navToShowForum = () => router.push({ name: "show-forum" });
const navToCreateForum = () => router.push({ name: "CreateForum" });
const navToAiTest = () => router.push({ name: "ai_test" });
const navToCreateGroup = () => router.push({ name: "TryCreateGroup" });
</script>

<style scoped>
@import url("https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css");

/* 基础重置与布局 */
.social-container {
  max-width: 650px;
  margin: 40px auto;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica,
    Arial, sans-serif;
  color: #334155;
  padding: 0 20px;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 通用卡片样式 */
.card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05),
    0 2px 4px -1px rgba(0, 0, 0, 0.03);
  border: 1px solid #f1f5f9;
}

/* 公告栏专属样式 */
.announcement-card {
  background: linear-gradient(135deg, #fef1f2, #fff7ed);
  border: 1px solid #fed7aa;
  padding: 18px 24px;
}

.announcement-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #ea580c;
  font-weight: 700;
  font-size: 0.95rem;
  margin-bottom: 6px;
}

.announcement-body {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.6;
  color: #7c2d12;
}

/* 主卡片样式 */
.social-main-card {
  padding: 28px;
}

.section-header h2 {
  margin: 0 0 20px 0;
  font-size: 1.25rem;
  color: #0f172a;
  font-weight: 700;
}

.friend-management-section h3 {
  margin: 0 0 16px 0;
  font-size: 1.25rem;
  color: #0f172a;
  font-weight: 700;
}

/* 分割线 */
.divider {
  height: 1px;
  background: #e2e8f0;
  margin: 28px 0;
}

/* 导航按钮网格布局 */
.action-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.nav-btn {
  padding: 12px 16px;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-radius: 12px;
  border: 1px solid transparent;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.nav-btn:active {
  transform: translateY(0);
}

/* 各按钮精致配色 */
.nav-forum-btn {
  background: #f8fafc;
  border-color: #e2e8f0;
  color: #475569;
}
.nav-forum-btn:hover {
  background: #f1f5f9;
  color: #0f172a;
  border-color: #cbd5e1;
}

.nav-show-forums-btn {
  background: #f0fdfa;
  color: #0d9488;
}
.nav-show-forums-btn:hover {
  background: #0d9488;
  color: white;
}

.nav-ai-btn {
  background: #f0fdf4;
  color: #16a34a;
}
.nav-ai-btn:hover {
  background: #16a34a;
  color: white;
}

.nav-group-btn {
  background: #eef2ff;
  color: #4f46e5;
}
.nav-group-btn:hover {
  background: #4f46e5;
  color: white;
}

/* 好友搜索输入框区域 */
.input-group {
  display: flex;
  gap: 12px;
}

.input-wrapper {
  position: relative;
  flex: 1;
}

.input-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 1.1rem;
}

input {
  width: 100%;
  padding: 12px 16px 12px 40px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  outline: none;
  font-size: 0.95rem;
  color: #1e293b;
  transition: all 0.2s ease;
  background: #f8fafc;
}

input:focus {
  border-color: #6366f1;
  background: white;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
}

/* 提交按钮 */
.submit-request-btn {
  padding: 0 24px;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: white;
  border-radius: 12px;
  border: none;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 4px 10px rgba(99, 102, 241, 0.2);
  transition: all 0.2s ease;
}

.submit-request-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 14px rgba(99, 102, 241, 0.3);
}

.submit-request-btn:disabled {
  background: #cbd5e1;
  box-shadow: none;
  cursor: not-allowed;
  color: #94a3b8;
}

/* 提示横幅美化 */
.message-banner {
  margin-top: 16px;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
}

.success-banner {
  background-color: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #065f46;
}
.success-banner::before {
  content: "✨";
  margin-right: 8px;
}

.error-banner {
  background-color: #fef2f2;
  border: 1px solid #fca5a5;
  color: #991b1b;
}
.error-banner::before {
  content: "❌";
  margin-right: 8px;
}

/* 加载动画 */
.spin {
  animation: loading-rotate 1s linear infinite;
  display: inline-block;
}

@keyframes loading-rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Vue 3 动画过渡效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
