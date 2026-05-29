<template>
  <div class="forum-page">
    <div class="hero-section">
      <h1>探索热门社区</h1>
      <p>加入你感兴趣的论坛，与志同道合的人交流。</p>

      <div class="search-wrapper">
        <i class="ri-search-line search-icon"></i>
        <input
          type="text"
          v-model="searchQuery"
          placeholder="搜索论坛名称或描述..."
          class="search-input"
        />
      </div>
    </div>

    <div class="forum-grid">
      <div
        v-for="forum in filteredForums"
        :key="forum.id"
        class="forum-card"
        @click="enterForum(forum.id)"
      >
        <div class="thumb-wrapper">
          <img :src="forum.icon_base64" alt="icon" />
        </div>
        <div class="card-content">
          <h3>{{ forum.name }}</h3>
          <p class="desc">{{ forum.description }}</p>
          <div class="stats">
            <span
              ><i class="ri-user-line"></i> {{ forum.member_count }} 成员</span
            >
            <span><i class="ri-quill-pen-line"></i> {{ forum.creator }}</span>
          </div>
        </div>
        <button class="join-btn" @click.stop="joinForum(forum)">加入</button>
      </div>

      <div v-if="filteredForums.length === 0" class="no-results">
        <i class="ri-search-eye-line"></i>
        <p>未找到匹配的论坛</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from "axios";
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

const forums = ref([]);
const searchQuery = ref("");
const router = useRouter();

// 计算属性：根据搜索词过滤论坛
const filteredForums = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return forums.value.filter(
    (f) =>
      f.name.toLowerCase().includes(query) ||
      f.description.toLowerCase().includes(query),
  );
});

const fetchForums = async () => {
  try {
    const { data } = await axios.get("/api/users/get_ten_forums/");
    forums.value = data.forums || [];
  } catch (err) {
    console.error("加载失败", err);
  }
};

const joinForum = async (forum) => {
  try {
    await axios.post("/api/users/join_forum/", { forum_id: forum.id });
    alert(`成功加入 ${forum.name}！`);
    forum.member_count += 1;
  } catch (err) {
    console.warn("加入操作未成功:", err.response?.data?.detail);
  } finally {
    enterForum(forum.id);
  }
};

const enterForum = (id) => {
  router.push({ name: "ForumMain", params: { forum_id: id } });
};

onMounted(fetchForums);
</script>

<style scoped>
@import url("https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css");

.forum-page {
  padding: 60px 10%;
  background: #f4f7f6;
  min-height: 100vh;
}
.hero-section {
  margin-bottom: 40px;
}
.hero-section h1 {
  font-size: 2.5rem;
  color: #1a1a2e;
  margin-bottom: 10px;
}

/* 搜索框样式 */
.search-wrapper {
  position: relative;
  max-width: 400px;
  margin-top: 20px;
}
.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 1.2rem;
}
.search-input {
  width: 100%;
  padding: 14px 20px 14px 45px;
  border-radius: 30px;
  border: 2px solid #e2e8f0;
  outline: none;
  transition: 0.3s;
  font-size: 1rem;
}
.search-input:focus {
  border-color: #6366f1;
  background: white;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
}

/* 网格样式 */
.forum-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}
.forum-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  cursor: pointer;
  transition: 0.3s;
  border: 1px solid #eef0f2;
}
.forum-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
  border-color: #6366f1;
}

/* 搜索为空的提示 */
.no-results {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px;
  color: #94a3b8;
}
.no-results i {
  font-size: 3rem;
  display: block;
  margin-bottom: 10px;
}

/* 保持原有图标、按钮样式 */
.thumb-wrapper img {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  object-fit: cover;
  background: #f0f0f0;
}
.card-content h3 {
  margin: 0 0 8px 0;
  font-size: 1.1rem;
  color: #333;
}
.desc {
  font-size: 0.9rem;
  color: #666;
  height: 3em;
  overflow: hidden;
  margin-bottom: 12px;
}
.stats {
  display: flex;
  gap: 12px;
  font-size: 0.8rem;
  color: #999;
}
.join-btn {
  margin-left: auto;
  padding: 8px 16px;
  border-radius: 30px;
  border: none;
  background: #eef2ff;
  color: #4f46e5;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s;
}
.join-btn:hover {
  background: #4f46e5;
  color: white;
}
</style>
