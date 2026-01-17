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
          @update:value="handleMenuSelect"
        />
        
        <div class="user-actions">
          <n-input 
            v-model:value="searchQuery" 
            placeholder="搜索岗位/资源" 
            class="search-input"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <n-icon :component="Search" />
            </template>
          </n-input>
          
          <!-- 通知中心 - 原生实现 -->
          <div class="notification-container" @mouseenter="openNotificationDropdown" @mouseleave="closeNotificationDropdown">
            <!-- 通知图标触发器 -->
            <div class="notification-trigger">
              <n-icon size="20">
                <Notifications />
              </n-icon>
              <!-- 未读通知数量 -->
              <span v-if="unreadCount > 0" class="notification-badge">
                {{ unreadCount > 99 ? '99+' : unreadCount }}
              </span>
            </div>
            
            <!-- 通知下拉菜单 -->
            <div v-if="showNotification" class="notification-dropdown">
              <div class="notification-header">
                <h3>通知中心</h3>
                <button class="notification-mark-all" @click="markAllAsRead">全部已读</button>
              </div>
              
              <div class="notification-list">
                <div v-if="notificationStore.isLoading" class="notification-loading">
                  加载中...
                </div>
                
                <div v-else-if="notifications.length === 0" class="notification-empty">
                  暂无通知
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
import { ref, onMounted, onErrorCaptured, computed } from 'vue'
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
  NPopover
} from 'naive-ui'
import { Briefcase, Search, Person, Notifications, NotificationsOutline } from '@vicons/ionicons5'
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

// 通知相关
const notificationStore = useNotificationStore()
const unreadCount = computed(() => notificationStore.unreadCount)
const notifications = computed(() => notificationStore.sortedNotifications.slice(0, 5)) // 只显示最近5条通知
const showNotification = ref(false)

// 打开通知下拉菜单
const openNotificationDropdown = () => {
  showNotification.value = true
  notificationStore.fetchNotifications()
}

// 关闭通知下拉菜单
const closeNotificationDropdown = () => {
  // 添加一个小延迟，确保用户有时间将鼠标从触发器移动到下拉菜单
  setTimeout(() => {
    showNotification.value = false
  }, 200)
}

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
const initializeComponent = async () => {
  try {
    // 检查登录状态
    isLogin.value = !!localStorage.getItem('accessToken')
    if (isLogin.value) {
      try {
        // 先从本地存储获取用户信息
        const storedUserInfo = localStorage.getItem('userInfo')
        if (storedUserInfo) {
          const userInfo = JSON.parse(storedUserInfo)
          if (userInfo.avatar) {
            userAvatar.value = userInfo.avatar
            console.log('从本地存储获取头像:', userAvatar.value)
          }
        } else {
          // 如果本地没有，从API获取用户信息，包括头像
          const response = await getUserInfo()
          if (response.data && response.data.avatar) {
            let avatarUrl = response.data.avatar
            // 处理URL，确保是完整URL
            if (avatarUrl && !avatarUrl.startsWith('http')) {
              avatarUrl = `http://localhost:8000${avatarUrl}`
              console.log('Header初始化时处理的完整URL:', avatarUrl)
            }
            userAvatar.value = avatarUrl
            
            // 保存到本地存储
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
        // 使用默认头像
        userAvatar.value = ''
      }
      // 初始化通知功能
      await notificationStore.init()
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
  // 跳转到通知中心页面
  router.push('/notifications')
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

/* 原生通知中心样式 */
.notification-container {
  position: relative;
  display: inline-block;
  margin-right: 16px;
  /* 确保容器足够大，包含触发器和下拉菜单 */
}

.notification-trigger {
  position: relative;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background-color: #ff4d4f;
  color: white;
  font-size: 12px;
  font-weight: bold;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

.notification-dropdown {
  position: absolute;
  top: calc(100% - 1px); /* 减少与触发器之间的间隙 */
  right: 0;
  width: 300px;
  background-color: white;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 10000;
  margin-top: 1px; /* 最小化间隙 */
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid #e8e8e8;
}

.notification-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
}

.notification-mark-all {
  background: none;
  border: none;
  color: #2d8cf0;
  font-size: 12px;
  cursor: pointer;
  padding: 0;
}

.notification-list {
  max-height: 400px;
  overflow-y: auto;
}

.notification-loading,
.notification-empty {
  padding: 20px;
  text-align: center;
  color: #999;
}

.notification-item {
  padding: 12px;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
  transition: background-color 0.2s;
}

.notification-item:hover {
  background-color: #f5f5f5;
}

.notification-item.unread {
  background-color: #f0f7ff;
}

.notification-title {
  font-weight: 500;
  margin-bottom: 4px;
  color: #1d2129;
}

.notification-message {
  font-size: 13px;
  color: #666;
  margin-bottom: 4px;
}

.notification-time {
  font-size: 12px;
  color: #999;
}

.notification-footer {
  padding: 8px 12px;
  border-top: 1px solid #e8e8e8;
  text-align: right;
}

.notification-view-all {
  background: none;
  border: none;
  color: #2d8cf0;
  font-size: 12px;
  cursor: pointer;
  padding: 0;
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

/* 通知相关样式 */
.notification-trigger {
  position: relative;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-trigger:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.notification-badge {
  position: absolute;
  top: 0;
  right: 0;
  transform: translate(30%, -30%);
}

.notification-dropdown {
  width: 380px;
  max-height: 500px;
  padding: 8px 0;
  z-index: 10000;
  background-color: white;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  border-radius: 8px;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px 8px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.notification-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.notification-list {
  max-height: 360px;
  overflow-y: auto;
}

.notification-loading {
  padding: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.notification-empty {
  padding: 40px 20px;
  text-align: center;
  color: rgba(0, 0, 0, 0.4);
}

.notification-empty p {
  margin: 12px 0 0;
  font-size: 14px;
}

.notification-item {
  padding: 12px 16px;
  display: flex;
  align-items: flex-start;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.notification-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.notification-item.unread {
  background-color: rgba(45, 140, 240, 0.05);
}

.notification-icon {
  font-size: 24px;
  margin-right: 12px;
  flex-shrink: 0;
  margin-top: 2px;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
  color: rgba(0, 0, 0, 0.9);
}

.notification-message {
  font-size: 13px;
  color: rgba(0, 0, 0, 0.6);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.notification-time {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.4);
}

.notification-footer {
  padding: 8px 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  text-align: center;
}
</style>