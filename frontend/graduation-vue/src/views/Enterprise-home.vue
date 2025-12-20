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
                <DocumentText />
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
            @click="$router.push('/enterprise/applications')"
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

                <!-- 添加调试信息 -->
      <div v-if="debug" style="background: #f0f0f0; padding: 10px; margin-bottom: 10px;">
        数据调试: {{ recentRecruitments.length }} 条记录
        <pre>{{ JSON.stringify(recentRecruitments, null, 2) }}</pre>
      </div>
          <n-data-table 
            :data="recentRecruitments" 
            :columns="recentColumns"
            :bordered="true"
            :row-key="rowKey"
          />
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
  const debug = ref(true);
  const tableLoading = ref(false);
import { h, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useMessage } from 'naive-ui';
import { 
  DocumentText,
  List, 
  Briefcase, 
  BarChart,
  LogOut,
  Settings
} from '@vicons/ionicons5';
import {  
  NButton, 
  NCard, 
  NIcon, 
  NAvatar, 
  NDataTable, 
  NSpace, 
  NTag  // 添加 NTag 导入
} from 'naive-ui';
import axios from '@/utils/axios';

// 修复1：定义 rowKey 函数
const rowKey = (row) => row.id;

// 修复2：定义 recentRecruitments 变量
const recentRecruitments = ref([]);

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

// 最近招聘的列定义
const recentColumns = [
  {
    title: '标题',
    key: 'title',
    ellipsis: { tooltip: true },
  },
  {
    title: '职位名称',
    key: 'job',
    width: 200,
    ellipsis: { tooltip: true }
  },
  {
    title: '薪资范围',
    key: 'salary',
    width: 120,
    render: (row) => {
      const salary = row.salary || '面议';
      return salary;
    }
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row) => {
      // 兼容多种状态字段
      const status = row.status || 
                   (row.is_published ? 'PUBLISHED' : 'DRAFT') || 
                   (row.published ? 'PUBLISHED' : 'DRAFT') || 
                   'DRAFT';
      
      const type = status === 'PUBLISHED' ? 'success' : 
                  status === 'DRAFT' ? 'warning' : 'default';
      const text = status === 'PUBLISHED' ? '已发布' : 
                  status === 'DRAFT' ? '草稿' : '其他';
      
      return h(NTag, { type }, { default: () => text });
    }
  },
  {
    title: '发布时间',
    key: 'created_at',
    width: 180,
    render: (row) => {
      // 处理多种日期字段
      const dateStr = row.created_at || row.publish_time || row.create_time;
      if (!dateStr) return '-';
      try {
        return new Date(dateStr).toLocaleDateString();
      } catch {
        return dateStr;
      }
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    render: (row) => {
      return h(NSpace, { size: 'small' }, {
        default: () => [
          h(NButton, {
            text: true,
            size: 'small',
            onClick: () => handleEditRecent(row.id),
            key: 'edit'
          }, { default: () => '编辑' }),
          h(NButton, {
            text: true,
            size: 'small',
            onClick: () => handleViewApplications(row.id),
            key: 'view'
          }, { default: () => '查看申请' })
        ]
      });
    }
  }
];

// 编辑最近招聘的函数
const handleEditRecent = (id) => {
  router.push(`/enterprise/recruitments/edit/${id}`);
};

// 生命周期
onMounted(async () => {
  if (isLogin.value) {
    try {
      console.log('开始获取企业信息...');
      
      // 获取企业信息
      const enterpriseRes = await axios.get('/enterprises/');
      console.log('企业信息API完整响应:', enterpriseRes);
      
      if (enterpriseRes.data) {
        let enterpriseData = enterpriseRes.data;
        
        if (Array.isArray(enterpriseData) && enterpriseData.length > 0) {
          enterpriseData = enterpriseData[0];
        }
        
        if (enterpriseData && enterpriseData.name) {
          enterpriseLogo.value = enterpriseData.logo || '';
          enterpriseName.value = enterpriseData.name;
          enterpriseDesc.value = enterpriseData.description || '';
        }
      }
      
      // 获取招聘信息
      await fetchRecentRecruitments();
      
    } catch (error) {
      console.error('获取企业数据失败:', error);
    }
  } else {
    router.push('/login');
  }
});

const fetchRecentRecruitments = async () => {
  tableLoading.value = true;
  try {
    const jobsRes = await axios.get('/recruitments/?limit=5');
    console.log('🔍 原始API响应:', jobsRes);
    
    if (jobsRes.data) {
      // 处理不同的响应格式
      let data = jobsRes.data;
      
      // 如果数据在 results 字段中
      if (jobsRes.data.results) {
        data = jobsRes.data.results;
        console.log('📊 从results字段获取数据:', data);
      }
      
      // 确保数据是数组
      if (Array.isArray(data)) {
        recentRecruitments.value = data;
        console.log('✅ 成功设置招聘数据:', recentRecruitments.value);
        
        // 检查数据结构
        if (recentRecruitments.value.length > 0) {
          console.log('📋 第一条数据示例:', recentRecruitments.value[0]);
        }
      } else {
        console.warn('⚠️ 数据不是数组格式:', data);
        recentRecruitments.value = [];
      }
      
      activeRecruitments.value = recentRecruitments.value.length;
    }
  } catch (jobError) {
    console.error('❌ 获取招聘信息失败:', jobError);
    // 设置默认数据
    recentRecruitments.value = getDefaultData();
  } finally {
    tableLoading.value = false;
    debug.value = false; // 调试完成后关闭
  }
};

// 默认数据函数
const getDefaultData = () => {
  return [
    {
      id: 1,
      title: '前端开发工程师',
      work_location: '北京',
      salary: '15k-25k',
      created_at: '2024-09-10',
      status: 'PUBLISHED'
    },
    {
      id: 2,
      title: '产品经理',
      work_location: '上海',
      salary: '20k-30k',
      created_at: '2024-09-05',
      status: 'PUBLISHED'
    }
  ];
};

// 事件处理
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