<template>
  <div class="enterprise-edit-page">
    <n-card title="完善企业信息" class="edit-card">
      <n-form 
        ref="formRef" 
        :model="formData" 
        :rules="rules"
        label-placement="top"
      >
        <div class="form-grid">
          <!-- 企业基本信息区域 -->
          <div class="form-section">
            <h3 class="section-title">企业基本信息</h3>
            
            <div class="form-row">
              <div class="form-col">
                <n-form-item path="name" label="企业名称">
                  <n-input 
                    v-model:value="formData.name" 
                    placeholder="请输入企业名称"
                    class="form-input"
                  />
                </n-form-item>
              </div>
            </div>

            <div class="form-row">
              <div class="form-col">
                <n-form-item path="logo" label="企业Logo">
                  <div class="logo-upload-section">
                    <n-upload
                      :default-file-list="fileList"
                      @change="handleFileChange"
                      :max-count="1" 
                      type="select" 
                    >
                      <n-button type="primary" class="upload-btn">选择图片</n-button>
                    </n-upload>
                    
                    <div class="logo-preview-container" v-if="formData.logo || previewLogoUrl">
                      <n-image 
                        :src="previewLogoUrl || formData.logo" 
                        class="logo-preview"
                      />
                      <div class="logo-hint">
                        {{ previewLogoUrl ? '新选择Logo预览' : '当前Logo预览' }}
                      </div>
                    </div>
                  </div>
                </n-form-item>
              </div>
            </div>

            <div class="form-row">
              <div class="form-col">
                <n-form-item path="description" label="企业简介">
                  <n-input 
                    v-model:value="formData.description" 
                    type="textarea"
                    rows="4"
                    placeholder="请输入企业简介"
                    class="form-input"
                  />
                </n-form-item>
              </div>
            </div>

            <div class="form-row">
              <div class="form-col">
                <n-form-item path="industry" label="所属行业">
                  <n-select 
                    v-model:value="formData.industry" 
                    :options="industryOptions"
                    placeholder="请选择所属行业"
                    class="form-input"
                  />
                </n-form-item>
              </div>
              
              <div class="form-col">
                <n-form-item path="scale" label="企业规模">
                  <n-select 
                    v-model:value="formData.scale" 
                    :options="scaleOptions"
                    placeholder="请选择企业规模"
                    class="form-input"
                  />
                </n-form-item>
              </div>
            </div>

            <div class="form-row">
              <div class="form-col">
                <n-form-item path="website" label="企业官网">
                  <n-input 
                    v-model:value="formData.website" 
                    placeholder="请输入企业官网链接"
                    class="form-input"
                  />
                </n-form-item>
              </div>
            </div>
          </div>

          <!-- 联系方式区域 -->
          <div class="form-section">
            <h3 class="section-title">联系方式</h3>
            
            <div class="form-row">
              <div class="form-col">
                <n-form-item path="contact_person" label="联系人">
                  <n-input 
                    v-model:value="formData.contact_person" 
                    placeholder="请输入联系人姓名"
                    class="form-input"
                  />
                </n-form-item>
              </div>
              
              <div class="form-col">
                <n-form-item path="contact_phone" label="联系电话">
                  <n-input 
                    v-model:value="formData.contact_phone" 
                    placeholder="请输入联系电话"
                    class="form-input"
                  />
                </n-form-item>
              </div>
            </div>

            <div class="form-row">
              <div class="form-col">
                <n-form-item path="contact_email" label="联系邮箱">
                  <n-input 
                    v-model:value="formData.contact_email" 
                    placeholder="请输入联系邮箱"
                    class="form-input"
                  />
                </n-form-item>
              </div>
            </div>

            <div class="form-row">
              <div class="form-col">
                <n-form-item path="address" label="企业地址">
                  <n-input 
                    v-model:value="formData.address" 
                    placeholder="请输入企业地址"
                    class="form-input"
                  />
                </n-form-item>
              </div>
            </div>
          </div>
        </div>

        <div class="form-actions">
          <n-button 
            type="primary" 
            @click="handleSubmit"
            :loading="loading"
            size="large"
            class="submit-btn"
          >
            保存信息
          </n-button>
        </div>
      </n-form>
    </n-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, NForm, NFormItem, NInput, NButton, NCard, NUpload, NImage, NSelect } from 'naive-ui'
import axios from '@/utils/axios'

const message = useMessage();
const formData = ref({
  id: null,
  name: '',
  logo: '',
  description: '',
  industry: 'OTHER',
  scale: 'SMALL',
  website: '',
  contact_person: '',
  contact_phone: '',
  contact_email: '',
  address: ''
})

const fileList = ref([])
// 实时预览URL
const previewLogoUrl = ref('')
const formRef = ref(null)
const loading = ref(false)
const router = useRouter()

const rules = {
  name: [
    { required: true, message: '请输入企业名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入企业简介', trigger: 'blur' }
  ],
  industry: [
    { required: true, message: '请选择所属行业', trigger: 'change' }
  ],
  scale: [
    { required: true, message: '请选择企业规模', trigger: 'change' }
  ],
  website: [
    { type: 'url', message: '请输入正确的网址格式', trigger: 'blur' }
  ],
  contact_person: [
    { required: true, message: '请输入联系人', trigger: 'blur' }
  ],
  contact_phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { 
      pattern: /^[\d\-\+\s\(\)]{7,20}$/, 
      message: '请输入有效的电话号码', 
      trigger: 'blur' 
    }
  ],
  contact_email: [
    { required: true, message: '请输入联系邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  address: [
    { required: true, message: '请输入企业地址', trigger: 'blur' }
  ]
}

// 获取企业信息
const fetchEnterpriseInfo = async () => {
  try {
    const response = await axios.get('/enterprises/')
    // 确保获取到的是单个对象而非数组
    if (Array.isArray(response.data) && response.data.length > 0) {
      formData.value = response.data[0]  // 取数组第一个元素
    } else if (typeof response.data === 'object') {
      formData.value = response.data  // 直接使用对象
    } else {
      // 初始化空对象
      formData.value = {
        id: null,
        name: '',
        logo: '',
        description: '',
        industry: 'OTHER',
        scale: 'SMALL',
        website: '',
        contact_person: '',
        contact_phone: '',
        contact_email: '',
        address: ''
      }
    }
    if (formData.value.logo) {
    fileList.value = [{
      id: 'logo',
      name: 'logo.png',
      url: formData.value.logo
    }]
    
    // 设置初始化预览URL
    previewLogoUrl.value = formData.value.logo;
    console.log('初始化Logo预览URL:', previewLogoUrl.value);
  }
  } catch (error) {
    console.error('获取企业信息失败:', error)
  }
}


const industryOptions = [
  { label: '信息技术', value: 'IT' },
  { label: '金融', value: 'FINANCE' },
  { label: '教育', value: 'EDUCATION' },
  { label: '传媒', value: 'MEDIA' },
  { label: '制造业', value: 'MANUFACTURING' },
  { label: '服务业', value: 'SERVICE' },
  { label: '其他', value: 'OTHER' }
]

const scaleOptions = [
  { label: '微型企业（<10人）', value: 'MICRO' },
  { label: '小型企业（10-99人）', value: 'SMALL' },
  { label: '中型企业（100-999人）', value: 'MEDIUM' },
  { label: '大型企业（1000人以上）', value: 'LARGE' }
]

// 处理文件上传
// 提交表单 - 简化版
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    // 1. 先保存基本信息
    const submitData = { ...formData.value }
    delete submitData.logo

    let response;
    if (submitData.id) {
      response = await axios.put(`/enterprises/${submitData.id}/`, submitData)
    } else {
      response = await axios.post('/enterprises/', submitData)
      formData.value.id = response.data.id
    }
    
    // 2. 如果有logo文件，上传logo
    if (fileList.value.length > 0 && fileList.value[0].file) {
      console.log('检测到logo文件，开始上传...');
      const uploadFormData = new FormData();
      uploadFormData.append('logo', fileList.value[0].file);
      
      const uploadResponse = await axios.post(
        `/enterprises/${formData.value.id}/upload_logo/`, 
        uploadFormData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      
      formData.value.logo = uploadResponse.data.logo_url;
      console.log('Logo上传成功，URL:', uploadResponse.data.logo_url);
    }
    
    message.success('企业信息保存成功！')
    
    // 更新本地存储的企业信息
    const enterpriseInfo = {
      id: formData.value.id,
      name: formData.value.name,
      logo: formData.value.logo,
      avatar: formData.value.logo, // 保持兼容性
      industry: formData.value.industry,
      scale: formData.value.scale,
      website: formData.value.website
    }
    localStorage.setItem('enterpriseInfo', JSON.stringify(enterpriseInfo))
    
    router.push('/enterprise/home')
    
  } catch (error) {
    console.error('保存失败:', error)
    message.error('保存失败，请检查信息')
  } finally {
    loading.value = false
  }
}

// 处理文件上传并添加实时预览
const handleFileChange = (data) => {
  // 只保留最新选择的一个文件
  fileList.value = data.fileList.slice(-1); // 只取最后一个文件
  
  // 如果有新文件，生成预览
  if (fileList.value.length > 0 && fileList.value[0].file) {
    const file = fileList.value[0].file;
    
    // 验证文件类型和大小
    const isValid = validateLogoFile(file);
    if (!isValid) {
      fileList.value = [];
      previewLogoUrl.value = '';
      return;
    }
    
    // 使用FileReader生成预览
    const reader = new FileReader();
    reader.onload = (e) => {
      previewLogoUrl.value = e.target.result;
      console.log('Logo预览生成:', previewLogoUrl.value);
    };
    reader.readAsDataURL(file);
  } else {
    // 没有文件，清空预览
    previewLogoUrl.value = '';
  }
};

// 校验Logo文件
const validateLogoFile = (file) => {
  // 检查文件类型
  const validTypes = ['image/jpeg', 'image/png'];
  if (!validTypes.includes(file.type)) {
    message.error('只支持JPG和PNG格式的图片');
    return false;
  }
  
  // 检查文件大小 (2MB)
  const maxSize = 2 * 1024 * 1024;
  if (file.size > maxSize) {
    message.error('图片大小不能超过2MB');
    return false;
  }
  
  return true;
};

onMounted(() => {
  fetchEnterpriseInfo()
})
</script>

<style scoped>
.enterprise-edit-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.edit-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 30px;
}

.form-section {
  background: #fafafa;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #1890ff;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 20px 0;
  color: #333;
  padding-bottom: 8px;
  border-bottom: 1px solid #e8e8e8;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.form-col {
  width: 100%;
}

.form-input {
  width: 100%;
  border-radius: 4px;
}

.logo-upload-section {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 15px;
}

.logo-preview-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 15px;
  padding: 15px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.logo-preview {
  width: 120px !important;
  height: 120px !important;
  object-fit: contain !important;
  border-radius: 4px !important;
  max-width: 120px !important;
  max-height: 120px !important;
  min-width: 120px !important;
  min-height: 120px !important;
  display: block !important;
}

/* 强制n-image容器也使用相同的尺寸 */
.logo-preview-container :deep(.n-image) {
  width: 120px !important;
  height: 120px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.logo-preview-container :deep(.n-image img) {
  width: 100% !important;
  height: 100% !important;
  object-fit: contain !important;
}

.logo-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #999;
}

.upload-btn {
  border-radius: 4px;
}

.form-actions {
  display: flex;
  justify-content: center;
  padding: 20px 0;
  margin-top: 20px;
  border-top: 1px solid #e8e8e8;
}

.submit-btn {
  border-radius: 4px;
  min-width: 120px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .logo-upload-section {
    align-items: stretch;
  }
  
  .upload-btn {
    width: 100%;
  }
  
  .logo-preview {
    width: 100px;
    height: 100px;
  }
}
</style>