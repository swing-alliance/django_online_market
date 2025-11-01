<template>
  <div class="personal-page">
    <div class="welcome-message">
      <p>欢迎，{{ username }}！</p>
    </div>
  </div>
</template>

<script>
export default {
  name: "PersonalPage",
  props: {
    username: {
      type: String,
      required: true,
    },
  },
};
</script>

<style scoped>
.personal-page {
  display: flex;
  justify-content: flex-end;
  padding: 20px;
}

.welcome-message {
  font-size: 18px;
  color: #333;
  font-weight: bold;
}
</style>
