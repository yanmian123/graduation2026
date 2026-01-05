// 集中管理状态，如聊天室列表、当前聊天室、消息等
// 优点：全局状态管理，组件间共享数据
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ChatRoom, Message, User } from '@/types/chat'
import { chatApi } from '@/services/api'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const chatRooms = ref<ChatRoom[]>([])
  const currentRoom = ref<ChatRoom | null>(null)
  const messages = ref<Message[]>([])
  const unreadTotal = ref(0)
  const onlineUsers = ref<Set<number>>(new Set())
  const loading = ref(false)

  // 计算属性
  const sortedChatRooms = computed(() => 
    [...chatRooms.value].sort((a, b) => 
      new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    )
  )

  const currentUser = computed(() => {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  })

  const oppositeUser = computed(() => {
    if (!currentRoom.value || !currentUser.value) return null
    
    // 修复：使用正确的属性名进行比较
    const currentUserId = currentUser.value.id
    const enterpriseUserId = currentRoom.value.enterprise_user
    
    // 修复：比较用户ID而不是整个对象
    return currentUserId === enterpriseUserId
      ? currentRoom.value.job_seeker_user_info
      : currentRoom.value.enterprise_user_info
  })

  // 方法
  const fetchChatRooms = async () => {
    loading.value = true
    try {
      const response = await chatApi.getChatRooms()
      chatRooms.value = response.data
      unreadTotal.value = chatRooms.value.reduce((total, room) => total + (room.unread_count || 0), 0)
    } catch (error) {
      console.error('获取聊天室列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  const fetchMessages = async (roomId: number) => {
    try {
      const response = await chatApi.getMessages(roomId)
      messages.value = response.data
    } catch (error) {
      console.error('获取消息失败:', error)
    }
  }

  // 修复：添加正确的API调用
  const setCurrentRoomById = async (roomId: string) => {
    try {
      // 将字符串roomId转换为数字进行比较
      const numericRoomId = parseInt(roomId, 10)
      
      // 修复：使用正确的比较方式
      const room = sortedChatRooms.value.find(r => r.id === numericRoomId)
      
      if (room) {
        currentRoom.value = room
        await fetchMessages(numericRoomId)
      } else {
        // 如果不在当前列表，尝试从API获取
        // 修复：使用chatApi而不是未定义的api
        const response = await chatApi.getChatRoom(numericRoomId)
        currentRoom.value = response.data
        await fetchMessages(numericRoomId)
      }
    } catch (error) {
      console.error('设置聊天室失败:', error)
    }
  }

  const startChat = async (params: {
    enterprise_user_id?: number
    job_seeker_user_id?: number
    recruitment_id?: number
  }) => {
    try {
      const response = await chatApi.startChat(params)
      await fetchChatRooms()
      return response.data
    } catch (error) {
      console.error('创建聊天室失败:', error)
      throw error
    }
  }

  const sendMessage = async (roomId: number, content: string, type: string = 'text') => {
    try {
      const response = await chatApi.sendMessage(roomId, content, type)
      return response.data
    } catch (error) {
      console.error('发送消息失败:', error)
      throw error
    }
  }

  const markAsRead = async (messageId: number) => {
    if (!currentRoom.value) return
    
    try {
      await chatApi.markAsRead(currentRoom.value.id, messageId)
      
      // 更新本地状态
      const message = messages.value.find(m => m.id === messageId)
      if (message && !message.is_read) {
        message.is_read = true
        message.read_at = new Date().toISOString()
        
        // 更新未读计数
        const room = chatRooms.value.find(r => r.id === currentRoom.value!.id)
        if (room && (room.unread_count || 0) > 0) {
          room.unread_count = (room.unread_count || 0) - 1
          unreadTotal.value--
        }
      }
    } catch (error) {
      console.error('标记已读失败:', error)
    }
  }

  const uploadFile = async (roomId: number, file: File) => {
    try {
      const response = await chatApi.uploadFile(roomId, file)
      return response.data
    } catch (error) {
      console.error('上传文件失败:', error)
      throw error
    }
  }

  const setCurrentRoom = (room: ChatRoom | null) => {
    currentRoom.value = room
    if (room) {
      fetchMessages(room.id)
    } else {
      messages.value = []
    }
  }

  const addMessage = (message: Message) => {
    // 避免重复消息
    if (messages.value.some(m => m.id === message.id)) return
    
    messages.value.push(message)
    
    // 更新聊天室列表中的最后消息
    const room = chatRooms.value.find(r => r.id === message.chat_room)
    if (room) {
      room.last_message = message
      room.updated_at = new Date().toISOString()
      
      // 如果是别人发来的消息且不在当前聊天室，增加未读计数
      if (currentRoom.value?.id !== message.chat_room && 
          message.sender !== currentUser.value?.id) {
        room.unread_count = (room.unread_count || 0) + 1
        unreadTotal.value++
      }
    }
  }

  const setUserOnline = (userId: number) => {
    onlineUsers.value.add(userId)
  }

  const setUserOffline = (userId: number) => {
    onlineUsers.value.delete(userId)
  }

  const isUserOnline = (userId: number) => {
    return onlineUsers.value.has(userId)
  }

  return {
    // 状态
    chatRooms,
    currentRoom,
    messages,
    unreadTotal,
    loading,
    onlineUsers,
    
    // 计算属性
    sortedChatRooms,
    currentUser,
    oppositeUser,
    
    // 方法
    fetchChatRooms,
    fetchMessages,
    startChat,
    sendMessage,
    markAsRead,
    uploadFile,
    setCurrentRoom,
    addMessage,
    setUserOnline,
    setUserOffline,
    isUserOnline,
    setCurrentRoomById // 确保导出这个方法
  }
})