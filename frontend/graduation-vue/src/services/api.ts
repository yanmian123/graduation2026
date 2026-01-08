import axios from 'axios'
import type { ChatRoom, Message } from '@/types/chat'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    console.log("当前用户的Token:", token)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token过期，跳转到登录页
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 聊天相关API
export const chatApi = {
  // 已有的方法...
  getChatRooms: () => api.get('api/chat/chatrooms/'),
  getMessages: (roomId: number) => api.get(`api/chat/chatrooms/${roomId}/messages/`),
  sendMessage: (roomId: number, content: string, type: string = 'text') => 
    api.post(`api/chat/chatrooms/${roomId}/messages/`, { 
      content: content,
      message_type: type,
      type: type  // 双重保险，确保字段匹配
    }),
  // 新增缺失的方法
  getChatRoom: (roomId: number) => api.get(`api/chat/chatrooms/${roomId}/`),
  startChat: (params: any) => api.post('api/chat/chatrooms/start_chat/', params),
  markAsRead: (roomId: number, messageId: number) => 
    api.post(`api/chat/chatrooms/${roomId}/messages/${messageId}/mark_as_read/`),
  uploadFile: (roomId: number, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('message_type', 'file')
    return api.post(`api/chat/chatrooms/${roomId}/messages/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

export { api }; 