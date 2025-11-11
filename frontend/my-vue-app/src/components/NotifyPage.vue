<template>
  <div class="notifications-page" style="padding: 20px;">
    
    <h2>通知中心</h2>

    <p v-if="loading" style="color: #007bff;">正在加载通知...</p>
    <p v-else-if="error" style="color: #f44336;">加载失败: {{ error }}</p>
    <p v-else-if="!loading && notifications.length === 0" style="color: #555;">暂无新的通知。</p>

    <div class="notification-list" style="margin-top: 20px; display: flex; flex-direction: column; gap: 10px;">
      
        <NotifyCard 
          v-for="item in notifications"
          :key="item.request_id" 
          :notify_name="item.notify_name"              
          :notify_content="item.notify_content"  
          :created_at="item.created_at"    
          :request_id="item.request_id"  
        />

    </div>
    
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
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
        const rawData = response.data.notifications || response.data;
        if (Array.isArray(rawData)) {
            notifications.value = rawData.map((item) => {
                return {
                    fromuserid: item.from_user_id,
                    notify_name: item.notify_name || item.name || item.from_user_name || '未知发送者',
                    notify_content: item.notify_content || item.content || item.message || '未提供内容',
                    created_at: item.created_at,
                    request_id: item.request_id
                };
            });
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
onMounted(fetchNotifications); 
</script>