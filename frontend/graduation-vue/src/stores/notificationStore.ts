import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Notification } from '@/types/notification'
import { notificationApi } from '@/services/api'
import { getNotificationWebSocketService } from '@/services/notificationWebSocket'

export const useNotificationStore = defineStore('notification', () => {
  // 状态
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const isWebSocketConnected = ref(false)
  
  // 动态获取WebSocket服务
  let notificationWebSocketService: ReturnType<typeof getNotificationWebSocketService> | null = null
  
  const getWebSocketService = () => {
    if (!notificationWebSocketService) {
      notificationWebSocketService = getNotificationWebSocketService()
    }
    return notificationWebSocketService
  }

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
      console.log('📡 [NotificationStore] 开始获取通知列表')
      const response = await notificationApi.getNotifications()
      notifications.value = response.data.results || response.data
      updateUnreadCount()
      console.log('✅ [NotificationStore] 通知列表获取成功', {
        count: notifications.value.length,
        unreadCount: unreadCount.value
      })
    } catch (err: any) {
      error.value = err.message || '获取通知失败'
      console.error('❌ [NotificationStore] 获取通知失败:', err)
    } finally {
      isLoading.value = false
    }
  }

  const fetchUnreadCount = async () => {
    try {
      console.log('📡 [NotificationStore] 开始获取未读通知数量')
      const response = await notificationApi.getUnreadCount()
      unreadCount.value = response.data.unread_count
      console.log('✅ [NotificationStore] 未读通知数量获取成功', {
        unreadCount: unreadCount.value
      })
    } catch (err) {
      console.error('❌ [NotificationStore] 获取未读通知数量失败:', err)
    }
  }

  const markAsRead = async (notificationId: number) => {
    try {
      console.log('📋 [NotificationStore] 标记通知为已读', { notificationId })
      await notificationApi.markAsRead(notificationId)
      const notification = notifications.value.find(n => n.id === notificationId)
      if (notification) {
        notification.is_read = true
      }
      updateUnreadCount()
      console.log('✅ [NotificationStore] 通知已标记为已读')
    } catch (err) {
      console.error('❌ [NotificationStore] 标记通知为已读失败:', err)
    }
  }

  const markAllAsRead = async () => {
    try {
      console.log('📋 [NotificationStore] 标记所有通知为已读')
      await notificationApi.markAllAsRead()
      notifications.value.forEach(notification => {
        notification.is_read = true
      })
      unreadCount.value = 0
      console.log('✅ [NotificationStore] 所有通知已标记为已读')
    } catch (err) {
      console.error('❌ [NotificationStore] 标记所有通知为已读失败:', err)
    }
  }

  const addNotification = (notification: Notification) => {
    console.log('📢 [NotificationStore] 添加新通知到store', {
      notificationId: notification.id,
      isRead: notification.is_read,
      type: notification.notification_type
    })
    
    // 检查是否已存在相同的通知，避免重复添加
    const existingNotification = notifications.value.find(n => n.id === notification.id)
    if (existingNotification) {
      console.log('⚠️ [NotificationStore] 通知已存在，跳过添加', {
        notificationId: notification.id
      })
      return
    }
    
    // 添加到通知列表开头
    notifications.value.unshift(notification)
    updateUnreadCount()
    
    console.log('✅ [NotificationStore] 新通知已添加到store', {
      notificationId: notification.id,
      unreadCount: unreadCount.value,
      totalNotifications: notifications.value.length
    })
  }

  const updateUnreadCount = () => {
    const unread = notifications.value.filter(n => !n.is_read).length
    unreadCount.value = unread
    console.log('🔢 [NotificationStore] 更新未读通知数量', {
      unreadCount: unreadCount.value,
      totalNotifications: notifications.value.length,
      unreadNotifications: unread
    })
  }

  const deleteNotification = async (notificationId: number) => {
    try {
      console.log('🗑️ [NotificationStore] 删除通知', { notificationId })
      await notificationApi.deleteNotification(notificationId)
      const index = notifications.value.findIndex(n => n.id === notificationId)
      if (index > -1) {
        notifications.value.splice(index, 1)
        updateUnreadCount()
      }
      console.log('✅ [NotificationStore] 通知已删除')
    } catch (err) {
      console.error('❌ [NotificationStore] 删除通知失败:', err)
    }
  }

  const deleteAllRead = async () => {
    try {
      console.log('🗑️ [NotificationStore] 删除所有已读通知')
      await notificationApi.deleteAllRead()
      const readNotifications = notifications.value.filter(n => n.is_read)
      readNotifications.forEach(n => {
        const index = notifications.value.findIndex(m => m.id === n.id)
        if (index > -1) {
          notifications.value.splice(index, 1)
        }
      })
      updateUnreadCount()
      console.log('✅ [NotificationStore] 所有已读通知已删除')
    } catch (err) {
      console.error('❌ [NotificationStore] 删除所有已读通知失败:', err)
    }
  }

  // WebSocket相关
  const connectWebSocket = () => {
    console.log('🔌 [NotificationStore] 准备连接WebSocket...', {
      hasToken: !!(sessionStorage.getItem('accessToken') || sessionStorage.getItem('enterpriseToken'))
    })
    
    const wsService = getWebSocketService()
    
    const token = sessionStorage.getItem('accessToken') || sessionStorage.getItem('enterpriseToken')
    if (token && !wsService.isConnected.value) {
      console.log('✅ [NotificationStore] 开始连接WebSocket服务')
      wsService.connect()
    } else {
      console.log('⚠️ [NotificationStore] 跳过WebSocket连接', {
        hasToken: !!token,
        isConnected: wsService.isConnected.value
      })
    }
  }

  const disconnectWebSocket = () => {
    console.log('🔚 [NotificationStore] 断开WebSocket连接')
    getWebSocketService().disconnect()
  }

  // 处理实时通知
  const handleRealTimeNotification = (notification: Notification) => {
    console.log('🔔 [NotificationStore] 收到实时通知', {
      id: notification.id,
      type: notification.notification_type,
      isRead: notification.is_read,
      currentUnreadCount: unreadCount.value
    })
    
    // 添加到通知列表
    addNotification(notification)
    
    console.log('✅ [NotificationStore] 实时通知处理完成', {
      newUnreadCount: unreadCount.value,
      totalNotifications: notifications.value.length
    })
  }

  // 初始化
  const init = async () => {
    console.log('🚀 [NotificationStore] 初始化通知store')
    await Promise.all([fetchNotifications(), fetchUnreadCount()])
    console.log('📊 [NotificationStore] 初始化完成', {
      unreadCount: unreadCount.value,
      totalNotifications: notifications.value.length
    })
  }

  // 注册实时通知处理程序
  const registerNotificationHandler = () => {
    console.log('📝 [NotificationStore] 注册通知处理程序')
    
    const wsService = getWebSocketService()
    
    wsService.onNotification(handleRealTimeNotification)
    
    wsService.onConnected(() => {
      console.log('✅ [NotificationStore] WebSocket连接已建立')
      isWebSocketConnected.value = true
    })
    
    wsService.onDisconnected(() => {
      console.log('🔌 [NotificationStore] WebSocket连接已断开')
      isWebSocketConnected.value = false
    })
    
    wsService.onError((error) => {
      console.error('❌ [NotificationStore] WebSocket错误', error)
      error.value = error.message || 'WebSocket连接错误'
    })
    
    connectWebSocket()
  }

  // 移除实时通知处理程序
  const unregisterNotificationHandler = () => {
    console.log('📝 [NotificationStore] 移除通知处理程序')
    getWebSocketService().removeNotificationCallback(handleRealTimeNotification)
  }

  return {
    // 状态
    notifications,
    unreadCount,
    isLoading,
    error,
    isWebSocketConnected,
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
    deleteNotification,
    deleteAllRead,
    init,
    connectWebSocket,
    disconnectWebSocket,
    registerNotificationHandler,
    unregisterNotificationHandler
  }
})
