<template>
  <div>
    <h2>发起好友请求</h2>
    <input type="text" placeholder="输入用户ID或名称" v-model="name_or_id">

    <button @click="sendFriendRequest" :disabled="!name_or_id.trim() || isLoading">
      {{ isLoading ? '发送中...' : '发起好友请求' }}
    </button>
    
    <p v-if="message" :class="isError ? 'error-message' : 'success-message'" v-html="message"></p>
    <div class="message_ring" @click="openModal">
      <img src="/image/ring.png" style="width: 30px; height: 30px;"/>
    </div>
                <div v-if="isModalVisible" class="modal-overlay">
                    <div class="modal-content">
                      <h2>通知</h2>
                      <p>这里是弹出的内容...</p>
                      <button @click="closeModal">关闭</button>
                    </div>
                </div>
  </div>
</template>

<script>
import axios from 'axios';
import { setupAxiosInterceptor } from '@/utils/AxiosInterceptor.js';


setupAxiosInterceptor();

const apiUrl = 'http://127.0.0.1:8000/api/users/add_friend_request/';

export default {
  name: 'AddFriendRequest', 
  data() {
    return {
      name_or_id: '',
      isLoading: false,
      message: '',
      isError: false,
      isModalVisible: false
    };
  },
  
  computed: {
    // 检查输入是否为纯数字，以判断它是 ID 还是 Name
    isAccountId() {
      const trimmedInput = this.name_or_id.trim();
      if(trimmedInput.length <7){return false;}
      return true;
    },
    
    // 构建发送给后端的数据体
    requestPayload() {
      const payload = {};
      const value = this.name_or_id.trim();
      
      if (this.isAccountId) {
        payload.account_id = value;
        payload.account_name = ""; 
      } else {
        payload.account_id = "";
        payload.account_name = value;
      }
      return payload;
    }
  },
  
  methods: {
    async sendFriendRequest() {
      this.message = '';
      this.isError = false;
      
      if (!this.name_or_id.trim()) {
        this.message = '请输入用户 ID 或名称。';
        this.isError = true;
        return;
      }
      
      this.isLoading = true;
      const payloadToSend = this.requestPayload;
      console.log('--- [DEBUG] 发送给后端的数据 ---');
      console.log('Payload:', payloadToSend);
      console.log('--- ----------------------- ---');


      try {
        const response = await axios.post(apiUrl, payloadToSend);

        // ⭐️ 调试代码 2: 打印成功响应
        console.log('API 成功响应:', response.data);
        
        this.message = response.data.message || '好友请求已成功发送！';
        this.isError = false;

      } catch (error) {
        this.isError = true;
        
        if (error.response) {
          // ⭐️ 调试代码 3: 打印错误响应的原始数据
          console.error('API 错误状态码:', error.response.status);
          console.error('API 错误原始数据:', error.response.data);
          
          const errorData = error.response.data;
          let errMsg = '请求失败，请稍后重试。';
          
          if (errorData.detail) {
            errMsg = `请求失败: ${errorData.detail}`;
          } else if (errorData.account_id || errorData.account_name || errorData.non_field_errors) {
            // 序列化器 Validation 错误
            // 注意：检查是否是因为拼写错误导致后端返回 accout_id 或 accout_name
            const validationError = errorData.account_id || errorData.account_name || errorData.non_field_errors;
            errMsg = `验证失败: ${Array.isArray(validationError) ? validationError[0] : validationError}`;
          } else {
             // 针对前端无法解析的错误格式，将原始 JSON 错误信息显示出来
             errMsg = `服务器错误 (${error.response.status}): ${JSON.stringify(errorData)}`;
          }
          
          this.message = errMsg;
        } else {
          this.message = '网络连接失败，请检查网络设置。';
        }
      } finally {
        this.isLoading = false;
      }
    },

    openModal() {
      this.isModalVisible = true; // 显示弹窗
    },

    closeModal() {
      this.isModalVisible = false; // 关闭弹窗
    }

  }
};
</script>

<style>
.message_ring {
max-width: 30px;  /* 设置最大宽度 */
  max-height: 30px;  /* 设置最大高度 */
  width: auto;  /* 自动调整宽度 */
  height: auto;  
}


</style>