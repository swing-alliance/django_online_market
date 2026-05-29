<template>
  <div class="chat-container">
    <div class="chat-header">
      <button @click="goBack" class="back-btn">
        <i class="ri-arrow-left-line"></i> 返回
      </button>
      <div class="room-info">
        <i class="ri-team-line room-icon"></i>
        <span class="room-name">{{ groupId }}</span>
      </div>
      <button
        @click="fetchChatHistory"
        class="sync-btn"
        :disabled="isHistoryLoading"
      >
        <i
          class="ri-restart-line"
          :class="{ 'spi-loader': isHistoryLoading }"
        ></i>
      </button>
    </div>

    <div class="chat-messages" ref="messageBox">
      <div v-if="isHistoryLoading && messages.length === 0" class="status-tip">
        正在拉取群聊历史记录...
      </div>
      <div v-else-if="messages.length === 0" class="status-tip">
        暂无消息，发送一条消息开始聊天吧！
      </div>

      <div v-else class="message-wrapper">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="message-item"
          :class="{ 'message-self': isSelf(msg.sender__username) }"
        >
          <span class="sender-name">{{ msg.sender__username }}</span>

          <div class="message-bubble">
            <p class="message-text">{{ msg.content }}</p>
            <span class="message-time">{{ formatTime(msg.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-footer">
      <div class="input-wrapper">
        <input
          type="text"
          placeholder="在此输入群消息..."
          v-model="textInput"
          @keyup.enter="sendMessage"
          :disabled="isSending"
        />
        <button
          @click="sendMessage"
          :disabled="!textInput.trim() || isSending"
          class="send-btn"
        >
          <i class="ri-send-plane-2-line" v-if="!isSending"></i>
          <span v-else class="mini-loader"></span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { setupAxiosInterceptor } from "@/utils/AxiosInterceptor.js";
import axios from "axios";

setupAxiosInterceptor();

const historyUrl = "/api/users/get_groupchat_his/";
const sendMsgUrl = "/api/users/user_chat_in_group/";

export default {
  name: "GroupChatRoom",
  data() {
    return {
      groupId: "", // 接收传过来的群聊名字 (如 "技术交流群")
      messages: [], // 存放接口返回的聊天记录数组
      textInput: "", // 双向绑定输入框文本
      isHistoryLoading: false,
      isSending: false,
      currentUser: "", // 当前登录用户的用户名
    };
  },
  mounted() {
    // 从 URL 的 Query 参数获取群聊名称
    this.groupId = this.$route.query.group_id || "未知群聊";

    // 从本地存储读取当前用户名，用于右侧绿色气泡判定区分
    this.currentUser = localStorage.getItem("current_username") || "";

    // 自动加载聊天记录
    this.fetchChatHistory();
  },
  methods: {
    // 📌 异步拉取群聊历史记录 (对应 get_groupchat_his)
    async fetchChatHistory() {
      if (!this.groupId) return;
      this.isHistoryLoading = true;
      try {
        const response = await axios.get(historyUrl, {
          params: { group_id: this.groupId }, // 传 query_params
        });
        if (response.data.status === "success") {
          this.messages = response.data.messages || [];
          this.scrollToBottom(); // 滚动到最底部最新消息
        }
      } catch (error) {
        console.error("加载聊天历史失败:", error);
      } finally {
        this.isHistoryLoading = false;
      }
    },

    // 📌 异步发送群聊消息 (对应 user_chat_in_group)
    async sendMessage() {
      const content = this.textInput.trim();
      if (!content || this.isSending) return;

      this.isSending = true;
      try {
        const response = await axios.post(sendMsgUrl, {
          group_id: this.groupId,
          content: content,
        });

        if (response.data.status === "success") {
          // 发送成功后在本地数组追加一条渲染，提供零延迟交互感
          this.messages.push({
            sender__username: this.currentUser || "我",
            content: content,
            created_at: new Date().toISOString(),
          });
          this.textInput = ""; // 清空输入框
          this.scrollToBottom();
        }
      } catch (error) {
        console.error("发送消息失败:", error);
      } finally {
        this.isSending = false;
      }
    },

    // 判定是否是自己发送的消息
    isSelf(senderName) {
      return senderName === this.currentUser;
    },

    // 格式化历史消息的时间格式 (显示 时:分)
    formatTime(isoString) {
      if (!isoString) return "";
      const date = new Date(isoString);
      return date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });
    },

    // 自动滑动至底部
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messageBox;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    },

    goBack() {
      this.$router.back();
    },
  },
};
</script>

<style scoped>
@import url("https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css");

.chat-container {
  max-width: 600px;
  height: 80vh;
  margin: 30px auto;
  background: #f1f5f9;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: "Inter", sans-serif;
}

/* 顶栏配置 */
.chat-header {
  background: white;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
}
.back-btn {
  background: #f8fafc;
  color: #64748b;
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}
.back-btn:hover {
  background: #e2e8f0;
  color: #0f172a;
}
.room-info {
  display: flex;
  align-items: center;
  gap: 8px;
}
.room-icon {
  font-size: 1.2rem;
  color: #6366f1;
}
.room-name {
  font-weight: 700;
  color: #1e293b;
  font-size: 1.1rem;
}
.sync-btn {
  background: transparent;
  color: #94a3b8;
  font-size: 1.2rem;
  padding: 6px;
}
.sync-btn:hover {
  color: #6366f1;
}

/* 聊天面板消息流 */
.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #f8fafc;
}
.status-tip {
  text-align: center;
  color: #94a3b8;
  font-size: 0.85rem;
  padding-top: 40px;
}
.message-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 他人消息样式（居左） */
.message-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  max-width: 80%;
}
.sender-name {
  font-size: 0.75rem;
  color: #64748b;
  margin-bottom: 4px;
  margin-left: 4px;
}
.message-bubble {
  background: white;
  color: #334155;
  padding: 11px 16px;
  border-radius: 4px 16px 16px 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.01);
}
.message-text {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.4;
  word-break: break-all;
}
.message-time {
  font-size: 0.7rem;
  color: #cbd5e1;
  display: block;
  text-align: right;
  margin-top: 4px;
}

/* 📌 核心样式：我自己发送的消息靠右展示，气泡着色 */
.message-item.message-self {
  align-self: flex-end;
  align-items: flex-end;
}
.message-item.message-self .sender-name {
  margin-right: 4px;
  margin-left: 0;
}
.message-item.message-self .message-bubble {
  background: #10b981; /* 精美的翡翠绿 */
  color: white;
  border-radius: 16px 4px 16px 16px;
}
.message-item.message-self .message-time {
  color: rgba(255, 255, 255, 0.7);
}

/* 底部功能盘 */
.chat-footer {
  background: white;
  padding: 16px 20px;
  border-top: 1px solid #e2e8f0;
}
.input-wrapper {
  display: flex;
  background: #f1f5f9;
  border-radius: 12px;
  padding: 6px 6px 6px 14px;
  align-items: center;
}
input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 0.95rem;
  color: #334155;
  padding: 8px 0;
}
.send-btn {
  background: #6366f1;
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.1rem;
  transition: background 0.2s;
}
.send-btn:hover:not(:disabled) {
  background: #4f46e5;
}
.send-btn:disabled {
  background: #cbd5e1;
}

.spi-loader {
  display: inline-block;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
