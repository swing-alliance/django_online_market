<template>
  <div class="create-post-page">
    <div class="scroll-container">
      <div class="create-card">
        <button class="back-btn" @click="$router.back()">← 返回社区</button>
        <h2 class="page-title">发布新帖</h2>

        <form @submit.prevent="submitPost" class="post-form">
          <div class="form-group">
            <label>帖子标题</label>
            <input
              v-model="form.title"
              placeholder="请输入有吸引力的标题"
              required
            />
          </div>

          <div class="form-group">
            <label>帖子内容</label>
            <textarea
              v-model="form.content"
              placeholder="分享你的想法、经历或问题..."
              rows="10"
              required
            ></textarea>
          </div>

          <div class="form-group">
            <label>封面图片（建议比例 16:9 或 4:3）</label>
            <label v-if="!form.cover_image_base64" class="upload-area">
              <i class="ri-image-add-line"></i>
              <span>点击选择封面图片</span>
              <input
                type="file"
                @change="handleFileChange"
                accept="image/*"
                hidden
              />
            </label>

            <div v-else class="preview-container">
              <img :src="form.cover_image_base64" class="preview-img" />
              <button
                type="button"
                class="remove-btn"
                @click="form.cover_image_base64 = ''"
              >
                <i class="ri-close-line"></i> 删除
              </button>
            </div>
          </div>

          <button type="submit" :disabled="loading" class="submit-btn">
            {{ loading ? "发布中..." : "确认发布帖子" }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from "axios";
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();
const loading = ref(false);

const form = reactive({
  forum_id: route.params.forum_id,
  title: "",
  content: "",
  cover_image_base64: "",
});

const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  if (file.size > 5 * 1024 * 1024) {
    alert("图片大小不能超过 5MB");
    return;
  }
  const reader = new FileReader();
  reader.readAsDataURL(file);
  reader.onload = () => {
    form.cover_image_base64 = reader.result;
  };
};

const submitPost = async () => {
  loading.value = true;
  try {
    await axios.post("/api/users/user_post_in_forum/", form);
    alert("🎉 帖子发布成功！");
    router.push({ name: "ForumMain", params: { forum_id: form.forum_id } });
  } catch (err) {
    alert(err.response?.data?.detail || "发布失败，请稍后重试");
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
@import url("https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css");

.create-post-page {
  background: #f8f9fc;
  min-height: 100vh;
  padding: 30px 15px;
}

.scroll-container {
  width: 100%;
  max-width: 780px;
  margin: 0 auto;
}

.create-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  padding: 40px 45px;
}

.back-btn {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 20px;
}

.page-title {
  font-size: 1.8rem;
  color: #1e2937;
  margin-bottom: 30px;
  font-weight: 600;
}

.post-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: #334155;
  font-size: 0.95rem;
}

input,
textarea {
  padding: 14px 16px;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1.02rem;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: #6366f1;
}

textarea {
  resize: vertical;
  min-height: 160px;
}

/* 上传区域 */
.upload-area {
  border: 2px dashed #cbd5e1;
  border-radius: 16px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  background: #f8fafc;
}

/* ==================== 重点修改：更扁的预览区域 ==================== */
.preview-container {
  position: relative;
  width: 100%;
  max-width: 420px; /* 更宽 */
  height: 180px; /* 明显变扁 */
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  background: #f1f5f9;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover; /* 保持填充效果 */
}

.remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.65);
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
}

.submit-btn {
  margin-top: 10px;
  padding: 16px;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
}

.submit-btn:disabled {
  background: #9ca3af;
}
</style>
