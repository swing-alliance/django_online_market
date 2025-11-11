<template>
  <div style="display: flex; flex-direction: column; gap: 10px; border: 1px solid #ccc; padding: 10px; background-color: #f9f9f9;">
    
    <h4 style="margin: 0 0 5px 0; color: #333;">
      消息: {{ notify_name }}
    </h4>
    
    <p style="margin: 0 0 10px 0; color: #555;">
      内容: {{ notify_content }}
    </p>
    
    </div>
</template>

<script setup>
import defineProps from 'vue';
defineProps({
    notify_name: {
        type: String,
        required: true
    },
    notify_content: {
        type: String,
        required: true
    },
    // request-id 可以作为 key 或将来处理请求时使用
    requestId: {
        type: [Number, String],
        default: null
    }
});
</script>