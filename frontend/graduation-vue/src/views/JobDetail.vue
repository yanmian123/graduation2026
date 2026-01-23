<template>
  <div class="job-detail">
    <n-card class="job-detail-card" bordered>
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

      <!-- 职位基本信息 -->
      <div class="job-header">
        <h1 class="job-title">{{ job.title }}</h1>
        <div class="job-tags">
          <n-tag
            v-if="job.is_urgent"
            type="error"
            size="small"
            class="urgent-tag"
            round
          >
            <template #icon>
              <n-icon><Flash /></n-icon>
            </template>
            急聘
          </n-tag>
          <n-tag
            :type="getJobTypeTag(job.job_type)"
            size="small"
            class="type-tag"
            round
          >
            {{ getJobTypeText(job.job_type) }}
          </n-tag>
        </div>
      </div>

      <!-- 企业信息 -->
      <div class="company-section" @click="handleCompanyClick">
        <div class="company-header">
          <n-avatar
            :src="job.enterprise_logo"
            size="large"
            round
            :fallback-src="defaultCompanyLogo"
          >
            <template #fallback>
              <n-icon><Business /></n-icon>
            </template>
          </n-avatar>
          <div class="company-info">
            <h3 class="company-name">{{ job.enterprise_name }}</h3>
            <p class="company-industry">{{ job.enterprise_industry }}</p>
          </div>
        </div>
      </div>

      <!-- 职位详细信息 -->
      <div class="job-info-section">
        <h2 class="section-title">职位信息</h2>
        <div class="job-info-grid">
          <div class="info-item">
            <n-icon class="info-icon"><LocationOutline /></n-icon>
            <div class="info-content">
              <div class="info-label">工作地点</div>
              <div class="info-value">{{ job.work_location }}</div>
            </div>
          </div>
          <div class="info-item">
            <n-icon class="info-icon"><CashOutline /></n-icon>
            <div class="info-content">
              <div class="info-label">薪资范围</div>
              <div class="info-value salary">{{ job.salary }}</div>
            </div>
          </div>
          <div class="info-item">
            <n-icon class="info-icon"><BriefcaseOutline /></n-icon>
            <div class="info-content">
              <div class="info-label">工作经验</div>
              <div class="info-value">{{ getExperienceText(job.experience) }}</div>
            </div>
          </div>
          <div class="info-item">
            <n-icon class="info-icon"><SchoolOutline /></n-icon>
            <div class="info-content">
              <div class="info-label">学历要求</div>
              <div class="info-value">{{ getEducationText(job.education) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 职位描述 -->
      <div class="job-description-section">
        <h2 class="section-title">职位描述</h2>
        <div class="job-description">{{ job.job_desc }}</div>
      </div>

      <!-- 投递按钮 -->
      <div class="apply-section">
        <n-button
          type="primary"
          size="large"
          class="apply-button"
          @click="handleApply"
          :loading="applying"
          round
        >
          <template #icon>
            <n-icon><PaperPlaneOutline /></n-icon>
          </template>
          {{ applying ? '投递中...' : '立即申请' }}
        </n-button>
        
        <n-button
          type="info"
          size="large"
          class="contact-button"
          @click="handleContact"
          :loading="contacting"
          round
        >
          <template #icon>
            <n-icon><ChatbubblesOutline /></n-icon>
          </template>
          {{ contacting ? '连接中...' : '联系企业' }}
        </n-button>
      </div>

      <!-- 简历选择模态框 -->
      <ResumeSelectModal
        v-if="job.id"
        v-model:show="showResumeModal"
        :job-id="job.id"
        @success="handleApplySuccess"
      />
    </n-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { NCard, NButton, NTag, NAvatar, NIcon } from 'naive-ui'
import {
  ChevronBackOutline,
  Flash,
  Business,
  LocationOutline,
  CashOutline,
  BriefcaseOutline,
  SchoolOutline,
  PaperPlaneOutline,
  ChatbubblesOutline
} from '@vicons/ionicons5'
import axios from '@/utils/axios'
import ResumeSelectModal from '@/components/common/ResumeSelectModal.vue'
import { useChatStore } from '@/stores/chatStore'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const chatStore = useChatStore()

// 获取路由参数
const jobId = ref(route.params.id)

// 数据状态
const job = ref({})
const loading = ref(true)
const applying = ref(false)
const contacting = ref(false)
const showResumeModal = ref(false)

// 默认公司Logo
const defaultCompanyLogo = ref('/images/default-company-logo.png')

// 工作类型映射
const jobTypeMap = {
  'FULL_TIME': { text: '全职', type: 'success' },
  'PART_TIME': { text: '兼职', type: 'info' },
  'INTERNSHIP': { text: '实习', type: 'warning' }
}

// 经验要求映射
const experienceMap = {
  'FRESH': '应届毕业生',
  'LESS_THAN_1': '1年以内',
  '1_3': '1-3年',
  '3_5': '3-5年',
  '5_10': '5-10年',
  'MORE_THAN_10': '10年以上'
}

// 学历要求映射
const educationMap = {
  'HIGH_SCHOOL': '高中及以下',
  'ASSOCIATE': '专科',
  'BACHELOR': '本科',
  'MASTER': '硕士',
  'DOCTOR': '博士及以上'
}

// 方法
const getJobTypeTag = (type) => {
  return jobTypeMap[type]?.type || 'default'
}

const getJobTypeText = (type) => {
  return jobTypeMap[type]?.text || type
}

const getExperienceText = (experience) => {
  return experienceMap[experience] || experience
}

const getEducationText = (education) => {
  return educationMap[education] || education
}

// 获取职位详情
const fetchJobDetail = async () => {
  try {
    loading.value = true
    const response = await axios.get(`/recruitments/${jobId.value}/`)
    job.value = response.data
  } catch (error) {
    console.error('获取职位详情失败:', error)
    message.error('获取职位详情失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 点击企业信息跳转到企业主页
const handleCompanyClick = () => {
  if (job.value.enterprise_user_id) {
    router.push(`/enterprise/${job.value.enterprise_user_id}`)
  }
}

// 申请职位
const handleApply = async () => {
  const isLogin = !!localStorage.getItem('accessToken')
  if (!isLogin) {
    message.warning('请先登录后再申请职位')
    router.push('/login')
    return
  }

  // 显示简历选择模态框
  showResumeModal.value = true
}

const handleApplySuccess = () => {
  applying.value = false
  message.success('职位申请成功！')
}

// 联系企业
const handleContact = async () => {
  const isLogin = !!localStorage.getItem('accessToken')
  if (!isLogin) {
    message.warning('请先登录后再联系企业')
    router.push('/login')
    return
  }

  // 验证企业用户ID是否存在
  if (!job.value.enterprise_user_id) {
    message.error('无法获取企业信息，请联系客服')
    return
  }

  contacting.value = true

  try {
    // 从正确的键名获取用户信息
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}')

    if (!currentUser.id) {
      // 尝试从其他可能的键名获取
      const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
      if (userInfo.id) {
        Object.assign(currentUser, userInfo)
      }

      if (!currentUser.id) {
        message.error('无法获取用户ID，请重新登录')
        contacting.value = false
        return
      }
    }

    // 验证当前用户类型
    if (currentUser.is_enterprise) {
      message.error('企业用户不能联系其他企业')
      contacting.value = false
      return
    }

    // 调用聊天室的 startChat 方法
    const chatRoom = await chatStore.startChat({
      enterprise_user_id: job.value.enterprise_user_id,
      job_seeker_user_id: currentUser.id,
      recruitment_id: job.value.id
    })

    // 设置当前聊天室
    chatStore.setCurrentRoom(chatRoom)
    message.success('已连接到企业聊天室')
    router.push(`/chat/${chatRoom.id}`)

  } catch (error) {
    console.error('创建聊天室失败:', error)
    message.error('联系企业失败: ' + (error.response?.data?.error || '请稍后重试'))
  } finally {
    contacting.value = false
  }
}

// 初始化
onMounted(() => {
  fetchJobDetail()
})
</script>

<style scoped>
.job-detail {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
  background-color: #f9fafb;
}

.job-detail-card {
  padding: 20px;
}

.back-button {
  margin-bottom: 20px;
}

.job-header {
  margin-bottom: 30px;
}

.job-title {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 15px;
  line-height: 1.3;
}

.job-tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.company-section {
  padding: 20px;
  background-color: #f3f4f6;
  border-radius: 8px;
  margin-bottom: 30px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.company-section:hover {
  background-color: #e5e7eb;
}

.company-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.company-info h3 {
  font-size: 20px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 8px 0;
}

.company-info p {
  font-size: 16px;
  color: #6b7280;
  margin: 0;
}

.job-info-section {
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

.job-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-icon {
  color: #6b7280;
  width: 20px;
  height: 20px;
}

.info-content .info-label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
}

.info-content .info-value {
  font-size: 16px;
  font-weight: 500;
  color: #374151;
}

.info-content .info-value.salary {
  color: #dc2626;
  font-weight: 600;
}

.job-description-section {
  margin-bottom: 30px;
}

.job-description {
  font-size: 16px;
  line-height: 1.8;
  color: #4b5563;
  white-space: pre-wrap;
}

.apply-section {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 2px solid #e5e7eb;
}

.apply-button, .contact-button {
  min-width: 200px;
  font-weight: 500;
  height: 48px;
  font-size: 16px;
}

@media (max-width: 768px) {
  .job-detail {
    padding: 10px;
  }
  
  .job-title {
    font-size: 24px;
  }
  
  .job-info-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .apply-section {
    flex-direction: column;
  }
  
  .apply-button, .contact-button {
    width: 100%;
  }
}
</style>