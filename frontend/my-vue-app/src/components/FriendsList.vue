<template>
  <div>
    <button @click="fetchFriends">加载并显示好友列表</button>
    
    <p v-if="message">{{ message }}</p>

    <div v-if="isListVisible">
      <h2>我的好友 ({{ friendDetails.length }} 人)</h2>
      
      <div 
        class="friendslist" 
        v-for="friend in friendDetails" 
        :key="friend.id"
      >
        <p>ID: {{ friend.id }} | 姓名: {{ friend.name }}</p>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'; // 引入 ref 和 onMounted
import axios from 'axios';
import { setupAxiosInterceptor } from '@/utils/AxiosInterceptor';

// 初始化拦截器
setupAxiosInterceptor();

const fetchfriendsurl = 'http://127.0.0.1:8000/api/users/user_fetch_friends/';

// --- 状态定义 (使用 ref 创建响应式数据) ---
const message = ref('');
const friendIds = ref([]); // 用于存储原始 ID 列表
const friendDetails = ref([]); // 最终用于 v-for 的数据源
const isListVisible = ref(false);

// --- 方法定义 (直接在 setup 中声明函数) ---
async function fetchFriends() {
    message.value = '正在加载...';
    isListVisible.value = false; // 加载前先隐藏列表

    try {
        const response = await axios.get(fetchfriendsurl);
        
        // 确保使用 .value 访问和修改 ref
        if (response.status === 200 && response.data && response.data.friend_id) {
            const ids = response.data.friend_id; 
            
            friendIds.value = ids; // 更新 ID 数组
            
            // 假设这里是简单地构造数据，实际可能需要另一个 API 调用获取详细信息
            friendDetails.value = ids.map(id => ({ id: id, name: `用户 ${id}` })); 
            
            message.value = '好友列表加载成功！';
            isListVisible.value = true; 
        } else {
            message.value = '加载失败：服务器数据格式错误。';
        }

    } catch (error) {
        console.error('请求好友列表时发生错误:', error);
        message.value = '好友列表加载失败，请检查网络。';
    }
}
onMounted(fetchFriends);
</script>
