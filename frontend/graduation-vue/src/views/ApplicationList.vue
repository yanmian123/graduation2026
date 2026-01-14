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
import { useMessage } from 'naive-ui'
import { NDataTable, NCard, NTag,NButton, NSelect,NSpace ,NDropdown} from 'naive-ui' // 确保导入所有使用的组件
import axios from '@/utils/axios'

// 调试模式
const debug = ref(true)
const message = useMessage()
// 数据状态
const applications = ref([])
const loading = ref(false)
const selectedApplications = ref([]) // 选中的申请ID
const bulkAction = ref(null) // 批量操作类型
const bulkUpdating = ref(false) // 批量更新中状态

// 批量操作选项
const bulkActions = ref([
  { label: '标记为已查看', value: 'VIEWED' },
  { label: '标记为待面试', value: 'INTERVIEW' },
  { label: '标记为已拒绝', value: 'REJECTED' },
  { label: '标记为已录用', value: 'HIRED' }
])

// 状态选项
const statusOptions = [
  { label: '待处理', value: 'PENDING' },
  { label: '已查看', value: 'VIEWED' },
  { label: '待面试', value: 'INTERVIEW' },
  { label: '已拒绝', value: 'REJECTED' },
  { label: '已录用', value: 'HIRED' }
]

// 状态类型映射
const statusTypeMap = {
  'PENDING': 'warning',
  'VIEWED': 'info', 
  'INTERVIEW': 'primary',
  'REJECTED': 'error',
  'HIRED': 'success'
}

// 状态文本映射
const statusTextMap = {
  'PENDING': '待处理',
  'VIEWED': '已查看',
  'INTERVIEW': '待面试',
  'REJECTED': '已拒绝',
  'HIRED': '已录用'
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
        const response = await axios.post(`/applications/${appId}/update_status/`, {
          status: bulkAction.value
        })
        console.log(`申请 ${appId} 更新成功`)
        return { success: true, id: appId }
      } catch (error) {
        console.error(`申请 ${appId} 更新失败:`, error)
        return { success: false, id: appId, error }
      }
    })

    // 等待所有更新完成
    const results = await Promise.all(updatePromises)
    
    // 统计成功和失败的数量
    const successfulUpdates = results.filter(result => result.success).length
    const failedUpdates = results.filter(result => !result.success).length
    
    if (failedUpdates === 0) {
      message.success(`成功更新 ${successfulUpdates} 条申请记录`)
    } else {
      message.warning(`成功更新 ${successfulUpdates} 条，失败 ${failedUpdates} 条`)
    }
    
    // 更新本地数据状态
    applications.value.forEach(app => {
      if (selectedApplications.value.includes(app.id)) {
        app.status = bulkAction.value
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
  },

  // 新增：状态操作列
  {
    title: '操作',
    key: 'actions',
    render: (row) => {
      return h(NSelect, {
        value: row.status,
        options: statusOptions,
        onUpdateValue: (value) => {
          updateApplicationStatus(row.id, value)
        },
        size: 'small',
        style: 'min-width: 120px;'
      })
    }
  },
  {
  title: '操作',
  key: 'actions',
  render: (row) => {
    const actions = [
      {
        label: '加入人才库',
        key: 'add_to_talent',
        onClick: () => addToTalentPool(row)
      },
      {
        label: '开始聊天',
        key: 'start_chat',
        onClick: () => startChat(row)
      }
    ]
    
    return h(NSpace, { size: 'small' }, {
      default: () => [
        // h(NSelect, {
        //   value: row.status,
        //   options: statusOptions,
        //   onUpdateValue: (value) => updateApplicationStatus(row.id, value),
        //   size: 'small',
        //   style: 'min-width: 120px; margin-right: 8px;'
        // }),
        h(NDropdown, {
          trigger: 'click',
          options: [
            {
              label: '加入人才库',
              key: 'add_to_talent',
              // 移除这里的onClick
            },
            {
              label: '开始聊天', 
              key: 'start_chat',
            }
          ],
          onSelect: (key) => {
            if (key === 'add_to_talent') {
              addToTalentPool(row)
            } else if (key === 'start_chat') {
              startChat(row)
            }
          },
          size: 'small'
        }, {
          default: () => h(NButton, { size: 'small' }, { default: () => '更多' })
        })
      ]
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

// 在 script 中添加加入人才库的方法
const addToTalentPool = async (application) => {
  try {
    const response = await axios.post('/talent_pool/add_from_application/', {
      application_id: application.id,
      tags: '来自申请', // 可以添加默认标签
      notes: `从职位"${application.recruitment_title}"申请中添加`
    })
    
    message.success('已成功加入人才库')
  } catch (error) {
    console.error('加入人才库失败:', error)
    if (error.response?.status === 400) {
      message.error(error.response.data.error || '该人才已存在人才库中')
    } else {
      message.error('加入人才库失败')
    }
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