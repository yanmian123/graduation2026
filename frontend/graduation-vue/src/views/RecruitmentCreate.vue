<template>
  <div class="recruitment-create-page">
    <n-card title="发布招聘信息">
      <n-form 
        ref="formRef" 
        :model="formData" 
        :rules="rules"
        label-placement="top"
      >
        <n-form-item path="title" label="招聘标题">
          <n-input 
            v-model:value="formData.title" 
            placeholder="请输入招聘标题"
          />
        </n-form-item>

        <n-form-item path="job" label="职位名称">
          <n-input 
            v-model:value="formData.job" 
            placeholder="请输入职位名称"
          />
        </n-form-item>

        <n-form-item path="work_location" label="工作地点">
          <n-input 
            v-model:value="formData.work_location" 
            placeholder="请输入工作地点"
          />
        </n-form-item>

        <n-form-item path="salary" label="薪资范围">
          <n-input 
            v-model:value="formData.salary" 
            placeholder="如：10k-20k/月"
          />
        </n-form-item>

        <n-form-item path="experience" label="工作经验要求">
          <n-input 
            v-model:value="formData.experience" 
            placeholder="如：3-5年"
          />
        </n-form-item>

        <n-form-item path="education" label="学历要求">
          <n-input 
            v-model:value="formData.education" 
            placeholder="如：本科及以上"
          />
        </n-form-item>

        <n-form-item path="job_desc" label="职位描述">
          <n-input 
            v-model:value="formData.job_desc" 
            type="textarea"
            rows="6"
            placeholder="请输入职位描述（岗位职责）"
          />
        </n-form-item>

        <n-form-item path="job_require" label="任职要求">
          <n-input 
            v-model:value="formData.job_require" 
            type="textarea"
            rows="6"
            placeholder="请输入任职要求"
          />
        </n-form-item>

        <n-form-item>
          <n-checkbox v-model:checked="formData.is_published">
            立即发布
          </n-checkbox>
        </n-form-item>

        <n-form-item>
          <n-button 
            type="primary" 
            @click="handleSubmit"
            :loading="loading"
          >
            保存招聘信息
          </n-button>
          <n-button 
            style="margin-left: 10px;"
            @click="router.back()"
          >
            取消
          </n-button>
        </n-form-item>
      </n-form>
    </n-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NForm, NFormItem, NInput, NButton, NCard, NCheckbox } from 'naive-ui'
import axios from '@/utils/axios'

const formData = ref({
  title: '',
  job: '',
  work_location: '',
  salary: '',
  experience: '',
  education: '',
  job_desc: '',
  job_require: '',
  is_published: true
})

const formRef = ref(null)
const loading = ref(false)
const router = useRouter()

const rules = {
  title: [
    { required: true, message: '请输入招聘标题', trigger: 'blur' }
  ],
  job: [
    { required: true, message: '请输入职位名称', trigger: 'blur' }
  ],
  work_location: [
    { required: true, message: '请输入工作地点', trigger: 'blur' }
  ],
  salary: [
    { required: true, message: '请输入薪资范围', trigger: 'blur' }
  ],
  experience: [
    { required: true, message: '请输入工作经验要求', trigger: 'blur' }
  ],
  education: [
    { required: true, message: '请输入学历要求', trigger: 'blur' }
  ],
  job_desc: [
    { required: true, message: '请输入职位描述', trigger: 'blur' }
  ],
  job_require: [
    { required: true, message: '请输入任职要求', trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    // 创建招聘信息
    await axios.post('/api/recruitments/', formData.value)
    
    router.push('/enterprise/recruitments')
  } catch (error) {
    console.error('发布招聘信息失败:', error)
    if (error.response && error.response.data.detail === '请先完善企业信息才能发布招聘') {
      // 如果提示需要完善企业信息，跳转到企业信息编辑页
      router.push('/enterprise/edit')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.recruitment-create-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}
</style>