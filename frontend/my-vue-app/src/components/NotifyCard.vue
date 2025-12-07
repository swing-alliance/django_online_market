<template>
  <div style="display: flex; flex-direction: column; gap: 10px; border: 1px solid #ccc; padding: 15px; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);width: 75%;margin: 0 auto;">
    
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 8px;">
      <h4 style="margin: 0; color: #333; font-size: 1.1em;">
        消息: {{ notify_name }}
      </h4>
      <span style="font-size: 0.8em; color: #999;">
        {{ timeAgo }} 前
      </span>
    </div>
    
    <p style="margin: 0 0 10px 0; color: #555; line-height: 1.5;">
      内容: {{ notify_content }}
    </p>

    <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 5px;">
      <button 
        @click="handleAction('approve')"
        style="padding: 8px 15px; border: none; border-radius: 4px; color: black;  cursor: pointer; font-size: 0.9em;"
      >
        接受
      </button>
      <button 
        @click="handleAction('reject')"
        style="padding: 8px 15px; border: none; border-radius: 4px; color: black;  cursor: pointer; font-size: 0.9em;"
      >
        拒绝
      </button>
      <button 
        @click="handleAction('ignore')"
        style="padding: 8px 15px; border: none; border-radius: 4px; color: black;  cursor: pointer; font-size: 0.9em;"
      >
        忽略
      </button>
    </div>
    
  </div>
</template>

<script setup>
import { computed} from 'vue'; 
import axios from 'axios';

const emit = defineEmits(['action']);
const userhandleurl = '/api/users/user_handle_request/';

const props = defineProps({
    notify_name: {
        type: String,
        required: true
    },
    notify_content: {
        type: String,
        required: true
    },
    created_at: { 
        type: [String, Date],
        required: true
    },
    request_id: {
        type: Number,
        required: true
    }
});


const timeAgo = computed(() => {
    const now = new Date();
    const past = new Date(props.created_at);
    if (isNaN(past.getTime())) {
        return '时间未知';
    }
    const diffSeconds = Math.floor((now - past) / 1000);
    if (diffSeconds < 60) return `${diffSeconds} 秒`;
    const diffMinutes = Math.floor(diffSeconds / 60);
    if (diffMinutes < 60) return `${diffMinutes} 分钟`;
    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) return `${diffHours} 小时`;
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 30) return `${diffDays} 天`;
    const diffMonths = Math.floor(diffDays / 30);
    return `${diffMonths} 个月`;
});


const handleAction = async (actionType) => {
    const payload = {
        request_id: props.request_id,
        action: actionType          
    };
    console.log(`处理请求 (${actionType}):`, payload);
    try {
        const response = await axios.post(userhandleurl, payload);
        emit('action', {
            request_id: props.request_id, // 修正属性名
            type: actionType,
            success: true
        });
        console.log(`操作 ${actionType} 成功，响应:`, response.data);
    } catch (error) {
        console.error(`处理请求失败 (${actionType}):`, error);
        emit('action', {
            request_id: props.request_id,
            type: actionType,
            success: false,
            message: error.response?.data?.message || '网络或服务器错误'
        });
    }
}
</script>