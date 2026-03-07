<template>
  <div class="admin-verification-container">
    <n-card class="verification-card" title="实名认证审核">
      <template #header-extra>
        <n-space>
          <n-select
            v-model:value="filterStatus"
            :options="statusOptions"
            placeholder="筛选状态"
            style="width: 150px"
            @update:value="fetchApplications"
          />
          <n-select
            v-model:value="filterType"
            :options="typeOptions"
            placeholder="筛选类型"
            style="width: 150px"
            @update:value="fetchApplications"
          />
        </n-space>
      </template>

      <n-spin :show="loading">
        <div v-if="applications.length === 0" class="empty-state">
          <n-icon size="64" class="empty-icon">
            <DocumentOutline />
          </n-icon>
          <p>暂无认证申请</p>
        </div>

        <div v-else class="application-list">
          <n-card
            v-for="application in applications"
            :key="application.id"
            class="application-item"
            :bordered="true"
          >
            <template #header>
              <div class="application-header">
                <div class="application-info">
                  <n-tag :type="getStatusType(application.status)" round>
                    {{ getStatusText(application.status) }}
                  </n-tag>
                  <span class="application-type">
                    {{ application.verification_type === 'ENTERPRISE' ? '企业认证' : '个人认证' }}
                  </span>
                  <span class="application-user">{{ application.user?.username }}</span>
                </div>
                <div class="application-time">
                  {{ formatTime(application.created_at) }}
                </div>
              </div>
            </template>

            <n-descriptions :column="2" bordered>
              <n-descriptions-item label="真实姓名">
                {{ application.name }}
              </n-descriptions-item>
              <n-descriptions-item label="身份证号">
                {{ application.id_number }}
              </n-descriptions-item>
              <n-descriptions-item label="联系电话">
                {{ application.phone }}
              </n-descriptions-item>
              <n-descriptions-item label="认证类型">
                {{ application.verification_type === 'ENTERPRISE' ? '企业认证' : '个人认证' }}
              </n-descriptions-item>
            </n-descriptions>

            <div v-if="application.business_license" class="file-section">
              <h4>营业执照</h4>
              <n-image
                v-if="isImage(application.business_license)"
                :src="getFileUrl(application.business_license)"
                width="200"
                object-fit="contain"
              />
              <a v-else :href="getFileUrl(application.business_license)" target="_blank" class="file-link">
                <n-icon><Document /></n-icon>
                查看文件
              </a>
            </div>

            <div v-if="application.student_card" class="file-section">
              <h4>学信网截图</h4>
              <n-image
                v-if="isImage(application.student_card)"
                :src="getFileUrl(application.student_card)"
                width="200"
                object-fit="contain"
              />
              <a v-else :href="getFileUrl(application.student_card)" target="_blank" class="file-link">
                <n-icon><Document /></n-icon>
                查看文件
              </a>
            </div>

            <div v-if="application.other_files && application.other_files.length > 0" class="file-section">
              <h4>其他证明文件</h4>
              <div class="other-files">
                <div v-for="(file, index) in application.other_files" :key="index" class="other-file-item">
                  <n-image
                    v-if="isImage(file)"
                    :src="getFileUrl(file)"
                    width="100"
                    object-fit="contain"
                  />
                  <a v-else :href="getFileUrl(file)" target="_blank" class="file-link">
                    <n-icon><Document /></n-icon>
                    文件 {{ index + 1 }}
                  </a>
                </div>
              </div>
            </div>

            <div v-if="application.status === 'REJECTED'" class="reject-reason">
              <h4>拒绝原因</h4>
              <p>{{ application.reject_reason }}</p>
            </div>

            <template #footer v-if="application.status === 'PENDING'">
              <n-space justify="end">
                <n-button
                  type="success"
                  @click="handleApprove(application.id)"
                  :loading="approving === application.id"
                >
                  通过认证
                </n-button>
                <n-button
                  type="error"
                  @click="showRejectDialog(application.id)"
                  :loading="rejecting === application.id"
                >
                  拒绝认证
                </n-button>
              </n-space>
            </template>
          </n-card>
        </div>
      </n-spin>
    </n-card>

    <n-modal v-model:show="showRejectModal" preset="dialog" title="拒绝认证">
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
          <n-button type="error" @click="handleReject" :loading="rejecting">
            确认拒绝
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMessage, NCard, NSpin, NTag, NDescriptions, NDescriptionsItem, NButton, NSpace, NModal, NForm, NFormItem, NInput, NSelect, NIcon, NImage } from 'naive-ui'
import { Document, DocumentOutline } from '@vicons/ionicons5'
import axios from '@/utils/axios'

const message = useMessage()

const loading = ref(false)
const applications = ref([])
const filterStatus = ref(null)
const filterType = ref(null)
const approving = ref(null)
const rejecting = ref(null)
const showRejectModal = ref(false)
const rejectFormRef = ref(null)
const currentRejectId = ref(null)

const rejectForm = ref({
  reason: ''
})

const rejectRules = {
  reason: { required: true, message: '请输入拒绝原因', trigger: 'blur' }
}

const statusOptions = [
  { label: '全部状态', value: null },
  { label: '待审核', value: 'PENDING' },
  { label: '已通过', value: 'APPROVED' },
  { label: '已拒绝', value: 'REJECTED' }
]

const typeOptions = [
  { label: '全部类型', value: null },
  { label: '企业认证', value: 'ENTERPRISE' },
  { label: '个人认证', value: 'INDIVIDUAL' }
]

const fetchApplications = async () => {
  try {
    loading.value = true
    let url = '/user/verifications/'
    const params = []
    
    if (filterStatus.value) {
      params.push(`status=${filterStatus.value}`)
    }
    if (filterType.value) {
      params.push(`verification_type=${filterType.value}`)
    }
    
    if (params.length > 0) {
      url += '?' + params.join('&')
    }
    
    const response = await axios.get(url)
    applications.value = response.data.results || response.data || []
  } catch (error) {
    console.error('获取认证申请失败:', error)
    message.error('获取认证申请失败')
  } finally {
    loading.value = false
  }
}

const handleApprove = async (id) => {
  try {
    approving.value = id
    await axios.post(`/user/verifications/${id}/approve/`)
    message.success('认证已通过')
    await fetchApplications()
  } catch (error) {
    console.error('通过认证失败:', error)
    message.error('通过认证失败')
  } finally {
    approving.value = null
  }
}

const showRejectDialog = (id) => {
  currentRejectId.value = id
  rejectForm.value.reason = ''
  showRejectModal.value = true
}

const handleReject = async () => {
  try {
    await rejectFormRef.value?.validate()
    rejecting.value = currentRejectId.value
    
    await axios.post(`/user/verifications/${currentRejectId.value}/reject/`, {
      reject_reason: rejectForm.value.reason
    })
    
    message.success('认证已拒绝')
    showRejectModal.value = false
    await fetchApplications()
  } catch (error) {
    console.error('拒绝认证失败:', error)
    message.error('拒绝认证失败')
  } finally {
    rejecting.value = null
  }
}

const getStatusType = (status) => {
  switch (status) {
    case 'PENDING':
      return 'warning'
    case 'APPROVED':
      return 'success'
    case 'REJECTED':
      return 'error'
    default:
      return 'default'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'PENDING':
      return '待审核'
    case 'APPROVED':
      return '已通过'
    case 'REJECTED':
      return '已拒绝'
    default:
      return status
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

const getFileUrl = (filePath) => {
  if (!filePath) return ''
  if (filePath.startsWith('http')) return filePath
  return `http://localhost:8000${filePath}`
}

const isImage = (filePath) => {
  if (!filePath) return false
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
  const lowerPath = filePath.toLowerCase()
  return imageExtensions.some(ext => lowerPath.includes(ext))
}

onMounted(() => {
  fetchApplications()
})
</script>

<style scoped>
.admin-verification-container {
  max-width: 1200px;
  margin: 24px auto;
  padding: 0 20px;
}

.verification-card {
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

.application-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.application-item {
  transition: all 0.3s ease;
}

.application-item:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.application-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.application-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.application-type {
  font-weight: 600;
  color: #333;
}

.application-user {
  color: #666;
}

.application-time {
  color: #999;
  font-size: 14px;
}

.file-section {
  margin-top: 16px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 8px;
}

.file-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #333;
}

.file-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #10b981;
  text-decoration: none;
  padding: 8px 16px;
  background: white;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.file-link:hover {
  background: #e0f2f1;
}

.other-files {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.other-file-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.reject-reason {
  margin-top: 16px;
  padding: 12px;
  background: #fef2f2;
  border-left: 3px solid #ef4444;
  border-radius: 4px;
}

.reject-reason h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #ef4444;
}

.reject-reason p {
  margin: 0;
  color: #666;
  font-size: 14px;
}
</style>
