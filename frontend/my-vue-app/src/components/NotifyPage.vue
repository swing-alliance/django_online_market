<template>
  <div class="notifications-page" style="padding: 20px;">
    
    <h2>好友通知中心 (总数: {{ notifications.length }})</h2>

    <p v-if="loading" style="color: #007bff;">正在加载通知...</p>
    <p v-else-if="error" style="color: #f44336;">加载失败: {{ error }}</p>
    <p v-else-if="!loading && notifications.length === 0" style="color: #555;">暂无新的通知。</p>

    <div class="notification-list" style="margin-top: 20px; display: flex; flex-direction: column; gap: 10px;">
      
      <NotifyCard 
        v-for="item in notifications"
        :key="item.id" 
        :notify_name="item.notify_name"              :notify_content="item.notify_content"        :request-id="item.id"
      />

    </div>
    
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
// 确保路径正确，例如如果它们在同一文件夹，则为 './NotifyCard.vue'
import NotifyCard from './NotifyCard.vue'; 
import { setupAxiosInterceptor } from '@/utils/AxiosInterceptor';
setupAxiosInterceptor(); 


// --- 状态定义 ---
const notifications = ref([]); // 存储通知列表数组
const loading = ref(true);
const error = ref(null);

const getfriendnotifyurl = 'http://127.0.0.1:8000/api/users/fetch_user_notifications/';


// --- 数据获取逻辑 (路由加载时自动触发) ---
async function fetchNotifications() {
    loading.value = true;
    error.value = null;

    try {
        const response = await axios.get(getfriendnotifyurl);
        
        // 🚨 关键：假设后端返回一个包含通知对象的数组
        const rawData = response.data.notifications || response.data;

        if (Array.isArray(rawData)) {
            notifications.value = rawData.map((item, index) => ({
                // 确保有唯一的 key 和 request_id
                id: item.id || index, 
                // 从 API 响应中提取字段，注意字段命名兼容性 (notify_name, name, from_user_name)
                notify_name: item.notify_name || item.name || item.from_user_name || '未知发送者',
                notify_content: item.notify_content || item.content || item.message || '未提供内容',
            }));
        } else {
             throw new Error('API响应数据结构不正确，预期为数组。');
        }
        
    } catch (e) {
        error.value = e.message || '网络请求失败';
        console.error("加载通知列表出错:", e);
    } finally {
        loading.value = false;
    }
}

// 🌟 核心：在组件（路由）加载时触发一次数据获取 🌟
onMounted(fetchNotifications); 
</script>