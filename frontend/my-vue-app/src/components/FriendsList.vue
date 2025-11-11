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
<script>
import axios from 'axios';
import { setupAxiosInterceptor } from '@/utils/AxiosInterceptor';
setupAxiosInterceptor();

const fetchfriendsurl='http://127.0.0.1:8000/api/users/user_fetch_friends/';
export default {
  data() {
    return {
      message: '',
      friendIds: [], // 用于存储原始 ID 列表
      friendDetails: [], // 假设这是您最终用于 v-for 的数据源
      isListVisible: false, 
    };
  },
  methods: {
    async fetchFriends() {
      this.message = '正在加载...';
      this.isListVisible = false; // 加载前先隐藏列表

      try {
        const response = await axios.get(fetchfriendsurl);
        if (response.status === 200 && response.data && response.data.friend_id) {
          const friendIds = response.data.friend_id; 
          this.friendIds = friendIds; // 更新 ID 数组
          this.friendDetails = friendIds.map(id => ({ id: id, name: `用户 ${id}` })); 
          
          this.message = '好友列表加载成功！';
          this.isListVisible = true; 
        } else {
          this.message = '加载失败：服务器数据格式错误。';
        }

      } catch (error) {
        console.error('请求好友列表时发生错误:', error);
        this.message = '好友列表加载失败，请检查网络。';
      }
    }
  }
};
</script>
