<template>
  <div class="admin-report-container">
    <n-card class="report-card" title="举报管理">
      <template #header-extra>
        <n-space>
          <n-select
            v-model:value="filterStatus"
            :options="statusOptions"
            placeholder="筛选状态"
            style="width: 150px"
            @update:value="fetchReports"
          />
          <n-select
            v-model:value="filterType"
            :options="typeOptions"
            placeholder="筛选类型"
            style="width: 150px"
            @update:value="fetchReports"
          />
        </n-space>
      </template>

      <n-spin :show="loading">
        <div v-if="reports.length === 0" class="empty-state">
          <n-icon size="64" class="empty-icon">
            <AlertCircleOutline />
          </n-icon>
          <p>暂无举报记录</p>
        </div>

        <div v-else class="report-list">
          <n-card
            v-for="report in reports"
            :key="report.id"
            class="report-item"
            :bordered="true"
          >
            <template #header>
              <div class="report-header">
                <div class="report-info">
                  <n-tag :type="getStatusType(report.status)" round>
                    {{ getStatusText(report.status) }}
                  </n-tag>
                  <span class="report-type">
                    {{ getReportTypeText(report.report_type) }}
                  </span>
                  <span class="report-id">#{{ report.id }}</span>
                </div>
                <div class="report-time">
                  {{ formatTime(report.created_at) }}
                </div>
              </div>
            </template>

            <n-descriptions :column="2" bordered>
              <n-descriptions-item label="举报人">
                {{ report.reporter_nickname || report.reporter_username }}
              </n-descriptions-item>
              <n-descriptions-item label="被举报人">
                {{ report.reported_user_nickname || report.reported_user_username }}
              </n-descriptions-item>
              <n-descriptions-item label="举报原因" :span="2">
                {{ report.reason }}
              </n-descriptions-item>
              <n-descriptions-item v-if="report.description" label="详细描述" :span="2">
                {{ report.description }}
              </n-descriptions-item>
            </n-descriptions>

            <div v-if="report.admin_feedback" class="feedback-section">
              <h4>管理员反馈</h4>
              <p>{{ report.admin_feedback }}</p>
            </div>

            <template #footer v-if="report.status === 'pending'">
              <n-space justify="end">
                <n-button
                  type="success"
                  @click="showApproveDialog(report.id)"
                  :loading="processing === report.id"
                >
                  通过举报
                </n-button>
                <n-button
                  type="error"
                  @click="showRejectDialog(report.id)"
                  :loading="processing === report.id"
                >
                  拒绝举报
                </n-button>
              </n-space>
            </template>
          </n-card>
        </div>
      </n-spin>

      <div v-if="reports.length > 0" class="pagination-container">
        <n-pagination
          v-model:page="currentPage"
          v-model:page-size="pageSize"
          :page-count="totalPages"
          show-size-picker
          :page-sizes="[10, 20, 50]"
          @update:page="fetchReports"
          @update:page-size="handlePageSizeChange"
        />
      </div>
    </n-card>

    <n-modal v-model:show="showApproveModal" preset="dialog" title="通过举报">
      <n-form ref="approveFormRef" :model="approveForm" :rules="approveRules">
        <n-form-item label="处理反馈" path="feedback">
          <n-input
            v-model:value="approveForm.feedback"
            type="textarea"
            placeholder="请输入处理反馈（选填）"
            :rows="4"
          />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="showApproveModal = false">取消</n-button>
          <n-button type="success" @click="handleApprove" :loading="processing">
            确认通过
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <n-modal v-model:show="showRejectModal" preset="dialog" title="拒绝举报">
      <n-form ref="rejectFormRef" :model="rejectForm" :rules="rejectRules">
        <n-form-item label="拒绝原因" path="reason">
          <n-input
            v-model:value="rejectForm.reason"
            type="textarea"
            placeholder="请输入拒绝原因"
            :rows="4"
          />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="showRejectModal = false">取消</n-button>
          <n-button type="error" @click="handleReject" :loading="processing">
            确认拒绝
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMessage, NCard, NSpin, NTag, NDescriptions, NDescriptionsItem, NButton, NSpace, NModal, NForm, NFormItem, NInput, NSelect, NIcon, NPagination } from 'naive-ui'
import { AlertCircleOutline } from '@vicons/ionicons5'
import axios from '@/utils/axios'

const message = useMessage()

const loading = ref(false)
const reports = ref([])
const filterStatus = ref(null)
const filterType = ref(null)
const processing = ref(null)
const currentPage = ref(1)
const pageSize = ref(10)
const totalPages = ref(1)
const totalReports = ref(0)

const showApproveModal = ref(false)
const showRejectModal = ref(false)
const approveFormRef = ref(null)
const rejectFormRef = ref(null)
const currentApproveId = ref(null)
const currentRejectId = ref(null)

const approveForm = ref({
  feedback: ''
})

const rejectForm = ref({
  reason: ''
})

const approveRules = {}

const rejectRules = {
  reason: { required: true, message: '请输入拒绝原因', trigger: 'blur' }
}

const statusOptions = [
  { label: '全部状态', value: null },
  { label: '待处理', value: 'pending' },
  { label: '已通过', value: 'approved' },
  { label: '已拒绝', value: 'rejected' }
]

const typeOptions = [
  { label: '全部类型', value: null },
  { label: '举报用户', value: 'user' },
  { label: '举报文章', value: 'article' },
  { label: '举报评论', value: 'comment' }
]

const fetchReports = async () => {
  try {
    loading.value = true
    let url = '/reports/'
    const params = []
    
    if (filterStatus.value) {
      params.push(`status=${filterStatus.value}`)
    }
    if (filterType.value) {
      params.push(`report_type=${filterType.value}`)
    }
    params.push(`page=${currentPage.value}`)
    params.push(`page_size=${pageSize.value}`)
    
    if (params.length > 0) {
      url += '?' + params.join('&')
    }
    
    const response = await axios.get(url)
    reports.value = response.data.results || response.data || []
    totalReports.value = response.data.count || 0
    totalPages.value = Math.ceil(totalReports.value / pageSize.value)
  } catch (error) {
    console.error('获取举报记录失败:', error)
    message.error('获取举报记录失败')
  } finally {
    loading.value = false
  }
}

const showApproveDialog = (id) => {
  currentApproveId.value = id
  approveForm.value.feedback = ''
  showApproveModal.value = true
}

const showRejectDialog = (id) => {
  currentRejectId.value = id
  rejectForm.value.reason = ''
  showRejectModal.value = true
}

const handleApprove = async () => {
  try {
    processing.value = currentApproveId.value
    
    await axios.post(`/reports/${currentApproveId.value}/approve/`, {
      admin_feedback: approveForm.value.feedback
    })
    
    message.success('举报已通过处理')
    showApproveModal.value = false
    await fetchReports()
  } catch (error) {
    console.error('通过举报失败:', error)
    message.error('通过举报失败')
  } finally {
    processing.value = null
  }
}

const handleReject = async () => {
  try {
    await rejectFormRef.value?.validate()
    processing.value = currentRejectId.value
    
    await axios.post(`/reports/${currentRejectId.value}/reject/`, {
      admin_feedback: rejectForm.value.reason
    })
    
    message.success('举报已拒绝处理')
    showRejectModal.value = false
    await fetchReports()
  } catch (error) {
    console.error('拒绝举报失败:', error)
    message.error('拒绝举报失败')
  } finally {
    processing.value = null
  }
}

const handlePageSizeChange = () => {
  currentPage.value = 1
  fetchReports()
}

const getStatusType = (status) => {
  switch (status) {
    case 'pending':
      return 'warning'
    case 'approved':
      return 'success'
    case 'rejected':
      return 'error'
    default:
      return 'default'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'pending':
      return '待处理'
    case 'approved':
      return '已通过'
    case 'rejected':
      return '已拒绝'
    default:
      return status
  }
}

const getReportTypeText = (type) => {
  switch (type) {
    case 'user':
      return '举报用户'
    case 'article':
      return '举报文章'
    case 'comment':
      return '举报评论'
    default:
      return type
  }
}

const formatTime = (timeString) => {
  const date = new Date(timeString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchReports()
})
</script>

<style scoped>
.admin-report-container {
  max-width: 1200px;
  margin: 24px auto;
  padding: 0 20px;
}

.report-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #999;
}

.empty-icon {
  color: #d9d9d9;
  margin-bottom: 16px;
}

.report-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.report-item {
  transition: all 0.3s ease;
}

.report-item:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.report-type {
  font-weight: 600;
  color: #333;
}

.report-id {
  color: #999;
  font-size: 14px;
}

.report-time {
  color: #999;
  font-size: 14px;
}

.feedback-section {
  margin-top: 16px;
  padding: 12px;
  background: #f0f9ff;
  border-left: 3px solid #10b981;
  border-radius: 4px;
}

.feedback-section h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #10b981;
}

.feedback-section p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}
</style>
