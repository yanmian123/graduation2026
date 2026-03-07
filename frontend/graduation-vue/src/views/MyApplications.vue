<template>
  <div class="my-applications">
    <n-card title="我的申请" class="applications-card">
      <template #header-extra>
        <n-space>
          <n-select
            v-model:value="statusFilter"
            :options="statusOptions"
            placeholder="筛选状态"
            clearable
            style="width: 150px"
            @update:value="handleFilterChange"
          />
          <n-button @click="loadApplications" :loading="loading">
            <template #icon>
              <n-icon><Refresh /></n-icon>
            </template>
            刷新
          </n-button>
        </n-space>
      </template>

      <n-spin :show="loading">
        <div v-if="applications.length === 0 && !loading" class="empty-state">
          <n-empty description="暂无申请记录">
            <template #icon>
              <n-icon size="64" color="#d9d9d9">
                <DocumentTextOutline />
              </n-icon>
            </template>
            <template #extra>
              <n-button type="primary" @click="router.push('/jobs')">
                去投递职位
              </n-button>
            </template>
          </n-empty>
        </div>

        <div v-else class="applications-list">
          <div
            v-for="application in applications"
            :key="application.id"
            class="application-item"
            @click="viewApplication(application)"
          >
            <div class="application-header">
              <div class="job-info">
                <h3 class="job-title">{{ application.recruitment_detail.title }}</h3>
                <div class="company-name">{{ application.recruitment_detail.enterprise.name }}</div>
              </div>
              <n-tag :type="getStatusType(application.status)" size="small">
                {{ getStatusText(application.status) }}
              </n-tag>
            </div>

            <div class="application-details">
              <div class="detail-item">
                <n-icon size="16" color="#666">
                  <TimeOutline />
                </n-icon>
                <span>申请时间：{{ formatDate(application.applied_at) }}</span>
              </div>
              <div class="detail-item">
                <n-icon size="16" color="#666">
                  <LocationOutline />
                </n-icon>
                <span>工作地点：{{ application.recruitment_detail.work_location }}</span>
              </div>
              <div class="detail-item">
                <n-icon size="16" color="#666">
                  <CashOutline />
                </n-icon>
                <span>薪资范围：{{ application.recruitment_detail.salary }}</span>
              </div>
            </div>

            <div class="application-footer">
              <n-space>
                <n-button
                  size="small"
                  @click.stop="viewJobDetail(application.recruitment_detail)"
                >
                  查看职位
                </n-button>
                <n-button
                  size="small"
                  type="error"
                  @click.stop="handleWithdraw(application)"
                  :disabled="application.status === 'HIRED' || application.status === 'REJECTED'"
                >
                  撤回申请
                </n-button>
              </n-space>
            </div>
          </div>
        </div>
      </n-spin>
    </n-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { 
  NCard, 
  NSpace, 
  NSelect, 
  NButton, 
  NIcon, 
  NTag, 
  NSpin, 
  NEmpty 
} from 'naive-ui'
import { 
  Refresh, 
  DocumentTextOutline, 
  TimeOutline, 
  LocationOutline, 
  CashOutline 
} from '@vicons/ionicons5'
import axios from '@/utils/axios'

const router = useRouter()
const message = useMessage()

const applications = ref([])
const loading = ref(false)
const statusFilter = ref(null)

const statusOptions = [
  { label: '待处理', value: 'PENDING' },
  { label: '已查看', value: 'VIEWED' },
  { label: '待面试', value: 'INTERVIEW' },
  { label: '已拒绝', value: 'REJECTED' },
  { label: '已录用', value: 'HIRED' }
]

const loadApplications = async () => {
  loading.value = true
  try {
    const params = {}
    if (statusFilter.value) {
      params.status = statusFilter.value
    }

    const response = await axios.get('applications/my_applications/', { params })
    applications.value = response.data.results || response.data || []
  } catch (error) {
    console.error('加载申请记录失败:', error)
    message.error('加载申请记录失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  loadApplications()
}

const viewApplication = (application) => {
  console.log('查看申请详情:', application)
}

const viewJobDetail = (recruitment) => {
  router.push(`/jobs/${recruitment.id}`)
}

const handleWithdraw = async (application) => {
  try {
    await axios.delete(`applications/${application.id}/`)
    message.success('申请已撤回')
    loadApplications()
  } catch (error) {
    console.error('撤回申请失败:', error)
    message.error('撤回申请失败，请稍后重试')
  }
}

const getStatusType = (status) => {
  const typeMap = {
    'PENDING': 'warning',
    'VIEWED': 'info',
    'INTERVIEW': 'primary',
    'REJECTED': 'error',
    'HIRED': 'success'
  }
  return typeMap[status] || 'default'
}

const getStatusText = (status) => {
  const textMap = {
    'PENDING': '待处理',
    'VIEWED': '已查看',
    'INTERVIEW': '待面试',
    'REJECTED': '已拒绝',
    'HIRED': '已录用'
  }
  return textMap[status] || status
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  const diffHours = Math.floor(diffTime / (1000 * 60 * 60))
  const diffMinutes = Math.floor(diffTime / (1000 * 60))

  if (diffDays > 0) {
    return `${diffDays}天前`
  } else if (diffHours > 0) {
    return `${diffHours}小时前`
  } else if (diffMinutes > 0) {
    return `${diffMinutes}分钟前`
  } else {
    return '刚刚'
  }
}

onMounted(() => {
  loadApplications()
})
</script>

<style scoped>
.my-applications {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.applications-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-radius: 12px;
}

.applications-card :deep(.n-card__header) {
  border-bottom: 1px solid #f0f0f0;
  padding: 20px;
}

.applications-card :deep(.n-card__content) {
  padding: 20px;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.applications-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.application-item {
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.application-item:hover {
  border-color: #10b981;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
  transform: translateY(-2px);
}

.application-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f5f5f5;
}

.job-info {
  flex: 1;
}

.job-title {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1d2129;
}

.company-name {
  font-size: 14px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 6px;
}

.application-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.application-footer {
  display: flex;
  justify-content: flex-end;
  padding-top: 12px;
  border-top: 1px solid #f5f5f5;
}

@media (max-width: 768px) {
  .my-applications {
    padding: 12px;
  }

  .applications-card :deep(.n-card__header) {
    padding: 16px;
  }

  .applications-card :deep(.n-card__content) {
    padding: 16px;
  }

  .application-item {
    padding: 16px;
  }

  .job-title {
    font-size: 16px;
  }

  .application-header {
    flex-direction: column;
    gap: 12px;
  }

  .application-footer {
    justify-content: center;
  }

  .application-footer :deep(.n-space) {
    width: 100%;
    justify-content: center;
  }
}
</style>
