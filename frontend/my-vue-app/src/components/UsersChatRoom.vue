<template>
  <div class="debug-container">
    <h2>聊天室调试信息</h2>
    <hr />
    <p><strong>我的数据库 ID (myId):</strong> {{ myId }}</p>
    <p><strong>好友账号ID (friendId):</strong> {{ friendId }}</p>
    <img
        :src="friendAvatar || defaultAvatarUrl"
        alt="好友头像"
        class="friend-avatar"
      />
    <img
        :src="myAvatarUrl || defaultAvatarUrl"
        alt="我的头像"
        class="my-avatar"
      />
      <input 
      v-model="message" 
      type="text" 
      placeholder="请输入内容..." 
      @keyup.enter="handleSend"
    />
    <button @click="handleSend">发送消息</button>
    <div v-if="!myId" style="color: red;">
      警告：未接收到 myId，请检查跳转逻辑！
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';


// 1. 获取当前路由对象
const route = useRoute();

const getavatarbyidurl = '/api/users/get_avatar_by_id/';
const defaultImg = '/image/default_avatar.png';
// 2. 使用计算属性获取参数（这样参数变化时会自动更新）
let myId = computed(() => route.params.myId);
let friendId = computed(() => route.params.friendId);
const myAvatarUrl = computed(() => {
    const avatar = localStorage.getItem('myavatar');
    return avatar ? avatar : defaultImg;
});
const friendAvatar = computed(() => {
    const rawData = localStorage.getItem('friendAvatarMap'); 
    if (rawData && friendId.value) {
        try {
            const datadict = JSON.parse(rawData);
            const avatar = datadict[friendId.value];
            if (avatar === null) {
                return defaultImg;
            }
            return avatar;
        } catch (e) {
            return null;
        }
    }
    return null;
});

const getmyavatar = async () =>{
    try{
        const response = await axios.get(getavatarbyidurl, {params:{account_id: localStorage.getItem('user_id')}}); // 确保携带认证信息
        let rawPath = response.data.avatar_url;
        console.log('后端返回的头像路径:', rawPath);
        if (!rawPath) {
            rawPath = '/media/avatar/default.png'; // 确保有一个默认路径
        }
        localStorage.setItem('myavatar',rawPath );
    }catch(error){
        localStorage.setItem('myavatar', null);
        console.error('获取头像失败:', error);
    }

}





onMounted(() => {
  if (!localStorage.getItem('myavatar')) {
    getmyavatar();
}
  
});
</script>

<style scoped>
.debug-container {
  padding: 20px;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin: 10px;
}
</style>