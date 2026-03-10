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

        <n-form-item path="recruit_type" label="招聘类型">
          <n-select 
            v-model:value="formData.recruit_type" 
            :options="recruitTypes"
            placeholder="请选择招聘类型"
          />
        </n-form-item>

        <n-form-item path="job_type" label="工作类型">
          <n-select 
            v-model:value="formData.job_type" 
            :options="jobTypes"
            placeholder="请选择工作类型"
          />
        </n-form-item>

        <n-form-item path="job_category" label="职位类别">
          <n-select 
            v-model:value="formData.job_category" 
            placeholder="请选择职位类别"
            :options="jobCategoryOptions"
            clearable
          />
        </n-form-item>

        <n-form-item path="job" label="岗位名称">
          <n-input 
            v-model:value="formData.job" 
            placeholder="请输入岗位名称，如“软件工程师”"
          />
        </n-form-item>

        <n-form-item path="work_location" label="工作地点">
          <n-select 
            v-model:value="formData.work_location" 
            placeholder="请选择工作地点"
            :options="locationOptions"
            clearable
          />
        </n-form-item>

        <n-form-item path="salary_type" label="薪资类型">
          <n-radio-group v-model:value="formData.salary_type">
            <n-radio value="range">选择月薪范围</n-radio>
            <n-radio value="custom">自定义详细薪资</n-radio>
            <n-radio value="negotiable">面议</n-radio>
          </n-radio-group>
        </n-form-item>

        <n-form-item v-if="formData.salary_type === 'range'" path="salary_range" label="月薪范围">
          <n-select 
            v-model:value="formData.salary_range" 
            :options="salaryRangeOptions"
            placeholder="请选择月薪范围"
          />
        </n-form-item>

        <n-form-item v-if="formData.salary_type === 'custom'" path="salary" label="详细薪资">
          <n-input 
            v-model:value="formData.salary" 
            type="textarea"
            rows="3"
            placeholder="请输入详细薪资构成，如：&#10;基本工资：15k&#10;绩效工资：3k&#10;年终奖：2-4个月&#10;五险一金：按国家标准缴纳"
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

        <n-form-item path="deadline" label="截止日期">
          <n-date-picker 
            v-model:value="formData.deadline" 
            type="date"
            placeholder="请选择截止日期"
            style="width: 100%"
            :is-date-disabled="isDateDisabled"
          />
        </n-form-item>

        <n-form-item>
          <n-checkbox v-model:checked="formData.is_urgent">
            标记为急聘
          </n-checkbox>
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
import { NForm, NFormItem, NInput, NButton, NCard, NCheckbox, NSelect, NInputNumber, NDatePicker, NCascader, NRadio, NRadioGroup, useMessage } from 'naive-ui'
import axios from '@/utils/axios'

const experienceOptions = [
  { label: '应届毕业生', value: 'FRESH' },
  { label: '1年以内', value: 'LESS_THAN_1' },
  { label: '1-3年', value: '1_3' },
  { label: '3-5年', value: '3_5' },
  { label: '5-10年', value: '5_10' },
  { label: '10年以上', value: 'MORE_THAN_10' }
]

const educationOptions = [
  { label: '高中及以下', value: 'HIGH_SCHOOL' },
  { label: '专科', value: 'ASSOCIATE' },
  { label: '本科', value: 'BACHELOR' },
  { label: '硕士', value: 'MASTER' },
  { label: '博士及以上', value: 'DOCTOR' }
]

const recruitTypes = [
  { label: '校招', value: 'CAMPUS' },
  { label: '社招', value: 'SOCIAL' },
  { label: '实习', value: 'INTERNSHIP' }
]

const jobTypes = [
  { label: '全职', value: 'FULL_TIME' },
  { label: '兼职', value: 'PART_TIME' },
  { label: '实习', value: 'INTERNSHIP' }
]

const jobCategoryOptions = [
  { label: '软件开发', value: 'SOFTWARE' },
  { label: '测试', value: 'TEST' },
  { label: '运维', value: 'DEVOPS' },
  { label: '产品', value: 'PRODUCT' },
  { label: '设计', value: 'DESIGN' },
  { label: '市场', value: 'MARKETING' },
  { label: '销售', value: 'SALES' },
  { label: '人力资源', value: 'HR' },
  { label: '财务', value: 'FINANCE' },
  { label: '其他', value: 'OTHER' }
]

const locationOptions = [
  { label: '北京', value: '北京' },
  { label: '上海', value: '上海' },
  { label: '广州', value: '广州' },
  { label: '深圳', value: '深圳' },
  { label: '杭州', value: '杭州' },
  { label: '成都', value: '成都' }
]

const salaryRangeOptions = [
  { label: '5k以下', value: '0-5000' },
  { label: '5k-10k', value: '5000-10000' },
  { label: '10k-15k', value: '10000-15000' },
  { label: '15k-20k', value: '15000-20000' },
  { label: '20k-30k', value: '20000-30000' },
  { label: '30k以上', value: '30000-999999' }
]

const formData = ref({
  title: '',
  job: '',
  recruit_type: 'SOCIAL',
  job_type: 'FULL_TIME',
  job_category: null,
  work_location: null,
  salary_type: 'range',
  salary_range: null,
  salary: '',
  experience: 'FRESH',
  education: 'HIGH_SCHOOL',
  job_desc: '',
  job_require: '',
  deadline: null,
  is_urgent: false,
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
  recruit_type: [
    { required: true, message: '请选择招聘类型', trigger: 'blur' }
  ],
  job_type: [
    { required: true, message: '请选择工作类型', trigger: 'blur' }
  ],
  job_category: [
    { required: true, message: '请选择职位类别', trigger: 'blur' }
  ],
  job: [
    { required: true, message: '请输入岗位名称', trigger: 'blur' }
  ],
  work_location: [
    { required: true, message: '请选择工作地点', trigger: 'blur' }
  ],
  salary_type: [
    { required: true, message: '请选择薪资类型', trigger: 'blur' }
  ],
  salary_range: [
    { required: true, message: '请选择月薪范围', trigger: 'blur' }
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
  ],
  deadline: [
    { 
      required: true, 
      message: '请选择截止日期', 
      trigger: ['change', 'blur'],
      type: 'number'
    }
  ]
}

const fetchRecruitmentDetail = async () => {
  try {
    loading.value = true
    const response = await axios.get(`/recruitments/${recruitmentId.value}/`)
    const data = response.data
    
    let salaryType = 'range'
    let salaryRange = null
    
    if (data.salary === '面议') {
      salaryType = 'negotiable'
    } else if (data.salary && !data.salary.includes('k')) {
      salaryType = 'custom'
    } else {
      salaryRange = data.salary
    }
    
    formData.value = {
      title: data.title,
      job: data.job,
      recruit_type: data.recruit_type,
      job_type: data.job_type || 'FULL_TIME',
      job_category: data.job_category,
      work_location: data.work_location,
      salary_type: salaryType,
      salary_range: salaryRange,
      salary: salaryType === 'custom' ? data.salary : '',
      experience: data.experience,
      education: data.education,
      job_desc: data.job_desc,
      job_require: data.job_require,
      deadline: data.deadline ? new Date(data.deadline).getTime() : null,
      is_urgent: data.is_urgent || false,
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
    
    let submitData = {
      ...formData.value,
      deadline: formData.value.deadline ? formatDate(formData.value.deadline) : null
    }
    
    if (formData.value.salary_type === 'range') {
      submitData.salary = formData.value.salary_range
    } else if (formData.value.salary_type === 'negotiable') {
      submitData.salary = '面议'
    }
    
    await axios.patch(`/recruitments/${recruitmentId.value}/`, submitData)
    
    message.success('招聘信息更新成功')
    router.push('/enterprise/recruitments')
  } catch (error) {
    console.error('更新招聘信息失败:', error)
    message.error('更新招聘信息失败')
  } finally {
    loading.value = false
  }
}

const formatDate = (date) => {
  if (!date) return null
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const isDateDisabled = (timestamp) => {
  const date = new Date(timestamp)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return date < today
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
