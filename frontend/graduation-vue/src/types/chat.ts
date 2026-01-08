// 定义聊天相关的接口类型
export interface User {
  id: number
  username: string
  nickname: string
  avatar?: string
  is_enterprise: boolean
  email?: string
  phone?: string
}

export interface Message {
  id: number
  chat_room: number
  sender: number
  sender_info: User
  content: string
  message_type: 'text' | 'file' | 'system'
  file?: string
  file_name?: string
  file_size?: number
  is_read: boolean
  read_at?: string
  created_at: string
}

export interface ChatRoom {
  id: number
  enterprise_user: number
  job_seeker_user: number
  recruitment?: number
  enterprise_user_info: User
  job_seeker_user_info: User
  last_message?: Message
  unread_count: number
  is_active: boolean
  created_at: string
  updated_at: string
    // 添加临时消息标识
  is_temp?: boolean
  // 可选：添加发送状态
  send_status?: 'sending' | 'sent' | 'failed'
}

export interface WebSocketData {
  type: 'chat_message' | 'read_receipt' | 'connection_established'
  message?: Message
  message_id?: number
  reader_id?: number
}
// 使用示例：在其他文件中导入类型，获得类型检查