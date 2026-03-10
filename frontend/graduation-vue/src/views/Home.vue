<template>
  <div class="home-container">
    <!-- 顶部导航栏测试111111 -->


    <!-- 主体内容区 -->
    <main class="main-content">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <n-spin size="large" />
      </div>
      
      <!-- 内容展示 -->
      <template v-else>
      <!-- Banner轮播区 -->
      <n-carousel 
        autoplay 
        :interval="5000" 
        class="banner-carousel"
        indicator-placement="bottom"
      >
        <div v-for="banner in banners" :key="banner.id" class="banner-item">
          <img :src="banner.imgUrl" :alt="banner.title" class="banner-img" />
          <div class="banner-info">
            <h2>{{ banner.title }}</h2>
            <p>{{ banner.desc }}</p>
            <n-button 
              type="primary" 
              @click="handleBannerClick(banner)"
            >
              {{ banner.btnText }}
            </n-button>
          </div>
        </div>
      </n-carousel>

      <!-- 个性化推荐区 -->
      <section class="recommendation-section">
        <div class="section-header">
          <h2>为你推荐</h2>
          <n-button text @click="seeMore('recommendation')">查看更多</n-button>
        </div>
        
        <div class="recommendation-cards">
          <n-card 
            v-for="item in recommendedJobs" 
            :key="item.id" 
            class="recommendation-card"
            hoverable
            @click="$router.push(`/jobs/${item.id}`)"
          >
            <div class="job-card-header">
              <n-avatar :src="item.companyLogo" class="company-logo" />
              <div class="job-info">
                <h3>{{ item.title }}</h3>
                <p>{{ item.company }}</p>
              </div>
            </div>
            <div class="job-details">
              <span class="salary">{{ item.salary }}</span>
              <span class="location">{{ item.location }}</span>
              <span class="type">{{ item.type }}</span>
            </div>
            <div class="job-tags">
              <n-tag v-for="tag in item.tags" :key="tag" size="small">{{ tag }}</n-tag>
            </div>
          </n-card>
        </div>
      </section>

      <!-- 招聘信息速递 -->
      <section class="jobs-section">
        <div class="section-header">
          <h2>热门招聘</h2>
          <n-button text @click="seeMore('enterprises')">查看更多</n-button>
        </div>
        
        <div class="jobs-list">
          <div 
            v-for="enterprise in enterprises" 
            :key="enterprise.id" 
            class="job-item"
            @click="$router.push(`/enterprise/${enterprise.id}`)"
          >
            <div class="job-item-left">
              <n-avatar :src="enterprise.logo" class="enterprise-avatar" />
              <div class="enterprise-info">
                <h3>{{ enterprise.name }}</h3>
                <p class="company">{{ enterprise.industry }}</p>
                <div class="job-meta">
                  <span>{{ enterprise.scale }}</span>
                  <span>{{ enterprise.location }}</span>
                </div>
              </div>
            </div>
            <div class="job-item-right">
              <span class="job-count">有{{ enterprise.jobCount }}个在招职位</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 就业资源共享区 -->
      <section class="resources-section">
        <div class="section-header">
          <h2>精选就业资源</h2>
          <n-button text @click="seeMore('resources')">查看更多</n-button>
        </div>
        
        <div class="resources-grid">
          <n-card 
            v-for="resource in resources" 
            :key="resource.id" 
            class="resource-card"
            hoverable
            @click="handleResourceClick(resource)"
          >
            <div class="resource-icon">
              <n-icon :component="resource.icon" size="24" />
            </div>
            <h3 class="resource-title">{{ resource.title }}</h3>
            <p class="resource-desc">{{ resource.desc }}</p>
            <div class="resource-meta">
              <span>{{ resource.downloads }} 下载</span>
              <span>{{ resource.updateTime }}</span>
            </div>
          </n-card>
        </div>
      </section>

      <!-- 经验交流社区 -->
      <section class="community-section">
        <div class="section-header">
          <h2>学长学姐经验分享</h2>
          <n-button text @click="seeMore('community')">进入社区</n-button>
        </div>
        
        <div class="articles-list">
          <div 
            v-for="article in articles" 
            :key="article.id" 
            class="article-item"
            @click="$router.push(`/community/${article.id}`)"
          >
            <h3 class="article-title">{{ article.title }}</h3>
            <p class="article-excerpt">{{ article.excerpt }}</p>
            <div class="article-meta">
              <span class="author">
                <n-avatar size="small" :src="article.authorAvatar" />
                {{ article.author }}
              </span>
              <span class="date">{{ article.date }}</span>
              <span class="likes">
                <n-icon size="16"><Heart /></n-icon>
                {{ article.likes }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- 就业服务工具 -->
      <section class="tools-section">
        <h2 class="section-title">就业服务工具</h2>
        <div class="tools-grid">
          <div 
            class="tool-card" 
            v-for="tool in tools" 
            :key="tool.id"
            @click="handleToolClick(tool)"
          >
            <n-icon :component="tool.icon" size="32" class="tool-icon" />
            <p class="tool-name">{{ tool.name }}</p>
          </div>
        </div>
      </section>
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, markRaw } from 'vue';
import { useRouter } from 'vue-router';
import { useMessage } from 'naive-ui';
import { 
  Briefcase,
  Search,
  Person,
  DocumentText,
  Book,
  BarChart,
  Calendar,
  Heart,
  Download,
  Create,
  CheckmarkCircle
} from '@vicons/ionicons5';
import { NLayoutHeader, NMenu, NInput, NDropdown, NButton, NCarousel, NCard, NTag, NIcon, NAvatar, NSpin, NSpace } from 'naive-ui';
import axios from '@/utils/axios';
import { articleApi } from '@/services/api';

// 路由与消息提示
const router = useRouter();
const message = useMessage();

// 状态管理
const isLogin = ref(!!sessionStorage.getItem('accessToken') || !!sessionStorage.getItem('enterpriseToken'));
const userAvatar = ref('');
const searchQuery = ref('');
const loading = ref(true);

// 模拟数据 - Banner
const banners = [
  {
    id: 1,
    title: '2024届秋招专场',
    desc: '名企校招信息实时更新，把握最佳求职时机',
    btnText: '立即查看',
    imgUrl: '/public/images/chinatelecom.jpg',
    link: '/jobs'
  },
  {
    id: 2,
    title: '简历模板免费领取',
    desc: '300+专业简历模板，助你脱颖而出',
    btnText: '领取模板',
    imgUrl: 'https://picsum.photos/id/239/1200/400',
    link: '/resumes/create'
  },
  {
    id: 3,
    title: '大厂面试经验分享',
    desc: '学长学姐亲述面试技巧，助你顺利通关',
    btnText: '查看经验',
    imgUrl: 'https://picsum.photos/id/240/1200/400',
    link: '/community?tag=interview'
  }
];

// 推荐岗位数据
const recommendedJobs = ref([]);

// 热门企业数据
const enterprises = ref([]);

// 社区文章数据
const articles = ref([]);

// 就业资源数据
const resources = ref([]);



// 工具列表
const tools = [
  {
    id: 1,
    name: '简历生成器',
    icon: markRaw(Create),
    path: '/resumes/create'
  },
  {
    id: 2,
    name: '简历诊断',
    icon: markRaw(CheckmarkCircle),
    path: '/tools/resume-check'
  },
  {
    id: 3,
    name: '薪资查询',
    icon: markRaw(BarChart),
    path: '/tools/salary'
  },
  {
    id: 4,
    name: '宣讲会日历',
    icon: markRaw(Calendar),
    path: '/events'
  }
];

// 生命周期
onMounted(async () => {
  // 检查登录状态并获取用户信息
  if (isLogin.value) {
    try {
      const res = await axios.get('user/info');
      userAvatar.value = res.data.avatar || '';
    } catch (error) {
      console.error('获取用户信息失败', error);
      localStorage.removeItem('accessToken');
      isLogin.value = false;
    }
  }
  
  // 获取推荐岗位
  await fetchRecommendedJobs();
  
  // 获取热门企业
  await fetchHotEnterprises();
  
  // 获取社区文章
  await fetchArticles();
  
  // 获取就业资源
  await fetchResources();
  
  loading.value = false;
});

// 获取推荐岗位
const fetchRecommendedJobs = async () => {
  try {
    const response = await axios.get('/recruitments/', { 
      params: { limit: 3, ordering: '-created_at' }
    });
    recommendedJobs.value = (response.data.results || response.data).slice(0, 3).map(job => ({
      id: job.id,
      title: job.title,
      company: job.enterprise?.name || '未知企业',
      companyLogo: job.enterprise?.logo || '',
      salary: job.salary,
      location: job.work_location,
      type: job.job_type,
      tags: [job.job_category, job.recruit_type]
    }));
  } catch (error) {
    console.error('获取推荐岗位失败:', error);
  }
};

// 获取热门企业
const fetchHotEnterprises = async () => {
  try {
    const response = await axios.get('/enterprises/list_public/', { 
      params: { limit: 20 }
    });
    const enterprisesData = (response.data.results || response.data).slice(0, 20);
    
    console.log('获取到的企业数据:', enterprisesData);
    
    if (enterprisesData.length === 0) {
      console.warn('没有找到任何企业数据');
      return;
    }
    
    // 为每个企业获取职位数量
    const enterprisesWithJobCount = await Promise.all(
      enterprisesData.map(async (enterprise) => {
        try {
          const jobsResponse = await axios.get(`/recruitments/?enterprise_id=${enterprise.id}`);
          const jobs = jobsResponse.data.results || jobsResponse.data;
          
          console.log(`企业 ${enterprise.name} 的职位数量:`, jobs.length);
          
          // 处理logo URL
          let logoUrl = enterprise.logo || enterprise.company_logo || '';
          if (logoUrl && !logoUrl.startsWith('http')) {
            logoUrl = `http://localhost:8000${logoUrl}`;
          }
          
          return {
            id: enterprise.id,
            name: enterprise.name,
            industry: getIndustryText(enterprise.industry),
            scale: getScaleText(enterprise.scale),
            location: enterprise.address || '未知地点',
            logo: logoUrl,
            jobCount: jobs.length,
            recruitType: jobs.length > 0 ? jobs[0].recruit_type : 'all'
          };
        } catch (error) {
          console.error(`获取企业${enterprise.id}的职位失败:`, error);
          return {
            id: enterprise.id,
            name: enterprise.name,
            industry: getIndustryText(enterprise.industry),
            scale: getScaleText(enterprise.scale),
            location: enterprise.address || '未知地点',
            logo: enterprise.logo || enterprise.company_logo || '',
            jobCount: 0,
            recruitType: 'all'
          };
        }
      })
    );
    
    console.log('处理后的企业数据:', enterprisesWithJobCount);
    
    // 按职位数量降序排序，显示职位最多的前3个企业
    enterprises.value = enterprisesWithJobCount
      .sort((a, b) => b.jobCount - a.jobCount)
      .slice(0, 3);
      
    console.log('最终显示的企业:', enterprises.value);
  } catch (error) {
    console.error('获取热门企业失败:', error);
    message.error('获取企业信息失败，请稍后重试');
  }
};

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

// 获取社区文章
const fetchArticles = async () => {
  try {
    const response = await axios.get('/posts/', { 
      params: { limit: 6, ordering: '-created_at' }
    });
    articles.value = (response.data.results || response.data).slice(0, 6).map(article => ({
      id: article.id,
      title: article.title,
      excerpt: article.content?.substring(0, 100) + '...' || '暂无简介',
      author: article.user?.username || '匿名用户',
      authorAvatar: article.user?.avatar || '',
      date: formatTime(article.created_at),
      likes: article.like_count || 0
    }));
  } catch (error) {
    console.error('获取社区文章失败:', error);
  }
};

// 获取就业资源
const fetchResources = async () => {
  try {
    // 由于系统中没有专门的资源API，这里使用模拟数据
    resources.value = [
      {
        id: 1,
        title: '简历模板大全',
        desc: '包含100+专业简历模板，涵盖各行各业',
        icon: markRaw(DocumentText),
        downloads: 12580,
        updateTime: '2024-03-01'
      },
      {
        id: 2,
        title: '面试技巧指南',
        desc: '大厂面试官亲授面试技巧和注意事项',
        icon: markRaw(Book),
        downloads: 8932,
        updateTime: '2024-02-28'
      },
      {
        id: 3,
        title: '职业规划手册',
        desc: '帮助你制定清晰的职业发展路径',
        icon: markRaw(Briefcase),
        downloads: 6754,
        updateTime: '2024-02-25'
      },
      {
        id: 4,
        title: '薪资查询工具',
        desc: '查询各行业各岗位的薪资水平',
        icon: markRaw(BarChart),
        downloads: 15432,
        updateTime: '2024-03-05'
      }
    ];
  } catch (error) {
    console.error('获取就业资源失败:', error);
  }
};

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '未知';
  const date = new Date(timeStr);
  const now = new Date();
  const diff = Math.floor((now - date) / 1000);
  
  if (diff < 60) return '刚刚';
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`;
  if (diff < 2592000) return `${Math.floor(diff / 86400)}天前`;
  
  return date.toLocaleDateString('zh-CN');
};


const handleBannerClick = (banner) => {
  router.push(banner.link);
};

const handleResourceClick = (resource) => {
  router.push(`/resources/${resource.id}`);
};

const handleToolClick = (tool) => {
  router.push(tool.path);
};

const seeMore = (type) => {
  switch (type) {
    case 'recommendation':
      router.push('/jobs?type=recommended');
      break;
    case 'enterprises':
      router.push('/enterprises');
      break;
    case 'resources':
      router.push('/resources');
      break;
    case 'community':
      router.push('/community');
      break;
  }
};
</script>

<style scoped>
/* 基础样式 */
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 16px 0 12px;
}

.section-header h2 {
  font-size: 20px;
  font-weight: 600;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.logo-icon {
  margin-right: 8px;
  color: #2d8cf0;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #1d2129;
}

.main-menu {
  flex: 1;
  margin: 0 20px;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 240px;
}

.user-avatar {
  cursor: pointer;
}

/* Banner轮播 */
.banner-carousel {
  width: 100%;
  height: 400px;
  margin: 16px 0;
  border-radius: 8px;
  overflow: hidden;
}

.banner-item {
  position: relative;
  height: 100%;
}

.banner-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.banner-info {
  position: absolute;
  top: 50%;
  left: 50px;
  transform: translateY(-50%);
  color: #fff;
  max-width: 500px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.banner-info h2 {
  font-size: 32px;
  margin-bottom: 16px;
}

.banner-info p {
  font-size: 16px;
  margin-bottom: 24px;
}

/* 推荐区域 */
.recommendation-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}

.recommendation-card {
  transition: transform 0.2s;
}

.recommendation-card:hover {
  transform: translateY(-4px);
}

.job-card-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.company-logo {
  margin-right: 12px;
}

.job-info h3 {
  margin: 0 0 4px 0;
  font-size: 16px;
}

.job-info p {
  margin: 0;
  color: #86909c;
  font-size: 14px;
}

.job-details {
  display: flex;
  gap: 12px;
  margin: 8px 0;
  font-size: 14px;
}

.salary {
  color: #f53f3f;
  font-weight: 500;
}

.job-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

/* 招聘列表 */
.jobs-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.job-item {
  display: flex;
  flex-direction: column;
  padding: 16px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  background-color: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.job-item:hover {
  background-color: #f7f8fa;
  border-color: #2d8cf0;
  box-shadow: 0 2px 8px rgba(45, 140, 240, 0.1);
}

.job-item-left {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 12px;
}

.enterprise-avatar {
  width: 56px;
  height: 56px;
  flex-shrink: 0;
}

.enterprise-info {
  flex: 1;
  min-width: 0;
}

.enterprise-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1d2129;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.company {
  color: #86909c;
  font-size: 14px;
  margin: 0 0 8px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.job-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 13px;
  color: #4e5969;
  line-height: 1.5;
}

.job-meta span {
  display: inline-flex;
  align-items: center;
}

.job-item-right {
  text-align: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e8e8e8;
}

.job-count {
  color: #2d8cf0;
  font-weight: 500;
  font-size: 14px;
  white-space: nowrap;
}

.load-more-btn {
  width: 100%;
  margin: 16px 0;
}

/* 资源共享区 */
.resources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
  gap: 16px;
}

.resource-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.resource-icon {
  color: #2d8cf0;
  margin-bottom: 12px;
}

.resource-title {
  font-size: 16px;
  margin: 0 0 8px 0;
}

.resource-desc {
  color: #4e5969;
  font-size: 14px;
  margin: 0 0 16px 0;
  flex: 1;
}

.resource-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #86909c;
}

/* 社区区域 */
.articles-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(540px, 1fr));
  gap: 16px;
}

.article-item {
  padding: 12px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.article-item:hover {
  border-color: #2d8cf0;
  box-shadow: 0 2px 8px rgba(45, 140, 240, 0.1);
}

.article-title {
  margin: 0 0 8px 0;
  font-size: 18px;
}

.article-excerpt {
  color: #4e5969;
  font-size: 14px;
  margin: 0 0 16px 0;
  display: -webkit-box;
  /* -webkit-line-clamp: 2;
  -webkit-box-orient: vertical; */
  overflow: hidden;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #86909c;
}

.author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.likes {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 工具区域 */
.tools-section {
  margin: 40px 0;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 20px;
}

.tool-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.tool-card:hover {
  background-color: #f7f8fa;
  transform: translateY(-4px);
}

.tool-icon {
  color: #2d8cf0;
  margin-bottom: 12px;
}

.tool-name {
  font-size: 14px;
  text-align: center;
}

/* 底部 */
.footer {
  background-color: #f7f8fa;
  border-top: 1px solid #e8e8e8;
  margin-top: 60px;
}

.footer-content {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.footer-logo {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
}

.footer-links {
  display: flex;
  gap: 80px;
  margin-bottom: 32px;
}

.link-group h3 {
  font-size: 16px;
  margin-bottom: 16px;
}

.link-group ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.link-group li {
  margin-bottom: 8px;
}

.link-group a {
  color: #4e5969;
  text-decoration: none;
  font-size: 14px;
}

.link-group a:hover {
  color: #2d8cf0;
}

.copyright {
  text-align: center;
  color: #86909c;
  font-size: 14px;
  padding-top: 20px;
  border-top: 1px solid #e8e8e8;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .header-content {
    height: auto;
    padding: 12px 20px;
    flex-wrap: wrap;
  }

  .main-menu {
    order: 3;
    width: 100%;
    margin: 12px 0 0 0;
  }

  .search-input {
    width: 160px;
  }

  .banner-carousel {
    height: 200px;
  }

  .banner-info {
    left: 20px;
  }

  .banner-info h2 {
    font-size: 20px;
  }

  .banner-info p {
    font-size: 14px;
    margin-bottom: 16px;
  }

  .job-item-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .enterprise-avatar {
    width: 48px;
    height: 48px;
  }

  .enterprise-info h3 {
    font-size: 16px;
  }

  .job-meta {
    flex-direction: column;
    gap: 4px;
  }

  .articles-list {
    grid-template-columns: 1fr;
  }

  .footer-links {
    flex-direction: column;
    gap: 30px;
  }
}
</style>