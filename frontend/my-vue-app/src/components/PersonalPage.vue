<template>
  <div class="page-wrapper">
    <div class="personal-page">
      <h2 class="title">个人信息中心</h2>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="loader-spinner"></div>
        <p>正在加载用户信息...</p>
      </div>

      <!-- 用户信息 -->
      <div v-else-if="userInfo.username" class="info-card-wrapper">
        <div class="info-card">

          <!-- 双击头像上传 -->
          <div 
            class="avatar-container" 
            @dblclick="triggerFileInput"
            :class="{ 'uploading': isUploading }"
          >
            <img 
              :src="localAvatarPreview || userInfo.account_avatar || defaultAvatar" 
              alt="用户头像" 
              class="user-avatar"
              @error="handleImageError"
            />

            <!-- 隐藏文件输入 -->
            <input 
              type="file" 
              ref="fileInput"
              accept="image/*"
              @change="handleAvatarChange"
              class="hidden-file-input"
            />

            <!-- 错误提示 -->
            <p v-if="uploadError" class="upload-error-text">{{ uploadError }}</p>
          </div>

          <!-- 基本信息 -->
          <div class="user-details">
            <p><strong>用户名</strong> <span class="info-value">{{ userInfo.username }}</span></p>
            <p><strong>账户ID</strong> <span class="info-value">{{ userInfo.account_id }}</span></p>
          </div>

          <!-- 退出登录 -->
          <button @click="handleLogout" class="logout-button">
            退出登录
          </button>
        </div>
      </div>

      <!-- 错误状态 -->
      <div v-else class="error-state">
        <p class="error-message">获取用户信息失败。</p>
        <router-link to="/login" class="link-button">转到登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { setupAxiosInterceptor } from '@/utils/AxiosInterceptor.js';

// 初始化拦截器（你已在其中统一处理 headers、token）
setupAxiosInterceptor();

const router = useRouter();

// ==================== 响应式数据 ====================
const userInfo = ref({});
const loading = ref(true);
const uploadError = ref('');
const isUploading = ref(false);
const localAvatarPreview = ref(null);
const fileInput = ref(null);

const defaultAvatar = '/image/default_avatar.png'; // public/image/default_avatar.png

const API_URL = '/api/users/fetch_user_info/';
const AVATAR_UPDATE_URL = '/api/users/user_upload_avatar/';

// ==================== 双击触发 ====================
const triggerFileInput = () => {
  fileInput.value?.click();
};

// ==================== 头像上传（纯 axios，无 headers）===================
const handleAvatarChange = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  const originalUrl = userInfo.value.account_avatar;
  localAvatarPreview.value = URL.createObjectURL(file);
  const formData = new FormData();
  formData.append('account_avatar', file);
  isUploading.value = true;
  uploadError.value = '';
  try {
    const response = await axios.patch(AVATAR_UPDATE_URL, formData);
    userInfo.value.account_avatar = response.data.account_avatar;
    alert('头像更新成功！');
  } catch (error) {
    console.error('上传失败:', error);
    uploadError.value = error.response?.data?.account_avatar?.[0] || '上传失败，请重试';
    userInfo.value.account_avatar = originalUrl;
  } finally {
    isUploading.value = false;
    localAvatarPreview.value && URL.revokeObjectURL(localAvatarPreview.value);
    localAvatarPreview.value = null;
    event.target.value = '';
  }
};

// ==================== 图片错误 ====================
const handleImageError = (e) => {
  e.target.src = defaultAvatar;
  userInfo.value.account_avatar = defaultAvatar;
};

// ==================== 获取用户信息 ====================
const fetchUserInfo = async () => {
  loading.value = true;

  if (!localStorage.getItem('access_token')) {
    loading.value = false;
    router.push('/login');
    return;
  }

  try {
    const response = await axios.get(API_URL);
    userInfo.value = response.data;
  } catch (error) {
    console.error('获取用户信息失败:', error);
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      router.push('/login');
    }
  } finally {
    loading.value = false;
  }
};

// ==================== 退出登录 ====================
const handleLogout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  router.push('/login');
};

// ==================== 生命周期 ====================
onMounted(() => {
  fetchUserInfo();
});
</script>

<style scoped>
/* ==================== 整体布局 ==================== */
.page-wrapper {
  display: flex;
  justify-content: center;
  padding: 40px 20px;
  min-height: calc(100vh - 120px);
  background: #f7f9fc;
}

.personal-page {
  width: 100%;
  max-width: 450px;
  background: #fff;
  border-radius: 18px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0,0,0,.1);
  border: 1px solid #e9ecef;
}

.title {
  text-align: center;
  font-size: 1.8rem;
  color: #2c3e50;
  margin-bottom: 30px;
  font-weight: 700;
}

/* ==================== 头像区域 ==================== */
.avatar-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.avatar-container:hover {
  transform: scale(1.03);
}

.avatar-container:active {
  transform: scale(0.98);
}

.avatar-container.uploading .user-avatar {
  opacity: 0.7;
  filter: grayscale(30%);
}

.user-avatar {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 50%;
  border: 5px solid #0a0b0b;
  box-shadow: 0 4px 12px rgba(0,0,0,.15);
  transition: all 0.2s ease;
}

/* 完全隐藏 input */
.hidden-file-input {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0,0,0,0);
  white-space: nowrap;
  border: 0;
  opacity: 0;
}

.upload-error-text {
  margin-top: 12px;
  color: #e74c3c;
  font-size: 0.9em;
  text-align: center;
  min-height: 1.2em;
}

/* ==================== 用户信息 ==================== */
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
  color: #7f8c8d;
  font-weight: 600;
}

.info-value {
  color: #2c3e50;
  font-weight: 500;
}

/* ==================== 退出按钮 ==================== */
.logout-button {
  width: 100%;
  padding: 12px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1.1em;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 10px rgba(231,76,60,.3);
}

.logout-button:hover {
  background: #c0392b;
  transform: translateY(-1px);
}

/* ==================== 加载 & 错误 ==================== */
.loading-state, .error-state {
  text-align: center;
  padding: 30px;
  background: #ecf0f1;
  border-radius: 8px;
  margin-top: 20px;
}

.loader-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #42b983;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  color: #e74c3c;
  font-weight: 600;
  margin-bottom: 15px;
}

.link-button {
  display: inline-block;
  padding: 10px 20px;
  background: #3498db;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  transition: background 0.3s;
}

.link-button:hover {
  background: #2980b9;
}
</style>