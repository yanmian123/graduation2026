<template>
  <div class="application-list">
    <n-card title="收到的简历申请">
      <!-- 添加调试信息 -->
      <div v-if="debug" style="background: #f0f0f0; padding: 10px; margin-bottom: 10px;">
        数据调试: {{ applications.length }} 条记录
        <pre>{{ JSON.stringify(applications, null, 2) }}</pre>
      </div>
      
      <n-data-table
        :columns="columns"
        :data="applications"
        :loading="loading"
        :pagination="pagination"
        :row-key="rowKey"
      />
    </n-card>
  </div>
</template>

<script setup>
import { h, ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { NDataTable, NCard, NTag,NButton } from 'naive-ui' // 确保导入所有使用的组件
import axios from '@/utils/axios'

// 调试模式
const debug = ref(true)

// 数据状态
const applications = ref([])
const loading = ref(false)
const message = useMessage()

// 行键函数
const rowKey = (row) => row.id



// 学历映射
const educationMap = {
  'HIGH_SCHOOL': '高中及以下',
  'ASSOCIATE': '专科',
  'BACHELOR': '本科',
  'MASTER': '硕士',
  'DOCTOR': '博士及以上'
}

// 列定义
const columns = [
  {
    title: '申请人',
    key: 'applicant_name',
    render: (row) => {
        // 优先使用快照中的姓名
        const resumeName = row.resume_snapshot?.name || 
                          row.resume_name || 
                          '未知申请人'
        return resumeName
    }
  },
  {
    title: '职位',
    key: 'recruitment_title',
    render: (row) => {
      // 兼容不同字段名
      const title = row.recruitment_title || row.recruitment?.title || row.job?.title || '未知'
      return title
    }
  },
  {
    title: '学历',
    key: 'education',
    render: (row) => {
      // 直接使用后端返回的education字段
      const education = row.education
      // 映射为中文显示
      return educationMap[education] || education || '未填写'
    }
  },
  {
    title: '联系方式',
    key: 'contact',
    render: (row) => {
        // 从快照获取联系方式
        const phone = row.resume_snapshot?.phone || row.phone || '未填写'
        const email = row.resume_snapshot?.email || row.email || '未填写'
        return `${phone} / ${email}`
    }
  },
  {
  title: '简历',
  key: 'resume_action',
  render: (row) => {
      // 检查是否有PDF文件或原始简历ID
      const hasPdf = row.pdf_file || row.resume_snapshot?.has_pdf
      const originalResumeId = row.resume_snapshot?.original_resume_id
      
      if (hasPdf && row.pdf_file) {
          return h(NButton, {
              size: 'small',
              type: 'primary',
              onClick: () => window.open(row.pdf_file, '_blank')
          }, { default: () => '查看PDF' })
      } else if (originalResumeId) {
          return h(NButton, {
              size: 'small',
              type: 'info',
              onClick: () => window.open(`/resumes/preview/${originalResumeId}`, '_blank')
          }, { default: () => '查看原简历' })
      } else {
          return h(NTag, { type: 'default' }, { default: () => '无附件' })
      }
  }
},
  {
    title: '状态',
    key: 'status',
    render: (row) => {
      const statusMap = {
        'PENDING': { text: '待处理', type: 'warning' },
        'VIEWED': { text: '已查看', type: 'info' },
        'INTERVIEW': { text: '待面试', type: 'primary' },
        'REJECTED': { text: '已拒绝', type: 'error' },
        'HIRED': { text: '已录用', type: 'success' }
      }
      
      // 兼容不同状态字段名
      const status = row.status || row.application_status || 'PENDING'
      const statusInfo = statusMap[status] || { text: status, type: 'default' }
      
      return h(NTag, { type: statusInfo.type }, { default: () => statusInfo.text })
    }
  },
  {
    title: '申请时间',
    key: 'applied_at',
    render: (row) => {
      // 兼容不同时间字段名
      const timeStr = row.applied_at || row.created_at || row.apply_time
      if (!timeStr) return '-'
      
      try {
        return new Date(timeStr).toLocaleString('zh-CN')
      } catch {
        return timeStr
      }
    }
  }
]

// 分页配置
const pagination = {
  pageSize: 10
}

// 获取申请记录
const fetchApplications = async () => {
  loading.value = true
  try {
    const response = await axios.get('/applications/')
    console.log('API响应:', response)
    
    // 处理不同的响应格式
    let data = response.data
    if (response.data && response.data.results) {
      data = response.data.results
      console.log('从results字段获取数据:', data)
    }
    
    if (Array.isArray(data)) {
      applications.value = data
      console.log('成功设置申请数据:', applications.value)
    } else {
      console.warn('数据不是数组格式:', data)
      applications.value = []
    }
  } catch (error) {
    console.error('获取申请记录失败:', error)
    message.error('获取申请记录失败')
    
    // 设置默认数据用于测试
    applications.value = getDefaultData()
  } finally {
    loading.value = false
    debug.value = false // 调试完成后关闭
  }
}

// 默认数据函数
const getDefaultData = () => {
  return [
    {
      id: 1,
      applicant_name: '张三',
      recruitment_title: '前端开发工程师',
      resume_name: '张三的简历',
      status: 'PENDING',
      applied_at: '2024-01-15T10:30:00Z'
    },
    {
      id: 2,
      applicant_name: '李四',
      recruitment_title: '产品经理',
      resume_name: '李四的简历',
      status: 'VIEWED',
      applied_at: '2024-01-14T14:20:00Z'
    },
    {
      id: 3,
      applicant_name: '王五',
      recruitment_title: 'UI设计师',
      resume_name: '王五的作品集',
      status: 'INTERVIEW',
      applied_at: '2024-01-13T09:15:00Z'
    }
  ]
}

onMounted(() => {
  fetchApplications()
})
</script>

<style scoped>
.application-list {
  padding: 20px;
}
</style>