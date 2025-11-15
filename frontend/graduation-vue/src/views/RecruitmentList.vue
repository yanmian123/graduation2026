<template>
  <div class="recruitment-list-page">
    <div class="page-header">
      <h2>我的招聘信息</h2>
      <n-button 
        type="primary" 
        @click="router.push('/enterprise/recruitments/create')"
      >
        发布新招聘
      </n-button>
    </div>
    
    <n-card>
      <n-table 
        :data="recruitments" 
        :columns="columns"
        row-key="id"
      >
        <template #status="{ row }">
          <n-tag type="success" v-if="row.is_published">已发布</n-tag>
          <n-tag type="default" v-else>未发布</n-tag>
        </template>
        
        <template #actions="{ row }">
          <n-button 
            text 
            size="small" 
            @click="handleEdit(row.id)"
          >
            编辑
          </n-button>
          <n-button 
            text 
            size="small" 
            @click="handleTogglePublish(row)"
          >
            {{ row.is_published ? '下架' : '发布' }}
          </n-button>
          <n-button 
            text 
            size="small" 
            type="error"
            @click="handleDelete(row.id)"
          >
            删除
          </n-button>
        </template>
      </n-table>
    </n-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NTable, NButton, NCard, NTag, useMessage } from 'naive-ui'
import axios from '@/utils/axios'

const recruitments = ref([])
const router = useRouter()
const message = useMessage()

const columns = [
  {
    title: '标题',
    key: 'title',
    width: 200
  },
  {
    title: '职位',
    key: 'job'
  },
  {
    title: '工作地点',
    key: 'work_location'
  },
  {
    title: '薪资',
    key: 'salary'
  },
  {
    title: '状态',
    key: 'status',
    render: 'status'
  },
  {
    title: '发布时间',
    key: 'created_at',
    width: 160
  },
  {
    title: '操作',
    key: 'actions',
    render: 'actions',
    width: 200
  }
]

// 获取招聘信息列表
const fetchRecruitments = async () => {
  try {
    const response = await axios.get('/api/recruitments/')
    recruitments.value = response.data
  } catch (error) {
    console.error('获取招聘信息失败:', error)
  }
}

// 编辑招聘信息
const handleEdit = (id) => {
  router.push(`/enterprise/recruitments/${id}/edit`)
}

// 切换发布状态
const handleTogglePublish = async (row) => {
  try {
    await axios.patch(`/api/recruitments/${row.id}/`, {
      is_published: !row.is_published
    })
    row.is_published = !row.is_published
    message.success(`招聘信息已${row.is_published ? '发布' : '下架'}`)
  } catch (error) {
    console.error('更新发布状态失败:', error)
    message.error('操作失败')
  }
}

// 删除招聘信息
const handleDelete = async (id) => {
  if (confirm('确定要删除这条招聘信息吗？')) {
    try {
      await axios.delete(`/api/recruitments/${id}/`)
      recruitments.value = recruitments.value.filter(item => item.id !== id)
      message.success('删除成功')
    } catch (error) {
      console.error('删除招聘信息失败:', error)
      message.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchRecruitments()
})
</script>

<style scoped>
.recruitment-list-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>