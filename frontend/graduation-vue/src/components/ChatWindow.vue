<template>
  <div class="chat-window">

    <!-- 聊天头部 -->
    <div class="chat-header">
      <n-space align="center" :size="12">
        <!-- 有头像时只显示图片 -->
        <n-avatar
          v-if="displayUser?.avatar"
          round
          :size="40"
          :src="getFullAvatarUrl(displayUser.avatar)"
          @error="handleAvatarError"
        />
        
        <!-- 无头像时显示文字 -->
        <n-avatar
          v-else
          round
          :size="40"
        >
          {{ displayUser?.nickname?.charAt(0) || 'U' }}
        </n-avatar>

        <div class="user-info">
          <div class="username">{{ displayUser?.nickname }}</div>
        </div>
      </n-space>
    </div>

    <!-- 消息区域 -->
    <div class="messages-container" ref="messagesContainer">
      <n-scrollbar :use-native-scrollbar="true">
        <div v-for="message in messages" :key="message.id" class="message-wrapper">
          <!-- 系统消息 -->
          <div v-if="message.message_type === 'system'" class="system-message">
            <n-text type="info" depth="3">{{ message.content }}</n-text>
          </div>
          
          <!-- 普通消息 -->
          <div v-else :class="['message-item', { 'own-message': isOwnMessage(message) }]">
            <!-- 对方的消息（左侧显示） -->
            <div v-if="!isOwnMessage(message)" class="other-message">
              <!-- 对方头像 -->
              <n-avatar
                v-if="displayUser?.avatar"
                round
                :size="36"
                :src="getFullAvatarUrl(displayUser.avatar)"
                class="message-avatar"
                @error="handleAvatarError"
              />
              <n-avatar
                v-else
                round
                :size="36"
                class="message-avatar"
              >
                {{ displayUser?.nickname?.charAt(0) || 'U' }}
              </n-avatar>
              
              <!-- 图片消息 - 直接显示，不带气泡 -->
              <div v-if="message.message_type === 'image'" class="image-message-wrapper">
                <n-image
                  :src="getFullAvatarUrl(message.file)"
                  :alt="message.file_name || '图片'"
                  :preview-src="getFullAvatarUrl(message.file)"
                  width="200"
                  object-fit="contain"
                  class="chat-image"
                />
              </div>
              
              <!-- 其他消息（文本和文件）- 带气泡 -->
              <div v-else class="message-bubble other-bubble">
                <!-- 文件消息 -->
                <div v-if="message.message_type === 'file'" class="file-message">
                  <n-space align="center" :size="12">
                    <n-icon size="24" color="#409eff">
                      <DocumentIcon />
                    </n-icon>
                    <div class="file-info">
                      <div class="file-name">{{ message.file_name }}</div>
                      <div class="file-size">{{ formatFileSize(message.file_size || 0) }}</div>
                    </div>
                    <n-button type="primary" text @click="downloadFile(message)">
                      下载
                    </n-button>
                  </n-space>
                </div>
                
                <!-- 文本消息 -->
                <div v-else class="text-message">
                  {{ message.content }}
                </div>
                
                <div class="message-meta">
                  <span class="time">{{ formatMessageTime(message.created_at) }}</span>
                </div>
              </div>
            </div>
            
            <!-- 自己的消息（右侧显示） -->
            <div v-else class="own-message">
              <!-- 图片消息 - 直接显示，不带气泡 -->
              <div v-if="message.message_type === 'image'" class="image-message-wrapper">
                <n-image
                  :src="getFullAvatarUrl(message.file)"
                  :alt="message.file_name || '图片'"
                  :preview-src="getFullAvatarUrl(message.file)"
                  width="200"
                  object-fit="contain"
                  class="chat-image"
                />
              </div>
              
              <!-- 其他消息（文本和文件）- 带气泡 -->
              <div v-else class="message-bubble own-bubble">
                <!-- 文件消息 -->
                <div v-if="message.message_type === 'file'" class="file-message">
                  <n-space align="center" :size="12">
                    <n-icon size="24" color="#000">
                      <DocumentIcon />
                    </n-icon>
                    <div class="file-info">
                      <div class="file-name" style="color: #000">{{ message.file_name }}</div>
                      <div class="file-size" style="color: rgba(0,0,0,0.8)">{{ formatFileSize(message.file_size || 0) }}</div>
                    </div>
                    <n-button type="primary" text @click="downloadFile(message)" style="color: #000">
                      下载
                    </n-button>
                  </n-space>
                </div>
                
                <!-- 文本消息 -->
                <div v-else class="text-message">
                  {{ message.content }}
                </div>
                
                <div class="message-meta">
                  <span class="time">{{ formatMessageTime(message.created_at) }}</span>
                  <span v-if="isLastOwnMessage(message)" :class="['read-status-text', message.is_read ? 'read' : 'unread']" style="margin-left: 8px;">
                    {{ message.is_read ? '已读' : '未读' }}
                  </span>
                </div>
              </div>
              
              <!-- 自己头像 -->
              <n-avatar
                v-if="chatStore.isCurrentUserEnterprise && chatStore.currentRoom?.enterprise_info?.logo"
                round
                :size="36"
                :src="getFullAvatarUrl(chatStore.currentRoom?.enterprise_info?.logo)"
                class="message-avatar"
                @error="handleAvatarError"
              />
              <n-avatar
                v-else-if="currentUser?.avatar"
                round
                :size="36"
                :src="getFullAvatarUrl(currentUser?.avatar)"
                class="message-avatar"
                @error="handleAvatarError"
              />
              <n-avatar
                v-else
                round
                :size="36"
                class="message-avatar"
              >
                {{ currentUser?.nickname?.charAt(0) || 'U' }}
              </n-avatar>
            </div>
          </div>
        </div>
      </n-scrollbar>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <div class="input-tools">
        <input 
          ref="imageInputRef"
          type="file"
          accept="image/*"
          style="display: none"
          @change="handleImageFileChange"
        />
        <n-button quaternary circle @click="() => imageInputRef?.click()">
          <n-icon><ImageIcon /></n-icon>
        </n-button>
        
        <input 
          ref="fileInputRef"
          type="file"
          style="display: none"
          @change="handleFileFileChange"
        />
        <n-button quaternary circle @click="() => fileInputRef?.click()">
          <n-icon><AttachIcon /></n-icon>
        </n-button>
      </div>
      
      <n-input
        v-model:value="inputMessage"
        type="textarea"
        :rows="3"
        placeholder="输入消息..."
        :disabled="!isConnected"
        @keydown.enter="handleKeyDown"
        class="message-input"
      />
      
      <n-button
        type="primary"
        :disabled="!inputMessage.trim() || !isConnected"
        @click="sendTextMessage"
        class="send-button"
      >
        发送
      </n-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { 
  NAvatar, NButton, NSpace, NIcon, NText, NScrollbar, 
  NInput, NUpload, NImage
} from 'naive-ui'
import { 
  Document as DocumentIcon,
  Attach as AttachIcon,
  Image as ImageIcon
} from '@vicons/ionicons5'
import { useChatStore } from '@/stores/chatStore'
import { webSocketService } from '@/services/websocket'
import type { Message } from '@/types/chat'
import { CheckmarkOutline as CheckIcon } from '@vicons/ionicons5'
const chatStore = useChatStore()
const inputMessage = ref('')
const messagesContainer = ref<HTMLElement>()
const imageInputRef = ref<HTMLInputElement>()
const fileInputRef = ref<HTMLInputElement>()

// 使用 storeToRefs 保持响应式
import { storeToRefs } from 'pinia'
const { 
  currentRoom, 
  messages, 
  oppositeUser 
} = storeToRefs(chatStore)

const { 
  sendMessage, 
  uploadFile, 
  markAsRead,
  addMessage 
} = chatStore

// 新增计算属性：当前用户头像
const currentUser = computed(() => chatStore.currentUser)
const currentUserAvatar = computed(() => {
  // 这里根据你的用户数据结构调整，假设头像字段是 avatar
  return currentUser.value?.avatar || ''
})

const isConnected = computed(() => webSocketService.isConnected.value)

const isOwnMessage = (message: Message) => {
  const currentUserId = chatStore.currentUser?.id
  return message.sender === chatStore.currentUser?.id
}

const isLastOwnMessage = (message: Message) => {
  if (!isOwnMessage(message)) return false
  
  const ownMessages = messages.value.filter(m => isOwnMessage(m))
  const lastOwnMessage = ownMessages[ownMessages.length - 1]
  
  return lastOwnMessage?.id === message.id
}

// 发送文本消息
const sendTextMessage = async () => {
  if (!inputMessage.value.trim() || !currentRoom.value) return

  try {
    await sendMessage(currentRoom.value.id, inputMessage.value, 'text')
    inputMessage.value = ''
    scrollToBottom()
  } catch (error) {
    console.error('发送消息失败:', error)
  }
}

// 处理图片文件选择
const handleImageFileChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file || !currentRoom.value) return

  console.log('📤 上传图片信息:', {
    name: file.name,
    size: file.size,
    type: file.type,
    roomId: currentRoom.value.id
  })

  try {
    await uploadFile(currentRoom.value.id, file)
    target.value = ''
  } catch (error) {
    console.error('上传图片失败详情:', error)
  }
}

// 处理文件选择
const handleFileFileChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file || !currentRoom.value) return

  console.log('📤 上传文件信息:', {
    name: file.name,
    size: file.size,
    type: file.type,
    roomId: currentRoom.value.id
  })

  try {
    await uploadFile(currentRoom.value.id, file)
    target.value = ''
  } catch (error) {
    console.error('上传文件失败详情:', error)
  }
}

// 处理键盘事件
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendTextMessage()
  }
}

// WebSocket消息处理
const handleNewMessage = (message: Message) => {
  addMessage(message)
  scrollToBottom()
  
  // 如果是接收到的消息，标记为已读
  if (!isOwnMessage(message)) {
    markAsRead(message.id)
    webSocketService.sendReadReceipt(message.id)
  }
}

const handleReadReceipt = (messageId: number, readerId: number) => {
  const message = messages.value.find(m => m.id === messageId)
  if (message && isOwnMessage(message)) {
    message.is_read = true
    message.read_at = new Date().toISOString()
  }
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      const scrollEl = messagesContainer.value.querySelector('.n-scrollbar-container')
      if (scrollEl) {
        scrollEl.scrollTop = scrollEl.scrollHeight
      }
    }
  })
}

// 工具函数
const formatMessageTime = (time: string) => {
  const messageDate = new Date(time)
  const today = new Date()
  const isToday = messageDate.toDateString() === today.toDateString()
  
  if (isToday) {
    return messageDate.toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  } else {
    return messageDate.toLocaleString('zh-CN', { 
      month: '2-digit', 
      day: '2-digit',
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }
}

const formatFileSize = (bytes: number) => {
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

const downloadFile = (message: Message) => {
  if (message.file) {
    window.open(message.file, '_blank')
  }
}

// 使用在线默认头像URL，避免依赖本地文件
const defaultAvatar = ref('https://picsum.photos/id/237/100/100')
const defaultCompanyLogo = ref('https://picsum.photos/id/1005/100/100')

// 添加一个处理头像URL的函数
const getFullAvatarUrl = (avatarPath: string | undefined): string | undefined => {
  if (!avatarPath) {
    console.log('❌❌ 头像路径为空')
    return undefined
  }
  
  // 显式转换为字符串，避免Vue Proxy对象的影响
  const path = String(avatarPath)
  // console.log('🔍 原始avatarPath:', avatarPath)
  // console.log('🔍 转换为字符串后:', path)
  
  // 如果已经是完整URL，直接返回
  if (path.startsWith('http')) {
    // console.log('✅ 已经是完整URL:', path)
    return path
  }
  
  // 处理相对路径，特别是企业logo的/media路径
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  
  // 确保路径格式正确
  let normalizedPath = path
  if (!path.startsWith('/')) {
    normalizedPath = `/${path}`
  }
  
  const fullUrl = `${baseUrl}${normalizedPath}`
  console.log('✅ 生成完整URL:', fullUrl)
  return fullUrl
}

// 计算显示的用户信息
const displayUser = computed(() => {
  const room = chatStore.currentRoom
  const currentUser = chatStore.currentUser
  
  // console.log('🔍🔍🔍🔍 当前聊天室数据:', room)
  // console.log('🔍🔍🔍🔍 企业信息:', room?.enterprise_info)
  // console.log('🔍🔍🔍🔍 企业logo:', room?.enterprise_info?.logo)
  
  if (!room || !currentUser) {
    return {
      nickname: '未知用户',
      avatar: defaultAvatar.value,
      is_enterprise: false
    }
  }
  
  const isCurrentUserEnterprise = currentUser.id === room.enterprise_user
  // console.log('🔍🔍🔍🔍 当前用户ID:', currentUser.id)
  // console.log('🔍🔍🔍🔍 企业用户ID:', room.enterprise_user)
  // console.log('🔍🔍🔍🔍 是否企业用户:', isCurrentUserEnterprise)
  
  if (isCurrentUserEnterprise) {
    // 当前用户是企业，显示求职者
    const jobSeekerInfo = room.job_seeker_user_info
    return {
      id: room.job_seeker_user,
      username: jobSeekerInfo?.username || `user_${room.job_seeker_user}`,
      nickname: jobSeekerInfo?.nickname || jobSeekerInfo?.username || '求职者',
      avatar: jobSeekerInfo?.avatar || defaultAvatar.value,
      is_enterprise: false
    }
  } else {
    // 当前用户是求职者，显示企业
    if (room.enterprise_info && room.enterprise_info.logo) {
      const logoUrl = room.enterprise_info.logo
      // console.log('✅ 使用企业logo:', logoUrl)
      return {
        id: room.enterprise_user,
        username: room.enterprise_info.name || `enterprise_${room.enterprise_user}`,
        nickname: room.enterprise_info.name || '企业用户',
        avatar: logoUrl,
        is_enterprise: true
      }
    } else if (room.enterprise_user_info) {
      console.log('⚠️ 没有企业信息，使用企业用户信息')
      return {
        id: room.enterprise_user,
        username: room.enterprise_user_info.username || `enterprise_${room.enterprise_user}`,
        nickname: room.enterprise_user_info.nickname || room.enterprise_user_info.username || '企业用户',
        avatar: defaultCompanyLogo.value,
        is_enterprise: true
      }
    } else {
      console.log('❌❌ 无任何企业信息，使用默认')
      return {
        id: room.enterprise_user,
        username: `enterprise_${room.enterprise_user}`,
        nickname: '企业用户',
        avatar: defaultCompanyLogo.value,
        is_enterprise: true
      }
    }
  }
})

const handleAvatarError = (e: Event) => {
  console.error('❌❌ 头像加载错误:', {
    target: e.target,
    src: (e.target as HTMLImageElement)?.src
  })
}

// 生命周期
onMounted(() => {
  if (currentRoom.value) {
    webSocketService.connect(currentRoom.value.id)
    
    webSocketService.onMessage(handleNewMessage)
    webSocketService.onReadReceipt(handleReadReceipt)
    
    setTimeout(() => {
      scrollToBottom()
    }, 300)
  }
})

onUnmounted(() => {
  webSocketService.disconnect()
  webSocketService.removeMessageCallback(handleNewMessage)
  webSocketService.removeReadReceiptCallback(handleReadReceipt)
})

// 监听当前聊天室变化
watch(currentRoom, (newRoom) => {
  if (newRoom) {
    webSocketService.connect(newRoom.id)
    webSocketService.onMessage(handleNewMessage)
    webSocketService.onReadReceipt(handleReadReceipt)
    
    // 延迟滚动，确保消息加载完成
    setTimeout(() => {
      scrollToBottom()
    }, 300)
  } else {
    webSocketService.disconnect()
  }
})
</script>

<style scoped>
/* 样式保持不变 */
.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: white;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: 600;
  font-size: 16px;
  color: #333;
}

.messages-container {
  flex: 1;
  overflow: hidden;
  background: #f8f9fa;
  padding: 16px;
}

.system-message {
  text-align: center;
  margin: 12px 0;
  font-size: 12px;
}

.message-wrapper {
  margin-bottom: 16px;
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: relative;
}

/* 消息项容器 */
.message-item {
  margin-bottom: 16px;
}

/* 对方消息布局（左侧） */
.other-message {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  width: 100%;
}

/* 自己消息布局（右侧） */
.own-message {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: flex-end;
  width: 100%;
  gap: 8px;
}

/* 消息头像 */
.message-avatar {
  margin: 0 8px;
}

/* 消息气泡基础样式 */
.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  position: relative;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  word-wrap: break-word;
  overflow-wrap: break-word;
  flex-shrink: 0;
}

/* 对方消息气泡（左侧，浅色） */
.other-bubble {
  background: white;
  color: #333;
  margin-right: 8px;
}

/* 自己消息气泡（右侧，蓝色） */
.own-bubble {
  background: #75cba3;
  color: #000;
  margin-left: 8px;
}

/* 文本消息样式 */
.text-message {
  line-height: 1.5;
  word-break: break-word;
}

/* 图片消息样式 */
.image-message {
  display: flex;
  justify-content: center;
  align-items: center;
}

.image-message-wrapper {
  display: inline-block;
  margin: 4px 0;
}

.chat-image {
  max-width: 200px;
  max-height: 200px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chat-image:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 文件消息样式 */
.file-message {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
}

.file-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
  margin-left: 8px;
}

.file-name {
  word-break: break-all;
  overflow-wrap: break-word;
  max-width: 200px;
  font-weight: 500;
  font-size: 14px;
}

.file-size {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.6);
  margin-top: 2px;
}

/* 消息元信息（时间、已读状态） */
.message-meta {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 4px;
  font-size: 12px;
  opacity: 0.8;
}

.read-status {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 8px;
  font-size: 12px;
}

.read-status-text {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.read-status-text.read {
  background: rgba(0, 0, 0, 0.1);
  color: rgba(0, 0, 0, 0.6);
}

.read-status-text.unread {
  background: rgba(0, 0, 0, 0.15);
  color: rgba(0, 0, 0, 0.8);
}

.text-message {
  line-height: 1.5;
  word-break: break-word;
}

/* 消息元信息（时间、已读状态） */
.message-meta {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 4px;
  font-size: 12px;
  opacity: 0.8;
}

.input-area {
  border-top: 1px solid #e0e0e0;
  background: white;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-tools {
  display: flex;
  gap: 0;
  align-items: center;
}

.input-tools input[type="file"] {
  display: none;
}

.message-input {
  flex: 1;
}

.send-button {
  align-self: flex-end;
  width: 100px;
}
</style>