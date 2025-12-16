<template>
  <div class="header-container">
    <!-- 调试标记 -->
    <!-- <div style="background: red; color: white; padding: 10px;">
      调试：LayoutHeader 组件已加载
    </div> -->
    
    <n-layout-header class="header">
      <div class="header-content">
        <div class="logo" @click="handleLogoClick">
          <n-icon size="28" class="logo-icon">
            <Briefcase />
          </n-icon>
          <span class="logo-text">职享圈</span>
        </div>
        
        <n-menu 
          mode="horizontal" 
          :options="menuOptions" 
          class="main-menu"
          @select="handleMenuSelect"
        />
        
        <div class="user-actions">
          <n-input 
            v-model:value="searchQuery" 
            placeholder="搜索岗位/资源" 
            class="search-input"
            :prefix="Search"
            @keyup.enter="handleSearch"
          />
          
          <n-dropdown 
            v-if="isLogin" 
            trigger="hover" 
            :options="userDropdownOptions"
            @select="handleUserAction"
          >
            <n-avatar 
              size="small" 
              class="user-avatar"
              :src="userAvatar"
            >
              <template #fallback>
                <n-icon><Person /></n-icon>
              </template>
            </n-avatar>
          </n-dropdown>
          
          <n-button 
            v-else 
            type="primary" 
            size="small" 
            @click="handleLogin"
          >
            登录
          </n-button>
        </div>
      </div>
    </n-layout-header>
  </div>
</template>

<script setup>
import { ref, onMounted, onErrorCaptured } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  NLayoutHeader, 
  NMenu, 
  NInput, 
  NDropdown, 
  NButton, 
  NIcon, 
  NAvatar 
} from 'naive-ui'
import { Briefcase, Search, Person } from '@vicons/ionicons5'

// 错误处理
const error = ref(null)
onErrorCaptured((err) => {
  console.error('Header组件错误:', err)
  error.value = err.message
  return false
})

// 路由
const router = useRouter()
const route = useRoute()

// 状态管理
const isLogin = ref(false)
const userAvatar = ref('')
const searchQuery = ref('')

// 导航菜单配置
const menuOptions = ref([
  { key: 'home', label: '首页' },
  { key: 'jobs', label: '招聘信息' },
  { key: 'resources', label: '就业资源' },
  { key: 'community', label: '经验社区' },
  { key: 'events', label: '宣讲会' }
])

// 用户下拉菜单
const userDropdownOptions = ref([
  { key: 'userinfo', label: '个人中心' },
  { key: 'resumes', label: '我的简历' },
  { key: 'applications', label: '我的申请' },
  { key: 'logout', label: '退出登录', type: 'warning' }
])

// 消息提示（简化处理）
const message = {
  info: (msg) => console.log('INFO:', msg),
  success: (msg) => console.log('SUCCESS:', msg),
  warning: (msg) => console.log('WARNING:', msg),
  error: (msg) => console.log('ERROR:', msg)
}

// 生命周期
onMounted(() => {
  console.log('Header组件挂载完成')
  initializeComponent()
})

// 初始化组件
const initializeComponent = () => {
  try {
    // 检查登录状态
    isLogin.value = !!localStorage.getItem('accessToken')
    if (isLogin.value) {
      userAvatar.value = 'https://picsum.photos/id/100/40/40'
    }
    
    // 设置当前激活的菜单项
    updateActiveMenu()
  } catch (err) {
    console.error('初始化失败:', err)
    error.value = err.message
  }
}

// 更新激活菜单
const updateActiveMenu = () => {
  const currentRouteName = route.name
  console.log('当前路由:', currentRouteName)
  
  menuOptions.value = menuOptions.value.map(option => ({
    ...option,
    active: option.key === currentRouteName
  }))
}

// 事件处理函数
const handleLogoClick = () => {
  router.push('/')
}

const handleMenuSelect = (key) => {
  console.log('菜单选择:', key)
  router.push(`/${key}`)
}

const handleUserAction = (key) => {
  console.log('用户操作:', key)
  switch (key) {
    case 'userinfo':
      router.push('/userinfo')
      break
    case 'resumes':
      router.push('/resumes')
      break
    case 'applications':
      router.push('/applications')
      break
    case 'logout':
      handleLogout()
      break
  }
}

const handleLogin = () => {
  router.push('/login')
}

const handleLogout = () => {
  localStorage.removeItem('accessToken')
  localStorage.removeItem('refreshToken')
  isLogin.value = false
  message.success('已退出登录')
  router.push('/login')
}

const handleSearch = () => {
  const keyword = searchQuery.value.trim()
  if (keyword) {
    message.info(`搜索: ${keyword}`)
    // 实际搜索逻辑
  }
}
</script>

<style scoped>
.header-container {
  width: 100%;
  position: relative;
}

/* 关键：添加缺失的 .header 样式 */
.header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 1000;
  height: 64px;
  width: 100%;
  display: block;
  border-bottom: 1px solid #e8e8e8;
}

.header-content {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: opacity 0.2s;
}

.logo:hover {
  opacity: 0.8;
}

.logo-icon {
  margin-right: 8px;
  color: #2d8cf0;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #1d2129;
}

.main-menu {
  flex: 1;
  margin: 0 20px;
  min-width: 0; /* 允许收缩 */
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0; /* 防止收缩 */
}

.search-input {
  width: 240px;
  min-width: 150px;
}

.user-avatar {
  cursor: pointer;
  transition: transform 0.2s;
}

.user-avatar:hover {
  transform: scale(1.05);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header {
    height: auto;
    min-height: 64px;
  }
  
  .header-content {
    flex-wrap: wrap;
    padding: 8px 20px;
  }
  
  .logo {
    order: 1;
  }
  
  .main-menu {
    order: 3;
    width: 100%;
    margin: 8px 0 0 0;
  }
  
  .user-actions {
    order: 2;
    margin-left: auto;
  }
  
  .search-input {
    width: 150px;
  }
}

@media (max-width: 480px) {
  .header-content {
    padding: 8px 16px;
  }
  
  .search-input {
    width: 120px;
  }
  
  .logo-text {
    font-size: 16px;
  }
}
</style>