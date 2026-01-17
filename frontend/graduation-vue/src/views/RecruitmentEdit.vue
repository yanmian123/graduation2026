<template>
  <div class="recruitment-edit-page">
    <n-card title="编辑招聘信息">
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

        <n-form-item path="job" label="岗位名称">
          <n-input 
            v-model:value="formData.job" 
            placeholder="请输入岗位名称，如“软件工程师”"
          />
        </n-form-item>

        <n-form-item path="job_type" label="工作类型">
          <n-select 
            v-model:value="formData.job_type" 
            :options="jobTypes"
            placeholder="请选择工作类型"
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
          <n-select 
            v-model:value="formData.experience" 
            :options="experienceOptions"
            placeholder="请选择工作经验要求"
          />
        </n-form-item>

        <n-form-item path="education" label="学历要求">
          <n-select 
            v-model:value="formData.education" 
            :options="educationOptions"
            placeholder="请选择学历要求"
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
            更新招聘信息
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
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NForm, NFormItem, NInput, NButton, NCard, NCheckbox, useMessage } from 'naive-ui'
import axios from '@/utils/axios'

// 经验选项（与后端模型一致）
const experienceOptions = [
  { label: '应届毕业生', value: 'FRESH' },
  { label: '1年以内', value: 'LESS_THAN_1' },
  { label: '1-3年', value: '1_3' },
  { label: '3-5年', value: '3_5' },
  { label: '5-10年', value: '5_10' },
  { label: '10年以上', value: 'MORE_THAN_10' }
]

// 学历选项（与后端模型一致）
const educationOptions = [
  { label: '高中及以下', value: 'HIGH_SCHOOL' },
  { label: '专科', value: 'ASSOCIATE' },
  { label: '本科', value: 'BACHELOR' },
  { label: '硕士', value: 'MASTER' },
  { label: '博士及以上', value: 'DOCTOR' }
]

const jobTypes = [
  { label: '全职', value: 'FULL_TIME' },
  { label: '兼职', value: 'PART_TIME' },
  { label: '实习', value: 'INTERNSHIP' }
]

const formData = ref({
  title: '',
  job: '',
  job_type: 'FULL_TIME',
  work_location: '',
  salary: '',
  experience: 'FRESH',
  education: 'HIGH_SCHOOL',
  job_desc: '',
  job_require: '',
  is_published: true
})

const formRef = ref(null)
const loading = ref(false)
const router = useRouter()
const route = useRoute()
const message = useMessage()
const recruitmentId = ref(Number(route.params.id))

const rules = {
  title: [
    { required: true, message: '请输入招聘标题', trigger: 'blur' }
  ],
  job: [
    { required: true, message: '请输入岗位名称', trigger: 'blur' }
  ],
  job_type:[
    { required: true, message: '请选择工作类型', trigger: 'blur' }
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

// 获取招聘详情
const fetchRecruitmentDetail = async () => {
  try {
    loading.value = true
    const response = await axios.get(`/recruitments/${recruitmentId.value}/`)
    const data = response.data
    
    // 填充表单数据
    formData.value = {
      title: data.title,
      job: data.job,
      job_type: data.job_type,
      work_location: data.work_location,
      salary: data.salary,
      experience: data.experience,
      education: data.education,
      job_desc: data.job_desc,
      job_require: data.job_require,
      is_published: data.status === 'PUBLISHED'
    }
  } catch (error) {
    console.error('获取招聘详情失败:', error)
    message.error('获取招聘详情失败')
    router.back()
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    // 更新招聘信息
    await axios.patch(`/recruitments/${recruitmentId.value}/`, formData.value)
    
    message.success('招聘信息更新成功')
    router.push('/enterprise/recruitments')
  } catch (error) {
    console.error('更新招聘信息失败:', error)
    message.error('更新招聘信息失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchRecruitmentDetail()
})
</script>

<style scoped>
.recruitment-edit-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}
</style>