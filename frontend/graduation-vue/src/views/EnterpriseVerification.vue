<template>
  <div class="verification-container">
    <n-card class="verification-card" title="企业实名认证">
      <n-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-placement="left"
        label-width="120px"
      >
        <n-form-item label="认证类型" path="verification_type">
          <n-radio-group v-model:value="formData.verification_type" name="verification_type">
            <n-radio value="ENTERPRISE">企业认证</n-radio>
          </n-radio-group>
        </n-form-item>

        <n-form-item label="真实姓名" path="name">
          <n-input v-model:value="formData.name" placeholder="请输入真实姓名" />
        </n-form-item>

        <n-form-item label="身份证号" path="id_number">
          <n-input v-model:value="formData.id_number" placeholder="请输入身份证号" maxlength="18" />
        </n-form-item>

        <n-form-item label="联系电话" path="phone">
          <n-input v-model:value="formData.phone" placeholder="请输入联系电话" />
        </n-form-item>

        <n-form-item label="营业执照" path="business_license" required>
          <n-upload
            v-model:file-list="businessLicenseList"
            :max="1"
            accept=".jpg,.jpeg,.png,.pdf"
            :custom-request="handleUpload"
            @change="handleBusinessLicenseChange"
          >
            <n-button>选择文件</n-button>
            <template #tip>
              请上传营业执照图片或PDF文件
            </template>
          </n-upload>
        </n-form-item>

        <n-form-item>
          <template #label>
            <span>其他证明文件</span>
            <n-tooltip trigger="hover" placement="right">
              <template #trigger>
                <n-icon size="16" color="#999">
                  <HelpCircle />
                </n-icon>
              </template>
              可选上传其他证明材料，如组织机构代码证等
            </n-tooltip>
          </template>
          <n-upload
            v-model:file-list="otherFilesList"
            :max="5"
            accept=".jpg,.jpeg,.png,.pdf"
            multiple
            :custom-request="handleUpload"
            @change="handleOtherFilesChange"
          >
            <n-button>选择文件</n-button>
            <template #tip>
              最多上传5个文件，支持jpg、png、pdf格式
            </template>
          </n-upload>
        </n-form-item>

        <n-form-item :show-label="false">
          <n-space>
            <n-button type="primary" @click="handleSubmit" :loading="loading">
              提交认证
            </n-button>
            <n-button @click="handleReset">
              重置
            </n-button>
          </n-space>
        </n-form-item>
      </n-form>
    </n-card>

    <n-card v-if="application" class="status-card" title="认证状态">
      <n-descriptions bordered :column="1">
        <n-descriptions-item label="认证类型">
          {{ application.verification_type === 'ENTERPRISE' ? '企业认证' : '个人认证' }}
        </n-descriptions-item>
        <n-descriptions-item label="审核状态">
          <n-tag
            :type="getStatusType(application.status)"
            round
          >
            {{ getStatusText(application.status) }}
          </n-tag>
        </n-descriptions-item>
        <n-descriptions-item v-if="application.reject_reason" label="拒绝原因">
          {{ application.reject_reason }}
        </n-descriptions-item>
        <n-descriptions-item label="提交时间">
          {{ formatTime(application.created_at) }}
        </n-descriptions-item>
        <n-descriptions-item v-if="application.reviewed_at" label="审核时间">
          {{ formatTime(application.reviewed_at) }}
        </n-descriptions-item>
      </n-descriptions>
    </n-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, NCard, NForm, NFormItem, NInput, NButton, NSpace, NUpload, NRadioGroup, NRadio, NDescriptions, NDescriptionsItem, NTag, NTooltip, NIcon } from 'naive-ui'
import { HelpCircle } from '@vicons/ionicons5'
import axios from '@/utils/axios'

const router = useRouter()
const message = useMessage()

const formRef = ref(null)
const loading = ref(false)
const application = ref(null)
const businessLicenseList = ref([])
const otherFilesList = ref([])

const formData = ref({
  verification_type: 'ENTERPRISE',
  name: '',
  id_number: '',
  phone: '',
  business_license: null,
  other_files: []
})

const rules = {
  name: { required: true, message: '请输入真实姓名', trigger: 'blur' },
  id_number: { required: true, message: '请输入身份证号', trigger: 'blur' },
  phone: { required: true, message: '请输入联系电话', trigger: 'blur' }
}

const handleUpload = ({ file, onError, onFinish }) => {
  const formData = new FormData()
  formData.append('file', file.file)
  
  axios.post('/user/upload/file/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
    .then(response => {
      file.url = response.data.url
      onFinish()
    })
    .catch(error => {
      onError(error)
      message.error('文件上传失败')
    })
}

const handleBusinessLicenseChange = (options) => {
  if (options.fileList && options.fileList.length > 0) {
    formData.value.business_license = options.fileList[0].url
  }
}

const handleOtherFilesChange = (options) => {
  if (options.fileList) {
    formData.value.other_files = options.fileList.map(file => file.url)
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    
    if (application.value && application.value.status === 'PENDING') {
      message.warning('您已有待审核的认证申请，请等待管理员审核')
      return
    }
    
    if (!formData.value.business_license) {
      message.error('请上传营业执照')
      return
    }
    
    loading.value = true
    
    const submitData = {
      verification_type: formData.value.verification_type,
      name: formData.value.name,
      id_number: formData.value.id_number,
      phone: formData.value.phone,
      business_license: formData.value.business_license,
      other_files: formData.value.other_files || []
    }
    
    console.log('提交的数据:', submitData)
    
    await axios.post('/user/verifications/', submitData)
    
    message.success('认证申请已提交，请等待管理员审核')
    await fetchApplication()
  } catch (error) {
    console.error('提交认证申请失败:', error)
    console.error('错误详情:', error.response?.data)
    message.error(error.response?.data?.error || '提交失败，请重试')
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  formRef.value?.restoreValidation()
  formData.value = {
    verification_type: 'ENTERPRISE',
    name: '',
    id_number: '',
    phone: '',
    business_license: null,
    other_files: []
  }
  businessLicenseList.value = []
  otherFilesList.value = []
}

const fetchApplication = async () => {
  try {
    const response = await axios.get('/user/verifications/my_application/')
    if (response.data) {
      application.value = response.data
    }
  } catch (error) {
    console.error('获取认证申请失败:', error)
    if (error.response?.status === 401) {
      message.warning('请先登录系统')
    } else if (error.response?.status === 404) {
      message.warning('暂无认证申请')
    } else {
      message.error('获取认证申请失败，请稍后重试')
    }
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

onMounted(() => {
  fetchApplication()
})
</script>

<style scoped>
.verification-container {
  max-width: 800px;
  margin: 24px auto;
  padding: 0 20px;
}

.verification-card,
.status-card {
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
</style>
