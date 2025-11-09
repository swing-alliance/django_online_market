<template>
  <div style="display: flex; flex-direction: column; gap: 10px;">
    
    <div style="border: 1px solid #ccc; padding: 10px; margin: 5px 0;">
      
      <h4 style="margin: 0 0 5px 0;">
        {{ notify_name }}
      </h4>
      
      <p style="margin: 0;">
        {{ notify_content }}
      </p>
      
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';
defineProps({
  notify_name: {
    type: String,
    required: true
  },
  notify_content: {
    type: String,
    required: true
  }
});
</script>