<!-- src/components/enterprise/EnterpriseHeader.vue -->
<template>
  <header class="enterprise-header" :class="{ 'header-scrolled': isScrolled }">
    <div class="enterprise-header-content">
      <div class="enterprise-brand" @click="$router.push('/enterprise')">
        <div class="brand-icon-wrapper">
          <n-icon size="32" class="brand-icon">
            <Business />
          </n-icon>
        </div>
        <span class="brand-text">企业服务中心</span>
      </div>

      <n-menu 
        mode="horizontal" 
        :options="enterpriseMenuOptions" 
        class="enterprise-nav-menu"
        @update-value="handleMenuSelect"
        responsive
      />

      <div class="enterprise-actions">
        <n-button 
          type="primary" 
          size="medium" 
          @click="handlePublishJob"
          round
        >
          <template #icon>
            <n-icon><Add /></n-icon>
          </template>
          发布招聘
        </n-button>
        
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
          trigger="hover" 
          :options="userDropdownOptions"
          @select="handleUserAction"
        >
          <div class="user-info">
            <n-avatar 
              size="small" 
              :src="userAvatar"
              class="user-avatar"
              round
              bordered
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
import { ref, onMounted, onUnmounted, computed, h } from 'vue'
import { useRouter } from 'vue-router'
import { 
  NMenu, NButton, NIcon, NAvatar, NDropdown, NBadge, NSpin 
} from 'naive-ui'
import { Add, PersonCircle, Settings, LogOut, Business, Notifications, NotificationsOutline } from '@vicons/ionicons5'
import { useNotificationStore } from '@/stores/notificationStore'
import axios from '@/utils/axios'

const router = useRouter()

const userAvatar = ref('')
const userName = ref('企业用户')
const isScrolled = ref(false)

const notificationStore = useNotificationStore()
const unreadCount = computed(() => notificationStore.unreadCount)
const notifications = computed(() => notificationStore.sortedNotifications.slice(0, 5))
const showNotification = ref(false)

const openNotificationDropdown = () => {
  showNotification.value = true
  notificationStore.fetchNotifications()
}

const closeNotificationDropdown = () => {
  setTimeout(() => {
    showNotification.value = false
  }, 200)
}

const enterpriseMenuOptions = ref([
  {key:'home', label:'首页'},
  { key: 'recruitments', label: '招聘管理' },
  { key: 'applications', label: '简历库', },
  {key:'talent-pool', label:'人才库'},
  { key: 'analytics', label: '数据统计', },
  { key: 'company', label: '企业信息',}
])

const userDropdownOptions = ref([
  { key: 'profile', label: '企业资料', icon: Settings },
  { key: 'settings', label: '账户设置', icon: Settings },
  { key: 'divider', type: 'divider' },
  { key: 'logout', label: '退出登录', icon: LogOut, type: 'warning' }
])

const handleMenuSelect = (key) => {
  if (key === 'company') {
    const enterpriseInfo = JSON.parse(localStorage.getItem('enterpriseInfo') || '{}')
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
    const userId = userInfo.id
    if (userId) {
      router.push(`/enterprise/${userId}`)
    } else {
      router.push('/enterprise/edit')
    }
  } else {
    router.push(`/enterprise/${key}`)
  }
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

const handleScroll = () => {
  isScrolled.value = window.scrollY > 50
}

onMounted(() => {
  initializeEnterpriseUser()
  notificationStore.registerNotificationHandler()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  notificationStore.unregisterNotificationHandler()
  window.removeEventListener('scroll', handleScroll)
})

const initializeEnterpriseUser = async () => {
  try {
    const response = await axios.get('/enterprises/')
    let enterpriseData = response.data
    
    if (Array.isArray(enterpriseData) && enterpriseData.length > 0) {
      enterpriseData = enterpriseData[0]
    } else if (!enterpriseData || typeof enterpriseData !== 'object') {
      enterpriseData = {}
    }
    
    const enterpriseInfo = {
      id: enterpriseData.id,
      name: enterpriseData.name,
      logo: enterpriseData.logo,
      avatar: enterpriseData.logo
    }
    localStorage.setItem('enterpriseInfo', JSON.stringify(enterpriseInfo))
    
    userAvatar.value = enterpriseInfo.logo || enterpriseInfo.avatar || ''
    userName.value = enterpriseInfo.name || '企业用户'
    
  } catch (error) {
    console.error('获取企业信息失败:', error)
    const enterpriseInfo = JSON.parse(localStorage.getItem('enterpriseInfo') || '{}')
    userAvatar.value = enterpriseInfo.logo || enterpriseInfo.avatar || ''
    userName.value = enterpriseInfo.name || '企业用户'
  } finally {
    await notificationStore.init()
  }
}

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
  console.log('跳转到通知列表页面')
}
</script>

<style scoped>
.enterprise-header {
  background: linear-gradient(135deg, #bad2ce 0%, #9ddcd0 100%);
  color: rgb(48, 35, 35);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
  transition: all 0.3s ease;
}

.header-scrolled {
  background: linear-gradient(135deg,  #bad2ce 0%, #9ddcd0 100%);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

/* .header-placeholder {
  height: 64px;
  transition: height 0.3s ease;
}

.header-scrolled + .header-placeholder {
  height: 56px;
} */

.enterprise-header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  transition: all 0.3s ease;
}

.header-scrolled .enterprise-header-content {
  height: 56px;
}

.enterprise-brand {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: 600;
  font-size: 18px;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.enterprise-brand:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.brand-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 10px;
  margin-right: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.brand-icon {
  color: rgb(26, 25, 25);
}

.brand-text {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.enterprise-nav-menu {
  flex: 1;
  margin: 0 40px;
}

.enterprise-nav-menu :deep(.n-menu-item) {
  color: rgba(255, 255, 255, 0.9) !important;
  border-radius: 8px;
  margin: 0 4px;
  transition: all 0.2s ease;
}

.enterprise-nav-menu :deep(.n-menu-item:hover) {
  background: rgba(255, 255, 255, 0.1);
}

.enterprise-nav-menu :deep(.n-menu-item.n-menu-item--selected) {
  background: rgba(255, 255, 255, 0.2);
  color: white !important;
  font-weight: 600;
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
  padding: 4px 12px;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.1);
}

.user-name {
  font-size: 14px;
  color: white;
  font-weight: 500;
}

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

.notification-icon {
  color: rgba(255, 255, 255, 0.9);
  transition: color 0.2s ease;
}

.notification-trigger:hover .notification-icon {
  color: white;
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

.user-avatar {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid rgba(255, 255, 255, 0.5);
}

.user-avatar:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

@media (max-width: 768px) {
  .enterprise-header-content {
    flex-wrap: wrap;
    padding: 8px 20px;
  }
  
  .enterprise-brand {
    order: 1;
  }
  
  .enterprise-nav-menu {
    order: 3;
    width: 100%;
    margin: 8px 0 0 0;
  }
  
  .enterprise-actions {
    order: 2;
    margin-left: auto;
  }
  
  .notification-dropdown {
    width: 320px;
    right: -20px;
  }
}

@media (max-width: 480px) {
  .enterprise-header-content {
    padding: 8px 16px;
  }
  
  .brand-icon-wrapper {
    width: 36px;
    height: 36px;
  }
  
  .brand-icon-wrapper .n-icon {
    font-size: 24px;
  }
  
  .brand-text {
    font-size: 16px;
  }
  
  .notification-dropdown {
    width: 280px;
  }
}
</style>