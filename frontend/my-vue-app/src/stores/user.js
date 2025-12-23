import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
  state: () => ({
    mydatabaseId: null, // 初始值为空
    username: ''
  }),
  actions: {
    setDatabaseId(id) {
      this.mydatabaseId = id;
    }
  },
  persist: true 
});