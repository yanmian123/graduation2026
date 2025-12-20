<template>
  <n-modal 
    v-model:show="showModal" 
    :mask-closable="true"
    :on-after-leave="handleAfterLeave"
    preset="card"
    style="width: 90%; max-width: 650px;"
    title="选择投递简历"
    size="huge"
    :bordered="false"
    class="resume-select-modal"
    :on-close="handleClose"
  >
    <template #header>
      <div class="modal-header">
        <div class="header-content">
          <n-icon size="24" color="#1890ff" class="header-icon">
            <DocumentTextOutline />
          </n-icon>
          <span class="header-title">选择投递简历</span>
        </div>
        <n-button quaternary circle @click="closeModal" class="close-button">
          <template #icon>
            <n-icon size="20"><CloseOutline /></n-icon>
          </template>
        </n-button>
      </div>
    </template>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <n-spin size="large" description="加载中...">
        <template #icon>
          <n-icon size="30" color="#1890ff">
            <SyncOutline />
          </n-icon>
        </template>
      </n-spin>
    </div>

    <!-- 简历列表 -->
    <div v-else-if="resumes.length > 0" class="resume-content">
      <div class="selection-info">
        <n-alert type="info" :bordered="false" class="info-alert">
          <template #icon>
            <n-icon><InformationCircleOutline /></n-icon>
          </template>
          请选择一份简历进行投递，已选择: 
          <strong v-if="selectedResume">{{ getSelectedResumeName() }}</strong>
          <span v-else class="no-selection">暂未选择</span>
        </n-alert>
      </div>
      
      <div class="resume-list">
        <n-radio-group v-model:value="selectedResumeId" class="resume-radio-group">
          <n-space vertical :size="12">
            <n-card
              v-for="resume in resumes"
              :key="resume.id"
              :class="['resume-card', selectedResumeId === resume.id ? 'selected' : '']"
              @click="selectedResumeId = resume.id"
              content-style="padding: 20px;"
              hoverable
            >
              <div class="resume-info">
                <div class="resume-radio-section">
                  <n-radio :value="resume.id" class="resume-radio" />
                  <div class="selection-indicator" v-if="selectedResumeId === resume.id">
                    <n-icon size="16" color="#1890ff">
                      <CheckmarkCircleOutline />
                    </n-icon>
                  </div>
                </div>
                
                <div class="resume-details">
                  <div class="resume-header">
                    <h4 class="resume-title">{{ resume.name }}</h4>
                    <n-tag v-if="resume.is_default" type="primary" size="small" round>
                      默认简历
                    </n-tag>
                  </div>
                  
                  <p class="resume-objective">{{ resume.job_objective }}</p>
                  
                  <div class="resume-meta">
                    <div class="meta-item">
                      <n-icon size="14" color="#8c8c8c"><SchoolOutline /></n-icon>
                      <span>{{ resume.education }}</span>
                    </div>
                    <div class="meta-item">
                      <n-icon size="14" color="#8c8c8c"><BriefcaseOutline /></n-icon>
                      <span>{{ resume.work_experience }}</span>
                    </div>
                  </div>
                  
                  <p class="update-time">
                    <n-icon size="12" color="#bfbfbf"><TimeOutline /></n-icon>
                    最后更新: {{ formatDate(resume.updated_at) }}
                  </p>
                </div>
                
                <div class="resume-actions">
                  <n-button 
                    size="tiny" 
                    quaternary 
                    @click.stop="previewResume(resume.id)"
                    class="preview-btn"
                  >
                    预览
                  </n-button>
                </div>
              </div>
            </n-card>
          </n-space>
        </n-radio-group>
      </div>
    </div>

    <!-- 无简历提示 -->
    <div v-else class="no-resume">
      <n-result status="404" title="暂无可用简历" description="您还没有创建任何简历，请先创建简历后再进行投递">
        <template #icon>
          <n-icon size="80" color="#d9d9d9">
            <DocumentTextOutline />
          </n-icon>
        </template>
        <template #footer>
          <n-space vertical>
            <n-button type="primary" @click="goToCreateResume" size="large" class="create-btn">
              <template #icon>
                <n-icon><AddOutline /></n-icon>
              </template>
              立即创建简历
            </n-button>
            <n-button @click="closeModal" size="medium" type="tertiary">
              稍后创建
            </n-button>
          </n-space>
        </template>
      </n-result>
    </div>

    <!-- 底部操作区域 -->
    <template #footer v-if="resumes.length > 0">
      <div class="modal-footer">
        <div class="footer-actions">
          <n-button 
            @click="closeModal" 
            size="large" 
            class="cancel-btn"
            :disabled="submitting"
          >
            <template #icon>
              <n-icon><CloseOutline /></n-icon>
            </template>
            关闭
          </n-button>
          
          <div class="primary-actions">
            <n-button 
              type="primary" 
              :disabled="!selectedResumeId"
              :loading="submitting"
              @click="handleSubmit"
              size="large"
              class="submit-btn"
            >
              <template #icon>
                <n-icon><PaperPlaneOutline /></n-icon>
              </template>
              sadasdad
              {{ submitting ? '投递中...' : `确认投递${selectedResume ? ' - ' + getSelectedResumeName() : ''}` }}
            </n-button>
          </div>
        </div>
        
        <!-- 选择状态提示 -->
        <div v-if="selectedResume" class="selection-confirm">
          <n-text depth="3" class="confirm-text">
            即将投递简历: <strong>{{ selectedResume.name }}</strong>
          </n-text>
        </div>
      </div>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import {
  NModal,
  NAlert,
  NRadio,
  NRadioGroup,
  NText,
  // ... 其他组件
} from 'naive-ui'
import { 
  CloseOutline, 
  DocumentTextOutline,
  CheckmarkCircleOutline,
  PaperPlaneOutline,
  SyncOutline,
  InformationCircleOutline,
  SchoolOutline,
  BriefcaseOutline,
  TimeOutline,
  AddOutline
} from '@vicons/ionicons5'
import axios from '@/utils/axios'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  jobId: {
    type: [Number, String],
    required: true
  }
})

const emit = defineEmits(['update:show', 'success'])

const router = useRouter()
const message = useMessage()
const showModal = ref(false)
const resumes = ref([])
const selectedResumeId = ref(null)
const submitting = ref(false)
const loading = ref(false)

// 计算属性
const selectedResume = computed(() => {
  return resumes.value.find(resume => resume.id === selectedResumeId.value) || null
})

// 获取用户简历列表
const fetchResumes = async () => {
  loading.value = true
  try {
    const response = await axios.get('/resumes/')
    resumes.value = response.data
    
    // 如果有默认简历，自动选择
    const defaultResume = resumes.value.find(r => r.is_default)
    if (defaultResume) {
      selectedResumeId.value = defaultResume.id
    }
  } catch (error) {
    console.error('获取简历列表失败:', error)
    message.error('获取简历列表失败')
    resumes.value = []
  } finally {
    loading.value = false
  }
}

// 格式化日期
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 获取选中简历名称
const getSelectedResumeName = () => {
  return selectedResume.value ? selectedResume.value.name : ''
}

// 预览简历
const previewResume = (resumeId) => {
  // 在新标签页打开简历预览
  window.open(`/resumes/preview/${resumeId}`, '_blank')
}

// 跳转到创建简历页面
const goToCreateResume = () => {
  closeModal()
  router.push('/resumes/create')
}

// 关闭模态框
const closeModal = () => {
  showModal.value = false
}

// 处理模态框关闭
const handleClose = () => {
  if (submitting.value) {
    message.warning('正在投递中，请稍候...')
    return false // 阻止关闭
  }
  return true
}

// 处理模态框关闭后的清理
const handleAfterLeave = () => {
  selectedResumeId.value = null
  resumes.value = []
  loading.value = false
  submitting.value = false
}

// 处理投递
const handleSubmit = async () => {
  if (!selectedResumeId.value) {
    message.warning('请选择要投递的简历')
    return
  }

  submitting.value = true
  try {
    await axios.post(`/recruitments/${props.jobId}/apply/`, {
      resume_id: selectedResumeId.value
    })
    
    message.success('简历投递成功！')
    emit('success')
    closeModal()
  } catch (error) {
    console.error('投递失败:', error)
    const errorMsg = error.response?.data?.error || '投递失败，请重试'
    message.error(errorMsg)
  } finally {
    submitting.value = false
  }
}

// 监听show属性变化
watch(() => props.show, (newVal) => {
  showModal.value = newVal
  if (newVal) {
    fetchResumes()
  }
})

// 监听内部showModal变化，同步到父组件
watch(showModal, (newVal) => {
  emit('update:show', newVal)
})
</script>

<style scoped>
.resume-select-modal {
  border-radius: 12px;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  display: flex;
  align-items: center;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.close-button {
  color: #6b7280;
  transition: all 0.3s ease;
}

.close-button:hover {
  color: #374151;
  background-color: #f3f4f6;
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  flex-direction: column;
  gap: 16px;
}

.resume-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.selection-info {
  margin-bottom: 8px;
}

.info-alert {
  border-radius: 8px;
}

.no-selection {
  color: #f59e0b;
  font-style: italic;
}

.resume-list {
  max-height: 400px;
  overflow-y: auto;
  padding: 4px 8px 4px 4px;
}

.resume-radio-group {
  width: 100%;
}

.resume-card {
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  position: relative;
}

.resume-card:hover {
  border-color: #3b82f6;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.resume-card.selected {
  border-color: #3b82f6;
  background: linear-gradient(135deg, #f0f7ff 0%, #f8faff 100%);
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.15);
}

.resume-info {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.resume-radio-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding-top: 4px;
}

.selection-indicator {
  animation: bounceIn 0.5s ease;
}

@keyframes bounceIn {
  0% { transform: scale(0.8); opacity: 0; }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); opacity: 1; }
}

.resume-details {
  flex: 1;
  min-width: 0;
}

.resume-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.resume-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.4;
}

.resume-objective {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #4b5563;
  line-height: 1.5;
}

.resume-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #6b7280;
}

.update-time {
  margin: 0;
  font-size: 12px;
  color: #9ca3af;
  display: flex;
  align-items: center;
  gap: 4px;
}

.resume-actions {
  display: flex;
  align-items: flex-start;
}

.preview-btn {
  font-size: 12px;
}

.modal-footer {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #f3f4f6;
}

.footer-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.primary-actions {
  display: flex;
  gap: 12px;
}

.cancel-btn {
  min-width: 100px;
  color: #6b7280;
}

.submit-btn {
  min-width: 180px;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
  transition: all 0.3s ease;
}

.submit-btn:hover:not(.n-button--disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.selection-confirm {
  text-align: center;
  padding: 8px;
  background-color: #f8fafc;
  border-radius: 6px;
  border-left: 3px solid #3b82f6;
}

.confirm-text {
  font-size: 13px;
}

.no-resume {
  text-align: center;
  padding: 40px 20px;
}

.create-btn {
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

/* 滚动条样式 */
.resume-list::-webkit-scrollbar {
  width: 6px;
}

.resume-list::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.resume-list::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.resume-list::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

@media (max-width: 768px) {
  .resume-select-modal {
    width: 95%;
    margin: 20px;
  }
  
  .footer-actions {
    flex-direction: column-reverse;
  }
  
  .primary-actions {
    width: 100%;
  }
  
  .cancel-btn, .submit-btn {
    width: 100%;
  }
  
  .resume-info {
    flex-direction: column;
    gap: 12px;
  }
  
  .resume-actions {
    align-self: flex-end;
  }
}
</style>