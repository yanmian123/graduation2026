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
        // 🔥 添加详细错误日志
    console.error('API Error Details:', {
      status: error.response?.status,
      data: error.response?.data,
      url: error.config?.url
    })
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
  markAllAsRead: (roomId: number) => 
    api.post(`api/chat/chatrooms/${roomId}/mark_all_as_read/`),
  uploadFile: (roomId: number, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('content', file.name)
    
    console.log('📤 上传文件信息:', {
      name: file.name,
      type: file.type,
      size: file.size,
      roomId: roomId
    })
    
    // 使用正确的上传路由，让后端自动判断文件类型
    return api.post(`api/chat/chatrooms/${roomId}/upload/`, formData, {
      headers: { 
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
      }
    })
  }
}

// 通知相关API
export const notificationApi = {
  getNotifications: () => api.get('api/notifications/'),
  getUnreadCount: () => api.get('api/notifications/unread_count/'),
  markAsRead: (notificationId: number) => api.patch(`api/notifications/${notificationId}/mark_as_read/`),
  markAllAsRead: () => api.patch('api/notifications/mark_all_as_read/')
}

// 文章相关API
export const articleApi = {
  // 获取当前用户的文章
  getMyArticles: () => api.get('api/posts/', { params: { user_only: 'true' } }),
  // 获取当前用户的评论
  getMyComments: () => api.get('api/comments/', { params: { user_only: 'true' } }),
  // 获取当前用户的收藏
  getMyCollections: () => api.get('api/posts/collections/')
}

// 投递记录相关API
export const applicationApi = {
  // 获取当前用户的投递记录
  getMyApplications: () => api.get('api/applications/')
}

export { api }; 