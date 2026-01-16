import { defineStore } from 'pinia'
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { Notification } from '@/types/notification'
import { notificationApi } from '@/services/api'
import { notificationWebSocketService } from '@/services/notificationWebSocket'

export const useNotificationStore = defineStore('notification', () => {
  // 状态
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const unreadNotifications = computed(() => {
    return notifications.value.filter(notification => !notification.is_read)
  })

  const sortedNotifications = computed(() => {
    return [...notifications.value].sort((a, b) => {
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    })
  })

  // 动作
  const fetchNotifications = async () => {
    try {
      isLoading.value = true
      error.value = null
      const response = await notificationApi.getNotifications()
      notifications.value = response.data.results || response.data
      updateUnreadCount()
    } catch (err: any) {
      error.value = err.message || '获取通知失败'
      console.error('获取通知失败:', err)
    } finally {
      isLoading.value = false
    }
  }

  const fetchUnreadCount = async () => {
    try {
      const response = await notificationApi.getUnreadCount()
      unreadCount.value = response.data.unread_count
    } catch (err) {
      console.error('获取未读通知数量失败:', err)
    }
  }

  const markAsRead = async (notificationId: number) => {
    try {
      await notificationApi.markAsRead(notificationId)
      const notification = notifications.value.find(n => n.id === notificationId)
      if (notification) {
        notification.is_read = true
      }
      updateUnreadCount()
    } catch (err) {
      console.error('标记通知为已读失败:', err)
    }
  }

  const markAllAsRead = async () => {
    try {
      await notificationApi.markAllAsRead()
      notifications.value.forEach(notification => {
        notification.is_read = true
      })
      unreadCount.value = 0
    } catch (err) {
      console.error('标记所有通知为已读失败:', err)
    }
  }

  const addNotification = (notification: Notification) => {
    notifications.value.unshift(notification)
    updateUnreadCount()
  }

  const updateUnreadCount = () => {
    unreadCount.value = notifications.value.filter(n => !n.is_read).length
  }

  // WebSocket相关
  const connectWebSocket = () => {
    // 检查用户是否登录（有token）
    const token = localStorage.getItem('accessToken') || localStorage.getItem('enterpriseToken')
    if (token && !notificationWebSocketService.isConnected.value) {
      notificationWebSocketService.connect()
    }
  }

  const disconnectWebSocket = () => {
    notificationWebSocketService.disconnect()
  }

  // 处理实时通知
  const handleRealTimeNotification = (notification: Notification) => {
    // 添加到通知列表
    addNotification(notification)
    // 可以在这里添加弹窗提示等功能
    console.log('收到实时通知:', notification)
  }

  // 初始化
  const init = async () => {
    await Promise.all([fetchNotifications(), fetchUnreadCount()])
    // 连接WebSocket
    connectWebSocket()
  }

  // 组件挂载时连接WebSocket并监听通知
  onMounted(() => {
    notificationWebSocketService.onNotification(handleRealTimeNotification)
    connectWebSocket()
  })

  // 组件卸载时清理WebSocket连接
  onUnmounted(() => {
    notificationWebSocketService.removeNotificationCallback(handleRealTimeNotification)
    // 注意：这里不直接断开连接，因为可能有其他组件也在使用通知WebSocket
    // disconnectWebSocket()
  })

  return {
    // 状态
    notifications,
    unreadCount,
    isLoading,
    error,
    // 计算属性
    unreadNotifications,
    sortedNotifications,
    // 动作
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    addNotification,
    updateUnreadCount,
    init,
    connectWebSocket,
    disconnectWebSocket
  }
})