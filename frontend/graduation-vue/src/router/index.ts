import { createRouter, createWebHistory } from 'vue-router'
import Register from '../views/Register.vue'  // 假设新建了注册页面   // 假设新建了登录页面

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/register', name: 'Register', component: Register },
    // { path: '/login', name: 'Login', component: Login },
  ],
})

export default router
