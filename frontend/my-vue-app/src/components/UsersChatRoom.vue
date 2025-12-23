<template>
  <div class="debug-container">
    <h2>聊天室调试信息</h2>
    <hr />
    <p><strong>我的数据库 ID (mydatabaseId):</strong> {{ mydatabaseId }}</p>
    <p><strong>好友账号名称 (friendAccountName):</strong> {{ friendAccountName }}</p>
    
    <div v-if="!mydatabaseId" style="color: red;">
      警告：未接收到 mydatabaseId，请检查跳转逻辑！
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';

// 1. 获取当前路由对象
const route = useRoute();

// 2. 使用计算属性获取参数（这样参数变化时会自动更新）
const mydatabaseId = computed(() => route.params.mydatabaseId);
const friendAccountName = computed(() => route.params.friendAccountName);

// 3. 在控制台打印调试信息
onMounted(() => {
  console.log('--- 聊天室组件已加载 ---');
  console.log('路由对象参数 (params):', route.params);
  console.log('我的 ID:', mydatabaseId.value);
  console.log('好友名称:', friendAccountName.value);
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