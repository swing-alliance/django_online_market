<template>
  <div class="ban-modal">
    <h3>封禁用户</h3>
    <p>
      确定要封禁 <strong>{{ user_to_ban.username }}</strong> 吗？
    </p>

    <div class="form-group">
      <label>封禁时长（小时）</label>
      <input
        v-model="durationHours"
        type="number"
        min="1"
        max="720"
        placeholder="24"
      />
    </div>

    <div class="modal-actions">
      <button @click="$emit('close')" class="cancel-btn">取消</button>
      <button @click="confirmBan" class="ban-btn" :disabled="loading">
        {{ loading ? "封禁中..." : "确认封禁" }}
      </button>
    </div>
  </div>
</template>

<script setup>
import axios from "axios";
import { ref } from "vue";

const props = defineProps({
  forum_id: [String, Number],
  user_to_ban: Object,
});

const emit = defineEmits(["close", "success"]);

const durationHours = ref(24);
const loading = ref(false);

const confirmBan = async () => {
  if (!props.forum_id || !props.user_to_ban) return;

  loading.value = true;

  try {
    await axios.post("/api/users/ban_user_from_forum/", {
      forum_id: props.forum_id,
      user_id: props.user_to_ban.id,
      duration_hours: parseInt(durationHours.value),
    });

    alert(`已成功封禁 ${props.user_to_ban.username}`);
    emit("success"); // 刷新成员列表
    emit("close");
  } catch (err) {
    alert(err.response?.data?.detail || "封禁失败");
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.ban-modal {
  background: white;
  padding: 25px 30px;
  border-radius: 16px;
  width: 380px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.ban-modal h3 {
  margin-top: 0;
  color: #ef4444;
}

.form-group {
  margin: 15px 0;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 0.9rem;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.modal-actions {
  margin-top: 25px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.cancel-btn {
  padding: 10px 18px;
  background: #e5e7eb;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.ban-btn {
  padding: 10px 22px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.ban-btn:disabled {
  background: #f87171;
  cursor: not-allowed;
}
</style>
