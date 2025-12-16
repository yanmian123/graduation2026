<template>
  <div class="enterprise-edit-page">
    <n-card title="完善企业信息">
      <n-form 
        ref="formRef" 
        :model="formData" 
        :rules="rules"
        label-placement="top"
      >
        <n-form-item path="name" label="企业名称">
          <n-input 
            v-model:value="formData.name" 
            placeholder="请输入企业名称"
          />
        </n-form-item>

        <n-form-item path="logo" label="企业Logo">
          <n-upload
            :default-file-list="fileList"
            @change="handleFileChange"
            :max-count="1" 
            type="select" 
          >
            <n-button>选择图片</n-button>
          </n-upload>
          <n-image 
            v-if="formData.logo" 
            :src="formData.logo" 
            style="max-width: 200px; margin-top: 10px;"
          />
        </n-form-item>

        <n-form-item path="description" label="企业简介">
          <n-input 
            v-model:value="formData.description" 
            type="textarea"
            rows="4"
            placeholder="请输入企业简介"
          />
        </n-form-item>

        <n-form-item path="contact_person" label="联系人">
          <n-input 
            v-model:value="formData.contact_person" 
            placeholder="请输入联系人姓名"
          />
        </n-form-item>

        <n-form-item path="contact_phone" label="联系电话">
          <n-input 
            v-model:value="formData.contact_phone" 
            placeholder="请输入联系电话"
          />
        </n-form-item>

        <n-form-item path="contact_email" label="联系邮箱">
          <n-input 
            v-model:value="formData.contact_email" 
            placeholder="请输入联系邮箱"
          />
        </n-form-item>

        <n-form-item path="address" label="企业地址">
          <n-input 
            v-model:value="formData.address" 
            placeholder="请输入企业地址"
          />
        </n-form-item>

        <n-form-item>
          <n-button 
            type="primary" 
            @click="handleSubmit"
            :loading="loading"
          >
            保存信息
          </n-button>
        </n-form-item>
      </n-form>
    </n-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage,NForm, NFormItem, NInput, NButton, NCard, NUpload, NImage } from 'naive-ui'
import axios from '@/utils/axios'

const formData = ref({
  id: null,
  name: '',
  logo: '',
  description: '',
  contact_person: '',
  contact_phone: '',
  contact_email: '',
  address: ''
})

const fileList = ref([])
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
  contact_person: [
    { required: true, message: '请输入联系人', trigger: 'blur' }
  ],
  contact_phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' }
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
    }
  } catch (error) {
    console.error('获取企业信息失败:', error)
  }
}

const message = useMessage();
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
    router.push('/enterprise/home')
    
  } catch (error) {
    console.error('保存失败:', error)
    message.error('保存失败，请检查信息')
  } finally {
    loading.value = false
  }
}

// 简化handleFileChange，只更新文件列表
const handleFileChange = (data) => {
  fileList.value = data.fileList;
};

onMounted(() => {
  fetchEnterpriseInfo()
})
</script>

<style scoped>
.enterprise-edit-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}
</style>