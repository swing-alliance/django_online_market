<template>
    <div class="friends-page" style="padding: 20px;">
        <div class="title">
            <h2>我的好友列表 ({{ filteredFriendList.length }}人)</h2> 
        </div>

        <div class="search-bar">
            <input 
                type="text" 
                v-model="searchTerm"
                placeholder="输入好友名称或ID进行查找..."
                class="search-input"
            />
        </div>

        <div v-if="isLoading" class="loading-state">
            <p>正在加载好友数据...</p>
        </div>
        <div v-else-if="fetchError" class="error-state">
            <p>加载失败：{{ fetchError }}</p>
            <button @click="fetchfriends">点击重试</button>
        </div>
        <div v-else-if="allFriendList.length === 0" class="empty-state">
            <p>您还没有任何好友。</p>
        </div>
        <div v-else-if="searchTerm && filteredFriendList.length === 0" class="no-results">
            <p>未找到匹配 "{{ searchTerm }}" 的好友。</p>
        </div>

        <div v-else class="friend-cards-wrapper" style="margin-top: 20px; display: flex; margin-left: 60px; flex-direction: column; gap: 10px;">
            <FriendsListCard
                v-for="friend in filteredFriendList" :key="friend.id"
                :avatarUrl="friend.avatarUrl"
                :friendAccountName="friend.name"
                :friendAccountId="friend.accountId"
            />
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { setupAxiosInterceptor } from '@/utils/AxiosInterceptor.js';
import FriendsListCard from './FriendsListCard.vue'; 
setupAxiosInterceptor();
const FriendIdArray = ref([]);
const FriendAccountNameArray = ref([]);
const FriendAccountIdArray = ref([]);
const FriendAvatarUrlArray = ref([]);
const isLoading = ref(true);
const fetchError = ref(null);
// 【新增/修正：搜索关键字的响应式状态】
const searchTerm = ref(''); 
const fetchfriendsurl = 'http://127.0.0.1:8000/api/users/user_fetch_friends/';
const serve_base_url = 'http://127.0.0.1:8000';

const fetchfriends = async () => {
    isLoading.value = true;
    fetchError.value = null; 
    try {
        const response = await axios.get(fetchfriendsurl, { withCredentials: true }); // 确保携带认证信息
        FriendIdArray.value = response.data.friend_id || [];
        FriendAccountNameArray.value = response.data.friend_account_name || [];
        FriendAccountIdArray.value = response.data.friend_account_id || [];
        FriendAvatarUrlArray.value = response.data.avatar_url || [];
        console.log('好友列表获取成功');
    } catch(error) {
        console.error('获取好友列表失败:', error);
        fetchError.value = error.message || '网络请求失败';
    } finally {
        isLoading.value = false;
    }
}

const allFriendList = computed(() => { 
    const ids = FriendIdArray.value;
    if (ids.length === 0) {
        return [];
    }
    const length = ids.length;
    const combinedArray = [];
    for (let i = 0; i < length; i++) {
        let avatarPath = FriendAvatarUrlArray.value[i];
        if (avatarPath && avatarPath.startsWith('/')) {
            avatarPath = serve_base_url + avatarPath;
        }       
        combinedArray.push({
            id: ids[i],
            name: FriendAccountNameArray.value[i],
            accountId: FriendAccountIdArray.value[i],
            avatarUrl: avatarPath,
        });
    }
    return combinedArray;
});

// --- 核心计算属性 2：执行过滤操作 (最终渲染列表) ---
const filteredFriendList = computed(() => {
    const friends = allFriendList.value; 
    const term = searchTerm.value.toLowerCase().trim();
    if (!term) {
        return friends;
    }
    return friends.filter(friend => {
        const nameMatch = friend.name && String(friend.name).toLowerCase().includes(term);
        const idMatch = friend.accountId && String(friend.accountId).toLowerCase().includes(term);
        return nameMatch || idMatch;
    });
});



onMounted(() => {
    fetchfriends();
});
</script>

<style scoped>
.loading-state, .error-state, .empty-state, .no-results {
    text-align: center;
    padding: 30px;
    color: #666;
    border: 1px solid #eee;
    border-radius: 8px;
    margin-top: 15px;
}
.error-state p {
    color: #d32f2f;
}
.search-bar {
    margin: 15px 0 20px 0;
}
.search-input {
    width: 20%;
    padding: 10px 15px;
    border: 1px solid #f3eded;
    border-radius: 6px;
    font-size: 1em;
    box-sizing: border-box;
}
</style>