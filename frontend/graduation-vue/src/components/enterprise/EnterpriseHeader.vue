<!-- src/components/enterprise/EnterpriseHeader.vue -->
<template>
  <header class="enterprise-header">
    <div class="enterprise-header-content">
      <!-- 企业品牌标识 -->
      <div class="enterprise-brand" @click="$router.push('/enterprise')">
        <n-icon size="32" class="brand-icon">
          <Business />
        </n-icon>
        <span class="brand-text">企业服务中心</span>
      </div>

      <!-- 企业专属导航菜单 -->
      <n-menu 
        mode="horizontal" 
        :options="enterpriseMenuOptions" 
        class="enterprise-nav-menu"
        @update-value="handleMenuSelect"

      />

      <!-- 企业用户功能区 -->
      <div class="enterprise-actions">
        <n-button 
          type="primary" 
          size="small" 
          @click="handlePublishJob"
        >
          <template #icon>
            <n-icon><Add /></n-icon>
          </template>
          发布招聘
        </n-button>
        
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
          trigger="hover" 
          :options="userDropdownOptions"
          @select="handleUserAction"
        >
          <div class="user-info">
            <n-avatar 
              size="small" 
              :src="userAvatar"
              class="user-avatar"
              :round="false"
            >
              <template #fallback>
                <n-icon><Business /></n-icon>
              </template>
            </n-avatar>
            <span class="user-name">{{ userName }}</span>
          </div>
        </n-dropdown>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { 
  NMenu, NButton, NIcon, NAvatar, NDropdown, NBadge, NSpin 
} from 'naive-ui'
import {  Add, PersonCircle, Settings, LogOut, Business, Notifications, NotificationsOutline } from '@vicons/ionicons5'
import { useNotificationStore } from '@/stores/notificationStore'
import axios from '@/utils/axios'
// Building,
const router = useRouter()

// 企业用户信息
const userAvatar = ref('')
const userName = ref('企业用户')

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

// 企业专属菜单
const enterpriseMenuOptions = ref([
  { key: 'recruitments', label: '招聘管理'},
  { key: 'applications', label: '简历库' },
  { key: 'analytics', label: '数据统计' },
  { key: 'company', label: '企业信息' }
])

// 用户下拉菜单
const userDropdownOptions = ref([
  { key: 'profile', label: '企业资料', icon: Settings },
  { key: 'settings', label: '账户设置', icon: Settings },
  { key: 'divider', type: 'divider' },
  { key: 'logout', label: '退出登录', icon: LogOut, type: 'warning' }
])

const handleMenuSelect = (key) => {
  router.push(`/enterprise/${key}`)
}

const handlePublishJob = () => {
  router.push('/enterprise/recruitments/create')
}

const handleUserAction = (key) => {
  switch (key) {
    case 'profile':
      router.push('/enterprise/edit')
      break
    case 'settings':
      router.push('/enterprise/settings')
      break
    case 'logout':
      handleLogout()
      break
  }
}

const handleLogout = () => {
  localStorage.removeItem('enterpriseToken')
  router.push('/login?type=enterprise')
}

onMounted(() => {
  // 初始化企业用户信息
  initializeEnterpriseUser()
})

const initializeEnterpriseUser = async () => {
  try {
    // 先从API获取最新的企业信息
    const response = await axios.get('/enterprises/')
    let enterpriseData = response.data
    
    // 处理不同的响应格式
    if (Array.isArray(enterpriseData) && enterpriseData.length > 0) {
      enterpriseData = enterpriseData[0]
    } else if (!enterpriseData || typeof enterpriseData !== 'object') {
      enterpriseData = {}
    }
    
    // 更新本地存储
    const enterpriseInfo = {
      id: enterpriseData.id,
      name: enterpriseData.name,
      logo: enterpriseData.logo,
      avatar: enterpriseData.logo // 保持兼容性
    }
    localStorage.setItem('enterpriseInfo', JSON.stringify(enterpriseInfo))
    
    // 更新UI
    userAvatar.value = enterpriseInfo.logo || enterpriseInfo.avatar || ''
    userName.value = enterpriseInfo.name || '企业用户'
    
  } catch (error) {
    console.error('获取企业信息失败:', error)
    // 从本地存储获取作为备用
    const enterpriseInfo = JSON.parse(localStorage.getItem('enterpriseInfo') || '{}')
    userAvatar.value = enterpriseInfo.logo || enterpriseInfo.avatar || ''
    userName.value = enterpriseInfo.name || '企业用户'
  } finally {
    // 初始化通知功能
    await notificationStore.init()
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
  // 这里可以跳转到通知列表页面
  console.log('跳转到通知列表页面')
}
</script>

<style scoped>
.enterprise-header {
  background: linear-gradient(135deg, #e5e5ed 0%, #e5e5ed 0%);
  color: rgb(69, 44, 44);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.562);
}

.enterprise-header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.enterprise-brand {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: 600;
  font-size: 18px;
}

.brand-icon {
  margin-right: 8px;
}

.enterprise-nav-menu {
  flex: 1;
  margin: 0 40px;
  :deep(.n-menu-item) {
    color: rgba(255, 255, 255, 0.9) !important;
  }
  :deep(.n-menu-item.n-menu-item--selected) {
    color: white !important;
    background: rgba(255, 255, 255, 0.925);
  }
}

.enterprise-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.1);
}

.user-name {
  font-size: 14px;
  color: #000000;
}

/* 通知相关样式 */
.notification-container {
  position: relative;
  display: inline-block;
}

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
  background-color: rgba(255, 255, 255, 0.1);
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
  width: 380px;
  background-color: white;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 10000;
  margin-top: 1px; /* 最小化间隙 */
}

.notification-mark-all,
.notification-view-all {
  background: none;
  border: none;
  color: #2d8cf0;
  font-size: 12px;
  cursor: pointer;
  padding: 0;
}

.notification-dropdown {
  width: 380px;
  max-height: 500px;
  padding: 8px 0;
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