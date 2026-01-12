<template>
  <div class="chat-room-list">
    <div class="header">
      <h2>聊天列表</h2>
      <n-space>
        <n-button type="primary" @click="refresh" :loading="loading">
          <template #icon>
            <n-icon><RefreshIcon /></n-icon>
          </template>
          刷新
        </n-button>
        <n-badge :value="unreadTotal" :max="99" v-if="unreadTotal > 0" />
      </n-space>
    </div>

    <n-input
      v-model:value="searchKeyword"
      placeholder="搜索聊天"
      clearable
      class="search-input"
    >
      <template #prefix>
        <n-icon><SearchIcon /></n-icon>
      </template>
    </n-input>

    <n-scrollbar class="room-scrollbar">
      <n-list>
        <n-list-item
          v-for="room in filteredRooms"
          :key="room.id"
          class="room-item"
          :class="{ active: currentRoom?.id === room.id }"
          @click="selectRoom(room)"
        >
          <template #prefix>
            <n-avatar
              round
              :size="48"
              :src="getOppositeUser(room).avatar"
            >
              {{ getOppositeUser(room).nickname?.charAt(0) || 'U' }}
            </n-avatar>
          </template>
          
          <div class="room-content">
            <div class="room-header">
              <span class="username">{{ getOppositeUser(room).nickname }}</span>
              <span class="time">{{ formatTime(room.updated_at) }}</span>
            </div>
            
            <div class="last-message">
              <span class="preview">
                {{ room.last_message?.content?.substring(0, 30) || '暂无消息' }}
              </span>
              <n-badge 
                v-if="room.unread_count > 0"
                :value="room.unread_count"
                :max="99"
                type="error"
              />
            </div>
            
            <div class="user-info">
              <n-tag v-if="getOppositeUser(room).is_enterprise" type="info" size="small">
                企业
              </n-tag>
              <n-tag v-else type="success" size="small">
                求职者
              </n-tag>
            </div>
          </div>
        </n-list-item>
      </n-list>
    </n-scrollbar>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { NList, NListItem, NAvatar, NSpace, NButton, NBadge, NInput, NScrollbar, NIcon, NTag } from 'naive-ui'
import { Refresh as RefreshIcon, Search as SearchIcon } from '@vicons/ionicons5'
import { useChatStore } from '@/stores/chatStore'
import type { ChatRoom, User } from '@/types/chat'

const chatStore = useChatStore()
const searchKeyword = ref('')

const { loading, unreadTotal, sortedChatRooms, currentRoom, fetchChatRooms, setCurrentRoom } = chatStore

const filteredRooms = computed(() => {
  let rooms = sortedChatRooms
  
  // 先按搜索关键词过滤
  if (searchKeyword.value.trim()) {
    rooms = rooms.filter(room => {
      const user = getOppositeUser(room)
      return user.nickname?.toLowerCase().includes(searchKeyword.value.toLowerCase()) || 
             user.username?.toLowerCase().includes(searchKeyword.value.toLowerCase())
    })
  }
  
  // 对聊天室进行去重：同一个对方的聊天室只显示最新的一个
  const uniqueRooms = []
  const roomMap = new Map() // key: enterprise_user + job_seeker_user
  
  rooms.forEach(room => {
    const key = `${room.enterprise_user}-${room.job_seeker_user}`
    const existingRoom = roomMap.get(key)
    
    if (!existingRoom || new Date(room.updated_at) > new Date(existingRoom.updated_at)) {
      roomMap.set(key, room)
    }
  })
  
  // 将Map转换回数组并按更新时间排序
  return Array.from(roomMap.values()).sort((a, b) => 
    new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
  )
})

const getOppositeUser = (room: ChatRoom): User => {
  const currentUser = chatStore.currentUser
  if (!currentUser) return {} as User
  
  return currentUser.id === room.enterprise_user 
    ? room.job_seeker_user_info 
    : room.enterprise_user_info
}

const formatTime = (time: string) => {
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 24 * 60 * 60 * 1000) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else if (diff < 7 * 24 * 60 * 60 * 1000) {
    const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    return days[date.getDay()]
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}

const selectRoom = (room: ChatRoom) => {
  setCurrentRoom(room)
}

const refresh = () => {
  fetchChatRooms()
}

onMounted(() => {
  fetchChatRooms()
})
</script>

<style scoped>
.chat-room-list {
  width: 320px;
  height: 100vh;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  background: #fafafa;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
  background: white;
}

.header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.search-input {
  margin: 16px;
}

.room-scrollbar {
  flex: 1;
  height: 0;
}

.room-item {
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid #f0f0f0;
  background: white;
}

.room-item:hover {
  background-color: #f5f5f5;
}

.room-item.active {
  background-color: #e3f2fd;
}

.room-content {
  flex: 1;
  margin-left: 12px;
  min-width: 0;
}

.room-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.username {
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.time {
  font-size: 12px;
  color: #888;
}

.last-message {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.preview {
  font-size: 13px;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}
</style>