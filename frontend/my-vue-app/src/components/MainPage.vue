<template>
  <div>
    <h2>用户列表</h2>

    <router-link>
      + 加好友
    </router-link>

    <div v-for="user in users" :key="user.id">
      <UserListItem :user="user" @start-chat="goToChat" />
    </div>
  </div>
</template>

<script>

</script>