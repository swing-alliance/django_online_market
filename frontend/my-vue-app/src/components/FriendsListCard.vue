<template>
  <div class="friend-card">
    <div class="avatar-container">
      <img
        :src="props.avatarUrl || defaultAvatarUrl"
        alt="好友头像"
        class="friend-avatar"
      />
    </div>

    <div class="info-container">
      <h3 class="friend-name">{{ props.friendAccountName || '未知用户' }}</h3>
      
      <p class="account-id">
        账户ID: 
        <span class="id-value">{{ props.friendAccountId || '未知id' }}</span>
      </p>
    </div>
    
    <button class="message-btn" @click="HandleSendMessage">发消息</button>
  </div>
</template>

<script setup>
// 修正：使用命名导出 {} 来导入 ref
import { ref } from 'vue';
import router from '@/router';
const props = defineProps({
    avatarUrl: {
        type: String,
        default: '',
    },
    friendId: {
        type: [String, Number],
        required: true,

    },
    friendAccountName: {
        type: String,
        required: true, 
    },
    friendAccountId: {
        type: [String, Number],
        default: null,
    },
});
const defaultAvatarUrl = ref('/image/default_avatar.png');


function HandleSendMessage()
{
  router.push({
    name: 'chatroom',
    params: {
      mydatabaseId: localStorage.getItem('user_id'),
      friendAccountName: props.friendAccountName,
    }
  });
}
</script>



<style scoped>
.friend-card {
  display: flex;
  align-items: center;
  padding: 15px;
  margin: 0px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  background-color: #fff;
  transition: box-shadow 0.3s;
  max-width: 350px;
}

.friend-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.avatar-container {
  flex-shrink: 0; /* 防止头像被压缩 */
  margin-right: 15px;
}

.friend-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%; /* 圆形头像 */
  object-fit: cover; /* 确保图片不变形 */
  border: 2px solid #101111;
}

.info-container {
  flex-grow: 1;
  min-width: 0; /* 允许文本溢出时省略号生效 */
}

.friend-name {
  margin: 0 0 5px 0;
  font-size: 1.1em;
  font-weight: 600;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.account-id {
  margin: 0;
  font-size: 0.85em;
  color: #888;
}

.id-value {
    font-weight: 500;
    color: #555;
}

.message-btn {
    margin-left: 15px;
    padding: 8px 12px;
    background-color: #f7f7f7;
    color: rgb(3, 3, 3);
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.message-btn:hover {
    background-color: #cedede;
}
</style>