<template>
  <div class="chat-container" ref="chatBox">
    <div v-for="(msg, index) in props.messageQueue" :key="index" 
         :class="['message-row', msg.type === 'mine' ? 'row-right' : 'row-left']">
      
      <img :src="msg.type === 'mine' ? props.myAvatarUrl : props.friendAvatar" class="avatar" />

      <div class="message-content">
        <div class="timestamp">{{ formatTime(msg.timestamp) }}</div>
        <div class="bubble">
          {{ msg.words }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, ref, onUpdated, nextTick } from 'vue';

// 定义 Props
const props = defineProps({
  myAvatarUrl: String,
  friendAvatar: String,
  messageQueue: {
    type: Array,
    default: () => []
  }
});

const chatBox = ref(null);
/**
 * 自动滚动逻辑
 * 监听内容更新后，将滚动条拉到底部
 */
const scrollToBottom = async () => {
  await nextTick(); // 等待 DOM 更新完成
  if (chatBox.value) {
    chatBox.value.scrollTop = chatBox.value.scrollHeight;
  }
};

// 每次队列更新（收到新消息），触发滚动
onUpdated(() => {
  scrollToBottom();
});

const formatTime = (ts) => {
  // 格式化时间
  if (!ts) return '';
  const numericTs = parseFloat(ts);
  const date = new Date(numericTs < 10000000000 ? numericTs * 1000 : numericTs);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false // 使用24小时制，如果想用AM/PM就改为true
  });
};
</script>
<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 15px;
  background: #f5f5f5;
  height: 80vh;                /* 设置高度占视口的 80% */
  width: 60%;                  /* 宽度占父容器的 60%，留出 20% 边距 */
  margin: 0 auto;              /* 水平居中，确保左右各有 20% 的边距 */
  overflow-y: auto;
  box-sizing: border-box;      /* 包含 padding 和 border 计算在内 */
}

.message-row {
  display: flex;
  align-items: flex-start;
  max-width: 80%;
}

/* 对方的话：靠左，头像在左 */
.row-left {
  align-self: flex-start;
  flex-direction: row; 
}

/* 我的话：靠右，头像在右 */
.row-right {
  align-self: flex-end;
  flex-direction: row-reverse; /* 核心：翻转头像和气泡的位置 */
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  margin: 0 10px;
}

.message-content {
  display: flex;
  flex-direction: column;
}

.row-left .message-content { align-items: flex-start; }
.row-right .message-content { align-items: flex-end; }

.timestamp {
  font-size: 11px;
  color: #999;
  margin-bottom: 4px;
}

.bubble {
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-all;
  position: relative;
}

/* 气泡颜色区分 */
.row-left .bubble {
  background-color: #fff;
  color: #333;
  border: 1px solid #ddd;
}

.row-right .bubble {
  background-color: #95ec69; /* 经典微信绿 */
  color: #000;
}
</style>