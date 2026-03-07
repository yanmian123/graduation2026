import { ref } from 'vue'
import type { Notification } from '@/types/notification'

class NotificationWebSocketService {
  private socket: WebSocket | null = null
  private reconnectTimer: any = null
  private heartbeatTimer: any = null
  private notificationCallbacks: ((notification: Notification) => void)[] = []
  private connectionCallbacks: (() => void)[] = []
  private disconnectCallbacks: (() => void)[] = []
  private errorCallback: ((error: any) => void) | null = null

  public isConnected = ref(false)
  private reconnectAttempts = 0
  private maxReconnectAttempts = 10
  private reconnectDelay = 3000
  private heartbeatInterval = 30000
  private userId: string | null = null
  private currentToken: string | null = null
  private storageListener: (() => void) | null = null

  constructor() {
    this.userId = this.getUserId()
    this.currentToken = this.getToken()
    this.setupStorageListener()
  }

  private getToken(): string | null {
    return sessionStorage.getItem('accessToken') || sessionStorage.getItem('enterpriseToken')
  }

  private setupStorageListener() {
    this.storageListener = () => {
      const newToken = this.getToken()
      if (newToken !== this.currentToken) {
        console.log('🔄 [NotificationWebSocket] Token发生变化，重新连接', {
          oldTokenPrefix: this.currentToken?.substring(0, 20) + '...',
          newTokenPrefix: newToken?.substring(0, 20) + '...'
        })
        this.currentToken = newToken
        this.userId = this.getUserId()
        if (newToken) {
          this.connect()
        } else {
          this.disconnect()
        }
      }
    }
    
    window.addEventListener('storage', this.storageListener)
  }

  private getUserId(): string | null {
    const token = sessionStorage.getItem('accessToken') || sessionStorage.getItem('enterpriseToken')
    if (!token) return null
    
    try {
      const payload = token.split('.')[1]
      const decoded = JSON.parse(atob(payload))
      return decoded.user_id || decoded.userId || decoded.sub
    } catch (error) {
      console.error('❌ [NotificationWebSocket] 解析token失败', error)
      return null
    }
  }

  getInstanceKey(): string {
    return `notification_ws_${this.userId || 'anonymous'}`
  }

  connect() {
    console.log('🔌 [NotificationWebSocket] 开始连接WebSocket...', {
      currentConnectionState: this.isConnected.value,
      existingSocket: !!this.socket,
      userId: this.userId
    })
    
    if (this.socket && this.isConnected.value) {
      console.log('⚠️ [NotificationWebSocket] WebSocket已连接，跳过重复连接')
      return
    }
    
    const backendHost = 'localhost:8000' 
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    
    const token = sessionStorage.getItem('accessToken') || sessionStorage.getItem('enterpriseToken')
    if (!token) {
      console.error('❌ [NotificationWebSocket] 未找到token，无法建立WebSocket连接')
      console.log('🔍 [NotificationWebSocket] 检查sessionStorage:', {
        accessToken: !!sessionStorage.getItem('accessToken'),
        enterpriseToken: !!sessionStorage.getItem('enterpriseToken')
      })
      this.handleError(new Error('No token found'))
      return
    }
    
    const wsUrl = `${protocol}//${backendHost}/ws/notifications/?token=${token}`
    
    console.log(`🔄 [NotificationWebSocket] 正在连接通知WebSocket服务...`, {
      url: wsUrl.replace(token, '***'),
      protocol: protocol,
      backendHost: backendHost,
      tokenLength: token.length,
      tokenPrefix: token.substring(0, 20) + '...'
    })

    try {
      this.socket = new WebSocket(wsUrl)
      console.log('🎯 [NotificationWebSocket] WebSocket对象已创建，准备设置事件监听器')
      this.setupEventListeners()
    } catch (error) {
      console.error('❌ [NotificationWebSocket] WebSocket连接失败', error)
      this.handleError(error)
      this.scheduleReconnect()
    }
  }

  private setupEventListeners() {
    if (!this.socket) {
      console.error('❌ [NotificationWebSocket] Socket对象不存在，无法设置事件监听器')
      return
    }

    console.log('🎧 [NotificationWebSocket] 设置WebSocket事件监听器')

    this.socket.onopen = () => {
      console.log('✅ [NotificationWebSocket] WebSocket连接成功', {
        url: this.socket?.url,
        readyState: this.getReadyStateText(this.socket?.readyState),
        registeredCallbacks: this.notificationCallbacks.length
      })
      this.isConnected.value = true
      this.reconnectAttempts = 0 // 重置重连计数
      
      // 验证回调函数是否正确注册
      if (this.notificationCallbacks.length === 0) {
        console.warn('⚠️ [NotificationWebSocket] WebSocket已连接但没有注册任何通知回调函数！')
      } else {
        console.log('✅ [NotificationWebSocket] 已注册的通知回调函数数量:', this.notificationCallbacks.length)
      }
      
      // 启动心跳检测
      this.startHeartbeat()
      
      // 触发连接回调
      this.connectionCallbacks.forEach(callback => {
        try {
          callback()
        } catch (error) {
          console.error('❌ [NotificationWebSocket] 连接回调执行失败', error)
        }
      })
    }

    this.socket.onmessage = (event) => {
      console.log('📨 [NotificationWebSocket] 收到WebSocket消息', {
        rawData: event.data,
        timestamp: new Date().toISOString()
      })
      try {
        const data = JSON.parse(event.data)
        console.log('📨 [NotificationWebSocket] 解析后的消息', {
          type: data.type,
          hasNotification: !!data.notification,
          notificationId: data.notification?.id,
          notificationType: data.notification?.notification_type
        })
        this.handleIncomingData(data)
      } catch (error) {
        console.error('❌ [NotificationWebSocket] 解析消息失败', error, {
          rawData: event.data
        })
        this.handleError(error)
      }
    }

    this.socket.onclose = (event) => {
      console.log('🔌 [NotificationWebSocket] WebSocket连接关闭', {
        code: event.code,
        reason: event.reason,
        wasClean: event.wasClean,
        readyState: this.getReadyStateText(this.socket?.readyState)
      })
      this.isConnected.value = false
      this.stopHeartbeat()
      
      // 触发断开连接回调
      this.disconnectCallbacks.forEach(callback => {
        try {
          callback()
        } catch (error) {
          console.error('❌ [NotificationWebSocket] 断开连接回调执行失败', error)
        }
      })
      
      // 如果不是正常关闭，尝试重连
      if (!event.wasClean && event.code !== 1000) {
        console.warn('⚠️ [NotificationWebSocket] 连接异常关闭，尝试重连...')
        this.scheduleReconnect()
      }
    }

    this.socket.onerror = (error) => {
      console.error('❌ [NotificationWebSocket] WebSocket错误', {
        error: error,
        url: this.socket?.url,
        readyState: this.getReadyStateText(this.socket?.readyState)
      })
      this.handleError(error)
    }
  }

  private getReadyStateText(state: number | undefined): string {
    const states = {
      0: 'CONNECTING',
      1: 'OPEN',
      2: 'CLOSING',
      3: 'CLOSED'
    }
    return states[state as keyof typeof states] || 'UNKNOWN'
  }

  private handleIncomingData(data: any) {
    console.log('📥 [NotificationWebSocket] 处理收到的数据', {
      type: data.type,
      hasNotification: !!data.notification,
      callbacksCount: this.notificationCallbacks.length
    })
    
    try {
      switch (data.type) {
        case 'connection_established':
          console.log('✅ [NotificationWebSocket] 连接已建立确认', data)
          break
          
        case 'notification':
          if (data.notification) {
            console.log('🔔 [NotificationWebSocket] 收到新通知', {
              title: data.notification.title,
              type: data.notification.notification_type,
              id: data.notification.id,
              isRead: data.notification.is_read
            })
            this.notificationCallbacks.forEach(callback => {
              try {
                console.log('📤 [NotificationWebSocket] 调用通知回调函数', {
                  callbackIndex: this.notificationCallbacks.indexOf(callback),
                  totalCallbacks: this.notificationCallbacks.length
                })
                callback(data.notification as Notification)
              } catch (error) {
                console.error('❌ [NotificationWebSocket] 通知回调执行失败', error)
              }
            })
          } else {
            console.warn('⚠️ [NotificationWebSocket] 收到notification类型消息但没有notification数据', data)
          }
          break
          
        case 'pong':
          console.log('💓 [NotificationWebSocket] 收到心跳响应', {
            timestamp: data.timestamp
          })
          break
          
        case 'error':
          console.error('🚨 [NotificationWebSocket] 收到服务器错误', data)
          this.handleError(new Error(data.message || 'Server error'))
          break
          
        default:
          console.log('📥 [NotificationWebSocket] 收到未知类型消息', {
            type: data.type,
            data: data
          })
      }
    } catch (error) {
      console.error('❌ [NotificationWebSocket] 处理消息时出错', error)
      this.handleError(error)
    }
  }

  private startHeartbeat() {
    console.log('💓 [NotificationWebSocket] 启动心跳检测')
    this.stopHeartbeat()
    
    this.heartbeatTimer = setInterval(() => {
      if (this.socket && this.isConnected.value) {
        console.log('💓 [NotificationWebSocket] 发送心跳')
        this.socket.send(JSON.stringify({
          type: 'ping',
          timestamp: Date.now()
        }))
      }
    }, this.heartbeatInterval)
  }

  private stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
      console.log('⏹️ [NotificationWebSocket] 停止心跳检测')
    }
  }

  sendMarkAsRead(notificationId: number) {
    if (this.socket && this.isConnected.value) {
      console.log('📋 [NotificationWebSocket] 发送通知已读标记', {
        notificationId: notificationId
      })
      this.socket.send(JSON.stringify({
        type: 'mark_as_read',
        notification_id: notificationId
      }))
    } else {
      console.warn('⚠️ [NotificationWebSocket] WebSocket未连接，无法发送已读标记')
    }
  }

  disconnect() {
    console.log('🔚 [NotificationWebSocket] 主动断开WebSocket连接', {
      wasConnected: this.isConnected.value
    })
    
    this.stopHeartbeat()
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    
    if (this.socket) {
      this.socket.close(1000, 'Normal closure')
      this.socket = null
    }
    
    this.isConnected.value = false
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) return
    
    this.reconnectAttempts++
    
    if (this.reconnectAttempts > this.maxReconnectAttempts) {
      console.error('❌ [NotificationWebSocket] 达到最大重连次数，停止重连', {
        attempts: this.reconnectAttempts,
        maxAttempts: this.maxReconnectAttempts
      })
      this.handleError(new Error('Max reconnection attempts reached'))
      return
    }
    
    // 指数退避策略
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000)
    
    console.log(`🔄 [NotificationWebSocket] 准备重连... (尝试 ${this.reconnectAttempts}/${this.maxReconnectAttempts})`, {
      delay: `${delay}ms后`
    })
    
    this.reconnectTimer = setTimeout(() => {
      console.log('🔄 [NotificationWebSocket] 尝试重新连接...')
      this.connect()
    }, delay)
  }

  private handleError(error: any) {
    console.error('❌ [NotificationWebSocket] WebSocket错误', error)
    if (this.errorCallback) {
      try {
        this.errorCallback(error)
      } catch (e) {
        console.error('❌ [NotificationWebSocket] 错误回调执行失败', e)
      }
    }
  }

  // 事件监听
  onNotification(callback: (notification: Notification) => void) {
    this.notificationCallbacks.push(callback)
    console.log('📩 [NotificationWebSocket] 注册通知回调', {
      callbackCount: this.notificationCallbacks.length
    })
  }

  onConnected(callback: () => void) {
    this.connectionCallbacks.push(callback)
  }

  onDisconnected(callback: () => void) {
    this.disconnectCallbacks.push(callback)
  }

  onError(callback: (error: any) => void) {
    this.errorCallback = callback
  }

  removeNotificationCallback(callback: (notification: Notification) => void) {
    const index = this.notificationCallbacks.indexOf(callback)
    if (index > -1) {
      this.notificationCallbacks.splice(index, 1)
      console.log('📩 [NotificationWebSocket] 移除通知回调', {
        remainingCallbacks: this.notificationCallbacks.length
      })
    }
  }
}

export function getNotificationWebSocketService(): NotificationWebSocketService {
  const token = sessionStorage.getItem('accessToken') || sessionStorage.getItem('enterpriseToken')
  
  if (!token) {
    console.warn('⚠️ [NotificationWebSocket] 未找到token，返回默认实例')
    return new NotificationWebSocketService()
  }
  
  try {
    const payload = token.split('.')[1]
    const decoded = JSON.parse(atob(payload))
    const userId = decoded.user_id || decoded.userId || decoded.sub || 'anonymous'
    const instanceKey = `notification_ws_${userId}`
    
    console.log('🔑 [NotificationWebSocket] 获取WebSocket服务实例', {
      userId,
      instanceKey,
      existingInstance: !!(window as any)[instanceKey]
    })
    
    if (!(window as any)[instanceKey]) {
      console.log('✅ [NotificationWebSocket] 创建新的WebSocket服务实例', { userId })
      ;(window as any)[instanceKey] = new NotificationWebSocketService()
    }
    
    return (window as any)[instanceKey]
  } catch (error) {
    console.error('❌ [NotificationWebSocket] 解析token失败，返回默认实例', error)
    return new NotificationWebSocketService()
  }
}

export const notificationWebSocketService = getNotificationWebSocketService()
