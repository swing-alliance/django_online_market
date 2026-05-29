<template>
  <div class="social-container">
    <div class="main-content">
      <div class="card create-group-section">
        <div class="header-back">
          <button @click="goBack" class="back-btn">
            <i class="ri-arrow-left-line"></i> 返回
          </button>
          <h2>一键发起群聊</h2>
        </div>

        <div class="input-group group-name-input">
          <input
            type="text"
            placeholder="请输入群聊名称..."
            v-model="groupName"
          />
        </div>

        <div class="friend-select-box">
          <p class="section-title">选择要拉入群聊的好友：</p>
          <div v-if="isFetchingFriends" class="loading-text">
            正在加载好友列表...
          </div>
          <div v-else-if="friends.length === 0" class="empty-text">
            暂无可用好友，快去添加好友吧！
          </div>

          <div v-else class="checkbox-grid">
            <label
              v-for="friend in friends"
              :key="friend.id"
              class="checkbox-label"
            >
              <input
                type="checkbox"
                :value="friend.id"
                v-model="selectedFriendIds"
              />
              <span class="friend-name">用户名: {{ friend.username }}</span>
            </label>
          </div>
        </div>

        <button
          @click="createGroupChat"
          class="submit-group-btn"
          :disabled="!groupName.trim() || isCreatingGroup"
        >
          {{ isCreatingGroup ? "正在建群..." : "创建并邀请加入群聊" }}
        </button>

        <transition name="fade">
          <p
            v-if="groupMessage"
            :class="isGroupError ? 'error-message' : 'success-message'"
          >
            {{ groupMessage }}
          </p>
        </transition>
      </div>
    </div>
  </div>
</template>

<script>
import { setupAxiosInterceptor } from "@/utils/AxiosInterceptor.js";
import axios from "axios";

setupAxiosInterceptor();

const create_group_chat_url = "/api/users/user_launch_groupchat/";
const get_friend_id_url = "/api/users/user_fetch_friend_ids/";

export default {
  name: "TryCreateGroup",
  data() {
    return {
      groupName: "",
      friends: [], // 从后端拉取到的好友字典列表：[{id: 2, username: 'xxx'}, ...]
      selectedFriendIds: [], // 暗地里勾选并准备发送给后端的数字 ID 数组
      isFetchingFriends: false,
      isCreatingGroup: false,
      groupMessage: "",
      isGroupError: false,
    };
  },
  mounted() {
    // 页面一加载，自动去捞取当前用户的好友数据
    this.fetchFriendIds();
  },
  methods: {
    // 获取好友列表数据（包含 ID 和 Username）
    async fetchFriendIds() {
      this.isFetchingFriends = true;
      try {
        const response = await axios.get(get_friend_id_url);
        this.friends = response.data.friends || [];
      } catch (error) {
        console.error("加载好友列表失败", error);
      } finally {
        this.isFetchingFriends = false;
      }
    },

    // 发起群聊请求
    async createGroupChat() {
      if (!this.groupName.trim()) return;
      this.groupMessage = "";
      this.isCreatingGroup = true;

      // 发送标准的纯数字 ID 数组，严丝合缝匹配你的后端接口
      const payload = {
        group_id: this.groupName.trim(),
        user_ids: this.selectedFriendIds,
      };

      try {
        const response = await axios.post(create_group_chat_url, payload);
        this.isGroupError = false;
        this.groupMessage = "🚀 " + (response.data.message || "建群成功！");

        // 成功后清空表单
        this.groupName = "";
        this.selectedFriendIds = [];
      } catch (error) {
        this.isGroupError = true;
        this.groupMessage =
          "❌ " + (error.response?.data?.error || "发起群聊失败");
      } finally {
        this.isCreatingGroup = false;
      }
    },
    // 返回上一页
    goBack() {
      this.$router.back();
    },
  },
};
</script>

<style scoped>
@import url("https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css");

.social-container {
  max-width: 600px;
  margin: 40px auto;
  font-family: "Inter", sans-serif;
  color: #2c3e50;
  padding: 0 20px;
}
.main-content {
  width: 100%;
}
.card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.header-back {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 25px;
}
h2 {
  margin: 0;
  font-size: 1.4rem;
  color: #1a1a1a;
}

.back-btn {
  background: #f1f5f9;
  color: #475569;
  padding: 8px 14px;
  font-size: 0.85rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
}
.back-btn:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.input-group {
  display: flex;
  gap: 10px;
}
.group-name-input {
  margin-bottom: 20px;
}
input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #eee;
  border-radius: 10px;
  outline: none;
  transition: border-color 0.3s;
  width: 100%;
  box-sizing: border-box;
}
input:focus {
  border-color: #6366f1;
}

.friend-select-box {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 24px;
  border: 1px solid #f1f5f9;
}
.section-title {
  margin: 0 0 12px 0;
  font-weight: 600;
  font-size: 0.95rem;
  color: #475569;
}

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 10px;
  max-height: 160px;
  overflow-y: auto;
}
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.checkbox-label:hover {
  border-color: #6366f1;
  background: #f5f3ff;
}
.friend-name {
  font-size: 0.85rem;
  color: #334155;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.submit-group-btn {
  width: 100%;
  padding: 14px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.3s;
}
.submit-group-btn:hover:not(:disabled) {
  background: #059669;
}
.submit-group-btn:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

.loading-text,
.empty-text {
  font-size: 0.85rem;
  color: #94a3b8;
  text-align: center;
  padding: 15px 0;
}
.success-message {
  color: #10b981;
  margin-top: 15px;
  font-weight: 500;
  text-align: center;
}
.error-message {
  color: #ef4444;
  margin-top: 15px;
  font-weight: 500;
  text-align: center;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
