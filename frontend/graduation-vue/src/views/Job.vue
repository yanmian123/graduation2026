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
          <label class="filter-label">工作类型</label>
          <n-select 
            v-model:value="filterJobType" 
            :options="jobTypeOptions" 
            placeholder="选择工作类型"
            clearable
          />
        </div>
        <div class="filter-group">
          <label class="filter-label">职位类别</label>
          <n-select 
            v-model:value="filterJobCategory" 
            placeholder="选择职位类别"
            :options="jobCategoryOptions"
            clearable
          />
        </div>
        <div class="filter-group">
          <label class="filter-label">工作地点</label>
          <n-select 
            v-model:value="filterLocation" 
            placeholder="选择工作地点"
            :options="locationOptions"
            clearable
          />
        </div>
      </div>
      <div class="filters-row">
        <div class="filter-group">
          <label class="filter-label">薪资范围</label>
          <n-select 
            v-model:value="filterSalary" 
            :options="salaryOptions" 
            placeholder="选择薪资范围"
            clearable
          />
        </div>
        <div class="filter-group">
          <label class="filter-label">工作经验</label>
          <n-select 
            v-model:value="filterExperience" 
            :options="experienceOptions" 
            placeholder="选择工作经验"
            clearable
          />
        </div>
        <div class="filter-group">
          <label class="filter-label">学历要求</label>
          <n-select 
            v-model:value="filterEducation" 
            :options="educationOptions" 
            placeholder="选择学历要求"
            clearable
          />
        </div>
        <div class="filter-group">
          <label class="filter-label">企业行业</label>
          <n-select 
            v-model:value="filterIndustry" 
            :options="industryOptions" 
            placeholder="选择企业行业"
            clearable
          />
        </div>
      </div>
      <div class="filters-row">
        <div class="filter-group checkbox-group">
          <n-checkbox v-model:checked="filterUrgentOnly">
            只看急聘
          </n-checkbox>
        </div>
        <div class="filter-actions">
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
  NCheckbox
} from 'naive-ui'
import { DocumentText } from '@vicons/ionicons5'
import axios from '@/utils/axios' 
import JobCard from '@/components/common/JobCard.vue'
import Pagination from '@/components/common/Pagination.vue'

const router = useRouter()
const message = useMessage()

const allJobs = ref([]) 

const filterRecruitType = ref(null)
const filterJobType = ref(null)
const filterJobCategory = ref(null)
const filterLocation = ref(null)
const filterSalary = ref(null)
const filterExperience = ref(null)
const filterEducation = ref(null)
const filterIndustry = ref(null)
const filterUrgentOnly = ref(false)

const recruitTypeOptions = [
  { label: '校招', value: 'CAMPUS' },
  { label: '社招', value: 'SOCIAL' },
  { label: '实习', value: 'INTERNSHIP' }
]

const jobTypeOptions = [
  { label: '全职', value: 'FULL_TIME' },
  { label: '兼职', value: 'PART_TIME' },
  { label: '实习', value: 'INTERNSHIP' }
]

const salaryOptions = [
  { label: '5k以下', value: '0-5000' },
  { label: '5k-10k', value: '5000-10000' },
  { label: '10k-15k', value: '10000-15000' },
  { label: '15k-20k', value: '15000-20000' },
  { label: '20k-30k', value: '20000-30000' },
  { label: '30k以上', value: '30000-999999' }
]

const experienceOptions = [
  { label: '应届毕业生', value: 'FRESH' },
  { label: '1年以内', value: 'LESS_THAN_1' },
  { label: '1-3年', value: '1_3' },
  { label: '3-5年', value: '3_5' },
  { label: '5-10年', value: '5_10' },
  { label: '10年以上', value: 'MORE_THAN_10' }
]

const educationOptions = [
  { label: '高中及以下', value: 'HIGH_SCHOOL' },
  { label: '专科', value: 'ASSOCIATE' },
  { label: '本科', value: 'BACHELOR' },
  { label: '硕士', value: 'MASTER' },
  { label: '博士及以上', value: 'DOCTOR' }
]

const industryOptions = [
  { label: '信息技术', value: 'IT' },
  { label: '金融', value: 'FINANCE' },
  { label: '教育', value: 'EDUCATION' },
  { label: '传媒', value: 'MEDIA' },
  { label: '制造业', value: 'MANUFACTURING' },
  { label: '服务业', value: 'SERVICE' },
  { label: '其他', value: 'OTHER' }
]

const jobCategoryOptions = [
  { label: '软件开发', value: 'SOFTWARE' },
  { label: '测试', value: 'TEST' },
  { label: '运维', value: 'DEVOPS' },
  { label: '产品', value: 'PRODUCT' },
  { label: '设计', value: 'DESIGN' },
  { label: '市场', value: 'MARKETING' },
  { label: '销售', value: 'SALES' },
  { label: '人力资源', value: 'HR' },
  { label: '财务', value: 'FINANCE' },
  { label: '其他', value: 'OTHER' }
]

const locationOptions = [
  { label: '北京', value: '北京' },
  { label: '上海', value: '上海' },
  { label: '广州', value: '广州' },
  { label: '深圳', value: '深圳' },
  { label: '杭州', value: '杭州' },
  { label: '成都', value: '成都' }
]

// 添加数据获取函数
const fetchJobs = async () => {
  try {
    const response = await axios.get('/recruitments/')
    allJobs.value = response.data
    console.log('获取到的招聘数据:', response.data)
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
  
  console.log('筛选前职位数量:', result.length)
  
  // 按招聘类型筛选
  if (filterRecruitType.value) {
    result = result.filter(job => job.recruit_type === filterRecruitType.value)
    console.log('按招聘类型筛选后:', result.length)
  }
  
  // 按工作类型筛选
  if (filterJobType.value) {
    result = result.filter(job => job.job_type === filterJobType.value)
    console.log('按工作类型筛选后:', result.length)
  }
  
  // 按职位类别筛选
  if (filterJobCategory.value) {
    result = result.filter(job => job.job_category === filterJobCategory.value)
    console.log('按职位类别筛选后:', result.length, '筛选条件:', filterJobCategory.value)
  }
  
  // 按工作地点筛选
  if (filterLocation.value) {
    result = result.filter(job => job.work_location === filterLocation.value)
    console.log('按工作地点筛选后:', result.length, '筛选条件:', filterLocation.value)
  }
  
  // 按薪资范围筛选
  if (filterSalary.value) {
    const [min, max] = filterSalary.value.split('-').map(Number)
    result = result.filter(job => {
      const salary = parseSalary(job.salary)
      const inRange = salary >= min && salary <= max
      console.log(`薪资筛选: ${job.salary} -> ${salary}, 范围: ${min}-${max}, 符合: ${inRange}`)
      return inRange
    })
    console.log('按薪资范围筛选后:', result.length, '筛选条件:', filterSalary.value)
  }
  
  // 按工作经验筛选
  if (filterExperience.value) {
    result = result.filter(job => job.experience === filterExperience.value)
    console.log('按工作经验筛选后:', result.length)
  }
  
  // 按学历要求筛选
  if (filterEducation.value) {
    result = result.filter(job => job.education === filterEducation.value)
    console.log('按学历要求筛选后:', result.length)
  }
  
  // 按企业行业筛选
  if (filterIndustry.value) {
    result = result.filter(job => job.enterprise_industry === filterIndustry.value)
    console.log('按企业行业筛选后:', result.length)
  }
  
  // 只看急聘
  if (filterUrgentOnly.value) {
    result = result.filter(job => job.is_urgent === true)
    console.log('只看急聘筛选后:', result.length)
  }
  
  console.log('最终筛选结果:', result.length)
  return result
})

// 解析薪资字符串为数字
const parseSalary = (salaryStr) => {
  if (!salaryStr) return 0
  
  console.log('解析薪资:', salaryStr)
  
  // 如果是"面议"，返回一个很大的值，这样筛选时不会被排除
  if (salaryStr === '面议') {
    return 999999
  }
  
  // 处理各种薪资格式：10k-15k, 10K-15K, 10000-15000等
  const cleanStr = salaryStr.toLowerCase().replace(/k/g, '')
  
  // 如果是范围格式，取平均值
  if (cleanStr.includes('-')) {
    const parts = cleanStr.split('-')
    const min = parseFloat(parts[0].replace(/[^0-9.]/g, ''))
    const max = parseFloat(parts[1].replace(/[^0-9.]/g, ''))
    if (!isNaN(min) && !isNaN(max)) {
      const avg = (min + max) / 2
      console.log(`范围薪资: ${salaryStr} -> ${min}-${max} -> 平均: ${avg}`)
      return avg
    }
  }
  
  // 如果是单个数字
  const num = parseFloat(cleanStr.replace(/[^0-9.]/g, ''))
  console.log(`单个数字薪资: ${salaryStr} -> ${num}`)
  return isNaN(num) ? 0 : num
}

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
  filterJobType.value = null
  filterJobCategory.value = null
  filterLocation.value = null
  filterSalary.value = null
  filterExperience.value = null
  filterEducation.value = null
  filterIndustry.value = null
  filterUrgentOnly.value = false
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
  router.push(`/jobs/${job.id}`)
}
</script>

<style scoped>
.jobs-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 16px;
  color: #6b7280;
  margin: 0;
}

.filters-container {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.filters-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.filters-row:last-child {
  margin-bottom: 0;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.checkbox-group {
  align-items: center;
  justify-content: center;
}

.filter-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  align-items: center;
}

.jobs-section {
  margin-bottom: 30px;
}

.jobs-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.empty-state-icon {
  font-size: 64px;
  color: #9ca3af;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 8px 0;
}

.empty-state p {
  font-size: 16px;
  color: #6b7280;
  margin: 0 0 24px 0;
}

@media (max-width: 1024px) {
  .filters-row {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .jobs-list {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .filters-row {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .jobs-list {
    grid-template-columns: 1fr;
  }
  
  .filter-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .filter-actions button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .filters-row {
    grid-template-columns: 1fr;
  }
  
  .page-title {
    font-size: 24px;
  }
}
</style>
