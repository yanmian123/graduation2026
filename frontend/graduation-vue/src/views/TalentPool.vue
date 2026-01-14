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

    <!-- 添加标签模态框 -->
    <n-modal v-model:show="showTagModal">
      <n-card
        style="width: 600px"
        title="管理标签"
        :bordered="false"
        size="huge"
        role="dialog"
        aria-modal="true"
      >
        <template #header-extra>
          <n-button quaternary circle @click="showTagModal = false">
            <template #icon>
              <n-icon><Close /></n-icon>
            </template>
          </n-button>
        </template>
        
        <div class="tag-management">
          <n-input 
            v-model:value="newTag" 
            placeholder="输入新标签，用逗号分隔"
            @keyup.enter="addTags"
          >
            <template #suffix>
              <n-button text @click="addTags">
                <template #icon>
                  <n-icon><Add /></n-icon>
                </template>
              </n-button>
            </template>
          </n-input>
          
          <div class="current-tags">
            <n-tag
              v-for="tag in currentEditingTags"
              :key="tag"
              closable
              @close="removeTag(tag)"
              style="margin: 4px;"
            >
              {{ tag }}
            </n-tag>
          </div>
        </div>
        
        <template #footer>
          <n-space justify="end">
            <n-button @click="showTagModal = false">取消</n-button>
            <n-button type="primary" @click="saveTags">保存</n-button>
          </n-space>
        </template>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup>
import { h, ref, onMounted, computed } from 'vue'
import { useMessage } from 'naive-ui'
import { useRouter } from 'vue-router'
import { 
  NButton, NCard, NTag, NDataTable, NSpace, NInput, NSelect, NIcon, NModal,
  NRate, NDropdown
} from 'naive-ui'
import { Search, Add, Close } from '@vicons/ionicons5'
import axios from '@/utils/axios'

const message = useMessage()

// 数据状态
const talents = ref([])
const loading = ref(false)
const searchKeyword = ref('')
const filterStatus = ref('')
const showTagModal = ref(false)
const newTag = ref('')
const currentEditingTalent = ref(null)
const currentEditingTags = ref([])

const currentUser = ref({
  id: null,
  username: '企业用户'
})

const loadCurrentUser = () => {
  try {
    const userInfoStr = localStorage.getItem('userInfo')
    console.log('🔍 从localStorage获取的userInfo:', userInfoStr)
    
    if (userInfoStr) {
      const userInfo = JSON.parse(userInfoStr)
      console.log('🔍 解析后的用户信息:', userInfo)
      
      currentUser.value = {
        id: userInfo.id,
        username: userInfo.username || '企业用户'
      }
      
      console.log('✅ 设置当前用户:', currentUser.value)
    } else {
      console.warn('⚠️ 未找到userInfo，检查localStorage')
      // 尝试从其他可能的键名获取
      const userId = localStorage.getItem('user_id')
      const username = localStorage.getItem('username')
      if (userId) {
        currentUser.value.id = parseInt(userId)
        currentUser.value.username = username || '企业用户'
        console.log('✅ 从备用键名设置用户:', currentUser.value)
      }
    }
  } catch (error) {
    console.error('❌ 解析用户信息失败:', error)
  }
}

// 状态选项
const statusOptions = [
  { label: '活跃', value: 'ACTIVE' },
  { label: '已归档', value: 'ARCHIVED' },
  { label: '黑名单', value: 'BLACKLIST' }
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
    title: '标签',
    key: 'tags',
    render: (row) => {
      const tags = row.tags_list || []
      return h('div', { style: 'display: flex; flex-wrap: wrap; gap: 4px;' }, 
        tags.map(tag => 
          h(NTag, { 
            size: 'small', 
            type: 'info',
            bordered: false
          }, { default: () => tag })
        )
      )
    }
  },
  {
    title: '评分',
    key: 'rating',
    width: 150,
    render: (row) => {
      return h(NRate, {
        value: row.rating,
        size: 'small',
        readonly: true
      })
    }
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row) => {
      const statusMap = {
        'ACTIVE': { text: '活跃', type: 'success' },
        'ARCHIVED': { text: '已归档', type: 'warning' },
        'BLACKLIST': { text: '黑名单', type: 'error' }
      }
      const statusInfo = statusMap[row.status] || { text: row.status, type: 'default' }
      return h(NTag, { type: statusInfo.type }, { default: () => statusInfo.text })
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
        label: '编辑标签',
        key: 'edit_tags'
      },
      {
        label: row.status === 'ACTIVE' ? '归档' : '激活',
        key: 'toggle_status'
      },
      {
        label: '开始聊天',
        key: 'start_chat'
      },
      {
        label: '查看简历',
        key: 'view_resume'
      }
    ]

    // 处理下拉菜单选择
    const handleSelect = (key) => {
      console.log('🎯 下拉菜单被点击!', 'key:', key, '行数据:', row)
      
      // 添加调试信息
      message.info(`执行操作: ${key}`)
      
      switch (key) {
        case 'edit_tags':
          console.log('编辑标签:', row)
          openTagModal(row)
          break
        case 'toggle_status':
          console.log('切换状态:', row)
          toggleTalentStatus(row)
          break
        case 'start_chat':
          console.log('开始聊天:', row)
          startChat(row)
          break
        case 'view_resume':
          console.log('查看简历:', row)
          viewResume(row)
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

// const startChat = (talent) => {
//   console.log('🔥 按钮被点击了!', talent)
//   message.success(`开始与 ${talent.job_seeker_name || '求职者'} 聊天`)
  
//   // 临时跳转
//   router.push('/chat')
// }

// 其他函数的简单定义
// const openTagModal = (talent) => {
//   message.info('编辑标签功能开发中')
// }

// const toggleTalentStatus = (talent) => {
//   message.info('状态切换功能开发中')
// }

// const viewResume = (talent) => {
//   message.info('查看简历功能开发中')
// }

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
        talent.job_seeker_name.toLowerCase().includes(keyword) ||
        (talent.resume_snapshot?.skills || '').toLowerCase().includes(keyword) ||
        (talent.tags || '').toLowerCase().includes(keyword) ||
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

// 打开标签编辑模态框
const openTagModal = (talent) => {
  currentEditingTalent.value = talent
  currentEditingTags.value = [...(talent.tags_list || [])]
  showTagModal.value = true
}

// 添加标签
const addTags = () => {
  if (!newTag.value.trim()) return
  
  const tagsToAdd = newTag.value.split(',').map(tag => tag.trim()).filter(tag => tag)
  tagsToAdd.forEach(tag => {
    if (tag && !currentEditingTags.value.includes(tag)) {
      currentEditingTags.value.push(tag)
    }
  })
  newTag.value = ''
}

// 移除标签
const removeTag = (tagToRemove) => {
  currentEditingTags.value = currentEditingTags.value.filter(tag => tag !== tagToRemove)
}

// 保存标签
const saveTags = async () => {
  if (!currentEditingTalent.value) return
  
  try {
    const response = await axios.patch(`/talent_pool/${currentEditingTalent.value.id}/`, {
      tags: currentEditingTags.value.join(',')
    })
    
    message.success('标签更新成功')
    
    // 更新本地数据
    const index = talents.value.findIndex(t => t.id === currentEditingTalent.value.id)
    if (index !== -1) {
      talents.value[index].tags = currentEditingTags.value.join(',')
      talents.value[index].tags_list = [...currentEditingTags.value]
    }
    
    showTagModal.value = false
  } catch (error) {
    console.error('保存标签失败:', error)
    message.error('保存标签失败')
  }
}

// 切换人才状态
const toggleTalentStatus = async (talent) => {
  const newStatus = talent.status === 'ACTIVE' ? 'ARCHIVED' : 'ACTIVE'
  const statusText = newStatus === 'ACTIVE' ? '激活' : '归档'
  
  try {
    const response = await axios.post(`/talent_pool/${talent.id}/update_status/`, {
      status: newStatus
    })
    
    message.success(`已${statusText}该人才`)
    
    // 更新本地数据
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
    const response = await axios.post('/chat/chatrooms/start_chat/', {
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