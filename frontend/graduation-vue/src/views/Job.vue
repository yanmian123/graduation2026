<template>
  <div class="jobs-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">招聘信息</h1>
        <p class="page-subtitle">发现适合你的职业机会</p>
      </div>
      <n-statistic label="共找到" :value="filteredJobs.length">
        <template #suffix>个职位</template>
      </n-statistic>
    </div>

    <!-- 筛选条件 -->
    <div class="filters-container">
      <div class="filters-row">
        <div class="filter-group">
          <label class="filter-label">工作地点</label>
          <n-select 
            v-model:value="filterLocation" 
            :options="locationOptions" 
            placeholder="选择工作地点"
            clearable
          />
        </div>
        <!-- 其他筛选条件 -->
      </div>
      <div class="filters-row">
        <n-button 
          type="primary" 
          ghost 
          @click="resetFilters"
        >
          重置筛选
        </n-button>
        <n-button 
          type="primary" 
          @click="applyFilters"
        >
          应用筛选
        </n-button>
      </div>
    </div>

    <!-- 招聘信息列表 -->
    <section class="jobs-section">
      <div v-if="filteredJobs.length > 0" class="jobs-list">
        <JobCard 
          v-for="job in paginatedJobs" 
          :key="job.id" 
          :job="job"
          @click="viewJobDetail(job)"
        />
      </div>
      
      <div v-else class="empty-state">
        <n-icon class="empty-state-icon">
          <DocumentText />
        </n-icon>
        <h3>暂无符合条件的招聘信息</h3>
        <p>尝试调整筛选条件或搜索关键词</p>
        <n-button type="primary" @click="resetFilters">
          重置筛选条件
        </n-button>
      </div>
    </section>

    <!-- 分页 -->
    <!-- <Pagination 
      v-if="filteredJobs.length > 0"
      :current-page="currentPage"
      :total-pages="totalPages"
      :page-size="pageSize"
      @page-change="handlePageChange"
      @page-size-change="handlePageSizeChange"
    /> -->
    <Pagination 
    v-if="filteredJobs.length > 0"
    v-model:current-page="currentPage"
    v-model:page-size="pageSize"
    :total-pages="totalPages"
  />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { 
  NStatistic, 
  NSelect, 
  NButton, 
  NIcon 
} from 'naive-ui'
import { DocumentText } from '@vicons/ionicons5'
import axios from '@/utils/axios' 
import JobCard from '@/components/common/JobCard.vue'
import Pagination from '@/components/common/Pagination.vue'

const router = useRouter()
const message = useMessage()

const allJobs = ref([]) // 所有招聘信息
// 筛选条件

// 添加数据获取函数
const fetchJobs = async () => {
  try {
    const response = await axios.get('/recruitments/')  // 调用后端API
    allJobs.value = response.data
  } catch (error) {
    console.error('获取招聘信息失败:', error)
    message.error('数据加载失败')
  }
}

// 在组件挂载时获取数据
onMounted(() => {
  fetchJobs()
})


// 保留原有的filteredJobs和paginatedJobs计算属性
const filteredJobs = computed(() => {
  // 可添加筛选逻辑（如按地点过滤），但初始直接返回allJobs
  return allJobs.value
})
// 分页
const currentPage = ref(1)
const pageSize = ref(12)


const paginatedJobs = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize.value
  const endIndex = startIndex + pageSize.value
  return filteredJobs.value.slice(startIndex, endIndex)
})

const totalPages = computed(() => {
  return Math.ceil(filteredJobs.value.length / pageSize.value)
})

// 事件处理
const applyFilters = () => {
  currentPage.value = 1
  message.info('已应用筛选条件')
}

const resetFilters = () => {
  filterLocation.value = null
  // ... 重置其他筛选条件
  currentPage.value = 1
  message.info('已重置筛选条件')
}

const handlePageChange = (page) => {
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handlePageSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const viewJobDetail = (job) => {
  message.info(`查看职位详情: ${job.title}`)
}
</script>

<style scoped>
/* 招聘信息页面特定样式 */
</style>