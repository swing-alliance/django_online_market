<template>
  <div id="app">
    <user-login /> 
    </div>
</template>

<script>
// 1. 修改导入路径
import UserLogin from './components/UserLogin.vue'; 

export default {
  name: 'App',
  components: {
    // 2. 修改注册名称
    UserLogin 
  }
};
</script>