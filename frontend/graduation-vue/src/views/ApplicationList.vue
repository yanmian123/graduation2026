<template>
  <div class="application-list">
    <!-- 批量操作工具栏 -->
    <n-card v-if="selectedApplications.length > 0" class="bulk-actions-toolbar">
      <div class="bulk-actions-content">
        <span class="selected-count">已选择 {{ selectedApplications.length }} 条申请</span>
        <div class="action-controls">
          <n-select 
            v-model:value="bulkAction" 
            :options="bulkActions" 
            placeholder="选择批量操作"
            style="width: 200px; margin-right: 12px;"
            size="small"
          />
          <n-button 
            type="primary" 
            size="small" 
            :loading="bulkUpdating"
            @click="handleBulkAction"
            :disabled="!bulkAction"
          >
            {{ bulkUpdating ? '处理中...' : '应用' }}
          </n-button>
          <n-button 
            size="small" 
            @click="clearSelection"
            style="margin-left: 8px;"
          >
            取消选择
          </n-button>
        </div>
      </div>
    </n-card>    
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
        :checked-row-keys="selectedApplications"
        @update:checked-row-keys="handleCheckedRowKeysChange"
      />
    </n-card>
  </div>
</template>

<script setup>
import { h, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { NDataTable, NCard, NTag,NButton, NSelect,NSpace ,NDropdown} from 'naive-ui' // 确保导入所有使用的组件
import axios from '@/utils/axios'

// 调试模式
const debug = ref(true)
const message = useMessage()
const router = useRouter()
// 数据状态
const applications = ref([])
const loading = ref(false)
const selectedApplications = ref([]) // 选中的申请ID
const bulkAction = ref(null) // 批量操作类型
const bulkUpdating = ref(false) // 批量更新中状态

// 批量操作选项
const bulkActions = ref([
  { label: '通过并加入人才库', value: 'PASS' },
  { label: '不通过', value: 'REJECT' }
])

// 状态选项
const statusOptions = [
  { label: '初筛', value: 'PENDING' },
  { label: '已归入人才库', value: 'INTERVIEW' },
  { label: '已拒绝', value: 'REJECTED' }
]

// 状态类型映射
const statusTypeMap = {
  'PENDING': 'warning',
  'INTERVIEW': 'success',
  'REJECTED': 'error'
}

// 状态文本映射
const statusTextMap = {
  'PENDING': '初筛',
  'INTERVIEW': '已归入人才库',
  'REJECTED': '已拒绝'
}

// 行属性，支持点击选择
const rowProps = (row) => {
  return {
    style: 'cursor: pointer;',
    onClick: () => {
      toggleRowSelection(row.id)
    }
  }
}

// 切换行选择状态
const toggleRowSelection = (rowId) => {
  const index = selectedApplications.value.indexOf(rowId)
  if (index > -1) {
    selectedApplications.value.splice(index, 1)
  } else {
    selectedApplications.value.push(rowId)
  }
}

// 清除选择
const clearSelection = () => {
  selectedApplications.value = []
  bulkAction.value = null
}

// 批量更新申请状态
const handleBulkAction = async () => {
  if (!bulkAction.value || selectedApplications.value.length === 0) {
    message.warning('请选择要操作的申请和操作类型')
    return
  }

  bulkUpdating.value = true
  try {
    console.log('开始批量更新，选中的申请:', selectedApplications.value)
    
    // 使用单个更新接口循环处理
    const updatePromises = selectedApplications.value.map(async (appId) => {
      try {
        const application = applications.value.find(app => app.id === appId)
        if (bulkAction.value === 'PASS') {
          // 通过并加入人才库（使用INTERVIEW状态表示通过初筛）
          await axios.post(`/applications/${appId}/update_status/`, {
            status: 'INTERVIEW'
          })
          // 加入人才库
          await axios.post('/talent_pool/add_from_application/', {
            application_id: appId,
            tags: '通过初筛',
            notes: `加入人才库`
          })
          // 发送通知
          await sendStatusNotification(application, 'PASS')
          console.log(`申请 ${appId} 通过并加入人才库成功`)
        } else if (bulkAction.value === 'REJECT') {
          // 不通过
          await axios.post(`/applications/${appId}/update_status/`, {
            status: 'REJECTED'
          })
          // 发送通知
          await sendStatusNotification(application, 'REJECT')
          console.log(`申请 ${appId} 拒绝成功`)
        }
        return { success: true, id: appId }
      } catch (error) {
        console.error(`申请 ${appId} 操作失败:`, error)
        return { success: false, id: appId, error }
      }
    })

    // 等待所有更新完成
    const results = await Promise.all(updatePromises)
    
    // 统计成功和失败的数量
    const successfulUpdates = results.filter(result => result.success).length
    const failedUpdates = results.filter(result => !result.success).length
    
    if (failedUpdates === 0) {
      message.success(`成功处理 ${successfulUpdates} 条申请记录`)
    } else {
      message.warning(`成功处理 ${successfulUpdates} 条，失败 ${failedUpdates} 条`)
    }
    
    // 更新本地数据状态
    applications.value.forEach(app => {
      if (selectedApplications.value.includes(app.id)) {
        if (bulkAction.value === 'PASS') {
          app.status = 'INTERVIEW'
        } else if (bulkAction.value === 'REJECT') {
          app.status = 'REJECTED'
        }
      }
    })
    
    // 清除选择
    clearSelection()
    
  } catch (error) {
    console.error('批量操作失败:', error)
    message.error('批量操作失败: ' + (error.response?.data?.error || error.message))
  } finally {
    bulkUpdating.value = false
  }
}
// 更新单个申请状态
const updateApplicationStatus = async (applicationId, newStatus) => {
  try {
    const response = await axios.post(`/applications/${applicationId}/update_status/`, {
      status: newStatus
    })
    
    message.success('状态更新成功')
    
    // 更新本地数据
    const index = applications.value.findIndex(app => app.id === applicationId)
    if (index !== -1) {
      applications.value[index].status = newStatus
    }
  } catch (error) {
    console.error('更新状态失败:', error)
    message.error('状态更新失败')
  }
}

// 发送申请状态通知
const sendApplicationNotification = async (applicationId) => {
  try {
    await axios.post(`/applications/${applicationId}/send_notification/`)
    console.log(`成功发送申请 ${applicationId} 的状态通知`)
    message.success('状态通知发送成功')
  } catch (error) {
    console.error('发送状态通知失败:', error)
    message.error('发送状态通知失败: ' + (error.response?.data?.error || error.message))
    throw error
  }
}

// 发送状态通知
const sendStatusNotification = async (application, action) => {
  try {
    console.log('发送通知，申请数据:', application)
    console.log('申请人ID:', application.applicant_id)
    
    const companyName = application.recruitment?.enterprise?.name || '公司'
    const jobTitle = application.recruitment_title || '岗位'
    
    const notificationData = {
      recipient_id: application.applicant_id,
      title: '申请状态更新',
      message: action === 'PASS' 
        ? `”${companyName}-${jobTitle}”招聘状态已更新为'通过初筛并进入下一阶段'`
        : `”${companyName}-${jobTitle}”很遗憾，您的投递未能进入下一阶段`,
      related_object_id: application.id,
      related_object_type: 'job_application'
    }
    
    console.log('发送通知数据:', notificationData)
    await axios.post('/notifications/create/', notificationData)
    console.log(`成功发送申请 ${application.id} 的状态通知`)
  } catch (error) {
    console.error('发送状态通知失败:', error)
    console.error('错误响应:', error.response?.data)
    throw error
  }
}



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
    type: 'selection',
    fixed: 'left',
    width: 50
  },
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
        'PENDING': { text: '初筛', type: 'warning' },
        'INTERVIEW': { text: '已归入人才库', type: 'success' },
        'REJECTED': { text: '已拒绝', type: 'error' },
        'VIEWED': { text: '已查看', type: 'info' },
        'HIRED': { text: '已录用', type: 'success' }
      }
      
      const status = row.status || row.application_status || 'PENDING'
      const statusInfo = statusMap[status] || { text: status, type: 'default' }
      
      return h(NTag, { type: statusInfo.type }, { default: () => statusInfo.text })
    }
  },
  {
    title: '申请时间',
    key: 'applied_at',
    render: (row) => {
      const timeStr = row.applied_at || row.created_at || row.apply_time
      if (!timeStr) return '-'
      
      try {
        return new Date(timeStr).toLocaleString('zh-CN')
      } catch {
        return timeStr
      }
    }
  },
  {
    title: '操作',
    key: 'actions',
    render: (row) => {
      const actionOptions = [
        { label: '加入人才库', value: 'PASS' },
        { label: '不通过', value: 'REJECT' },
        { label: '发起聊天', value: 'CHAT' },
        { label: '删除', value: 'DELETE' }
      ]
      
      return h(NSelect, {
        size: 'small',
        placeholder: '选择操作',
        options: actionOptions,
        style: { width: '140px' },
        onUpdateValue: (value) => handleAction(row, value)
      })
    }
  }
]

// 行键函数
const rowKey = (row) => row.id

// 分页配置
const pagination = {pageSize: 10}


// 处理选择变化
const handleCheckedRowKeysChange = (keys) => {
  selectedApplications.value = keys
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
      id:1,
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

// 处理单个申请的操作
const handleAction = async (application, action) => {
  try {
    if (action === 'PASS') {
      // 通过并加入人才库（使用INTERVIEW状态表示通过初筛）
      await axios.post(`/applications/${application.id}/update_status/`, {
        status: 'INTERVIEW'
      })
      // 加入人才库
      await axios.post('/talent_pool/add_from_application/', {
        application_id: application.id,
        tags: '通过初筛',
        notes: `加入人才库`
      })
      // 发送通知
      await sendStatusNotification(application, 'PASS')
      message.success('已通过并加入人才库')
      
      // 更新本地数据
      const index = applications.value.findIndex(app => app.id === application.id)
      if (index !== -1) {
        applications.value[index].status = 'INTERVIEW'
      }
    } else if (action === 'REJECT') {
      // 不通过
      await axios.post(`/applications/${application.id}/update_status/`, {
        status: 'REJECTED'
      })
      // 发送通知
      await sendStatusNotification(application, 'REJECT')
      message.success('已拒绝该申请')
      
      // 更新本地数据
      const index = applications.value.findIndex(app => app.id === application.id)
      if (index !== -1) {
        applications.value[index].status = 'REJECTED'
      }
    } else if (action === 'CHAT') {
      // 发起聊天
      await startChat(application)
    } else if (action === 'DELETE') {
      // 删除申请
      await deleteApplication(application)
    }
  } catch (error) {
    console.error('操作失败:', error)
    if (error.response?.status === 400) {
      message.error(error.response.data.error || '操作失败')
    } else {
      message.error('操作失败: ' + (error.response?.data?.error || error.message))
    }
  }
}

// 删除申请记录
const deleteApplication = async (application) => {
  try {
    await axios.delete(`/applications/${application.id}/`)
    message.success('删除成功')
    
    // 从本地数据中移除
    const index = applications.value.findIndex(app => app.id === application.id)
    if (index !== -1) {
      applications.value.splice(index, 1)
    }
  } catch (error) {
    console.error('删除失败:', error)
    message.error('删除失败')
  }
}

// 在 script 中添加加入人才库的方法
const addToTalentPool = async (application) => {
  try {
    const response = await axios.post('/talent_pool/add_from_application/', {
      application_id: application.id,
      tags: '来自申请',
      notes: `从职位"${application.recruitment_title}"申请中添加`
    })
    
    message.success('已成功加入人才库')
    
    // 更新申请状态为"已归入人才库"
    await updateApplicationStatus(application.id, 'TALENT_POOL')
  } catch (error) {
    console.error('加入人才库失败:', error)
    if (error.response?.status === 400) {
      message.error(error.response.data.error || '该人才已存在人才库中')
    } else {
      message.error('加入人才库失败')
    }
  }
}

// 开始聊天
const startChat = async (application) => {
  try {
    // 企业用户信息存储在 enterpriseInfo 中
    const enterpriseInfo = JSON.parse(localStorage.getItem('enterpriseInfo'))
    if (!enterpriseInfo || !enterpriseInfo.user_id) {
      message.error('企业信息不完整，请重新登录')
      return
    }
    
    console.log('发起聊天 - 申请数据:', application)
    console.log('发起聊天 - 企业信息:', enterpriseInfo)
    console.log('发起聊天 - 申请人ID:', application.applicant_id)
    console.log('发起聊天 - 企业用户ID:', enterpriseInfo.user_id)
    
    const response = await axios.post('/chat/chatrooms/start_chat/', {
      job_seeker_user_id: application.applicant_id,
      enterprise_user_id: enterpriseInfo.user_id
    })
    
    console.log('聊天室创建成功:', response.data)
    const roomId = response.data.id
    
    message.success('聊天室创建成功，正在跳转...')
    
    // 跳转到聊天页面，带上roomId参数
    router.push(`/chat/${roomId}`)
  } catch (error) {
    console.error('创建聊天失败:', error)
    console.error('错误响应:', error.response?.data)
    message.error('创建聊天失败: ' + (error.response?.data?.error || error.message))
  }
}

onMounted(() => {
  fetchApplications()
})
</script>

<style scoped>
.application-list {
  padding: 20px;
}

.bulk-actions-toolbar {
  margin-bottom: 16px;
  background-color: #f0f9ff;
  border: 1px solid #bae6fd;
}

.bulk-actions-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selected-count {
  font-weight: 600;
  color: #0369a1;
}

.action-controls {
  display: flex;
  align-items: center;
}

/* 选中行样式 */
:deep(.n-data-table-tr--checked) {
  background-color: #f0f9ff !important;
}

:deep(.n-data-table-td) {
  vertical-align: middle;
}
</style>