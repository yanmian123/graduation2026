<template>
  <n-card class="job-card" hoverable>
    <div class="job-header">
      <div class="job-title-section">
        <h3 class="job-title">{{ job.title }}</h3>
        <div class="tag-group">
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
    </div>
    
    <div class="company-info">
      <div class="company-logo-section">
        <n-avatar 
          :src="job.enterprise_logo" 
          class="company-logo"
          :fallback-src="defaultCompanyLogo"
          round
          size="large"
        >
          <template #fallback>
            <n-icon><Business /></n-icon>
          </template>
        </n-avatar>
        <div class="company-details">
          <h4 class="company-name">{{ job.enterprise_name }}</h4>
          <p class="company-industry">{{ job.enterprise_industry }}</p>
        </div>
      </div>
    </div>
    
    <div class="job-meta">
      <div class="meta-item">
        <n-icon class="meta-icon"><LocationOutline /></n-icon>
        <span>{{ job.work_location }}</span>
      </div>
      <div class="meta-item">
        <n-icon class="meta-icon"><CashOutline /></n-icon>
        <span class="salary">{{ job.salary }}</span>
      </div>
      <div class="meta-item">
        <n-icon class="meta-icon"><BriefcaseOutline /></n-icon>
        <span>{{ getExperienceText(job.experience) }}</span>
      </div>
      <div class="meta-item">
        <n-icon class="meta-icon"><SchoolOutline /></n-icon>
        <span>{{ getEducationText(job.education) }}</span>
      </div>
    </div>
    
    <p class="job-description">{{ job.job_desc }}</p>
    
    <div class="job-footer">
      <div class="publish-info">
        <n-icon size="14" class="time-icon"><TimeOutline /></n-icon>
        <span class="publish-time">{{ formatPublishTime(job.created_at) }}</span>
      </div>
      <n-button 
        type="primary" 
        size="small" 
        class="apply-btn"
        @click.stop="handleApply"
        :loading="applying"
        round
      >
        <template #icon>
          <n-icon><PaperPlaneOutline /></n-icon>
        </template>
        {{ applying ? '投递中...' : '立即申请' }}
      </n-button>
    </div>

    <!-- 简历选择模态框 -->
    <ResumeSelectModal 
      v-model:show="showResumeModal"
      :job-id="job.id"
      @success="handleApplySuccess"
    />
  </n-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { 
  NCard, 
  NTag, 
  NAvatar, 
  NIcon, 
  NButton 
} from 'naive-ui'
import { 
  Flash,
  Business,
  LocationOutline,
  CashOutline,
  BriefcaseOutline,
  SchoolOutline,
  TimeOutline,
  PaperPlaneOutline
} from '@vicons/ionicons5'
import ResumeSelectModal from '@/components/common/ResumeSelectModal.vue'

const props = defineProps({
  job: {
    type: Object,
    required: true,
    default: () => ({})
  }
})

const router = useRouter()
const message = useMessage()

const showResumeModal = ref(false)
const applying = ref(false)

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


// 计算属性
const isLogin = computed(() => {
  return !!localStorage.getItem('accessToken')
})

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

const formatPublishTime = (time) => {
  if (!time) return ''
  const now = new Date()
  const publishTime = new Date(time)
  const diff = now.getTime() - publishTime.getTime()
  
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return '今天发布'
  if (days === 1) return '昨天发布'
  if (days < 7) return `${days}天前发布`
  if (days < 30) return `${Math.floor(days / 7)}周前发布`
  
  return publishTime.toLocaleDateString('zh-CN')
}

const handleApply = async () => {
  if (!isLogin.value) {
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
</script>

<style scoped>
.job-card {
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  height: 100%;
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
}

.job-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #e0e0e0;
}

.job-header {
  margin-bottom: 16px;
}

.job-title-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.job-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #1f2937;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.tag-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.company-info {
  margin-bottom: 16px;
}

.company-logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.company-logo {
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.company-details h4 {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 6px 0;
  color: #374151;
}

.company-details p {
  font-size: 13px;
  color: #6b7280;
  margin: 0;
}

.job-meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin: 16px 0;
}

.meta-item {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #4b5563;
  padding: 4px 0;
}

.meta-icon {
  margin-right: 8px;
  color: #9ca3af;
  flex-shrink: 0;
  width: 16px;
  height: 16px;
}

.salary {
  color: #dc2626;
  font-weight: 600;
}

.job-description {
  color: #4b5563;
  font-size: 14px;
  margin: 16px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
  line-height: 1.6;
}

.job-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid #f3f4f6;
}

.publish-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.time-icon {
  color: #9ca3af;
}

.publish-time {
  font-size: 13px;
  color: #6b7280;
}

.apply-btn {
  min-width: 100px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .job-meta {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .job-title {
    font-size: 16px;
  }
  
  .job-footer {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .apply-btn {
    width: 100%;
  }
}
</style>