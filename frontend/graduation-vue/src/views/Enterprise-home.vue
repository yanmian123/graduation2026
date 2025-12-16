<template>
  <div class="enterprise-home">
    <!-- 主体内容区 -->
    <main class="main-content">
      <!-- 企业信息概览 -->
      <section class="overview-section">
        <n-card class="overview-card">
          <div class="overview-header">
            <h2>企业管理中心</h2>
            <n-button 
              type="primary" 
              size="small" 
              @click="$router.push('/enterprise/edit')"
            >
              编辑企业信息
            </n-button>
          </div>
          
          <div class="enterprise-info">
            <n-avatar :src="enterpriseLogo" size="large" class="enterprise-logo" />
            <div class="enterprise-details">
              <h3>{{ enterpriseName || '未完善企业信息' }}</h3>
              <p class="enterprise-desc">{{ enterpriseDesc || '请完善企业信息以提升曝光率' }}</p>
              <div class="enterprise-stats">
                <div class="stat-item">
                  <span class="stat-value">{{ activeRecruitments }}</span>
                  <span class="stat-label">正在招聘</span>
                </div>
                <div class="stat-item">
                  <span class="stat-value">{{ receivedResumes }}</span>
                  <span class="stat-label">收到简历</span>
                </div>
                <div class="stat-item">
                  <span class="stat-value">{{ pendingInterviews }}</span>
                  <span class="stat-label">待面试</span>
                </div>
              </div>
            </div>
          </div>
        </n-card>
      </section>

      <!-- 快捷操作区 -->
      <section class="actions-section">
        <div class="action-cards">
          <n-card 
            class="action-card" 
            hoverable
            @click="$router.push('/enterprise/recruitments/create')"
          >
            <div class="action-icon">
              <n-icon size="32" color="#18a058">
                <FileText />
              </n-icon>
            </div>
            <div class="action-info">
              <h3>发布新招聘</h3>
              <p>创建新的职位招聘信息</p>
            </div>
          </n-card>
          
          <n-card 
            class="action-card" 
            hoverable
            @click="$router.push('/enterprise/recruitments')"
          >
            <div class="action-icon">
              <n-icon size="32" color="#2080f0">
                <List />
              </n-icon>
            </div>
            <div class="action-info">
              <h3>管理招聘</h3>
              <p>查看和编辑所有招聘信息</p>
            </div>
          </n-card>
          
          <n-card 
            class="action-card" 
            hoverable
            @click="$router.push('/enterprise/resumes')"
          >
            <div class="action-icon">
              <n-icon size="32" color="#f59e0b">
                <Briefcase />
              </n-icon>
            </div>
            <div class="action-info">
              <h3>收到的简历</h3>
              <p>查看应聘者投递的简历</p>
            </div>
          </n-card>
          
          <n-card 
            class="action-card" 
            hoverable
            @click="$router.push('/enterprise/statistics')"
          >
            <div class="action-icon">
              <n-icon size="32" color="#722ed1">
                <BarChart />
              </n-icon>
            </div>
            <div class="action-info">
              <h3>招聘数据</h3>
              <p>查看招聘效果统计分析</p>
            </div>
          </n-card>
        </div>
      </section>

      <!-- 最近招聘信息 -->
      <section class="recent-jobs-section">
        <div class="section-header">
          <h2>最近发布的招聘</h2>
          <n-button text @click="$router.push('/enterprise/recruitments')">查看全部</n-button>
        </div>
        
        <n-card>
          <n-table 
            :data="recentRecruitments" 
            :columns="columns"
            row-key="id"
          >
            <!-- 状态列插槽 -->
            <template #cell(status)="{ row }">
              <n-tag type="success" v-if="row.is_published">已发布</n-tag>
              <n-tag type="default" v-else>未发布</n-tag>
            </template>
            
            <!-- 操作列插槽 -->
            <template #cell(actions)="{ row }">
              <div class="table-actions">
                <n-button 
                  text 
                  size="small" 
                  @click="$router.push(`/enterprise/recruitments/edit/${row.id}`)"
                >
                  编辑
                </n-button>
                <n-button 
                  text 
                  size="small" 
                  @click="handleViewApplications(row.id)"
                >
                  查看申请
                </n-button>
              </div>
            </template>
          </n-table>
        </n-card>
      </section>
    </main>

    <!-- 底部信息栏 -->
    <footer class="footer">
      <div class="footer-content">
        <div class="copyright">
          <p>© 2025 职享圈 版权所有 | 企业招聘管理平台</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useMessage } from 'naive-ui';
import { 
  // BriefcaseBusiness, 
  // FileText, 
  List, 
  Briefcase, 
  BarChart,
  LogOut,
  Settings
} from '@vicons/ionicons5';
import { NLayoutHeader, NMenu, NDropdown, NButton, NCard, NTag, NIcon, NAvatar, NTable } from 'naive-ui';
import axios from '@/utils/axios';

// 路由与消息提示
const router = useRouter();
const message = useMessage();

// 状态管理
const isLogin = ref(!!localStorage.getItem('accessToken'));
const enterpriseLogo = ref('');
const enterpriseName = ref('');
const enterpriseDesc = ref('');

// 统计数据
const activeRecruitments = ref(0);
const receivedResumes = ref(0);
const pendingInterviews = ref(0);

// 导航菜单配置
const menuOptions = [
  { key: 'dashboard', label: '控制台' },
  { key: 'recruitments', label: '招聘管理' },
  { key: 'resumes', label: '简历管理' },
  { key: 'statistics', label: '数据统计' }
];

// 用户下拉菜单
const userDropdownOptions = [
  { key: 'settings', label: '账号设置', icon: Settings },
  { key: 'logout', label: '退出登录', type: 'warning', icon: LogOut }
];

// 表格列定义（移除了JSX的render函数）
const columns = [
  { title: '职位名称', key: 'title' },
  { title: '工作地点', key: 'work_location' },
  { title: '薪资范围', key: 'salary' },
  { title: '发布时间', key: 'created_at' },
  { title: '状态', key: 'status' },  // 改为通过模板插槽实现
  { title: '操作', key: 'actions' }   // 改为通过模板插槽实现
];

// 最近招聘数据
const recentRecruitments = ref([
  {
    id: 1,
    title: '前端开发工程师',
    work_location: '北京',
    salary: '15k-25k',
    created_at: '2024-09-10',
    is_published: true
  },
  {
    id: 2,
    title: '产品经理',
    work_location: '上海',
    salary: '20k-30k',
    created_at: '2024-09-05',
    is_published: true
  }
]);

// 生命周期
onMounted(async () => {
  if (isLogin.value) {
    try {
      console.log('开始获取企业信息...');
      
      // 获取企业信息
      const enterpriseRes = await axios.get('/enterprises/');
      console.log('企业信息API完整响应:', enterpriseRes);
      console.log('响应数据:', enterpriseRes.data);
      
      if (enterpriseRes.data) {
        let enterpriseData = enterpriseRes.data;
        
        // 处理可能的数组响应
        if (Array.isArray(enterpriseData)) {
          if (enterpriseData.length > 0) {
            enterpriseData = enterpriseData[0];
            console.log('从数组中提取到企业数据:', enterpriseData);
          } else {
            console.log('企业信息数组为空');
            enterpriseData = null;
          }
        }
        
        if (enterpriseData && enterpriseData.name) {
          enterpriseLogo.value = enterpriseData.logo || '';
          enterpriseName.value = enterpriseData.name;
          enterpriseDesc.value = enterpriseData.description || '';
          console.log('成功设置企业信息:', {
            name: enterpriseName.value,
            desc: enterpriseDesc.value
          });
        } else {
          console.log('企业数据无效或为空');
          enterpriseName.value = '';
          enterpriseDesc.value = '';
        }
      } else {
        console.log('企业信息响应数据为空');
        enterpriseName.value = '';
        enterpriseDesc.value = '';
      }
      
      // 临时处理统计数据（避免404错误）
      activeRecruitments.value = 0;
      receivedResumes.value = 0;
      pendingInterviews.value = 0;
      
      // 获取最近招聘
      try {
        const jobsRes = await axios.get('/recruitments/?limit=5');
        if (jobsRes.data && jobsRes.data.results) {
          recentRecruitments.value = jobsRes.data.results;
          activeRecruitments.value = recentRecruitments.value.length;
        }
      } catch (jobError) {
        console.error('获取招聘信息失败:', jobError);
      }
      
    } catch (error) {
      console.error('获取企业数据失败:', error);
      // 设置默认值
      enterpriseName.value = '';
      enterpriseDesc.value = '';
    }
  } else {
    router.push('/login');
  }
});onMounted(async () => {
  if (isLogin.value) {
    try {
      console.log('开始获取企业信息...');
      
      // 获取企业信息
      const enterpriseRes = await axios.get('/enterprises/');
      console.log('企业信息API完整响应:', enterpriseRes);
      console.log('响应数据:', enterpriseRes.data);
      
      if (enterpriseRes.data) {
        let enterpriseData = enterpriseRes.data;
        
        // 处理可能的数组响应
        if (Array.isArray(enterpriseData)) {
          if (enterpriseData.length > 0) {
            enterpriseData = enterpriseData[0];
            console.log('从数组中提取到企业数据:', enterpriseData);
          } else {
            console.log('企业信息数组为空');
            enterpriseData = null;
          }
        }
        
        if (enterpriseData && enterpriseData.name) {
          enterpriseLogo.value = enterpriseData.logo || '';
          enterpriseName.value = enterpriseData.name;
          enterpriseDesc.value = enterpriseData.description || '';
          console.log('成功设置企业信息:', {
            name: enterpriseName.value,
            desc: enterpriseDesc.value
          });
        } else {
          console.log('企业数据无效或为空');
          enterpriseName.value = '';
          enterpriseDesc.value = '';
        }
      } else {
        console.log('企业信息响应数据为空');
        enterpriseName.value = '';
        enterpriseDesc.value = '';
      }
      
      // 临时处理统计数据（避免404错误）
      activeRecruitments.value = 0;
      receivedResumes.value = 0;
      pendingInterviews.value = 0;
      
      // 获取最近招聘
      try {
        const jobsRes = await axios.get('/recruitments/?limit=5');
        if (jobsRes.data && jobsRes.data.results) {
          recentRecruitments.value = jobsRes.data.results;
          activeRecruitments.value = recentRecruitments.value.length;
        }
      } catch (jobError) {
        console.error('获取招聘信息失败:', jobError);
      }
      
    } catch (error) {
      console.error('获取企业数据失败:', error);
      // 设置默认值
      enterpriseName.value = '';
      enterpriseDesc.value = '';
    }
  } else {
    router.push('/login');
  }
});

// 事件处理
const handleMenuSelect = (key) => {
  switch (key) {
    case 'dashboard':
      router.push('/enterprise');
      break;
    case 'recruitments':
      router.push('/enterprise/recruitments');
      break;
    case 'resumes':
      router.push('/enterprise/resumes');
      break;
    case 'statistics':
      router.push('/enterprise/statistics');
      break;
  }
};

const handleUserAction = (key) => {
  switch (key) {
    case 'settings':
      router.push('/enterprise/settings');
      break;
    case 'logout':
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      message.success('已退出登录');
      router.push('/login');
      break;
  }
};

const handleViewApplications = (jobId) => {
  router.push(`/enterprise/recruitments/${jobId}/applications`);
};
</script>

<style scoped>
/* 样式保持不变 */
.enterprise-home {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e5e7eb;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.logo-icon {
  margin-right: 8px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
}

.main-menu {
  flex: 1;
  margin: 0 20px;
}

.main-content {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 20px;
}

.overview-section {
  margin-bottom: 20px;
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.enterprise-info {
  display: flex;
  align-items: flex-start;
}

.enterprise-logo {
  margin-right: 16px;
}

.enterprise-details {
  flex: 1;
}

.enterprise-desc {
  color: #666;
  margin: 8px 0 16px;
}

.enterprise-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 600;
  color: #2080f0;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.actions-section {
  margin-bottom: 20px;
}

.action-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.action-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.action-card:hover {
  transform: translateY(-4px);
}

.action-icon {
  margin-bottom: 12px;
}

.recent-jobs-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-actions {
  display: flex;
  gap: 8px;
}

.footer {
  background-color: #f5f7fa;
  padding: 20px 0;
  border-top: 1px solid #e5e7eb;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  text-align: center;
}
</style>