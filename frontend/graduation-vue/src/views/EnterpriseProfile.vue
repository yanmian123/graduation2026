<template>
  <div class="enterprise-profile">
    <n-card class="profile-card" bordered>
      <!-- 返回按钮 -->
      <n-button
        type="default"
        size="small"
        class="back-button"
        @click="goBack"
      >
        <template #icon>
          <n-icon><ChevronBackOutline /></n-icon>
        </template>
        返回
      </n-button>

      <!-- 企业基本信息 -->
      <div class="enterprise-header">
        <n-avatar
          :src="enterpriseLogoUrl"
          size="large"
          round
          :fallback-src="defaultCompanyLogo"
        >
          <template #fallback>
            <n-icon><Business /></n-icon>
          </template>
        </n-avatar>
        <div class="enterprise-info">
          <h1 class="enterprise-name">{{ enterprise.name }}</h1>
          <p class="enterprise-industry">{{ getIndustryText(enterprise.industry) }}</p>
          <p class="enterprise-scale">{{ getScaleText(enterprise.scale) }}</p>
        </div>
      </div>

      <!-- 关注按钮/编辑按钮 -->
      <div class="follow-section">
        <n-button
          v-if="isOwnEnterprise"
          type="primary"
          size="large"
          round
          @click="goToEdit"
        >
          编辑企业信息
        </n-button>
        <n-button
          v-else
          :type="isFollowing ? 'default' : 'primary'"
          size="large"
          round
          @click="handleFollow"
          :loading="following"
        >
          {{ isFollowing ? '已关注' : '关注企业' }}
        </n-button>
      </div>

      <!-- 企业详细信息 -->
      <div class="enterprise-details">
        <h2 class="section-title">企业简介</h2>
        <div class="description">{{ enterprise.description }}</div>
      </div>

      <div class="enterprise-details">
        <h2 class="section-title">联系方式</h2>
        <div class="contact-info">
          <div class="contact-item">
            <n-icon class="contact-icon"><MailOutline /></n-icon>
            <span class="contact-label">招聘邮箱：</span>
            <span class="contact-value">{{ enterprise.contact_email }}</span>
          </div>
          <div class="contact-item">
            <n-icon class="contact-icon"><LocationOutline /></n-icon>
            <span class="contact-label">企业地址：</span>
            <span class="contact-value">{{ enterprise.address }}</span>
          </div>
          <div class="contact-item" v-if="enterprise.website">
            <n-icon class="contact-icon"><GlobeOutline /></n-icon>
            <span class="contact-label">企业官网：</span>
            <a :href="enterprise.website" target="_blank" class="contact-link">{{ enterprise.website }}</a>
          </div>
        </div>
      </div>

      <!-- 企业发布的职位 -->
      <div v-if="!isOwnEnterprise" class="enterprise-details">
        <h2 class="section-title">招聘职位</h2>
        <div v-if="recruitments.length === 0" class="empty-state">
          <n-empty description="暂无招聘职位" />
        </div>
        <div v-else class="recruitment-list">
          <n-card
            v-for="recruitment in recruitments"
            :key="recruitment.id"
            class="recruitment-card"
            hoverable
            @click="goToJobDetail(recruitment.id)"
          >
            <div class="recruitment-header">
              <h3 class="recruitment-title">{{ recruitment.title }}</h3>
              <n-tag
                v-if="recruitment.is_urgent"
                type="error"
                size="small"
                round
              >
                急聘
              </n-tag>
            </div>
            <div class="recruitment-info">
              <span class="info-item">
                <n-icon><CashOutline /></n-icon>
                {{ recruitment.salary }}
              </span>
              <span class="info-item">
                <n-icon><LocationOutline /></n-icon>
                {{ recruitment.work_location }}
              </span>
            </div>
          </n-card>
        </div>
      </div>
    </n-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { NCard, NButton, NAvatar, NIcon, NTag, NEmpty } from 'naive-ui'
import {
  ChevronBackOutline,
  Business,
  PersonOutline,
  CallOutline,
  MailOutline,
  LocationOutline,
  GlobeOutline,
  CashOutline
} from '@vicons/ionicons5'
import axios from '@/utils/axios'

const route = useRoute()
const router = useRouter()
const message = useMessage()

// 获取路由参数
const enterpriseUserId = ref(route.params.id)

// 数据状态
const enterprise = ref({})
const recruitments = ref([])
const loading = ref(true)
const isFollowing = ref(false)
const following = ref(false)

// 默认公司Logo
const defaultCompanyLogo = ref('/images/default-company-logo.png')

// 行业映射
const industryMap = {
  'IT': '信息技术',
  'FINANCE': '金融',
  'EDUCATION': '教育',
  'MEDIA': '传媒',
  'MANUFACTURING': '制造业',
  'SERVICE': '服务业',
  'OTHER': '其他'
}

// 规模映射
const scaleMap = {
  'MICRO': '微型企业（<10人）',
  'SMALL': '小型企业（10-99人）',
  'MEDIUM': '中型企业（100-999人）',
  'LARGE': '大型企业（1000人以上）'
}

// 方法
const getIndustryText = (industry) => {
  return industryMap[industry] || industry
}

const getScaleText = (scale) => {
  return scaleMap[scale] || scale
}

// 获取企业信息
const fetchEnterpriseInfo = async () => {
  try {
    loading.value = true
    const response = await axios.get(`/enterprises/user/${enterpriseUserId.value}/`)
    const data = response.data
    
    // 处理logo URL，添加localhost:8000前缀（如果是相对路径）
    if (data.logo) {
      data.logo = data.logo.startsWith('http') ? data.logo : `http://localhost:8000${data.logo}`
    } else if (data.company_logo) {
      data.logo = data.company_logo.startsWith('http') ? data.company_logo : `http://localhost:8000${data.company_logo}`
    }
    
    enterprise.value = data
    console.log('企业信息:', data)
    console.log('企业logo:', data.logo)
  } catch (error) {
    console.error('获取企业信息失败:', error)
    message.error('获取企业信息失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 获取企业发布的职位
const fetchEnterpriseRecruitments = async () => {
  try {
    const response = await axios.get(`/recruitments/?enterprise_user_id=${enterpriseUserId.value}`)
    recruitments.value = response.data.results || response.data
  } catch (error) {
    console.error('获取企业职位失败:', error)
  }
}

// 检查是否为企业用户查看自己的企业信息
const isOwnEnterprise = computed(() => {
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  return userInfo.is_enterprise && userInfo.id === parseInt(enterpriseUserId.value)
})

// 计算企业logo URL
const enterpriseLogoUrl = computed(() => {
  if (!enterprise.value) return defaultCompanyLogo.value
  
  const logo = enterprise.value.logo || enterprise.value.company_logo
  if (!logo) return defaultCompanyLogo.value
  
  // 如果已经是完整URL，直接返回
  if (logo.startsWith('http://') || logo.startsWith('https://')) {
    return logo
  }
  
  // 否则添加localhost:8000前缀
  return `http://localhost:8000${logo}`
})

// 检查是否已关注
const checkFollowStatus = async () => {
  // 如果是企业用户查看自己的企业信息，不检查关注状态
  if (isOwnEnterprise.value) {
    return
  }
  
  try {
    const response = await axios.get(`/users/${enterpriseUserId.value}/follow_status/`)
    isFollowing.value = response.data.is_following
  } catch (error) {
    console.error('获取关注状态失败:', error)
  }
}

// 关注/取消关注企业
const handleFollow = async () => {
  const isLogin = !!localStorage.getItem('accessToken')
  if (!isLogin) {
    message.warning('请先登录后再关注企业')
    router.push('/login')
    return
  }

  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  if (userInfo.is_enterprise) {
    message.error('企业用户不能关注其他企业')
    return
  }

  following.value = true
  try {
    if (isFollowing.value) {
      await axios.delete(`/users/${enterpriseUserId.value}/follow/`)
      isFollowing.value = false
      message.success('已取消关注')
    } else {
      await axios.post(`/users/${enterpriseUserId.value}/follow/`)
      isFollowing.value = true
      message.success('关注成功')
    }
  } catch (error) {
    console.error('关注操作失败:', error)
    message.error('操作失败，请稍后重试')
  } finally {
    following.value = false
  }
}

// 跳转到编辑页面
const goToEdit = () => {
  router.push('/enterprise/edit')
}

// 跳转到职位详情
const goToJobDetail = (jobId) => {
  router.push(`/jobs/${jobId}`)
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 初始化
onMounted(() => {
  fetchEnterpriseInfo()
  fetchEnterpriseRecruitments()
  checkFollowStatus()
})
</script>

<style scoped>
.enterprise-profile {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
  background-color: #f9fafb;
}

.profile-card {
  padding: 20px;
}

.back-button {
  margin-bottom: 20px;
}

.enterprise-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.enterprise-info h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.enterprise-info p {
  font-size: 16px;
  color: #6b7280;
  margin: 0 0 4px 0;
}

.follow-section {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f3f4f6;
  border-radius: 8px;
}

.enterprise-details {
  margin-bottom: 30px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 20px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e5e7eb;
}

.description {
  font-size: 16px;
  line-height: 1.8;
  color: #4b5563;
  white-space: pre-wrap;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
}

.contact-icon {
  color: #6b7280;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.contact-label {
  color: #6b7280;
  font-weight: 500;
}

.contact-value {
  color: #374151;
  font-weight: 500;
}

.contact-link {
  color: #059669;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.contact-link:hover {
  color: #047857;
  text-decoration: underline;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}

.recruitment-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recruitment-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.recruitment-card:hover {
  transform: translateY(-2px);
}

.recruitment-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.recruitment-title {
  font-size: 18px;
  font-weight: 600;
  color: #374151;
  margin: 0;
  flex: 1;
}

.recruitment-info {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #6b7280;
}

.info-item n-icon {
  width: 16px;
  height: 16px;
}

@media (max-width: 768px) {
  .enterprise-profile {
    padding: 10px;
  }
  
  .enterprise-header {
    flex-direction: column;
    text-align: center;
  }
  
  .recruitment-info {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
