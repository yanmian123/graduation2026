<template>
  <div class="chat-window">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <n-space align="center" :size="12">
        <n-avatar
          round
          :size="40"
          :src="oppositeUser?.avatar"
        >
          {{ oppositeUser?.nickname?.charAt(0) || 'U' }}
        </n-avatar>
        
        <div class="user-info">
          <div class="username">{{ oppositeUser?.nickname }}</div>
          <div class="status">
            <n-tag v-if="oppositeUser?.id !== undefined && isUserOnline(oppositeUser.id)" type="success" size="small" round>
              在线
            </n-tag>
            <n-tag v-else type="default" size="small" round>
              离线
            </n-tag>
            <span v-if="oppositeUser?.id !== undefined && isUserOnline(oppositeUser.id)" class="online-time">最后在线: 刚刚</span>
          </div>
        </div>
      </n-space>
      
      <n-space>
        <n-button quaternary circle @click="toggleEmoji">
          <n-icon><HappyOutlineIcon /></n-icon>
        </n-button>
        <n-button quaternary circle @click="showMoreOptions = !showMoreOptions">
          <n-icon><MoreIcon /></n-icon>
        </n-button>
      </n-space>
    </div>

    <!-- 消息区域 -->
    <div class="messages-container" ref="messagesContainer">
      <n-scrollbar>
        <div v-for="message in messages" :key="message.id" class="message-wrapper">
          <!-- 系统消息 -->
          <div v-if="message.message_type === 'system'" class="system-message">
            <n-text type="info" depth="3">{{ message.content }}</n-text>
          </div>
          
          <!-- 普通消息 -->
          <div v-else :class="['message-bubble', { 'own-message': isOwnMessage(message) }]">
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
              <n-space v-if="isOwnMessage(message)" align="center" :size="4">
                <n-icon
                  v-if="message.is_read"
                  size="16"
                  color="#409eff"
                >
                  <CheckIcon />
                </n-icon>
                <n-icon
                  v-else
                  size="16"
                  color="#ccc"
                >
                  <CheckIcon />
                </n-icon>
              </n-space>
            </div>
          </div>
        </div>
      </n-scrollbar>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <div class="input-tools">
        <n-upload
          :multiple="false"
          :show-file-list="false"
          :custom-request="handleFileUpload"
        >
          <n-button quaternary circle>
            <n-icon><AttachIcon /></n-icon>
          </n-button>
        </n-upload>
        <n-button quaternary circle @click="toggleEmoji">
          <n-icon><HappyIcon /></n-icon>
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

    <!-- 表情选择器 -->
    <n-dropdown
      v-if="showEmojiPicker"
      :options="emojiOptions"
      placement="top-start"
      @select="handleEmojiSelect"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { 
  NAvatar, NButton, NSpace, NIcon, NTag, NText, NScrollbar, 
  NInput, NUpload, NDropdown 
} from 'naive-ui'
import { 
  HappyOutline as HappyOutlineIcon,
  EllipsisHorizontal as MoreIcon,
  Document as DocumentIcon,
  Attach as AttachIcon,
  Happy as HappyIcon
} from '@vicons/ionicons5'
import { useChatStore } from '@/stores/chatStore'
import { webSocketService } from '@/services/websocket'
import type { Message } from '@/types/chat'
import { CheckmarkOutline as CheckIcon } from '@vicons/ionicons5'
const chatStore = useChatStore()
const inputMessage = ref('')
const showEmojiPicker = ref(false)
const showMoreOptions = ref(false)
const messagesContainer = ref<HTMLElement>()

// 使用 storeToRefs 保持响应式
import { storeToRefs } from 'pinia'
const { 
  currentRoom, 
  messages, 
  oppositeUser 
} = storeToRefs(chatStore)

const { 
  isUserOnline, 
  sendMessage, 
  uploadFile, 
  markAsRead,
  addMessage 
} = chatStore

const isConnected = computed(() => webSocketService.isConnected.value)

const isOwnMessage = (message: Message) => {
  return message.sender === chatStore.currentUser?.id
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

// 处理文件上传
import type { UploadCustomRequestOptions } from 'naive-ui'

const handleFileUpload = async (options: UploadCustomRequestOptions) => {
  if (!currentRoom.value) return

  const rawFile = options.file.file as File

  try {
    await uploadFile(currentRoom.value.id, rawFile)
    options.onFinish?.()
  } catch (error) {
    console.error('上传文件失败:', error)
    options.onError?.()
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
  return new Date(time).toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
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

// 表情选择器
const toggleEmoji = () => {
  showEmojiPicker.value = !showEmojiPicker.value
}

const handleEmojiSelect = (emoji: string) => {
  inputMessage.value += emoji
  showEmojiPicker.value = false
}

const emojiOptions = [
  { label: '😀', key: '😀' },
  { label: '😂', key: '😂' },
  { label: '❤️', key: '❤️' },
  { label: '👍', key: '👍' },
]

// 生命周期
onMounted(() => {
  if (currentRoom.value) {
    webSocketService.connect(currentRoom.value.id)
    
    webSocketService.onMessage(handleNewMessage)
    webSocketService.onReadReceipt(handleReadReceipt)
    
    scrollToBottom()
  }
})

onUnmounted(() => {
  webSocketService.disconnect()
  webSocketService.removeMessageCallback(handleNewMessage)
})

// 监听当前聊天室变化
watch(currentRoom, (newRoom) => {
  if (newRoom) {
    webSocketService.connect(newRoom.id)
    scrollToBottom()
  } else {
    webSocketService.disconnect()
  }
})
</script>

<style scoped>
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

.status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.online-time {
  font-size: 12px;
  color: #888;
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

.own-message {
  background: #409eff;
  color: white;
  margin-left: auto;
}

.text-message {
  line-height: 1.5;
  word-break: break-word;
}

.file-message {
  display: flex;
  align-items: center;
}

.file-info {
  flex: 1;
  margin-left: 8px;
}

.file-name {
  font-weight: 500;
  font-size: 14px;
}

.file-size {
  font-size: 12px;
  opacity: 0.8;
  margin-top: 2px;
}

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
  gap: 8px;
}

.message-input {
  flex: 1;
}

.send-button {
  align-self: flex-end;
  width: 100px;
}
</style>