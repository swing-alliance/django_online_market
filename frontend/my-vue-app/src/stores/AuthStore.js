import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useAuthStore = defineStore('auth', () => {
    const token = ref(localStorage.getItem('userToken') || null);
    const isAuthenticated = computed(() => !!token.value);
    const setLogin = (newToken) => {
        token.value = newToken;
        localStorage.setItem('userToken', newToken);
    };
    const logout = () => {
        token.value = null;
        localStorage.removeItem('userToken');
    };
    return { token, isAuthenticated, setLogin, logout };
});