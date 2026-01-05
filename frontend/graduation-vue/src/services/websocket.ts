import { ref } from 'vue'
import type { WebSocketData, Message } from '@/types/chat'

export class WebSocketService {
  private socket: WebSocket | null = null
  private reconnectTimer: any = null
  private messageCallbacks: ((message: Message) => void)[] = []
  private readReceiptCallbacks: ((messageId: number, readerId: number) => void)[] = []
  private connectionCallbacks: (() => void)[] = []
  private disconnectCallbacks: (() => void)[] = []

  public isConnected = ref(false)
  public roomId: number | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5

  connect(roomId: number) {
    this.roomId = roomId
    
    // 清理现有连接
    this.disconnect()

    const backendHost = 'localhost:8000' 
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${backendHost}/ws/chat/${roomId}/`
    
    console.log(`🔄 正在连接WebSocket服务...`, {
      url: wsUrl,
      roomId: roomId,
      protocol: protocol,
      backendHost: backendHost
    })

    try {
      this.socket = new WebSocket(wsUrl)
      this.setupEventListeners()
    } catch (error) {
      console.error('❌ WebSocket连接失败', error)
      this.scheduleReconnect()
    }
  }

  private setupEventListeners() {
    if (!this.socket) return

    this.socket.onopen = () => {
      console.log('✅ WebSocket连接成功', {
        roomId: this.roomId,
        url: this.socket?.url,
        readyState: this.getReadyStateText(this.socket?.readyState)
      })
      this.isConnected.value = true
      this.reconnectAttempts = 0 // 重置重连计数
      this.connectionCallbacks.forEach(callback => callback())
    }

    this.socket.onmessage = (event) => {
      try {
        const data: WebSocketData = JSON.parse(event.data)
        console.log('📨 收到WebSocket消息', {
          type: data.type,
          data: data,
          timestamp: new Date().toISOString()
        })
        this.handleIncomingData(data)
      } catch (error) {
        console.error('❌ 解析消息失败', error, {
          rawData: event.data
        })
      }
    }

    this.socket.onclose = (event) => {
      console.log('🔌 WebSocket连接关闭', {
        code: event.code,
        reason: event.reason,
        wasClean: event.wasClean,
        readyState: this.getReadyStateText(this.socket?.readyState)
      })
      this.isConnected.value = false
      this.disconnectCallbacks.forEach(callback => callback())
      
      if (!event.wasClean) {
        console.warn('⚠️ 连接异常关闭，尝试重连...')
        this.scheduleReconnect()
      }
    }

    this.socket.onerror = (error) => {
      console.error('❌ WebSocket错误', {
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

  private handleIncomingData(data: WebSocketData) {
    switch (data.type) {
      case 'connection_established':
        console.log('🔗 WebSocket连接已建立', {
          roomId: this.roomId,
          timestamp: new Date().toISOString()
        })
        break
        
      case 'chat_message':
        if (data.message) {
          console.log('💬 收到聊天消息', {
            messageId: data.message.id,
            content: data.message.content
          })
          this.messageCallbacks.forEach(callback => callback(data.message as Message))
        }
        break
        
      case 'read_receipt':
        if (data.message_id && data.reader_id) {
          console.log('👀 收到已读回执', {
            messageId: data.message_id,
            readerId: data.reader_id
          })
          this.readReceiptCallbacks.forEach(callback => 
            callback(data.message_id!, data.reader_id!)
          )
        }
        break
        
      default:
        console.log('📥 收到未知类型消息', {
          type: data.type,
          data: data
        })
    }
  }

  sendMessage(content: string, messageType: 'text' | 'file' = 'text') {
    if (this.socket && this.isConnected.value) {
      const message = {
        type: 'chat_message',
        content,
        message_type: messageType
      }
      console.log('📤 发送消息', {
        content: content,
        type: messageType,
        readyState: this.getReadyStateText(this.socket.readyState)
      })
      this.socket.send(JSON.stringify(message))
    } else {
      console.warn('⚠️ WebSocket未连接，无法发送消息', {
        isConnected: this.isConnected.value,
        socketExists: !!this.socket
      })
    }
  }

  sendReadReceipt(messageId: number) {
    if (this.socket && this.isConnected.value) {
      console.log('📋 发送已读回执', {
        messageId: messageId
      })
      this.socket.send(JSON.stringify({
        type: 'read_receipt',
        message_id: messageId
      }))
    } else {
      console.warn('⚠️ WebSocket未连接，无法发送已读回执')
    }
  }

  disconnect() {
    console.log('🔚 主动断开WebSocket连接', {
      roomId: this.roomId,
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
      console.error('❌ 达到最大重连次数，停止重连', {
        attempts: this.reconnectAttempts,
        maxAttempts: this.maxReconnectAttempts
      })
      return
    }
    
    console.log(`🔄 准备重连... (尝试 ${this.reconnectAttempts}/${this.maxReconnectAttempts})`, {
      delay: '3秒后',
      roomId: this.roomId
    })
    
    this.reconnectTimer = setTimeout(() => {
      if (this.roomId) {
        console.log('🔄 尝试重新连接...')
        this.connect(this.roomId)
      }
    }, 3000) // 3秒后重连
  }

  // 添加检查连接状态的方法
  checkConnectionStatus() {
    console.log('🔍 WebSocket连接状态检查', {
      isConnected: this.isConnected.value,
      roomId: this.roomId,
      socketExists: !!this.socket,
      readyState: this.socket ? this.getReadyStateText(this.socket.readyState) : 'NO_SOCKET',
      reconnectAttempts: this.reconnectAttempts,
      maxReconnectAttempts: this.maxReconnectAttempts
    })
  }

  // 事件监听
  onMessage(callback: (message: Message) => void) {
    this.messageCallbacks.push(callback)
    console.log('📩 注册消息回调', {
      callbackCount: this.messageCallbacks.length
    })
  }

  onReadReceipt(callback: (messageId: number, readerId: number) => void) {
    this.readReceiptCallbacks.push(callback)
  }

  onConnected(callback: () => void) {
    this.connectionCallbacks.push(callback)
  }

  onDisconnected(callback: () => void) {
    this.disconnectCallbacks.push(callback)
  }

  removeMessageCallback(callback: (message: Message) => void) {
    const index = this.messageCallbacks.indexOf(callback)
    if (index > -1) {
      this.messageCallbacks.splice(index, 1)
      console.log('📩 移除消息回调', {
        remainingCallbacks: this.messageCallbacks.length
      })
    }
  }
}

export const webSocketService = new WebSocketService()

// 在控制台快速检查的方法
declare global {
  interface Window {
    checkWebSocket: () => void;
  }
}

// 添加到全局，方便在浏览器控制台直接调用
if (typeof window !== 'undefined') {
  window.checkWebSocket = () => {
    webSocketService.checkConnectionStatus()
  }
  console.log('💡 提示: 在控制台输入 checkWebSocket() 来检查WebSocket状态')
}