<template>
    <div>
      <div class="chat-box"></div>
    
        <h2>向{{targetis}}聊天</h2>
        <div v-if="targetOnlineStatus" :class="targetOnlineStatus === 'online' ? 'status-online' : 'status-offline'">
        {{ targetOnlineStatus === 'online' ? '🟢 在线' : '⚪ 离线' }}
        </div>
    </div>
</template>
<script setup>

// const meis = props.getmyid;
const targetis = props.targetId;
const props = defineProps({
  targetId: {
    type: String,
    required: true
  },
  getmyid: {
    type: String,
    required: true
  }
});

</script>