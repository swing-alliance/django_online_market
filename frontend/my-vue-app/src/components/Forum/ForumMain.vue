<template>
  <div class="posts-page">
    <div class="header">
      <button class="back-btn" @click="$router.back()">
        <i class="ri-arrow-left-line"></i> 返回社区
      </button>
      <h1 class="page-title">社区动态</h1>
      <button class="post-trigger-btn" @click="goToCreatePost">
        <i class="ri-add-line"></i> 发布新帖
      </button>
    </div>

    <div class="main-layout">
      <div class="posts-area">
        <div class="posts-grid" v-if="posts.length > 0">
          <div
            v-for="post in posts"
            :key="post.id"
            class="post-card"
            @contextmenu.prevent="deletePost(post.id)"
            title="右键点击删除帖子"
          >
            <img
              v-if="post.cover_image"
              :src="post.cover_image"
              class="post-cover"
            />
            <div class="post-content">
              <h3 class="post-title">{{ post.title }}</h3>
              <div
                class="post-text"
                :class="{ expanded: expandedPosts[post.id] }"
              >
                <p>{{ post.content }}</p>
              </div>
              <button
                v-if="post.content && post.content.length > 120"
                class="toggle-btn"
                @click.stop="toggleContent(post.id)"
              >
                {{ expandedPosts[post.id] ? "收起" : "展开全文" }}
              </button>
              <div class="post-footer">
                <div class="footer-left">
                  <span class="author">
                    <i class="ri-user-smile-line"></i> {{ post.author }}
                  </span>
                  <span class="meta">
                    <i class="ri-calendar-line"></i> {{ post.created_at }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <i class="ri-quill-pen-line"></i>
          <p>暂无动态，快去发布第一条帖子吧！</p>
        </div>
      </div>

      <aside class="sidebar">
        <div class="sidebar-header">
          <h3>社区成员</h3>
          <span class="member-count">{{ members.length }} 人</span>
        </div>

        <div class="member-list">
          <div
            v-for="m in members"
            :key="m.id"
            class="member-item"
            @contextmenu.prevent="openBanModal(m)"
            title="右键点击以封禁该用户"
          >
            <div class="member-avatar">
              <i class="ri-user-fill"></i>
            </div>
            <span class="member-name">{{ m.username }}</span>
          </div>
        </div>

        <div class="sidebar-footer">
          <button class="quit-btn" @click="quitForum">
            <i class="ri-logout-box-r-line"></i> 退出论坛
          </button>
        </div>
      </aside>
    </div>

    <div
      v-if="showBanModal"
      class="modal-overlay"
      @click.self="showBanModal = false"
    >
      <BanUser
        :forum_id="forumId"
        :user_to_ban="selectedMember"
        @close="showBanModal = false"
        @success="fetchMembers"
      />
    </div>
  </div>
</template>

<script setup>
import axios from "axios";
import { onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import BanUser from "./BanUser.vue";

const route = useRoute();
const router = useRouter();

const posts = ref([]);
const members = ref([]);
const showBanModal = ref(false);
const selectedMember = ref(null);
const forumId = route.params.forum_id;
const expandedPosts = reactive({});

const goToCreatePost = () =>
  router.push({ name: "CreatePost", params: { forum_id: forumId } });

const toggleContent = (postId) => {
  expandedPosts[postId] = !expandedPosts[postId];
};

const fetchPosts = async () => {
  try {
    const { data } = await axios.get(
      `/api/users/get_all_posts/?forum_id=${forumId}`,
    );
    posts.value = data.posts || [];
  } catch (err) {
    console.error("加载帖子失败:", err);
  }
};

const fetchMembers = async () => {
  try {
    const { data } = await axios.get(`/api/users/forumsmembers/${forumId}/`);
    members.value = data.members || [];
  } catch (err) {
    console.error("加载成员失败:", err);
  }
};

const deletePost = async (postId) => {
  if (!confirm("确定要删除这条帖子吗？此操作不可恢复。")) return;
  try {
    await axios.delete(`/api/users/delete_post/${postId}/`);
    posts.value = posts.value.filter((p) => p.id !== postId);
  } catch (err) {
    alert("删除失败，无权限或帖子不存在");
  }
};

const openBanModal = (member) => {
  selectedMember.value = member;
  showBanModal.value = true;
};

// 新增：退出论坛功能逻辑
const quitForum = async () => {
  if (!confirm("确定要退出该论坛吗？此操作不可逆。")) return;
  try {
    // 这里的 URL 请替换为你实际配置在 urls.py 中的路由
    const response = await axios.post(`/api/users/forum/quit/`, {
      forum_id: forumId,
    });
    alert(response.data.message || "已成功退出论坛");
    // 退出成功后返回上一页或社区大厅
    router.back();
  } catch (err) {
    console.error("退出失败:", err);
    alert(err.response?.data?.detail || "退出论坛失败");
  }
};

onMounted(() => {
  fetchPosts();
  fetchMembers();
});
</script>

<style scoped>
@import url("https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css");

/* 基础重置与布局 */
.posts-page {
  padding: 30px 10% 0;
  background: #f8fafc;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica,
    Arial, sans-serif;
}

/* 头部样式 */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 24px;
}

.page-title {
  flex: 1;
  text-align: center;
  font-size: 1.75rem;
  color: #0f172a;
  margin: 0;
  font-weight: 700;
}

/* 按钮统一美化 */
.back-btn {
  background: white;
  border: 1px solid #e2e8f0;
  color: #64748b;
  padding: 8px 16px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
.back-btn:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.post-trigger-btn {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  transition: all 0.2s ease;
}
.post-trigger-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
}

/* 主体布局 */
.main-layout {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 30px;
  flex: 1;
  min-height: 0;
  overflow: hidden;
  padding-bottom: 30px;
}

/* 滚动区域 */
.posts-area {
  overflow-y: auto;
  padding-right: 8px;
}

/* Webkit 自定义滚动条 (针对左侧帖子区) */
.posts-area::-webkit-scrollbar {
  width: 6px;
}
.posts-area::-webkit-scrollbar-track {
  background: transparent;
}
.posts-area::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
.posts-area::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* 帖子卡片美化 */
.post-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #f1f5f9;
  display: flex;
  gap: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}
.post-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
  border-color: #e2e8f0;
}
.post-cover {
  width: 140px;
  height: 140px;
  object-fit: cover;
  border-radius: 12px;
  flex-shrink: 0;
}
.post-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.post-title {
  margin: 0 0 12px 0;
  font-size: 1.25rem;
  color: #1e293b;
}
.post-text {
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  line-height: 1.6;
  color: #475569;
  font-size: 0.95rem;
  flex: 1;
}
.post-text.expanded {
  display: block;
}
.toggle-btn {
  background: none;
  border: none;
  color: #6366f1;
  font-weight: 600;
  padding: 8px 0;
  margin-top: 4px;
  cursor: pointer;
  text-align: left;
  font-size: 0.9rem;
  align-self: flex-start;
}
.toggle-btn:hover {
  text-decoration: underline;
}
.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed #e2e8f0;
  font-size: 0.85rem;
  color: #64748b;
}
.footer-left {
  display: flex;
  gap: 16px;
}

/* 空状态美化 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #94a3b8;
  background: white;
  border-radius: 16px;
  border: 1px dashed #cbd5e1;
}
.empty-state i {
  font-size: 3rem;
  color: #cbd5e1;
  margin-bottom: 12px;
  display: block;
}

/* ---------------- 侧边栏及成员列表美化 (带底部固定按钮) ---------------- */
.sidebar {
  background: white;
  padding: 24px;
  border-radius: 16px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column; /* 改为 Flex 布局以便固定底部按钮 */
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f8fafc;
  flex-shrink: 0;
}
.sidebar-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #1e293b;
}
.member-count {
  background: #f1f5f9;
  color: #475569;
  padding: 2px 8px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

/* 成员列表滚动区 */
.member-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  overflow-y: auto; /* 转移滚动属性到这里 */
  padding-right: 6px;
}

/* 侧边栏成员列表滚动条美化 */
.member-list::-webkit-scrollbar {
  width: 4px;
}
.member-list::-webkit-scrollbar-track {
  background: transparent;
}
.member-list::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
.member-list::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.member-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s ease;
}
.member-item:hover {
  background: #f8fafc;
}
.member-avatar {
  width: 36px;
  height: 36px;
  background: #e0e7ff;
  color: #6366f1;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}
.member-name {
  font-weight: 500;
  color: #334155;
  font-size: 0.95rem;
}

/* 右下角退出按钮区域 */
.sidebar-footer {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed #e2e8f0;
  flex-shrink: 0;
}

.quit-btn {
  width: 100%;
  padding: 12px;
  background: #fef2f2;
  color: #ef4444;
  border: 1px solid #fecaca;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.quit-btn:hover {
  background: #ef4444;
  color: white;
  border-color: #ef4444;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

/* 弹窗遮罩 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
</style>
