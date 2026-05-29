import { createRouter, createWebHistory } from "vue-router";
// 导入你的目标组件
const routes = [
  {
    path: "/",
    name: "mainpage",
    component: () => import("../components/MainPage.vue"),
  },

  {
    path: "/register",
    name: "register",
    component: () => import("../components/RegisterForm.vue"),
  },
  {
    path: "/login",
    name: "login",
    component: () => import("../components/LoginForm.vue"),
  },
  {
    path: "/personalpage",
    name: "personalpage",
    component: () => import("../components/PersonalPage.vue"),
  },
  {
    path: "/friendslist",
    name: "friendslist",
    component: () => import("../components/FriendsPage.vue"),
  },
  {
    path: "/notification",
    name: "notification",
    component: () => import("../components/NotifyPage.vue"),
  },
  {
    path: "/test",
    name: "test",
    component: () => import("../components/ProtectedTest.vue"),
  },
  {
    path: "/test_ws",
    name: "test_ws",
    component: () => import("../components/WsStatusTes.vue"),
  },
  {
    path: "/chatroom/:myId/:friendId",
    name: "chatroom",
    component: () => import("../components/UsersChatRoom.vue"),
  },
  {
    path: "/ai_test",
    name: "ai_test",
    component: () => import("../components/AI/ai_test.vue"),
  },
  {
    path: "/group-main",
    name: "GroupChatMain", // 与跳转代码对应
    component: () => import("../components/Groupchat/GroupChatMain.vue"),
  },
  {
    path: "/group-room",
    name: "GroupChatRoom", // 与跳转代码对应
    component: () => import("../components/Groupchat/GroupChatRoom.vue"),
  },
  {
    path: "/create-group",
    name: "TryCreateGroup",
    component: () => import("../components/Groupchat/TryCreateGroup.vue"),
  },
  {
    path: "/create-forum",
    name: "CreateForum",
    component: () => import("../components/Forum/CreateForum.vue"),
  },
  {
    path: "/show-forum",
    name: "show-forum",
    component: () => import("../components/Forum/ShowForum.vue"),
  },
  {
    path: "/forum-main/:forum_id", // 必须加上 :forum_id 才能接收参数
    name: "ForumMain",
    component: () => import("../components/Forum/ForumMain.vue"),
  },
  {
    path: "/create-post/:forum_id",
    name: "CreatePost",
    component: () => import("../components/Forum/CreatePost.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
