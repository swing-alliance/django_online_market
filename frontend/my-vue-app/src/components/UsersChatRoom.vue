<template>
  <div class="chat-app-wrapper">
     <UsersChatLines 
      :myAvatarUrl="myAvatarUrl" 
      :friendAvatar="friendAvatar" 
      :messageQueue="messageQueue" 
    />   

    

    <div class="input-area">
      <input 
        v-model="messagebox" 
        type="text" 
        placeholder="请输入内容..." 
        @keyup.enter="handleSend"
      />
      <button @click="handleSend">发送</button>
    </div>
  </div>
</template>

<script setup>
//对话记录一定按照时间戳插入，以保证顺序正确
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import wsService from '@/utils/websoketservice.js';
import UsersChatLines from './UsersChatLines.vue'; // 导入刚才写的组件
import {setupAxiosInterceptor} from '@/utils/AxiosInterceptor.js';
import { useMessageStore } from '@/stores/WsStore.js';
import { watch } from 'vue';
const messageStore = useMessageStore();
setupAxiosInterceptor();
const route = useRoute();
const messagebox = ref('');
const messageQueue = ref([]); // 核心：对话队列

// ID 获取


// 1. 发送逻辑
const handleSend = () => {
    if (!messagebox.value.trim()) return;
    const nowTimestamp = (Date.now() / 1000).toString();
    const tempId = 'local_' + Date.now();
    const msgPayload = {
        tempId: tempId,
        sender_id: myId.value,
        receiver_id: friendId.value,
        type: "sendmessage",
        content: messagebox.value,
        timestamp: nowTimestamp
    };
    // ✅ 调用有序插入
    insertMessage({
        id: tempId,
        words: messagebox.value,
        timestamp: nowTimestamp,
        type: 'mine',
        status: 'sending'
    });
    wsService.send(msgPayload);
    messagebox.value = '';
};

// 2. 接收逻辑：你需要给 wsService 增加一个回调或者使用事件监听
// 这里假设你在 wsService.receive 里处理逻辑，或者通过 mitt 等发布订阅机制
// 简单起见，如果你在 wsService 里定义了 receive 回调：

watch(
  // 1. 明确监听数组的长度
  () => messageStore.receivedQueue.length, 
  (newLength) => {
    // 2. 只要长度大于 0，说明有新消息进来
    if (newLength > 0) {
      // 3. 循环处理队列中的所有消息（防止瞬间涌入多条）
      while (messageStore.receivedQueue.length > 0) {
        // 4. 从 Pinia 队列中“取出”第一条消息（同时会从原数组删除）
        const latestMsg = messageStore.receivedQueue.shift(); 
        console.log('⚡ 正在处理并移除 Pinia 缓存:', latestMsg);
        parsereceivedmessage(latestMsg);
      }
    }
  }
);
    

const parsereceivedmessage = (remoteData) => { 
    // ✅ 调用有序插入
    insertMessage({
        id: `hist_${remoteData.timestamp}_${Math.random()}`,
        words: remoteData.content,
        timestamp: remoteData.timestamp,
        type: 'friend'
    });
};


const insertMessage = (newMessage) => {
    // 1. 查找插入位置 (使用二进制搜索或简单的 findIndex)
    const index = messageQueue.value.findIndex(msg => 
        parseFloat(msg.timestamp) > parseFloat(newMessage.timestamp)
    );

    if (index === -1) {
        // 如果没找到比它晚的，说明它是目前最晚的，直接放最后
        messageQueue.value.push(newMessage);
    } else {
        // 插入到比它晚的消息之前
        messageQueue.value.splice(index, 0, newMessage);
    }
    // 2. 去重逻辑（防止历史记录拉取和实时推送重复）
    // 如果你有唯一 ID，可以在这里过滤掉重复 ID
};



const myId = computed(() => route.params.myId);
const friendId = computed(() => route.params.friendId);
// 头像逻辑 (保持你原来的)
const defaultImg = '/image/default_avatar.png';
const myAvatarUrl = computed(() => localStorage.getItem('myavatar') || defaultImg);
const friendAvatar = computed(() => {
    const rawData = localStorage.getItem('friendAvatarMap');
    if (rawData && friendId.value) {
        const datadict = JSON.parse(rawData);
        return datadict[friendId.value] || defaultImg;
    }
    return defaultImg;
});

// 获取头像的方法
const getmyavatar = async () => {
    try {
        const response = await axios.get('/api/users/get_avatar_by_id/', {
            params: { account_id: localStorage.getItem('user_id') }
        });
        localStorage.setItem('myavatar', response.data.avatar_url || defaultImg);
    } catch (error) {
        console.error('获取头像失败:', error);
    }
};

const fetchhistory = async () => {
    try {
        const response = await axios.get('/api/users/get_chat_history/', {
            params: {
                // 注意：后端是用 request.user.id，所以这里传 friend_id 即可
                friend_id: friendId.value
            }
        });
        const historyMessages = response.data || [];
        // 清空当前队列
        messageQueue.value = [];
        historyMessages.forEach(msg => {
            // ✅ 核心逻辑：判断字段名来确定身份
            const isMine = Object.prototype.hasOwnProperty.call(msg, 'myword');
            insertMessage({
                // 因为后端没传 ID，暂时用时间戳作为 ID
                id: `hist_${msg.timestamp}_${Math.random()}`, 
                words: isMine ? msg.myword : msg.friendword,
                timestamp: msg.timestamp,
                type: isMine ? 'mine' : 'friend'
            });
        });
    } catch (error) {
        console.error('获取聊天记录失败:', error);
    }
};

onMounted(() => {
    
    getmyavatar();
    fetchhistory();
});
</script>

<style scoped>
.chat-app-wrapper {
  display: flex;
  flex-direction: column;
  height: 100vh;      /* 强制等于屏幕高度 */
  overflow: hidden;   /* 严禁被子元素撑开 */
}
.input-area {
  /* 居中 + 宽度控制 */
  width: 60%;
  max-width: 600px;           /* 可选：防止超大屏幕太宽 */
  margin: 0 auto;             /* 水平居中 */
  padding: 12px 16px;         /* 建议加一点内边距，体验更好 */

  /* 布局：输入框和按钮横向排列 */
  display: flex;
  gap: 10px;                  /* 输入框和按钮之间的间距 */

  /* 可选：垂直居中（如果外面有高度约束） */
  /* align-items: center; */

  /* 去掉背景色（默认就是透明） */
  background: transparent;

  /* 文字不加粗 */
  font-weight: normal;
}

/* 输入框样式优化 */
.input-area input {
  flex: 1;                    /* 输入框占满剩余空间 */
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 16px;
  font-weight: normal;        /* 明确不加粗 */
  outline: none;
}

.input-area input:focus {
  border-color: #3f4040;      /* 可选：聚焦时蓝色边框（Element UI 风格） */
  box-shadow: 0 0 0 2px rgba(25, 25, 26, 0.2);
}

/* 按钮样式优化 */
.input-area button {
  padding: 0 24px;
  background: #747373;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: normal;        /* 不加粗 */
  font-size: 15px;
}

.input-area button:hover {
  background: #363636;
}

</style>