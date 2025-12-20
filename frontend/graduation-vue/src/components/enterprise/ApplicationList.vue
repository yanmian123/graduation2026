<!-- 新建 enterprise/ApplicationList.vue 
 如果您需要企业端查看收到的简历申请，可以添加以下组件：
 -->
<template>
  <div class="application-list">
    <n-card title="收到的简历申请">
      <n-data-table
        :columns="columns"
        :data="applications"
        :loading="loading"
        :pagination="pagination"
      />
    </n-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import axios from '@/utils/axios'

const applications = ref([])
const loading = ref(false)
const message = useMessage()

const columns = [
  {
    title: '申请人',
    key: 'applicant_name'
  },
  {
    title: '职位',
    key: 'recruitment_title'
  },
  {
    title: '简历',
    key: 'resume_name'
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
      const status = statusMap[row.status]
      return h(NTag, { type: status.type }, status.text)
    }
  },
  {
    title: '申请时间',
    key: 'applied_at',
    render: (row) => new Date(row.applied_at).toLocaleString('zh-CN')
  }
]

const pagination = {
  pageSize: 10
}

const fetchApplications = async () => {
  loading.value = true
  try {
    const response = await axios.get('/applications/')
    applications.value = response.data
  } catch (error) {
    message.error('获取申请记录失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchApplications()
})
</script>