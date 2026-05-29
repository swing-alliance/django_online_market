<template>
  <div class="social-container">
    <div class="main-content">
      <div class="card joined-groups-section">
        <div class="header-refresh">
          <h2>我加入的群聊</h2>
          <button
            @click="fetchJoinedGroups"
            class="refresh-btn"
            :disabled="isFetchingGroups"
          >
            <i
              class="ri-refresh-line"
              :class="{ 'spi-loader': isFetchingGroups }"
            ></i>
          </button>
        </div>

        <div v-if="isFetchingGroups" class="loading-text">
          正在努力加载群聊列表...
        </div>

        <div v-else-if="joinedGroups.length === 0" class="empty-text">
          你目前还没有加入或者创建任何群聊喔 ~
        </div>

        <div v-else class="group-list">
          <div
            v-for="group in joinedGroups"
            :key="group"
            class="group-item"
            @click="navToGroupRoom(group)"
          >
            <div class="group-info">
              <i class="ri-team-line group-icon"></i>
              <span class="group-title">{{ group }}</span>
            </div>

            <div class="group-actions">
              <button
                class="action-btn member-btn"
                title="查看群成员"
                @click.stop="showGroupMembers(group)"
              >
                <i class="ri-user-shared-line"></i>
              </button>

              <button
                class="action-btn delete-btn"
                title="退出或解散群聊"
                @click.stop="confirmDeleteOrExit(group)"
              >
                <i class="ri-logout-box-r-line"></i>
              </button>

              <i class="ri-arrow-right-s-line enter-arrow"></i>
            </div>
          </div>
        </div>
      </div>
    </div>

    <transition name="fade">
      <div v-if="showModal" class="modal-overlay" @click="closeModal">
        <div class="modal-card" @click.stop>
          <div class="modal-header">
            <h3>
              <i class="ri-group-line"></i>【{{ activeGroupName }}】群成员
            </h3>
            <button class="close-btn" @click="closeModal">×</button>
          </div>

          <div class="modal-body">
            <div v-if="isLoadingMembers" class="mini-loading">
              <i class="ri-loader-4-line spi-loader"></i> 正在读取成员数据...
            </div>
            <div v-else class="member-grid">
              <div
                v-for="member in currentGroupMembers"
                :key="member.id"
                class="member-tag"
              >
                <div class="avatar-stub">
                  {{ member.username.charAt(0).toUpperCase() }}
                </div>
                <div class="member-meta">
                  <span class="m-name">{{ member.username }}</span>
                  <span class="m-id">ID: {{ member.id }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { setupAxiosInterceptor } from "@/utils/AxiosInterceptor.js";
import axios from "axios";

setupAxiosInterceptor();

const getjoinedgroupchats = "/api/users/user_see_groupchat/";
const getGroupMembersUrl = "/api/users/user_fetch_friend_ids/";
// 📌 新增：对应后端的删除/退出接口URL
const deleteOrExitUrl = "/api/users/delete_group_chat/";

export default {
  name: "GroupChatMain",
  data() {
    return {
      joinedGroups: [],
      isFetchingGroups: false,

      showModal: false,
      activeGroupName: "",
      isLoadingMembers: false,
      currentGroupMembers: [],
    };
  },
  mounted() {
    this.fetchJoinedGroups();
  },
  methods: {
    async fetchJoinedGroups() {
      this.isFetchingGroups = true;
      try {
        const response = await axios.get(getjoinedgroupchats);
        this.joinedGroups = response.data.group_chats || response.data || [];
      } catch (error) {
        console.error("无法获取群聊列表:", error);
      } finally {
        this.isFetchingGroups = false;
      }
    },

    navToGroupRoom(groupName) {
      this.$router.push({
        name: "GroupChatRoom",
        query: { group_id: groupName },
      });
    },

    // 📌 新增：点击退出/解散时的二次确认逻辑
    async confirmDeleteOrExit(groupName) {
      const isConfirmed = confirm(
        `确定要离开群聊【${groupName}】吗？\n(如果您是群主将直接解散该群，普通成员则为退出)`,
      );
      if (!isConfirmed) return;

      try {
        const response = await axios.post(deleteOrExitUrl, {
          group_id: groupName,
        });
        if (response.data.status === "success") {
          alert(response.data.message);
          // 页面原地无刷新，直接过滤掉被删除/退出的群，体验极佳
          this.joinedGroups = this.joinedGroups.filter((g) => g !== groupName);
        }
      } catch (error) {
        alert("操作失败：" + (error.response?.data?.error || "服务器开小差了"));
      }
    },

    async showGroupMembers(groupName) {
      this.activeGroupName = groupName;
      this.showModal = true;
      this.isLoadingMembers = true;
      try {
        const response = await axios.get(getGroupMembersUrl);
        this.currentGroupMembers = response.data.friends || [];
      } catch (error) {
        console.error("拉取群成员失败:", error);
      } finally {
        this.isLoadingMembers = false;
      }
    },

    closeModal() {
      this.showModal = false;
      this.currentGroupMembers = [];
    },
  },
};
</script>

<style scoped>
@import url("https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css");

.social-container {
  max-width: 600px;
  margin: 40px auto;
  font-family: "Inter", -apple-system, sans-serif;
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
  margin-bottom: 25px;
}
.header-refresh {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
h2 {
  margin: 0;
  font-size: 1.4rem;
  color: #1a1a1a;
}
button {
  border: none;
  cursor: pointer;
  transition: all 0.3s;
}
button:disabled {
  cursor: not-allowed;
}

.refresh-btn {
  background: transparent;
  color: #64748b;
  padding: 8px;
  border-radius: 50%;
  font-size: 1.2rem;
}
.refresh-btn:hover:not(:disabled) {
  background: #f1f5f9;
  color: #6366f1;
}

.group-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.group-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  background: #f8fafc;
  border: 1px solid #edf2f7;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}
.group-item:hover {
  background: #ffffff;
  border-color: #6366f1;
  box-shadow: 0 6px 15px rgba(99, 102, 241, 0.08);
  transform: translateX(4px);
}

.group-info {
  display: flex;
  align-items: center;
  gap: 12px;
}
.group-icon {
  font-size: 20px;
  color: #6366f1;
  background: #eeebff;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.2s;
}
.group-item:hover .group-icon {
  background: #6366f1;
  color: #ffffff;
}
.group-title {
  font-weight: 600;
  color: #334155;
}

.group-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 📌 优化：动作控制按钮通用样式 */
.action-btn {
  color: #475569;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.05rem;
}
.member-btn {
  background: #f1f5f9;
}
.member-btn:hover {
  background: #e0e7ff;
  color: #4f46e5;
}

/* 📌 新增：删除/退群按钮特殊警告色 */
.delete-btn {
  background: #fee2e2;
  color: #ef4444;
}
.delete-btn:hover {
  background: #ef4444;
  color: white;
}

.enter-arrow {
  font-size: 18px;
  color: #94a3b8;
  transition: all 0.2s;
}
.group-item:hover .enter-arrow {
  color: #6366f1;
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

.loading-text,
.empty-text {
  font-size: 0.9rem;
  color: #94a3b8;
  text-align: center;
  padding: 30px 0;
  letter-spacing: 0.5px;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}
.modal-card {
  background: white;
  width: 90%;
  max-width: 440px;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.modal-header h3 {
  margin: 0;
  font-size: 1.15rem;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 6px;
}
.close-btn {
  background: transparent;
  font-size: 1.5rem;
  color: #94a3b8;
  padding: 0 5px;
}
.close-btn:hover {
  color: #475569;
}
.mini-loading {
  text-align: center;
  color: #64748b;
  padding: 30px 0;
  font-size: 0.9rem;
}
.member-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  max-height: 260px;
  overflow-y: auto;
  padding-right: 4px;
}
.member-tag {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #f8fafc;
  border-radius: 10px;
  border: 1px solid #f1f5f9;
}
.avatar-stub {
  width: 32px;
  height: 32px;
  background: #6366f1;
  color: white;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: 700;
  font-size: 0.85rem;
}
.member-meta {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.m-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #334155;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.m-id {
  font-size: 0.75rem;
  color: #94a3b8;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
