<template>
  <div class="talent-pool">
    <n-card title="企业人才库">
      <!-- 搜索和筛选工具栏 -->
      <div class="toolbar">
        <n-space>
          <n-input 
            v-model:value="searchKeyword" 
            placeholder="搜索姓名、职位、标签..." 
            clearable
            style="width: 300px;"
            @keyup.enter="handleSearch"
          >
            <template #suffix>
              <n-icon :component="Search" />
            </template>
          </n-input>
          
          <n-select 
            v-model:value="filterStatus" 
            :options="statusOptions" 
            placeholder="人才状态"
            clearable
            style="width: 150px;"
          />
          
          <n-button type="primary" @click="handleSearch">
            搜索
          </n-button>
          
          <n-button @click="handleReset">
            重置
          </n-button>
        </n-space>
      </div>

      <!-- 人才列表 -->
      <n-data-table
        :columns="columns"
        :data="filteredTalents"
        :loading="loading"
        :pagination="pagination"
        :row-key="rowKey"
      />
    </n-card>
  </div>
</template>

<script setup>
import { h, ref, onMounted, computed } from 'vue'
import { useMessage } from 'naive-ui'
import { useRouter } from 'vue-router'
import { 
  NButton, NCard, NTag, NDataTable, NSpace, NInput, NSelect, NIcon, NDropdown
} from 'naive-ui'
import { Search } from '@vicons/ionicons5'
import axios from '@/utils/axios'

const message = useMessage()

// 数据状态
const talents = ref([])
const loading = ref(false)
const searchKeyword = ref('')
const filterStatus = ref('')

const currentUser = ref({
  id: null,
  username: '企业用户'
})

const loadCurrentUser = () => {
  try {
    const enterpriseInfoStr = localStorage.getItem('enterpriseInfo')
    console.log('🔍 从localStorage获取的enterpriseInfo:', enterpriseInfoStr)
    
    if (enterpriseInfoStr) {
      const enterpriseInfo = JSON.parse(enterpriseInfoStr)
      console.log('🔍 解析后的企业信息:', enterpriseInfo)
      
      currentUser.value = {
        id: enterpriseInfo.user_id,
        username: enterpriseInfo.name || '企业用户'
      }
      
      console.log('✅ 设置当前用户:', currentUser.value)
    } else {
      console.warn('⚠️ 未找到enterpriseInfo，检查localStorage')
      message.error('企业信息不完整，请重新登录')
    }
  } catch (error) {
    console.error('❌ 解析用户信息失败:', error)
  }
}

// 状态选项
const statusOptions = [
  { label: '笔试', value: 'WRITTEN_TEST' },
  { label: '面试', value: 'INTERVIEW' },
  { label: '已录用', value: 'HIRED' },
  { label: '已淘汰', value: 'ELIMINATED' }
]

// 分页配置
const pagination = {
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  showQuickJumper: true
}

// 列定义
const columns = [
  {
    title: '姓名',
    key: 'applicant_name',
    width: 120,
    render: (row) => {
      // 优先使用快照中的姓名
      const resumeName = row.resume_snapshot?.name || 
                        row.job_seeker_name || 
                        '未知姓名'
      return resumeName
    }
  },
  {
    title: '联系方式',
    key: 'contact',
    render: (row) => {
      const snapshot = row.resume_snapshot || {}
      return `${snapshot.phone || ''} / ${snapshot.email || row.job_seeker_email || ''}`
    }
  },
  {
    title: '学历',
    key: 'education',
    render: (row) => {
      const educationMap = {
        'HIGH_SCHOOL': '高中及以下',
        'ASSOCIATE': '专科', 
        'BACHELOR': '本科',
        'MASTER': '硕士',
        'DOCTOR': '博士及以上'
      }
      const education = row.resume_snapshot?.education
      return educationMap[education] || education || '未填写'
    }
  },
  {
    title: '来源职位',
    key: 'source_job',
    render: (row) => {
      return row.application_info?.recruitment_title || '未知'
    }
  },
  {
    title: '状态',
    key: 'status',
    width: 150,
    render: (row) => {
      const statusMap = {
        'WRITTEN_TEST': { text: '笔试', type: 'info' },
        'INTERVIEW': { text: '面试', type: 'warning' },
        'HIRED': { text: '已录用', type: 'success' },
        'ELIMINATED': { text: '已淘汰', type: 'error' }
      }
      const statusInfo = statusMap[row.status] || { text: row.status, type: 'default' }
      
      return h(NSelect, {
        value: row.status,
        options: statusOptions,
        size: 'small',
        style: 'width: 120px;',
        onUpdateValue: (value) => updateTalentStatus(row, value)
      })
    }
  },
  {
    title: '添加时间',
    key: 'added_at',
    width: 180,
    render: (row) => {
      if (!row.added_at) return '-'
      try {
        return new Date(row.added_at).toLocaleDateString('zh-CN')
      } catch {
        return row.added_at
      }
    }
  },
{
  title: '操作',
  key: 'actions',
  width: 200,
  render: (row) => {
    const dropdownOptions = [
      {
        label: '开始聊天',
        key: 'start_chat'
      },
      {
        label: '查看简历',
        key: 'view_resume'
      },
      {
        label: '删除',
        key: 'delete'
      }
    ]

    const handleSelect = (key) => {
      switch (key) {
        case 'start_chat':
          startChat(row)
          break
        case 'view_resume':
          viewResume(row)
          break
        case 'delete':
          deleteTalent(row)
          break
        default:
          console.warn('未知的操作:', key)
      }
    }

    return h(NSpace, { size: 'small' }, {
      default: () => [
        h(NDropdown, {
          trigger: 'click',
          options: dropdownOptions,
          onSelect: handleSelect,
          size: 'small'
        }, {
          default: () => h(NButton, { 
            size: 'small',
            onClick: () => console.log('操作按钮被点击') // 添加按钮点击调试
          }, { default: () => '操作' })
        })
      ]
    })
  }
}
]

const router = useRouter()

// 过滤后的人才列表
const filteredTalents = computed(() => {
  let result = talents.value
  
  // 按状态筛选
  if (filterStatus.value) {
    result = result.filter(talent => talent.status === filterStatus.value)
  }
  
  // 按关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(talent => {
      return (
        (talent.resume_snapshot?.name || '').toLowerCase().includes(keyword) ||
        (talent.resume_snapshot?.education || '').toLowerCase().includes(keyword) ||
        (talent.resume_snapshot?.phone || '').toLowerCase().includes(keyword) ||
        (talent.resume_snapshot?.email || '').toLowerCase().includes(keyword) ||
        (talent.added_at || '').toLowerCase().includes(keyword) ||
        (talent.resume_snapshot?.skills || '').toLowerCase().includes(keyword) ||
        (talent.application_info?.recruitment_title || '').toLowerCase().includes(keyword)
      )
    })
  }
  
  return result
})

// 获取人才库数据
// 获取人才库数据
// 获取人才库数据
// 修复后的fetchTalents函数
const fetchTalents = async () => {
  loading.value = true
  try {
    const response = await axios.get('/talent_pool/')
    // ✅ 直接使用API返回的数据，不要覆盖pdf_file字段
    talents.value = response.data.results || response.data
    console.log('✅ 获取的人才数据:', talents.value)
  } catch (error) {
    console.error('获取人才库失败:', error)
    message.error('获取人才库失败')
  } finally {
    loading.value = false
  }
}

// 更新人才状态并发送通知
const updateTalentStatus = async (talent, newStatus) => {
  try {
    const companyName = talent.application_info?.enterprise_name || '公司'
    const jobTitle = talent.application_info?.recruitment_title || '岗位'
    const applicantName = talent.resume_snapshot?.name || '求职者'
    
    let messageText = ''
    
    switch (newStatus) {
      case 'INTERVIEW':
        messageText = `恭喜通过 “${companyName}-${jobTitle}” 的筛选，现在进入面试环节，请留意平台通知和邮箱`
        break
      case 'HIRED':
        messageText = `感谢您参加 “${companyName}-${jobTitle}” 的招聘，恭喜您已被录用，录用通知以及相关注意事项请留意邮箱`
        break
      case 'ELIMINATED':
        messageText = `感谢您参加 “${companyName}-${jobTitle}” 的招聘，很遗憾地通知您未能通过“${jobTitle}”的本轮招聘环节`
        break
      case 'WRITTEN_TEST':
        messageText = null
        break
      default:
        return
    }
    
    await axios.post(`/talent_pool/${talent.id}/update_status/`, {
      status: newStatus
    })
    
    if (messageText) {
      await axios.post('/notifications/create/', {
        recipient_id: talent.job_seeker,
        title: '招聘状态更新',
        message: messageText,
        related_object_id: talent.id,
        related_object_type: 'talent_pool'
      })
    }
    
    message.success('状态更新成功')
    
    const index = talents.value.findIndex(t => t.id === talent.id)
    if (index !== -1) {
      talents.value[index].status = newStatus
    }
  } catch (error) {
    console.error('更新状态失败:', error)
    message.error('更新状态失败')
  }
}

// 修复viewResume函数，确保使用正确的PDF路径
const viewResume = (talent) => {
  console.log('🔍🔍 查看简历 - 详细数据:', talent)
  
  // 直接使用后端返回的pdf_file路径（它已经是完整URL）
  if (talent.pdf_file) {
    console.log('📁📁 使用PDF文件:', talent.pdf_file)
    window.open(talent.pdf_file, '_blank')
    return
  }
  
  // 备用方案：使用原始简历预览
  const originalResumeId = talent.resume_snapshot?.original_resume_id
  if (originalResumeId) {
    console.log('📄📄 使用原始简历预览:', originalResumeId)
    window.open(`/resumes/preview/${originalResumeId}`, '_blank')
    return
  }
  
  message.error('无法找到简历文件')
}
// 开始聊天
const startChat = async (talent) => {
  console.log('🔥🔥🔥 开始聊天 - 详细调试信息')
  console.log('人才数据:', talent)
  console.log('当前用户对象:', currentUser.value)
  console.log('localStorage中的userInfo:', localStorage.getItem('userInfo'))
  
  // 验证用户ID
  if (!currentUser.value.id) {
    console.error('❌❌❌ 当前用户ID为空，无法创建聊天')
    message.error('用户信息不完整，请重新登录')
    return
  }
  
  if (!talent.job_seeker) {
    console.error('❌❌❌ 求职者ID为空:', talent)
    message.error('求职者信息不完整')
    return
  }
  
  console.log('📤 发送的请求数据:', {
    job_seeker_user_id: talent.job_seeker,
    enterprise_user_id: currentUser.value.id
  })
  
  try {
    const response = await axios.post('chat/chatrooms/start_chat/', {
      job_seeker_user_id: talent.job_seeker,
      enterprise_user_id: currentUser.value.id
    })
    
    console.log('✅ 聊天室创建成功:', response.data)
    message.success('聊天室创建成功')
    
    // 跳转到聊天页面
    router.push(`/chat/${response.data.id}`)
    
  } catch (error) {
    console.error('❌ 创建聊天失败详情:')
    console.error('错误对象:', error)
    
    if (error.response) {
      console.error('HTTP状态码:', error.response.status)
      console.error('响应数据:', error.response.data)
      console.error('请求URL:', error.config.url)
      console.error('请求数据:', error.config.data)
      
      if (error.response.status === 400) {
        const errorMsg = error.response.data.error || '请求参数错误'
        message.error(`创建聊天失败: ${errorMsg}`)
        
        // 特殊处理用户不匹配错误
        if (errorMsg.includes('用户不存在') || errorMsg.includes('用户类型不匹配')) {
          console.error('🔍 用户匹配问题，检查用户ID:')
          console.error('当前用户ID:', currentUser.value.id)
          console.error('求职者ID:', talent.job_seeker)
          
          // 重新加载用户信息
          loadCurrentUser()
          message.info('用户信息已刷新，请重试')
        }
      } else {
        message.error(`服务器错误: ${error.response.status}`)
      }
    } else {
      message.error('网络错误: ' + error.message)
    }
  }
}

// 删除人才记录
const deleteTalent = async (talent) => {
  try {
    await axios.delete(`/talent_pool/${talent.id}/`)
    message.success('删除成功')
    
    // 从本地数据中移除
    const index = talents.value.findIndex(t => t.id === talent.id)
    if (index !== -1) {
      talents.value.splice(index, 1)
    }
  } catch (error) {
    console.error('删除失败:', error)
    message.error('删除失败')
  }
}

// 搜索功能
const handleSearch = () => {
  // 计算属性会自动更新，这里只是触发重新计算
  console.log('执行搜索，关键词:', searchKeyword.value, '状态:', filterStatus.value)
}

// 重置搜索
const handleReset = () => {
  searchKeyword.value = ''
  filterStatus.value = ''
}

// 行键函数
const rowKey = (row) => row.id

onMounted(() => {
  loadCurrentUser() // 先加载用户信息
  fetchTalents()
})
</script>

<style scoped>
.talent-pool {
  padding: 20px;
}

.toolbar {
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.tag-management {
  margin: 16px 0;
}

.current-tags {
  margin-top: 12px;
  min-height: 40px;
}

.talent-actions {
  display: flex;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .toolbar {
    padding: 12px;
  }
  
  .talent-actions {
    flex-direction: column;
  }
}
</style>