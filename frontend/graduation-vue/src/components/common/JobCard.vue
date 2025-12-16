<template>
  <n-card class="job-card" hoverable @click="handleCardClick">
    <div class="job-header">
      <div class="job-title-section">
        <h3 class="job-title">{{ job.title }}</h3>
        <n-tag 
          v-if="job.isUrgent" 
          type="error" 
          size="small"
          class="urgent-tag"
        >
          急聘
        </n-tag>
        <n-tag 
          v-else 
          :type="getJobTypeTag(job.type)" 
          size="small"
          class="type-tag"
        >
          {{ getJobTypeText(job.type) }}
        </n-tag>
      </div>
    </div>
    
    <div class="company-info">
      <div class="company-logo-section">
        <n-avatar 
          :src="job.companyLogo" 
          class="company-logo"
          :fallback-src="defaultCompanyLogo"
        >
          <template #fallback>
            <n-icon><Briefcase /></n-icon>
          </template>
        </n-avatar>
        <div class="company-details">
          <h4 class="company-name">{{ job.company }}</h4>
          <p class="company-industry">{{ job.industry }}</p>
        </div>
      </div>
    </div>
    
    <div class="job-meta">
      <div class="meta-item">
        <n-icon class="meta-icon"><Location /></n-icon>
        <span>{{ job.location }}</span>
      </div>
      <div class="meta-item">
        <n-icon class="meta-icon"><Cash /></n-icon>
        <span class="salary">{{ job.salary }}</span>
      </div>
      <div class="meta-item">
        <n-icon class="meta-icon"><Briefcase /></n-icon>
        <span>{{ job.experience }}</span>
      </div>
      <div class="meta-item">
        <n-icon class="meta-icon"><School /></n-icon>
        <span>{{ job.education }}</span>
      </div>
    </div>
    
    <p class="job-description">{{ job.description }}</p>
    
    <div class="job-tags" v-if="job.tags && job.tags.length">
      <n-tag 
        v-for="tag in job.tags" 
        :key="tag" 
        size="small" 
        :bordered="false"
        class="skill-tag"
      >
        {{ tag }}
      </n-tag>
    </div>
    
    <div class="job-footer">
      <span class="publish-time">{{ formatPublishTime(job.publishTime) }}</span>
      <n-button 
        type="primary" 
        size="small" 
        class="apply-btn"
        @click.stop="handleApply"
      >
        立即申请
      </n-button>
    </div>
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
  Briefcase, 
  Location, 
  Cash, 
  School 
} from '@vicons/ionicons5'

// 定义 props
const props = defineProps({
  job: {
    type: Object,
    required: true,
    default: () => ({})
  },
  showApplyButton: {
    type: Boolean,
    default: true
  }
})

// 定义 emits
const emit = defineEmits(['view', 'apply'])

const router = useRouter()
const message = useMessage()

// 默认公司Logo
const defaultCompanyLogo = ref('https://picsum.photos/id/1/60/60')

// 工作类型标签映射
const jobTypeMap = {
  'campus': { text: '校招', type: 'success' },
  'intern': { text: '实习', type: 'info' },
  'social': { text: '社招', type: 'warning' },
  'parttime': { text: '兼职', type: 'default' }
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

const formatPublishTime = (time) => {
  if (!time) return ''
  
  // 简单的发布时间格式化
  if (time.includes('小时前')) return time
  if (time.includes('天前')) return time
  if (time.includes('周前')) return time
  
  // 如果是完整日期，可以进一步处理
  return time
}

const handleCardClick = () => {
  emit('view', props.job)
  // 实际项目中可以跳转到职位详情页
  // router.push(`/jobs/${props.job.id}`)
  message.info(`查看职位详情: ${props.job.title}`)
}

const handleApply = () => {
  if (!isLogin.value) {
    message.warning('请先登录后再申请职位')
    router.push('/login')
    return
  }
  
  emit('apply', props.job)
  message.success(`已申请职位: ${props.job.title}`)
  
  // 实际项目中这里应该调用申请API
  // applyJob(props.job.id)
}
</script>

<style scoped>
.job-card {
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.job-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.job-title-section {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.job-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #1d2129;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.urgent-tag, .type-tag {
  flex-shrink: 0;
}

.company-info {
  margin-bottom: 12px;
}

.company-logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.company-logo {
  flex-shrink: 0;
}

.company-details h4 {
  font-size: 14px;
  font-weight: 500;
  margin: 0 0 4px 0;
  color: #1d2129;
}

.company-details p {
  font-size: 12px;
  color: #86909c;
  margin: 0;
}

.job-meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin: 12px 0;
}

.meta-item {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #4e5969;
}

.meta-icon {
  margin-right: 6px;
  color: #86909c;
  flex-shrink: 0;
}

.salary {
  color: #f53f3f;
  font-weight: 500;
}

.job-description {
  color: #4e5969;
  font-size: 14px;
  margin: 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.job-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
}

.skill-tag {
  background-color: #f0f2f5;
  color: #4e5969;
}

.job-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.publish-time {
  font-size: 12px;
  color: #86909c;
}

.apply-btn {
  min-width: 80px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .job-meta {
    grid-template-columns: 1fr;
  }
  
  .job-title-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .job-footer {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .apply-btn {
    width: 100%;
  }
}
</style>