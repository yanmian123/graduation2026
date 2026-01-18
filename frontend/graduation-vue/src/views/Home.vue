<template>
  <div class="home-container">
    <!-- 顶部导航栏测试111111 -->


    <!-- 主体内容区 -->
    <main class="main-content">
      <!-- Banner轮播区 -->
      <n-carousel 
        autoplay 
        interval="5000" 
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
          <div class="jobs-filter">
            <n-select 
              v-model:value="jobFilter" 
              :options="jobFilterOptions" 
              size="small"
              @update:value="handleJobFilterChange"
            />
          </div>
        </div>
        
        <div class="jobs-list">
          <div 
            v-for="job in filteredJobs" 
            :key="job.id" 
            class="job-item"
            @click="$router.push(`/jobs/${job.id}`)"
          >
            <div class="job-item-left">
              <h3>{{ job.title }}</h3>
              <p class="company">{{ job.company }}</p>
              <div class="job-meta">
                <span>{{ job.location }}</span>
                <span>{{ job.experience }}</span>
                <span>{{ job.education }}</span>
              </div>
            </div>
            <div class="job-item-right">
              <span class="job-salary">{{ job.salary }}</span>
              <span class="publish-time">{{ job.publishTime }}</span>
            </div>
          </div>
        </div>
        
        <n-button 
          type="primary" 
          ghost 
          class="load-more-btn"
          @click="loadMoreJobs"
        >
          加载更多
        </n-button>
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
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useMessage } from 'naive-ui';
import { 
  Briefcase,        // 对应 BriefcaseBusiness（商务公文包）
  Search,           // 原图标存在，无需替换
  Person,           // 原图标存在，无需替换
  DocumentText,     // 对应 FileText（文件文本）
  Book,             // 对应 BookOpen（打开的书）
  BarChart,         // 原图标存在，无需替换
  Calendar,         // 原图标存在，无需替换
  Heart,            // 原图标存在，无需替换
  Download,         // 原图标存在，无需替换
  Create,           // 对应 Edit3（编辑）
  CheckmarkCircle   // 对应 CheckCircle2（勾选圆圈）
} from '@vicons/ionicons5';  // 假设路径保持一致

import { NLayoutHeader, NMenu, NInput, NDropdown, NButton, NCarousel, NCard, NTag, NIcon, NAvatar } from 'naive-ui';
import axios from '@/utils/axios';


console.log('Naive UI检查:', {
  naive: window.naive,
  NTable: window.NTable
})
// 路由与消息提示
const router = useRouter();
const message = useMessage();

// 状态管理
const isLogin = ref(!!localStorage.getItem('accessToken'));
const userAvatar = ref('');
const searchQuery = ref('');

// 模拟数据 - Banner
const banners = [
  {
    id: 1,
    title: '2024届秋招专场',
    desc: '名企校招信息实时更新，把握最佳求职时机',
    btnText: '立即查看',
    imgUrl: 'https://picsum.photos/id/237/1200/400',
    link: '/jobs?type=autumn'
  },
  {
    id: 2,
    title: '简历模板免费领取',
    desc: '300+专业简历模板，助你脱颖而出',
    btnText: '领取模板',
    imgUrl: 'https://picsum.photos/id/239/1200/400',
    link: '/resources?type=resume'
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

// 获取最近发布的三个招聘岗位
const fetchRecommendedJobs = async () => {
  try {
    const response = await axios.get('/recruitments/');
    // 筛选已发布的招聘，并按创建时间倒序排序，取最近的3个
    const publishedJobs = response.data.filter(job => job.status === 'PUBLISHED');
    publishedJobs.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    
    // 转换API数据为前端需要的格式
    recommendedJobs.value = publishedJobs.slice(0, 3).map(job => ({
      id: job.id,
      title: job.title,
      company: job.enterprise_name || '未知企业', // 企业名称（直接使用顶级字段）
      companyLogo: job.enterprise_logo || 'https://picsum.photos/id/1/60/60', // 企业logo（直接使用顶级字段）
      salary: job.salary,
      location: job.work_location, // 工作地点
      type: job.job_type === 'FULL_TIME' ? '全职' : job.job_type === 'PART_TIME' ? '兼职' : '实习', // 工作类型
      tags: ['JavaScript', 'Vue', 'React'] // 暂时使用默认标签
    }));
    
    console.log('📊 获取推荐岗位成功，数量:', recommendedJobs.value.length);
  } catch (error) {
    console.error('❌ 获取推荐岗位失败:', error);
    // 失败时使用默认数据
    recommendedJobs.value = [
      {
        id: 1,
        title: '前端开发工程师',
        company: '字节跳动',
        companyLogo: 'https://picsum.photos/id/1/60/60',
        salary: '15k-25k',
        location: '北京',
        type: '校招',
        tags: ['JavaScript', 'Vue', 'React']
      },
      {
        id: 2,
        title: '产品经理',
        company: '腾讯',
        companyLogo: 'https://picsum.photos/id/2/60/60',
        salary: '12k-20k',
        location: '深圳',
        type: '实习',
        tags: ['需求分析', '原型设计']
      },
      {
        id: 3,
        title: '数据分析师',
        company: '阿里巴巴',
        companyLogo: 'https://picsum.photos/id/3/60/60',
        salary: '18k-30k',
        location: '杭州',
        type: '校招',
        tags: ['Python', 'SQL', '可视化']
      }
    ];
  }
};

// 招聘信息
const allJobs = ref([
  {
    id: 101,
    title: 'Java开发工程师',
    company: '华为',
    location: '深圳',
    experience: '应届毕业生',
    education: '本科',
    salary: '18k-28k',
    publishTime: '2小时前'
  },
  {
    id: 102,
    title: 'UI设计师',
    company: '网易',
    location: '杭州',
    experience: '实习',
    education: '本科',
    salary: '8k-12k',
    publishTime: '1天前'
  },
  {
    id: 103,
    title: '算法工程师',
    company: '百度',
    location: '北京',
    experience: '应届毕业生',
    education: '硕士',
    salary: '25k-40k',
    publishTime: '3天前'
  }
]);

const jobFilter = ref('all');
const jobFilterOptions = [
  { label: '全部', value: 'all' },
  { label: '校招', value: 'campus' },
  { label: '实习', value: 'intern' },
  { label: '社招', value: 'social' }
];

const filteredJobs = computed(() => {
  // 实际项目中根据筛选条件过滤
  return allJobs.value;
});

// 资源共享区
const resources = [
  {
    id: 1,
    title: '2024互联网校招面试题集',
    desc: '包含各大厂技术岗面试真题及答案解析',
    icon: Book,
    downloads: 1254,
    updateTime: '2024-09-01'
  },
  {
    id: 2,
    title: '计算机专业简历模板',
    desc: '针对计算机相关岗位设计的专业简历模板',
    icon: DocumentText,
    downloads: 3241,
    updateTime: '2024-08-20'
  },
  {
    id: 3,
    title: '2024行业薪资报告',
    desc: '各行业薪资水平分析及就业前景预测',
    icon: BarChart,
    downloads: 876,
    updateTime: '2024-09-10'
  },
  {
    id: 4,
    title: '群面技巧与案例分析',
    desc: '群面常见问题及应对策略，附实战案例',
    icon: Create,
    downloads: 983,
    updateTime: '2024-08-15'
  }
];

// 社区文章
const articles = [
  {
    id: 1,
    title: '双非本科如何逆袭进入大厂',
    excerpt: '分享我的秋招备战经验，从简历准备到面试技巧，希望能帮到同样背景的同学...',
    author: '学长Alex',
    authorAvatar: 'https://picsum.photos/id/100/40/40',
    date: '2024-09-05',
    likes: 342
  },
  {
    id: 2,
    title: '产品经理面试全流程解析',
    excerpt: '结合自己5家大厂的面试经历，整理出产品经理面试的核心考察点和准备方法...',
    author: '学姐Mia',
    authorAvatar: 'https://picsum.photos/id/101/40/40',
    date: '2024-09-01',
    likes: 289
  }
];

// 工具列表
const tools = [
  {
    id: 1,
    name: '简历生成器',
    icon: Create,
    path: '/resumes/create'
  },
  {
    id: 2,
    name: '简历诊断',
    icon: CheckmarkCircle,
    path: '/tools/resume-check'
  },
  {
    id: 3,
    name: '薪资查询',
    icon: BarChart,
    path: '/tools/salary'
  },
  {
    id: 4,
    name: '宣讲会日历',
    icon: Calendar,
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
});


const handleBannerClick = (banner) => {
  router.push(banner.link);
};

const handleResourceClick = (resource) => {
  router.push(`/resources/${resource.id}`);
};

const handleToolClick = (tool) => {
  router.push(tool.path);
};

const handleJobFilterChange = () => {
  // 实际项目中处理筛选逻辑
};

const loadMoreJobs = () => {
  // 加载更多逻辑
  message.info('加载更多招聘信息...');
};

const seeMore = (type) => {
  switch (type) {
    case 'recommendation':
      router.push('/jobs?type=recommended');
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
  border-radius: 8px;
  border: 1px solid #e8e8e8;
  overflow: hidden;
}

.job-item {
  display: flex;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #e8e8e8;
  cursor: pointer;
  transition: background-color 0.2s;
}

.job-item:hover {
  background-color: #f7f8fa;
}

.job-item:last-child {
  border-bottom: none;
}

.job-item-left h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.company {
  color: #86909c;
  font-size: 14px;
  margin: 0 0 8px 0;
}

.job-meta {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #4e5969;
}

.job-item-right {
  text-align: right;
}

.job-salary {
  color: #f53f3f;
  font-weight: 500;
  display: block;
  margin-bottom: 4px;
}

.publish-time {
  font-size: 12px;
  color: #86909c;
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

  .articles-list {
    grid-template-columns: 1fr;
  }

  .footer-links {
    flex-direction: column;
    gap: 30px;
  }
}
</style>