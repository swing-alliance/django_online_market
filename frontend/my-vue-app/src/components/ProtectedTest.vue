<template>
  <div>
    <h2>上传头像</h2>
    <input type="file" @change="handleFileChange" />
    <button @click="uploadAvatar" :disabled="!file">上传</button>
    <p v-if="uploading">上传中...</p>
    <p v-if="uploadSuccess">头像上传成功！</p>
    <p v-if="uploadError" style="color: red;">上传失败：{{ uploadError }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const file = ref(null)  // 存储选中的文件
const uploading = ref(false)  // 上传状态
const uploadSuccess = ref(false)  // 上传成功标志
const uploadError = ref(null)  // 上传失败信息

// 处理文件选择
const handleFileChange = (event) => {
  file.value = event.target.files[0]  // 获取选中的文件
}

// 上传头像到后端
const uploadAvatar = async () => {
  if (!file.value) return  // 如果没有文件，则不执行上传

  const formData = new FormData()
  formData.append('account_avatar', file.value)  // 将文件添加到 FormData

  uploading.value = true
  uploadSuccess.value = false
  uploadError.value = null

  try {
    const response = await axios.patch('http://127.0.0.1:8000/api/users/user_upload_avatar/', formData, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,  // 如果需要认证，添加 token
        'Content-Type': 'multipart/form-data',  // 设置文件上传的 Content-Type
      },
    })

    if (response.status === 200) {
      uploadSuccess.value = true
    }
  } catch (error) {
    uploadError.value = error.response?.data?.message || '上传失败，请重试'
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
/* 样式可以根据需求自定义 */
</style>