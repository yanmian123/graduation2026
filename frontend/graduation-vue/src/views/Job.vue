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
          <label class="filter-label">招聘类型</label>
          <n-select 
            v-model:value="filterRecruitType" 
            :options="recruitTypeOptions" 
            placeholder="选择招聘类型"
            clearable
          />
        </div>
        <div class="filter-group">
          <label class="filter-label">职位类别</label>
          <n-cascader 
            v-model:value="filterJobCategory" 
            placeholder="选择职位类别"
            :options="jobCategoryOptions"
            check-strategy="child"
            clearable
          />
        </div>
        <div class="filter-group">
          <label class="filter-label">工作地点</label>
          <n-cascader 
            v-model:value="filterLocation" 
            placeholder="选择工作地点"
            :options="locationOptions"
            check-strategy="child"
            clearable
          />
        </div>
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

  <Pagination 
    v-if="filteredJobs.length > 0"
    :current-page="currentPage"
    :total-pages="totalPages"
    :page-size="pageSize"
    @update:current-page="handlePageChange"
    @update:page-size="handlePageSizeChange"
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
  NIcon,
  NCascader
} from 'naive-ui'
import { DocumentText } from '@vicons/ionicons5'
import axios from '@/utils/axios' 
import JobCard from '@/components/common/JobCard.vue'
import Pagination from '@/components/common/Pagination.vue'

const router = useRouter()
const message = useMessage()

const allJobs = ref([]) // 所有招聘信息

const filterRecruitType = ref(null)
const filterJobCategory = ref(null)
const filterLocation = ref(null)

const recruitTypeOptions = [
  { label: '校招', value: 'CAMPUS' },
  { label: '社招', value: 'SOCIAL' },
  { label: '实习', value: 'INTERNSHIP' }
]

const jobCategoryOptions = [
  {
    label: '软件开发',
    value: 'SOFTWARE',
    children: [
      { label: '后端开发', value: 'BACKEND' },
      { label: '前端开发', value: 'FRONTEND' },
      { label: '移动开发', value: 'MOBILE' }
    ]
  },
  {
    label: '测试',
    value: 'TEST',
    children: []
  },
  {
    label: '运维',
    value: 'DEVOPS',
    children: []
  },
  {
    label: '产品',
    value: 'PRODUCT',
    children: []
  },
  {
    label: '设计',
    value: 'DESIGN',
    children: []
  },
  {
    label: '市场',
    value: 'MARKETING',
    children: []
  },
  {
    label: '销售',
    value: 'SALES',
    children: []
  },
  {
    label: '人力资源',
    value: 'HR',
    children: []
  },
  {
    label: '财务',
    value: 'FINANCE',
    children: []
  },
  {
    label: '其他',
    value: 'OTHER',
    children: []
  }
]

const locationOptions = [
  {
    label: '北京',
    value: '北京',
    children: [
      { label: '朝阳区', value: '朝阳区' },
      { label: '海淀区', value: '海淀区' },
      { label: '东城区', value: '东城区' },
      { label: '西城区', value: '西城区' },
      { label: '丰台区', value: '丰台区' },
      { label: '石景山区', value: '石景山区' },
      { label: '通州区', value: '通州区' },
      { label: '顺义区', value: '顺义区' },
      { label: '昌平区', value: '昌平区' },
      { label: '大兴区', value: '大兴区' }
    ]
  },
  {
    label: '上海',
    value: '上海',
    children: [
      { label: '黄浦区', value: '黄浦区' },
      { label: '徐汇区', value: '徐汇区' },
      { label: '长宁区', value: '长宁区' },
      { label: '静安区', value: '静安区' },
      { label: '普陀区', value: '普陀区' },
      { label: '虹口区', value: '虹口区' },
      { label: '杨浦区', value: '杨浦区' },
      { label: '浦东新区', value: '浦东新区' },
      { label: '闵行区', value: '闵行区' },
      { label: '宝山区', value: '宝山区' },
      { label: '嘉定区', value: '嘉定区' },
      { label: '松江区', value: '松江区' }
    ]
  },
  {
    label: '广州',
    value: '广州',
    children: [
      { label: '天河区', value: '天河区' },
      { label: '越秀区', value: '越秀区' },
      { label: '海珠区', value: '海珠区' },
      { label: '荔湾区', value: '荔湾区' },
      { label: '白云区', value: '白云区' },
      { label: '黄埔区', value: '黄埔区' },
      { label: '番禺区', value: '番禺区' },
      { label: '花都区', value: '花都区' },
      { label: '南沙区', value: '南沙区' },
      { label: '增城区', value: '增城区' },
      { label: '从化区', value: '从化区' }
    ]
  },
  {
    label: '深圳',
    value: '深圳',
    children: [
      { label: '福田区', value: '福田区' },
      { label: '罗湖区', value: '罗湖区' },
      { label: '南山区', value: '南山区' },
      { label: '盐田区', value: '盐田区' },
      { label: '宝安区', value: '宝安区' },
      { label: '龙岗区', value: '龙岗区' },
      { label: '龙华区', value: '龙华区' },
      { label: '坪山区', value: '坪山区' },
      { label: '光明区', value: '光明区' },
      { label: '大鹏新区', value: '大鹏新区' }
    ]
  },
  {
    label: '杭州',
    value: '杭州',
    children: [
      { label: '上城区', value: '上城区' },
      { label: '拱墅区', value: '拱墅区' },
      { label: '西湖区', value: '西湖区' },
      { label: '滨江区', value: '滨江区' },
      { label: '萧山区', value: '萧山区' },
      { label: '余杭区', value: '余杭区' },
      { label: '临平区', value: '临平区' },
      { label: '钱塘区', value: '钱塘区' },
      { label: '富阳区', value: '富阳区' },
      { label: '临安区', value: '临安区' }
    ]
  },
  {
    label: '成都',
    value: '成都',
    children: [
      { label: '锦江区', value: '锦江区' },
      { label: '青羊区', value: '青羊区' },
      { label: '金牛区', value: '金牛区' },
      { label: '武侯区', value: '武侯区' },
      { label: '成华区', value: '成华区' },
      { label: '龙泉驿区', value: '龙泉驿区' },
      { label: '青白江区', value: '青白江区' },
      { label: '新都区', value: '新都区' },
      { label: '温江区', value: '温江区' },
      { label: '双流区', value: '双流区' },
      { label: '郫都区', value: '郫都区' }
    ]
  }
]

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
  let result = allJobs.value
  
  // 按招聘类型筛选
  if (filterRecruitType.value) {
    result = result.filter(job => job.recruit_type === filterRecruitType.value)
  }
  
  // 按职位类别筛选
  if (filterJobCategory.value && filterJobCategory.value.length > 0) {
    const selectedCategory = filterJobCategory.value[filterJobCategory.value.length - 1]
    result = result.filter(job => job.job_category === selectedCategory)
  }
  
  // 按工作地点筛选
  if (filterLocation.value && filterLocation.value.length > 0) {
    const selectedLocation = filterLocation.value.join('')
    result = result.filter(job => job.work_location && job.work_location.includes(selectedLocation))
  }
  
  return result
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
  filterRecruitType.value = null
  filterJobCategory.value = null
  filterLocation.value = null
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