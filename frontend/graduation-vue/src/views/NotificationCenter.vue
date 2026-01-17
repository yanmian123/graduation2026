<template>
  <div class="notification-center-container">
    <n-card class="main-card" title="通知中心">
      <!-- 顶部操作栏 -->
      <div class="top-actions">
        <n-select
          v-model:value="filterStatus"
          placeholder="筛选通知"
          class="filter-select"
          size="medium"
          :options="filterOptions"
        />
        
        <n-button
          type="primary"
          size="medium"
          @click="handleMarkAllAsRead"
          :disabled="notificationStore.isLoading || filteredNotifications.length === 0"
        >
          <template #icon>
            <n-icon><CheckmarkCircle /></n-icon>
          </template>
          全部标记为已读
        </n-button>
      </div>
      
      <!-- 通知列表 -->
      <div class="notification-list-container">
        <n-skeleton
          v-if="notificationStore.isLoading"
          :repeat="5"
          :row-props="{ width: '100%', height: '80px', marginBottom: '16px' }"
        />
        
        <n-empty
          v-else-if="filteredNotifications.length === 0"
          description="暂无通知"
          size="large"
        >
          <template #icon>
            <n-icon size="48"><NotificationsOff /></n-icon>
          </template>
        </n-empty>
        
        <n-card
          v-else
          v-for="notification in filteredNotifications"
          :key="notification.id"
          class="notification-card"
          :class="{ 'unread': !notification.is_read }"
          @click="handleNotificationClick(notification)"
        >
          <div class="notification-header">
            <n-tag
              :type="notification.is_read ? 'default' : 'primary'"
              size="small"
              round
            >
              {{ notification.is_read ? '已读' : '未读' }}
            </n-tag>
            <span class="notification-time">
              {{ formatNotificationTime(notification.created_at) }}
            </span>
          </div>
          
          <div class="notification-title">{{ notification.title }}</div>
          <div class="notification-content">{{ notification.message }}</div>
        </n-card>
      </div>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <n-pagination
          v-model:page="currentPage"
          v-model:page-size="pageSize"
          :page-count="totalPages"
          show-size-picker
          :page-sizes="[10, 20, 50]"
          @update:page="handlePageChange"
          @update:page-size="handlePageSizeChange"
        />
      </div>
    </n-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  NCard,
  NSelect,
  NButton,
  NIcon,
  NSkeleton,
  NEmpty,
  NTag,
  NPagination,
  useMessage
} from 'naive-ui'
import { CheckmarkCircle, NotificationsOff } from '@vicons/ionicons5'
import { useNotificationStore } from '@/stores/notificationStore'

const message = useMessage()
const router = useRouter()

// 通知存储
const notificationStore = useNotificationStore()

// 筛选和分页
const filterStatus = ref('all') // all, unread, read
const currentPage = ref(1)
const pageSize = ref(10)

// 筛选选项
const filterOptions = [
  { value: 'all', label: '全部通知' },
  { value: 'unread', label: '未读通知' },
  { value: 'read', label: '已读通知' }
]

// 计算属性：筛选后的通知
const filteredNotifications = computed(() => {
  let filtered = notificationStore.sortedNotifications
  
  switch (filterStatus.value) {
    case 'unread':
      filtered = filtered.filter(n => !n.is_read)
      break
    case 'read':
      filtered = filtered.filter(n => n.is_read)
      break
  }
  
  // 分页
  const startIndex = (currentPage.value - 1) * pageSize.value
  const endIndex = startIndex + pageSize.value
  return filtered.slice(startIndex, endIndex)
})

// 计算属性：总页数
const totalPages = computed(() => {
  const filtered = notificationStore.sortedNotifications.filter(n => {
    switch (filterStatus.value) {
      case 'unread':
        return !n.is_read
      case 'read':
        return n.is_read
      default:
        return true
    }
  })
  return Math.ceil(filtered.length / pageSize.value)
})

// 方法：标记所有通知为已读
const handleMarkAllAsRead = async () => {
  try {
    await notificationStore.markAllAsRead()
    message.success('所有通知已标记为已读')
  } catch (error) {
    console.error('标记全部已读失败:', error)
    message.error('标记全部已读失败')
  }
}

// 方法：点击通知
const handleNotificationClick = async (notification) => {
  if (!notification.is_read) {
    // 标记为已读
    await notificationStore.markAsRead(notification.id)
  }
  
  // 可以在这里添加通知点击后的逻辑，比如跳转到相关页面
  console.log('通知点击:', notification)
}

// 方法：分页变化
const handlePageChange = () => {
  // 页面变化时自动滚动到顶部
  window.scrollTo(0, 0)
}

// 方法：每页条数变化
const handlePageSizeChange = () => {
  currentPage.value = 1 // 重置到第一页
  window.scrollTo(0, 0)
}

// 方法：格式化通知时间（相对时间）
const formatNotificationTime = (timeValue) => {
  try {
    let date
    
    // 检查输入类型
    if (timeValue instanceof Date) {
      date = timeValue
    } else if (typeof timeValue === 'string' || typeof timeValue === 'number') {
      date = new Date(timeValue)
    } else {
      throw new Error('Invalid time value type')
    }
    
    // 检查时间是否有效
    if (isNaN(date.getTime())) {
      throw new Error('Invalid time value')
    }
    
    const now = new Date()
    const diffMs = now - date
    const diffSecs = Math.floor(diffMs / 1000)
    const diffMins = Math.floor(diffSecs / 60)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)
    
    if (diffDays > 30) {
      // 超过30天显示具体日期
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
    } else if (diffDays > 0) {
      return `${diffDays}天前`
    } else if (diffHours > 0) {
      return `${diffHours}小时前`
    } else if (diffMins > 0) {
      return `${diffMins}分钟前`
    } else {
      return '刚刚'
    }
  } catch (error) {
    console.warn('Invalid time value, using default display:', timeValue)
    return '未知时间'
  }
}

// 生命周期：组件挂载时加载通知
onMounted(async () => {
  await notificationStore.fetchNotifications()
})
</script>

<style scoped>
.notification-center-container {
  max-width: 800px;
  margin: 24px auto;
  padding: 0 20px;
}

.main-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-radius: 8px;
}

.top-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.filter-select {
  width: 180px;
}

.notification-list-container {
  margin-bottom: 24px;
}

.notification-card {
  margin-bottom: 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}

.notification-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.notification-card.unread {
  border-left-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(45, 140, 240, 0.15);
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.notification-title {
  font-weight: 600;
  font-size: 16px;
  margin-bottom: 8px;
  color: var(--text-color-strong);
}

.notification-content {
  font-size: 14px;
  color: var(--text-color-secondary);
  line-height: 1.5;
  white-space: pre-wrap;
}

.notification-time {
  font-size: 12px;
  color: var(--text-color-tertiary);
  font-weight: 400;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}
</style>