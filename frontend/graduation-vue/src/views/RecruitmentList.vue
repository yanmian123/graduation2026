<template>
  <div class="recruitment-list-page">
    <!-- 使用修复后的手动表格组件 -->
    <n-card>
      <manual-table 
        :data="recruitments" 
        :columns="columns"
        :bordered="true"
      />
    </n-card>
  </div>
</template>



<script setup>
import { h, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  NDataTable, NButton, NCard, NTag, NSpace, 
  useMessage 
} from 'naive-ui'
import axios from '@/utils/axios'

// ✅ 修复后的手动表格组件
const ManualTable = (props) => {
  console.log('🔧 ManualTable渲染，数据量:', props.data?.length)
  return h(NDataTable, {
    data: props.data,
    columns: props.columns,
    bordered: props.bordered,
    style: { width: '100%' },
    'row-key': (row) => row.id
  })
}

// 验证组件导入
console.log('🔍 组件导入检查:', {
  NDataTable: NDataTable ? '✅ 已导入' : '❌ 未定义',
  ManualTable: ManualTable ? '✅ 已定义' : '❌ 未定义'
})

const router = useRouter()
const message = useMessage()
const recruitments = ref([])
const loading = ref(false)
console.log('Naive UI检查:', {
  naive: window.naive,
  NTable: window.NTable
})
// 列定义保持不变
const columns = ref([
  {
    title: '标题',
    key: 'title',
    width: 200,
    ellipsis: { tooltip: true }
  },
  {
    title: '岗位名称',
    key: 'job',
    ellipsis: { tooltip: true }
  },
  {
    title: '工作地点',
    key: 'work_location',
    ellipsis: { tooltip: true }
  },
  {
    title: '薪资',
    key: 'salary',
    width: 120
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row) => {
      return h(NTag, {
        type: row.status === 'PUBLISHED' ? 'success' : 
              row.status === 'DRAFT' ? 'warning' : 'default'
      }, () => row.status === 'PUBLISHED' ? '已发布' : 
               row.status === 'DRAFT' ? '草稿' : '其他')
    }
  },
  {
    title: '发布时间',
    key: 'created_at',
    width: 180,
    render: (row) => new Date(row.created_at).toLocaleDateString()
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    render: (row) => {
      return h(NSpace, { size: 'small' }, () => [
        h(NButton, {
          text: true,
          size: 'small',
          onClick: () => handleEdit(row.id)
        }, () => '编辑'),
        h(NButton, {
          text: true,
          size: 'small',
          onClick: () => handleTogglePublish(row)
        }, () => row.status === 'PUBLISHED' ? '下架' : '发布'),
        h(NButton, {
          text: true,
          size: 'small',
          type: 'error',
          onClick: () => handleDelete(row.id)
        }, () => '删除')
      ])
    }
  }
])




// 数据获取和方法保持不变
const fetchRecruitments = async () => {
  try {
    loading.value = true
    const response = await axios.get('/recruitments/')
    recruitments.value = response.data
    console.log('📊 数据加载完成，条数:', recruitments.value.length)
  } catch (error) {
    console.error('❌ 数据加载失败:', error)
    message.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const handleEdit = (id) => {
  router.push(`/enterprise/recruitments/${id}/edit`)
}

const handleTogglePublish = async (row) => {
  try {
    const newStatus = row.status === 'PUBLISHED' ? 'DRAFT' : 'PUBLISHED'
    await axios.patch(`/recruitments/${row.id}/`, { status: newStatus })
    row.status = newStatus
    message.success('状态更新成功')
  } catch (error) {
    message.error('操作失败')
  }
}

const handleDelete = async (id) => {
  if (confirm('确定删除吗？')) {
    try {
      await axios.delete(`/recruitments/${id}/`)
      recruitments.value = recruitments.value.filter(item => item.id !== id)
      message.success('删除成功')
    } catch (error) {
      message.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchRecruitments()
})
</script>