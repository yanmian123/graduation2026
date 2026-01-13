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
    key: 'job_seeker_name',
    width: 120
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
          key: 'edit_tags',
          onClick: () => openTagModal(row)
        },
        {
          label: row.status === 'ACTIVE' ? '归档' : '激活',
          key: 'toggle_status',
          onClick: () => toggleTalentStatus(row)
        },
        {
          label: '开始聊天',
          key: 'start_chat',
          onClick: () => startChat(row)
        },
        {
          label: '查看简历',
          key: 'view_resume',
          onClick: () => viewResume(row)
        }
      ]

      return h(NSpace, { size: 'small' }, {
        default: () => [
          h(NDropdown, {
            trigger: 'click',
            options: dropdownOptions,
            onSelect: (key) => handleDropdownSelect(key, row)
          }, {
            default: () => h(NButton, { size: 'small' }, { default: () => '操作' })
          })
        ]
      })
    }
  }
]

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
const fetchTalents = async () => {
  loading.value = true
  try {
    const response = await axios.get('/talent_pool/')
    talents.value = response.data.results || response.data
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

// 查看简历
const viewResume = (talent) => {
  if (talent.resume_snapshot) {
    // 在新窗口打开简历详情页
    window.open(`/resumes/preview/${talent.resume_snapshot.original_resume_id}`, '_blank')
  } else {
    message.warning('该人才没有简历信息')
  }
}

// 开始聊天
const startChat = async (talent) => {
  try {
    // 调用聊天室创建接口
    const response = await axios.post('/chatrooms/start_chat/', {
      job_seeker_user_id: talent.job_seeker,
      enterprise_user_id: currentUser.value.id
    })
    
    message.success('聊天室创建成功')
    // 跳转到聊天页面
    router.push(`/chat/${response.data.id}`)
  } catch (error) {
    console.error('创建聊天失败:', error)
    message.error('创建聊天失败')
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