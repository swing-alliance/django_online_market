import { defineStore } from 'pinia';

export const useMessageStore = defineStore('message', {
  state: () => ({
    // 这就是你要的消息接收队列
    receivedQueue: [], 
    // 存储待处理请求数
    pendingCount: 0
  }),

  actions: {
    handleWsMessage(data) {
    const msgSource = (typeof data === 'string') ? JSON.parse(data) : data;

  if (msgSource.type === 'receivemessage') {
    const { sender_id, receiver_id, content, timestamp } = msgSource;
    const myId = localStorage.getItem('accountID'); 
    const isMine = String(sender_id) === String(myId);
    // 组装并存入响应式队列
    const message = {
      sender_id,
      receiver_id,
      content,
      timestamp,
      // 增加 type 方便你在 CSS 中区分左右气泡
      chatType: isMine ? 'mine' : 'friend' 
    };

    this.receivedQueue.push(message);
  } else {
    console.warn('⚠️ 收到非业务消息或未知类型:', msgSource.type);
  }
},

    // 提供给组件使用的清空方法
    clearQueue() {
      this.receivedQueue = [];
    }
  }
});