import { ref } from 'vue'
import type { Notification } from '@/types/notification'

export class NotificationWebSocketService {
  private socket: WebSocket | null = null
  private reconnectTimer: any = null
  private notificationCallbacks: ((notification: Notification) => void)[] = []
  private connectionCallbacks: (() => void)[] = []
  private disconnectCallbacks: (() => void)[] = []

  public isConnected = ref(false)
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5

  connect() {
    // 清理现有连接
    this.disconnect()

    const backendHost = 'localhost:8000' 
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    
    // 获取token（支持普通用户和企业用户）
    const token = localStorage.getItem('accessToken') || localStorage.getItem('enterpriseToken')
    if (!token) {
      console.warn('⚠️ 未找到token，无法建立WebSocket连接')
      return
    }
    
    // 在URL中添加token参数进行认证
    const wsUrl = `${protocol}//${backendHost}/ws/notifications/?token=${token}`
    
    console.log(`🔄 正在连接通知WebSocket服务...`, {
      url: wsUrl.replace(token, '***'), // 隐藏token
      protocol: protocol,
      backendHost: backendHost
    })

    try {
      this.socket = new WebSocket(wsUrl)
      this.setupEventListeners()
    } catch (error) {
      console.error('❌ 通知WebSocket连接失败', error)
      this.scheduleReconnect()
    }
  }

  private setupEventListeners() {
    if (!this.socket) return

    this.socket.onopen = () => {
      console.log('✅ 通知WebSocket连接成功', {
        url: this.socket?.url,
        readyState: this.getReadyStateText(this.socket?.readyState)
      })
      this.isConnected.value = true
      this.reconnectAttempts = 0 // 重置重连计数
      this.connectionCallbacks.forEach(callback => callback())
    }

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('📨 收到通知WebSocket消息', {
          type: data.type,
          data: data,
          timestamp: new Date().toISOString()
        })
        this.handleIncomingData(data)
      } catch (error) {
        console.error('❌ 解析通知消息失败', error, {
          rawData: event.data
        })
      }
    }

    this.socket.onclose = (event) => {
      console.log('🔌 通知WebSocket连接关闭', {
        code: event.code,
        reason: event.reason,
        wasClean: event.wasClean,
        readyState: this.getReadyStateText(this.socket?.readyState)
      })
      this.isConnected.value = false
      this.disconnectCallbacks.forEach(callback => callback())
      
      if (!event.wasClean) {
        console.warn('⚠️ 通知连接异常关闭，尝试重连...')
        this.scheduleReconnect()
      }
    }

    this.socket.onerror = (error) => {
      console.error('❌ 通知WebSocket错误', {
        error: error,
        url: this.socket?.url,
        readyState: this.getReadyStateText(this.socket?.readyState)
      })
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
    switch (data.type) {
      case 'notification':
        if (data.notification) {
          console.log('🔔 收到新通知', {
            title: data.notification.title,
            type: data.notification.notification_type
          })
          this.notificationCallbacks.forEach(callback => callback(data.notification as Notification))
        }
        break
        
      default:
        console.log('📥 收到未知类型通知消息', {
          type: data.type,
          data: data
        })
    }
  }

  sendMarkAsRead(notificationId: number) {
    if (this.socket && this.isConnected.value) {
      console.log('📋 发送通知已读标记', {
        notificationId: notificationId
      })
      this.socket.send(JSON.stringify({
        type: 'mark_as_read',
        notification_id: notificationId
      }))
    } else {
      console.warn('⚠️ 通知WebSocket未连接，无法发送已读标记')
    }
  }

  disconnect() {
    console.log('🔚 主动断开通知WebSocket连接', {
      wasConnected: this.isConnected.value
    })
    
    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    
    this.isConnected.value = false
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) return
    
    this.reconnectAttempts++
    
    if (this.reconnectAttempts > this.maxReconnectAttempts) {
      console.error('❌ 通知WebSocket达到最大重连次数，停止重连', {
        attempts: this.reconnectAttempts,
        maxAttempts: this.maxReconnectAttempts
      })
      return
    }
    
    console.log(`🔄 通知WebSocket准备重连... (尝试 ${this.reconnectAttempts}/${this.maxReconnectAttempts})`, {
      delay: '3秒后'
    })
    
    this.reconnectTimer = setTimeout(() => {
      console.log('🔄 通知WebSocket尝试重新连接...')
      this.connect()
    }, 3000) // 3秒后重连
  }

  // 事件监听
  onNotification(callback: (notification: Notification) => void) {
    this.notificationCallbacks.push(callback)
    console.log('📩 注册通知回调', {
      callbackCount: this.notificationCallbacks.length
    })
  }

  onConnected(callback: () => void) {
    this.connectionCallbacks.push(callback)
  }

  onDisconnected(callback: () => void) {
    this.disconnectCallbacks.push(callback)
  }

  removeNotificationCallback(callback: (notification: Notification) => void) {
    const index = this.notificationCallbacks.indexOf(callback)
    if (index > -1) {
      this.notificationCallbacks.splice(index, 1)
      console.log('📩 移除通知回调', {
        remainingCallbacks: this.notificationCallbacks.length
      })
    }
  }
}

export const notificationWebSocketService = new NotificationWebSocketService()