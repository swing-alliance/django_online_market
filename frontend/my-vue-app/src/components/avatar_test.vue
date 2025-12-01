<template>
  <div class="avatar-container">
    <img 
      :src="avatarUrl" 
      alt="用户头像" 
      class="user-avatar-img"
      @error="handleImageError" 
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios'; 
import { setupAxiosInterceptor } from '@/utils/AxiosInterceptor';
setupAxiosInterceptor();
const FALLBACK_AVATAR = '/image/fallback.png'; 
const API_URL = '/api/users/boosted_fetch_user_avatar/';
const avatarUrl = ref(FALLBACK_AVATAR);
const handleImageError = (event) => {
  event.target.src = FALLBACK_AVATAR;
  console.error("头像加载失败，已切换到备用图片。");
};

const fetchAvatar = async () => {
  try {
    const response = await axios.get(API_URL);
    const urlFromApi = response.data.avatar_url;

    if (urlFromApi) {
      avatarUrl.value = urlFromApi;
    } else {
      avatarUrl.value = FALLBACK_AVATAR;
    }

  } catch (error) {
    console.error('获取头像 API 请求失败:', error);
    avatarUrl.value = FALLBACK_AVATAR;
  }
};

onMounted(() => {
  fetchAvatar();
});
</script>

<style scoped>
.user-avatar-img {
  width: 50px;
  height: 50px;
  border-radius: 50%; /* 圆形头像 */
  object-fit: cover;
}
</style>