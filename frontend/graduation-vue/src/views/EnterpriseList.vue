<template>
  <div class="enterprise-list-container">
    <div class="page-header">
      <h1>企业列表</h1>
      <p class="subtitle">发现优质企业，开启职业新篇章</p>
    </div>

    <div class="search-section">
      <n-input
        v-model:value="searchKeyword"
        placeholder="搜索企业名称..."
        class="search-input"
        @keyup.enter="handleSearch"
        clearable
      >
        <template #prefix>
          <n-icon :component="Search" />
        </template>
      </n-input>
      <n-button type="primary" @click="handleSearch">搜索</n-button>
    </div>

    <div v-if="loading" class="loading-container">
      <n-spin size="large" />
      <p>加载中...</p>
    </div>

    <div v-else-if="enterprises.length === 0" class="empty-container">
      <n-icon size="64" class="empty-icon">
        <Business />
      </n-icon>
      <p>暂无企业信息</p>
    </div>

    <div v-else class="enterprise-list">
      <div 
        v-for="enterprise in enterprises"
        :key="enterprise.id"
        class="enterprise-item"
        @click="goToEnterprise(enterprise.id)"
      >
        <div class="enterprise-item-left">
          <n-avatar :src="enterprise.logo" class="enterprise-avatar" />
          <div class="enterprise-info">
            <h3>{{ enterprise.name }}</h3>
            <p class="company">{{ getIndustryText(enterprise.industry) }}</p>
            <div class="enterprise-meta">
              <span>{{ getScaleText(enterprise.scale) }}</span>
              <span>{{ enterprise.address }}</span>
            </div>
          </div>
        </div>
        <div class="enterprise-item-right">
          <span class="enterprise-count">有{{ enterprise.jobCount || 0 }}个在招职位</span>
        </div>
      </div>
    </div>

    <div v-if="enterprises.length > 0" class="pagination-container">
      <n-pagination
        v-model:page="currentPage"
        :page-count="totalPages"
        :page-size="pageSize"
        @update:page="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NInput, NButton, NAvatar, NSpin, NPagination, useMessage } from 'naive-ui'
import { Search } from '@vicons/ionicons5'
import axios from '@/utils/axios'

const router = useRouter()
const message = useMessage()

// 行业映射
const industryMap = {
  'IT': '信息技术',
  'FINANCE': '金融',
  'EDUCATION': '教育',
  'MEDIA': '传媒',
  'MANUFACTURING': '制造业',
  'SERVICE': '服务业',
  'OTHER': '其他'
};

// 规模映射
const scaleMap = {
  'MICRO': '微型企业（<10人）',
  'SMALL': '小型企业（10-99人）',
  'MEDIUM': '中型企业（100-999人）',
  'LARGE': '大型企业（1000人以上）'
};

const getIndustryText = (industry) => {
  return industryMap[industry] || industry || '未知行业';
};

const getScaleText = (scale) => {
  return scaleMap[scale] || scale || '未知规模';
};

const searchKeyword = ref('')
const enterprises = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(12)
const totalPages = ref(1)

const fetchEnterprises = async () => {
          try {
            loading.value = true
            const response = await axios.get('/enterprises/list_public/', {
              params: {
                page: currentPage.value,
                page_size: pageSize.value,
                search: searchKeyword.value || undefined
              }
            })
            
            const enterprisesData = response.data.results || response.data || []
            
            // 为每个企业获取职位数量
            const enterprisesWithJobCount = await Promise.all(
              enterprisesData.map(async (enterprise) => {
                try {
                  const jobsResponse = await axios.get(`/recruitments/?enterprise_id=${enterprise.id}`);
                  const jobs = jobsResponse.data.results || jobsResponse.data;
                  
                  // 处理logo URL
                  let logoUrl = enterprise.logo || enterprise.company_logo || '';
                  if (logoUrl && !logoUrl.startsWith('http')) {
                    logoUrl = `http://localhost:8000${logoUrl}`;
                  }
                  
                  return {
                    id: enterprise.id,
                    name: enterprise.name,
                    industry: enterprise.industry,
                    scale: enterprise.scale,
                    address: enterprise.address,
                    logo: logoUrl,
                    jobCount: jobs.length
                  };
                } catch (error) {
                  console.error(`获取企业${enterprise.id}的职位失败:`, error);
                  return {
                    id: enterprise.id,
                    name: enterprise.name,
                    industry: enterprise.industry,
                    scale: enterprise.scale,
                    address: enterprise.address,
                    logo: enterprise.logo || enterprise.company_logo || '',
                    jobCount: 0
                  };
                }
              })
            );
            
            enterprises.value = enterprisesWithJobCount
            
            if (response.data.count) {
              totalPages.value = Math.ceil(response.data.count / pageSize.value)
            } else if (response.data.results) {
              totalPages.value = Math.ceil(response.data.results.length / pageSize.value)
            }
          } catch (error) {
            console.error('获取企业列表失败:', error)
            message.error('获取企业列表失败')
          } finally {
            loading.value = false
          }
        }

const handleSearch = () => {
  currentPage.value = 1
  fetchEnterprises()
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchEnterprises()
}

const goToEnterprise = (enterpriseId) => {
  router.push(`/enterprise/${enterpriseId}`)
}

onMounted(() => {
  fetchEnterprises()
})
</script>

<style scoped>
.enterprise-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 12px 0;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.search-section {
  display: flex;
  gap: 12px;
  margin-bottom: 32px;
  justify-content: center;
}

.search-input {
  width: 400px;
}

.loading-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #999;
}

.empty-icon {
  color: #d9d9d9;
  margin-bottom: 16px;
}

/* 企业列表 */
.enterprise-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
  overflow: hidden;
  padding: 16px;
}

.enterprise-item {
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: background-color 0.2s;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 16px;
}

.enterprise-item:hover {
  background-color: #f7f8fa;
  border-color: #2d8cf0;
}

.enterprise-item-left {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.enterprise-avatar {
  width: 56px;
  height: 56px;
  flex-shrink: 0;
}

.enterprise-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1d2129;
}

.company {
  color: #86909c;
  font-size: 14px;
  margin: 0 0 8px 0;
}

.enterprise-meta {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #4e5969;
}

.enterprise-item-right {
  text-align: right;
  margin-top: 12px;
}

.enterprise-count {
  color: #2d8cf0;
  font-weight: 500;
  font-size: 15px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

@media (max-width: 768px) {
  .enterprise-list-container {
    padding: 24px 16px;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .subtitle {
    font-size: 14px;
  }
  
  .search-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input {
    width: 100%;
  }
  
  .enterprise-list {
    grid-template-columns: 1fr;
  }
}
</style>
