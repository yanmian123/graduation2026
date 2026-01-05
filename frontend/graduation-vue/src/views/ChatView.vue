<!-- ChatView.vue -->
<template>
  <div class="chat-layout">
    <div class="chat-sidebar">
      <ChatRoomList />
    </div>
    <div class="chat-main">
      <!-- 添加加载状态和错误处理 -->
      <div v-if="loading" class="loading-state">
        <n-spin size="large">
          <template #description>加载聊天室中...</template>
        </n-spin>
      </div>
      
      <div v-else-if="error" class="error-state">
        <n-result
          status="404"
          title="聊天室加载失败"
          :description="error"
        >
          <template #footer>
            <n-space>
              <n-button type="primary" @click="retryLoading">
                重试
              </n-button>
              <n-button @click="goBack">
                返回
              </n-button>
            </n-space>
          </template>
        </n-result>
      </div>
      
      <ChatWindow v-else-if="currentRoom" />
      
      <div v-else class="no-room-selected">
        <n-empty description="请选择一个聊天室开始对话">
          <template #extra>
            <n-button size="small" @click="showRoomList = true">
              查看聊天列表
            </n-button>
          </template>
        </n-empty>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useChatStore } from '@/stores/chatStore'
import ChatRoomList from '@/components/ChatRoomList.vue'
import ChatWindow from '@/components/ChatWindow.vue'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const chatStore = useChatStore()

// 添加状态管理
const loading = ref(false)
const error = ref(null)
const showRoomList = ref(false)

// 使用计算属性安全访问 store
const currentRoom = computed(() => chatStore.currentRoom)

// 加载聊天室的函数
const loadChatRoom = async (roomId) => {
  if (!roomId) {
    error.value = '聊天室ID不存在'
    return
  }

  try {
    loading.value = true
    error.value = null
    
    console.log('开始加载聊天室:', roomId)
    await chatStore.setCurrentRoomById(roomId)
    
    // 检查是否成功加载
    if (!chatStore.currentRoom) {
      error.value = '聊天室不存在或加载失败'
      console.warn('聊天室加载失败，currentRoom 为 null')
    } else {
      console.log('聊天室加载成功:', chatStore.currentRoom)
    }
  } catch (err) {
    console.error('加载聊天室失败:', err)
    
    // 根据错误类型设置错误信息
    if (err.response) {
      switch (err.response.status) {
        case 404:
          error.value = '聊天室不存在或已被删除'
          break
        case 403:
          error.value = '您没有权限访问此聊天室'
          break
        case 401:
          error.value = '请先登录'
          // 可以在这里跳转到登录页
          router.push('/login')
          break
        default:
          error.value = `服务器错误: ${err.response.status}`
      }
    } else if (err.request) {
      error.value = '网络错误，请检查网络连接'
    } else {
      error.value = `加载失败: ${err.message}`
    }
  } finally {
    loading.value = false
  }
}

// 重试加载函数
const retryLoading = () => {
  const roomId = route.params.roomId
  if (roomId) {
    loadChatRoom(roomId)
  }
}

// 返回函数
const goBack = () => {
  router.back()
}

// 监听路由参数变化
watch(() => route.params.roomId, async (newRoomId) => {
  if (newRoomId) {
    console.log('路由参数变化，加载聊天室:', newRoomId)
    await loadChatRoom(newRoomId)
  } else {
    // 如果没有 roomId，清空当前聊天室
    chatStore.setCurrentRoom(null)
    error.value = null
  }
})

// 生命周期
onMounted(async () => {
  // 如果URL中有roomId参数，直接进入对应聊天室
  const roomId = route.params.roomId
  if (roomId) {
    console.log('页面加载，初始化聊天室:', roomId)
    await loadChatRoom(roomId)
  } else {
    console.log('没有roomId参数，显示空状态')
  }
})

// 添加路由守卫，在离开页面时清理状态
import { onBeforeUnmount } from 'vue'

onBeforeUnmount(() => {
  // 离开页面时清空当前聊天室，避免状态残留
  chatStore.setCurrentRoom(null)
})
</script>

<style scoped>
.chat-layout {
  display: flex;
  height: 100vh;
}

.chat-sidebar {
  width: 320px;
  border-right: 1px solid #e0e0e0;
}

.chat-main {
  flex: 1;
  position: relative;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  flex-direction: column;
  gap: 16px;
}

.error-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 20px;
}

.no-room-selected {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}
</style>