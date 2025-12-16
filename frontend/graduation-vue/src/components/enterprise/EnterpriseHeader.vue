<!-- src/components/enterprise/EnterpriseHeader.vue -->
<template>
  <header class="enterprise-header">
    <div class="enterprise-header-content">
      <!-- 企业品牌标识 -->
      <div class="enterprise-brand" @click="$router.push('/enterprise')">
        <n-icon size="32" class="brand-icon">
          <Building />
        </n-icon>
        <span class="brand-text">企业服务中心</span>
      </div>

      <!-- 企业专属导航菜单 -->
      <n-menu 
        mode="horizontal" 
        :options="enterpriseMenuOptions" 
        class="enterprise-nav-menu"
        @select="handleMenuSelect"
      />

      <!-- 企业用户功能区 -->
      <div class="enterprise-actions">
        <n-button 
          type="primary" 
          size="small" 
          @click="handlePublishJob"
        >
          <template #icon>
            <n-icon><Add /></n-icon>
          </template>
          发布招聘
        </n-button>
        
        <n-dropdown 
          trigger="hover" 
          :options="userDropdownOptions"
          @select="handleUserAction"
        >
          <div class="user-info">
            <n-avatar 
              size="small" 
              :src="userAvatar"
              class="user-avatar"
            >
              <template #fallback>
                <n-icon><PersonCircle /></n-icon>
              </template>
            </n-avatar>
            <span class="user-name">{{ userName }}</span>
          </div>
        </n-dropdown>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  NMenu, NButton, NIcon, NAvatar, NDropdown 
} from 'naive-ui'
import {  Add, PersonCircle, Settings, LogOut } from '@vicons/ionicons5'
// Building,
const router = useRouter()

// 企业用户信息
const userAvatar = ref('')
const userName = ref('企业用户')

// 企业专属菜单
const enterpriseMenuOptions = ref([
  { key: 'recruitments', label: '招聘管理'},
  { key: 'resumes', label: '简历库' },
  { key: 'analytics', label: '数据统计' },
  { key: 'company', label: '企业信息' }
])

// 用户下拉菜单
const userDropdownOptions = ref([
  { key: 'profile', label: '企业资料', icon: Settings },
  { key: 'settings', label: '账户设置', icon: Settings },
  { key: 'divider', type: 'divider' },
  { key: 'logout', label: '退出登录', icon: LogOut, type: 'warning' }
])

const handleMenuSelect = (key) => {
  router.push(`/enterprise/${key}`)
}

const handlePublishJob = () => {
  router.push('/enterprise/recruitments/create')
}

const handleUserAction = (key) => {
  switch (key) {
    case 'profile':
      router.push('/enterprise/edit')
      break
    case 'settings':
      router.push('/enterprise/settings')
      break
    case 'logout':
      handleLogout()
      break
  }
}

const handleLogout = () => {
  localStorage.removeItem('enterpriseToken')
  router.push('/login?type=enterprise')
}

onMounted(() => {
  // 初始化企业用户信息
  initializeEnterpriseUser()
})

const initializeEnterpriseUser = () => {
  // 从本地存储或API获取企业用户信息
  const enterpriseInfo = JSON.parse(localStorage.getItem('enterpriseInfo') || '{}')
  userAvatar.value = enterpriseInfo.avatar || ''
  userName.value = enterpriseInfo.name || '企业用户'
}
</script>

<style scoped>
.enterprise-header {
  background: linear-gradient(135deg, #e5e5ed 0%, #e5e5ed 0%);
  color: rgb(69, 44, 44);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.562);
}

.enterprise-header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.enterprise-brand {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: 600;
  font-size: 18px;
}

.brand-icon {
  margin-right: 8px;
}

.enterprise-nav-menu {
  flex: 1;
  margin: 0 40px;
  :deep(.n-menu-item) {
    color: rgba(255, 255, 255, 0.9) !important;
  }
  :deep(.n-menu-item.n-menu-item--selected) {
    color: white !important;
    background: rgba(255, 255, 255, 0.925);
  }
}

.enterprise-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.1);
}

.user-name {
  font-size: 14px;
  color: white;
}
</style>