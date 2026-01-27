<template>
  <div class="header-container">
    <n-layout-header class="header" :class="{ 'header-scrolled': isScrolled }">
      <div class="header-content">
        <div class="logo" @click="handleLogoClick">
          <div class="logo-icon-wrapper">
            <n-icon size="28" class="logo-icon">
              <Briefcase />
            </n-icon>
          </div>
          <span class="logo-text">职享圈</span>
        </div>
        
        <n-menu 
          mode="horizontal" 
          :options="menuOptions" 
          class="main-menu"
          @update:value="handleMenuSelect"
          responsive
        />
        
        <div class="user-actions">
          <n-button 
            type="primary"
            class="create-btn"
            @click="handleCreate"
          >
            创作/发布
          </n-button>
          
          <n-input 
            v-model:value="searchQuery" 
            placeholder="搜索岗位/资源" 
            class="search-input"
            @keyup.enter="handleSearch"
            clearable
          >
            <template #prefix>
              <n-icon :component="Search" />
            </template>
          </n-input>
          
          <div class="notification-container" @mouseenter="openNotificationDropdown" @mouseleave="closeNotificationDropdown">
            <div class="notification-trigger">
              <n-badge :value="unreadCount" :max="99" :show="unreadCount > 0">
                <n-icon size="20" class="notification-icon">
                  <Notifications />
                </n-icon>
              </n-badge>
            </div>
            
            <div v-if="showNotification" class="notification-dropdown">
              <div class="notification-header">
                <h3>通知中心</h3>
                <button class="notification-mark-all" @click="markAllAsRead">全部已读</button>
              </div>
              
              <div class="notification-list">
                <div v-if="notificationStore.isLoading" class="notification-loading">
                  <n-spin size="small" />
                  <span>加载中...</span>
                </div>
                
                <div v-else-if="notifications.length === 0" class="notification-empty">
                  <n-icon size="48" class="empty-icon">
                    <NotificationsOutline />
                  </n-icon>
                  <p>暂无通知</p>
                </div>
                
                <div 
                  v-for="notification in notifications" 
                  :key="notification.id"
                  class="notification-item"
                  :class="{ 'unread': !notification.is_read }"
                  @click="markAsRead(notification.id)"
                >
                  <div class="notification-title">{{ notification.title }}</div>
                  <div class="notification-message">{{ notification.message }}</div>
                  <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
                </div>
              </div>
              
              <div class="notification-footer">
                <button class="notification-view-all" @click="showAllNotifications">查看全部</button>
              </div>
            </div>
          </div>
          
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
              round
              bordered
            >
              <template #fallback>
                <n-icon><Person /></n-icon>
              </template>
            </n-avatar>
          </n-dropdown>
          
          <n-button 
            v-else 
            type="primary" 
            size="medium" 
            @click="handleLogin"
            round
          >
            登录
          </n-button>
        </div>
      </div>
    </n-layout-header>
    
    <div class="header-placeholder"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, onErrorCaptured, computed, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  NLayoutHeader, 
  NMenu, 
  NInput, 
  NDropdown, 
  NButton, 
  NIcon, 
  NAvatar,
  NBadge,
  NSpin,
  NPopover,
  NConfigProvider,
  darkTheme,
  lightTheme
} from 'naive-ui'
import { Briefcase, Search, Person, Notifications, NotificationsOutline, LogoGithub, LogoWechat } from '@vicons/ionicons5'
import { useNotificationStore } from '@/stores/notificationStore'
import { getUserInfo } from '@/api/user'

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
const isScrolled = ref(false)

// 通知相关
const notificationStore = useNotificationStore()
const unreadCount = computed(() => notificationStore.unreadCount)
const notifications = computed(() => notificationStore.sortedNotifications.slice(0, 5))
const showNotification = ref(false)

// 打开通知下拉菜单
const openNotificationDropdown = () => {
  showNotification.value = true
  notificationStore.fetchNotifications()
}

// 关闭通知下拉菜单
const closeNotificationDropdown = () => {
  setTimeout(() => {
    showNotification.value = false
  }, 200)
}

// 导航菜单配置
const menuOptions = ref([
  { key: 'home', label: '首页' },
  { key: 'jobs', label: '招聘信息' },
  { key: 'resources', label: '就业资源' },
  { key: 'community', label: '经验社区'},
  { key: 'events', label: '宣讲会' }
])

// 用户下拉菜单
const userDropdownOptions = ref([
  { key: 'userinfo', label: '个人中心', icon: () => h(Person) },
  { key: 'resumes', label: '我的简历', icon: () => h(Person) },
  { key: 'applications', label: '我的申请', icon: () => h(Person) },
  { key: 'divider', type: 'divider' },
  { key: 'logout', label: '退出登录', icon: () => h(Person), type: 'warning' }
])

// 消息提示
const message = {
  info: (msg) => console.log('INFO:', msg),
  success: (msg) => console.log('SUCCESS:', msg),
  warning: (msg) => console.log('WARNING:', msg),
  error: (msg) => console.log('ERROR:', msg)
}

// 滚动监听
const handleScroll = () => {
  isScrolled.value = window.scrollY > 50
}

// 生命周期
onMounted(() => {
  console.log('Header组件挂载完成')
  initializeComponent()
  notificationStore.registerNotificationHandler()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  notificationStore.unregisterNotificationHandler()
  window.removeEventListener('scroll', handleScroll)
})

// 初始化组件
const initializeComponent = async () => {
  try {
    isLogin.value = !!localStorage.getItem('accessToken')
    if (isLogin.value) {
      try {
        const storedUserInfo = localStorage.getItem('userInfo')
        if (storedUserInfo) {
          const userInfo = JSON.parse(storedUserInfo)
          if (userInfo.avatar) {
            userAvatar.value = userInfo.avatar
            console.log('从本地存储获取头像:', userAvatar.value)
          }
        } else {
          const response = await getUserInfo()
          if (response.data && response.data.avatar) {
            let avatarUrl = response.data.avatar
            if (avatarUrl && !avatarUrl.startsWith('http')) {
              avatarUrl = `http://localhost:8000${avatarUrl}`
              console.log('Header初始化时处理的完整URL:', avatarUrl)
            }
            userAvatar.value = avatarUrl
            
            const userInfo = {
              id: response.data.id,
              username: response.data.username,
              avatar: avatarUrl
            }
            localStorage.setItem('userInfo', JSON.stringify(userInfo))
          }
        }
      } catch (err) {
        console.error('获取用户信息失败:', err)
        userAvatar.value = ''
      }
      await notificationStore.init()
    }
    
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
  }
}

const handleCreate = () => {
  router.push('/community/articlescreate')
}

// 通知相关方法
const formatTime = (timeString) => {
  const date = new Date(timeString)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  const diffHours = Math.floor(diffTime / (1000 * 60 * 60))
  const diffMinutes = Math.floor(diffTime / (1000 * 60))
  
  if (diffDays > 0) {
    return `${diffDays}天前`
  } else if (diffHours > 0) {
    return `${diffHours}小时前`
  } else if (diffMinutes > 0) {
    return `${diffMinutes}分钟前`
  } else {
    return '刚刚'
  }
}

const markAsRead = (notificationId) => {
  notificationStore.markAsRead(notificationId)
}

const markAllAsRead = () => {
  notificationStore.markAllAsRead()
}

const showAllNotifications = () => {
  router.push('/notifications')
}
</script>

<style scoped>
.header-container {
  width: 100%;
  position: relative;
}

.header-placeholder {
  height: 64px;
  transition: height 0.3s ease;
}

.header-scrolled + .header-placeholder {
  height: 56px;
}

.header {
  background: linear-gradient(135deg, #bad2ce 0%, #9ddcd0 100%);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 0;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  height: 64px;
  width: 100%;
  display: block;
  border-bottom: 1px solid #e8e8e8;
  transition: all 0.3s ease;
}

.header-scrolled {
  background-color: rgba(255, 255, 255, 0.98);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  height: 56px;
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
  transition: all 0.3s ease;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 8px 12px;
  border-radius: 8px;
}

.logo:hover {
  background-color: rgba(16, 185, 129, 0.1);
  transform: translateY(-2px);
}

.logo-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 10px;
  margin-right: 12px;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.logo-icon {
  color: white;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.5px;
}

.notification-container {
  position: relative;
  display: inline-block;
  margin-right: 16px;
}

.notification-trigger {
  position: relative;
  cursor: pointer;
  padding: 8px;
  display: flex;
  align-items: center;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.notification-trigger:hover {
  background-color: rgba(16, 185, 129, 0.1);
}

.notification-icon {
  color: #666;
  transition: color 0.2s ease;
}

.notification-trigger:hover .notification-icon {
  color: #10b981;
}

.notification-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 380px;
  background-color: white;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  z-index: 10000;
  overflow: hidden;
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
}

.notification-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
}

.notification-mark-all {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: none;
  color: white;
  font-size: 12px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 6px;
  transition: all 0.2s ease;
  font-weight: 500;
}

.notification-mark-all:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.notification-list {
  max-height: 400px;
  overflow-y: auto;
}

.notification-list::-webkit-scrollbar {
  width: 6px;
}

.notification-list::-webkit-scrollbar-track {
  background: #f5f5f5;
}

.notification-list::-webkit-scrollbar-thumb {
  background: #d9d9d9;
  border-radius: 3px;
}

.notification-list::-webkit-scrollbar-thumb:hover {
  background: #bfbfbf;
}

.notification-loading {
  padding: 40px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #999;
}

.notification-empty {
  padding: 60px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
}

.empty-icon {
  color: #d9d9d9;
  margin-bottom: 16px;
}

.notification-empty p {
  margin: 0;
  font-size: 14px;
}

.notification-item {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 1px solid #f5f5f5;
}

.notification-item:hover {
  background-color: #f0fdf4;
  transform: translateX(4px);
}

.notification-item.unread {
  background-color: rgba(16, 185, 129, 0.05);
  border-left: 3px solid #10b981;
}

.notification-title {
  font-weight: 600;
  margin-bottom: 6px;
  color: #1d2129;
  font-size: 14px;
}

.notification-message {
  font-size: 13px;
  color: #666;
  margin-bottom: 6px;
  line-height: 1.5;
}

.notification-time {
  font-size: 12px;
  color: #999;
}

.notification-footer {
  padding: 12px 20px;
  border-top: 1px solid #f0f0f0;
  text-align: center;
  background-color: #fafafa;
}

.notification-view-all {
  background: none;
  border: none;
  color: #10b981;
  font-size: 13px;
  cursor: pointer;
  padding: 6px 16px;
  border-radius: 6px;
  transition: all 0.2s ease;
  font-weight: 500;
}

.notification-view-all:hover {
  background-color: rgba(16, 185, 129, 0.1);
}

.main-menu {
  flex: 1;
  margin: 0 20px;
  min-width: 0;
}

.main-menu :deep(.n-menu-item) {
  border-radius: 8px;
  margin: 0 4px;
  transition: all 0.2s ease;
}

.main-menu :deep(.n-menu-item:hover) {
  background-color: rgba(16, 185, 129, 0.1);
}

.main-menu :deep(.n-menu-item.n-menu-item--selected) {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white !important;
  font-weight: 600;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.create-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: none;
  font-weight: 600;
  padding: 0 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.5);
}

.search-input {
  width: 240px;
  min-width: 150px;
  transition: width 0.3s ease;
}

.search-input:focus-within {
  width: 280px;
}

.search-input :deep(.n-input__border) {
  border-radius: 20px;
  border: 2px solid #e8e8e8;
  transition: all 0.2s ease;
}

.search-input:focus-within :deep(.n-input__border) {
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.user-avatar {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid #10b981;
}

.user-avatar:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

@media (max-width: 768px) {
  .header {
    height: auto;
    min-height: 64px;
  }
  
  .header-scrolled {
    height: 56px;
  }
  
  .header-content {
    flex-wrap: wrap;
    padding: 8px 20px;
  }
  
  .logo {
    order: 1;
  }
  
  .logo-text {
    font-size: 18px;
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
  
  .create-btn {
    padding: 0 16px;
    font-size: 14px;
  }
  
  .search-input {
    width: 150px;
  }
  
  .search-input:focus-within {
    width: 180px;
  }
  
  .notification-dropdown {
    width: 320px;
    right: -20px;
  }
}

@media (max-width: 480px) {
  .header-content {
    padding: 8px 16px;
  }
  
  .logo-icon-wrapper {
    width: 36px;
    height: 36px;
  }
  
  .logo-icon-wrapper .n-icon {
    font-size: 24px;
  }
  
  .search-input {
    width: 120px;
  }
  
  .search-input:focus-within {
    width: 140px;
  }
  
  .create-btn {
    padding: 0 12px;
    font-size: 13px;
  }
  
  .logo-text {
    font-size: 16px;
  }
  
  .notification-dropdown {
    width: 280px;
  }
}
</style>