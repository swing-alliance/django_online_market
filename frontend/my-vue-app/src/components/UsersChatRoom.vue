<template>
  <div class="debug-container">
    <h2>聊天室调试信息</h2>
    <hr />
    <p><strong>我的数据库 ID (myId):</strong> {{ myId }}</p>
    <p><strong>好友账号ID (friendId):</strong> {{ friendId }}</p>
    
    <div v-if="!myId" style="color: red;">
      警告：未接收到 myId，请检查跳转逻辑！
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
// 1. 获取当前路由对象
const route = useRoute();

// 2. 使用计算属性获取参数（这样参数变化时会自动更新）
const myId = computed(() => route.params.myId);
const friendId = computed(() => route.params.friendId);
const friendAvatar = computed(() => {
    const rawData = localStorage.getItem('friendAvatarMap'); 
    if (rawData && friendId.value) {
        try {
            const datadict = JSON.parse(rawData);
            const avatar = datadict[friendId.value];
            return avatar;
        } catch (e) {
            return null;
        }
    }
    return null;
});
// 3. 在控制台打印调试信息
onMounted(() => {
  console.log('--- 聊天室组件已加载 ---');
  console.log("朋友的头像地址是:", friendAvatar.value);
  console.log('我的 ID:', myId.value);
  console.log('好友 ID:', friendId.value);
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