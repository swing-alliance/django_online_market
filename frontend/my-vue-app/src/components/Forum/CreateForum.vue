<template>
  <div class="create-forum-container">
    <div class="form-card">
      <h2 class="title">创建新版块</h2>
      <p class="subtitle">建立一个属于你们的新天地</p>

      <form @submit.prevent="handleSubmit">
        <div class="input-group">
          <label>版块名称 <span class="required">*</span></label>
          <input
            v-model="form.name"
            type="text"
            placeholder="例如：主机交流区"
            required
            maxlength="100"
          />
        </div>

        <div class="input-group">
          <label>版块简介</label>
          <textarea
            v-model="form.description"
            rows="3"
            placeholder="写一段简洁的描述..."
          ></textarea>
        </div>

        <div class="input-group">
          <label>版块图标</label>
          <div class="upload-area">
            <input
              type="file"
              @change="handleFileChange"
              accept="image/*"
              id="file-input"
            />
            <div class="icon-preview">
              <img
                v-if="form.icon_base64"
                :src="form.icon_base64"
                alt="preview"
              />
              <span v-else>点击选择图片</span>
            </div>
          </div>
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? "同步数据中..." : "立即创建" }}
        </button>
      </form>

      <div v-if="feedback.msg" :class="['alert', feedback.type]">
        {{ feedback.msg }}
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from "axios";
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const loading = ref(false);

// 1. 统一使用此处定义的 API 地址
const apiUrl = "/api/users/create_forum/";

const form = reactive({
  name: "",
  description: "",
  icon_base64: "",
});

const feedback = reactive({ msg: "", type: "" });

const handleFileChange = (e) => {
  const file = e.target.files[0];
  if (!file) return;
  if (file.size > 1024 * 1024) {
    feedback.msg = "图片太大啦，请压缩到 1MB 以内";
    feedback.type = "error";
    return;
  }
  const reader = new FileReader();
  reader.onload = (event) => {
    form.icon_base64 = event.target.result;
  };
  reader.readAsDataURL(file);
};

const handleSubmit = async () => {
  loading.value = true;
  feedback.msg = ""; // 重置反馈状态
  try {
    // 2. 修正为使用定义的 apiUrl
    const response = await axios.post(apiUrl, form);

    feedback.msg = response.data.message;
    feedback.type = "success";

    setTimeout(
      () => router.push(`/forum/${response.data.forum_info.id}`),
      1500,
    );
  } catch (error) {
    feedback.type = "error";
    feedback.msg = error.response?.data?.detail || "创建失败，请检查数据";
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* 延续之前的高级蓝紫主题 */
.create-forum-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 90vh;
  background-color: #f8f9fe;
  padding: 20px;
}
.form-card {
  background: #ffffff;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(100, 100, 200, 0.08);
  width: 100%;
  max-width: 500px;
}
.input-group {
  margin-bottom: 20px;
}
label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #5d5d8a;
}
input,
textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #dcdde8;
  border-radius: 10px;
}
.upload-area {
  display: flex;
  align-items: center;
  gap: 15px;
}
.icon-preview {
  width: 60px;
  height: 60px;
  border: 2px dashed #dcdde8;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  color: #aaa;
  font-size: 10px;
  text-align: center;
}
.icon-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.submit-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #8a8ae6, #6b6bcf);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
}
.alert {
  margin-top: 15px;
  padding: 10px;
  text-align: center;
  border-radius: 8px;
  font-size: 14px;
}
.success {
  background: rgba(144, 238, 144, 0.2);
  color: #639a67;
}
.error {
  background: rgba(255, 182, 193, 0.2);
  color: #d17a86;
}
</style>
