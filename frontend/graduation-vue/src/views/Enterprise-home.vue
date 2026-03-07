<template>
  <div class="enterprise-home">
    <!-- 主体内容区 -->
    <main class="main-content">
      <!-- 企业信息概览 -->
      <section class="overview-section">
        <n-card class="overview-card">
          
          <n-page-header subtitle="企业管理中心" @back="handleBack">
            <n-grid :cols="5">
              <n-gi>
                <n-statistic label="正在招聘" :value="activeRecruitments" />
              </n-gi>
              <n-gi>
                <n-statistic label="收到简历" :value="receivedResumes" />
              </n-gi>
              <n-gi>
                <n-statistic label="人才库" :value="talentPoolCount" />
              </n-gi>
              <n-gi>
                <n-statistic label="待面试" :value="pendingInterviews" />
              </n-gi>
              <n-gi>
                <n-statistic label="总数据" value="" />
              </n-gi>
            </n-grid>
            <template #title>
              {{ enterpriseName || '未完善企业信息' }}
            </template>
            <template #header>
              <n-breadcrumb>
                <n-breadcrumb-item>企业</n-breadcrumb-item>
                <n-breadcrumb-item>管理中心</n-breadcrumb-item>
              </n-breadcrumb>
            </template>
            <template #avatar>
              <n-avatar
                :src="enterpriseLogo"
                size="large"
              />
            </template>
            <template #extra>
              <n-space>
                <n-button @click="$router.push('/enterprise/edit')">编辑信息</n-button>
                <n-dropdown :options="options" placement="bottom-start">
                  <n-button :bordered="false" style="padding: 0 4px">
                    ···
                  </n-button>
                </n-dropdown>
              </n-space>
            </template>
          </n-page-header>
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
          <n-card 
            class="action-card" 
            hoverable
            @click="$router.push('/enterprise/talent-pool')"
          >
            <div class="action-icon">
              <n-icon size="32" color="#722ed1">
                <People />
              </n-icon>
            </div>
            <div class="action-info">
              <h3>人才库</h3>
              <p>管理企业潜在人才资源</p>
            </div>
          </n-card>
          
          <n-card 
            class="action-card" 
            hoverable
            @click="$router.push('/chat')"
          >
            <div class="action-icon">
              <n-icon size="32" color="#8b5cf6">
                <Chatbubbles />
              </n-icon>
            </div>
            <div class="action-info">
              <h3>沟通列表</h3>
              <p>查看和管理聊天对话</p>
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

      <section class="applications-section" >
        <div class="section-header">
          <h2>最近收到的简历申请</h2>
          <n-button text @click="$router.push('/enterprise/applications')">查看全部</n-button>
        </div>
        
        <n-card>
          <n-list v-if="!applicationsLoading">
<!-- 修改申请列表项的显示 -->
              <n-list-item v-for="application in applications" :key="application.id">
                
                <div class="application-content">
                  <div class="application-header">
                    <!-- 显示求职者姓名 -->
                    <span class="applicant-name">
                      {{ application.resume_name || application.applicant_name || application.job_seeker?.nickname || application.job_seeker?.username }}
                    </span>
                    <span class="apply-time">{{ formatTime(application.created_at || application.applied_at) }}</span>
                  </div>
                  
                  <div class="application-details">
                    <!-- 显示职位名称 -->
                    <span class="job-title">
                      申请职位: {{ application.recruitment_title || application.recruitment?.title }}
                    </span>
                    <n-tag v-if="application.status" :type="getStatusType(application.status)" size="small">
                      {{ getStatusText(application.status) }}
                    </n-tag>
                  </div>
                </div>
                
                <template #suffix>
                  <n-button type="primary" @click="startChat(application)">
                    联系求职者
                  </n-button>
                </template>
              </n-list-item>
          </n-list>
          
          <div v-if="applicationsLoading" class="loading-container">
            <n-spin size="small" />
            <span>加载中...</span>
          </div>
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
  const applicationsLoading = ref(false);
import { h, ref, onMounted , computed } from 'vue';
import { useRouter } from 'vue-router';
import { useMessage } from 'naive-ui';

import { useChatStore } from '@/stores/chatStore'
import { api } from '@/services/api'
import { 
  DocumentText,
  List, 
  Briefcase, 
  BarChart,
  LogOut,
  Settings,
  People,
  Chatbubbles,
} from '@vicons/ionicons5';
import {  
  NButton, 
  NCard, 
  NIcon, 
  NAvatar, 
  NDataTable, 
  NSpace, 
  NTag,  
  NPageHeader,
  NGrid,
  NGridItem,
  NStatistic,
  NBreadcrumb,
  NBreadcrumbItem,
  NDropdown
} from 'naive-ui';
import axios from '@/utils/axios';

// 修复1：定义 rowKey 函数，添加空值检查
const rowKey = (row) => row?.id;

// 修复2：定义 recentRecruitments 变量
const recentRecruitments = ref([]);
const applications = ref([])
// 路由与消息提示
const router = useRouter();
const message = useMessage();
// 初始化 chatStore
const chatStore = useChatStore()

// 状态管理
const isLogin = ref(!!localStorage.getItem('accessToken'));
const enterpriseLogo = ref('');
const enterpriseName = ref('');
const enterpriseDesc = ref('');

// 统计数据
const activeRecruitments = ref(0);
const receivedResumes = ref(0);
const pendingInterviews = ref(0);

const currentUser = computed(() => chatStore.currentUser)

const startChat = async (application) => {
  try {
    console.log('=== 开始聊天调试信息 ===');
    console.log('完整的申请数据:', application);
    
    const token = localStorage.getItem('accessToken');
    if (!token) {
      message.error('请先登录');
      return;
    }
    
    // 获取当前用户信息
    let currentUser = null;
    try {
      const enterpriseRes = await axios.get('/enterprises/');
      console.log('企业信息响应:', enterpriseRes);
      
      if (enterpriseRes.data && enterpriseRes.data.length > 0) {
        const enterprise = enterpriseRes.data[0];
        currentUser = {
          id: enterprise.user, // 企业信息中的用户ID
          username: enterprise.user_info?.username || '企业用户',
          is_enterprise: true
        };
        console.log('从企业信息获取的用户:', currentUser);
      }
    } catch (error) {
      console.error('获取企业信息失败:', error);
      currentUser = chatStore.currentUser;
    }

    if (!currentUser || !currentUser.id) {
      message.error('用户信息不完整');
      return;
    }
    
    console.log('使用企业用户 ID:', currentUser.id);
    
    // 适配数据结构：从实际字段中提取求职者信息
    // 适配数据结构：从实际字段中提取求职者信息
    let jobSeekerUserId = null;
    let jobSeekerInfo = {};
    
    if (application.job_seeker && application.job_seeker.id) {
      jobSeekerUserId = application.job_seeker.id;
      jobSeekerInfo = application.job_seeker;
    } else if (application.applicant) {
      jobSeekerUserId = application.applicant;
      jobSeekerInfo = {
        id: application.applicant,
        username: application.applicant_name || '求职者',
        nickname: application.resume_name || application.applicant_name || '求职者'
      };
    } else {
      console.error('应用数据中缺少求职者信息:', application);
      message.error('应用数据不完整，无法创建聊天');
      return;
    }
    
    console.log('求职者用户ID:', jobSeekerUserId);
    
    // 尝试获取招聘信息ID（可选）
    let recruitmentId = null;
    if (application.recruitment && application.recruitment.id) {
      recruitmentId = application.recruitment.id;
    } else if (application.recruitment_id) {
      recruitmentId = application.recruitment_id;
    }
    // 如果没有招聘信息ID，也可以创建聊天
    
    const requestData = {
      enterprise_user_id: currentUser.id,
      job_seeker_user_id: jobSeekerUserId,
    };
    
    // 只有在有招聘信息ID时才添加
    if (recruitmentId) {
      requestData.recruitment_id = recruitmentId;
    }
    
    console.log('请求数据:', JSON.stringify(requestData, null, 2));
    
    const response = await api.post('/api/chat/chatrooms/start_chat/', requestData);
    
    console.log('聊天室创建成功:', response.data);
    message.success('聊天室创建成功！');
    router.push(`/chat/${response.data.id}`);
  } catch (error) {
    console.error('=== 创建聊天室失败 ===');
    console.error('错误对象:', error);
    
    if (error.response) {
      console.error('状态码:', error.response.status);
      console.error('响应头:', error.response.headers);
      console.error('响应数据:', error.response.data);
      
      if (error.response.status === 400) {
        if (error.response.data) {
          if (typeof error.response.data === 'object') {
            console.error('错误详情:', JSON.stringify(error.response.data, null, 2));
            
            if (error.response.data.enterprise_user_id) {
              message.error(`企业用户ID错误: ${error.response.data.enterprise_user_id}`);
            } else if (error.response.data.job_seeker_user_id) {
              message.error(`求职者用户ID错误: ${error.response.data.job_seeker_user_id}`);
            } else if (error.response.data.recruitment_id) {
              message.error(`招聘信息ID错误: ${error.response.data.recruitment_id}`);
            } else if (error.response.data.detail) {
              message.error(`请求错误: ${error.response.data.detail}`);
            } else if (error.response.data.message) {
              message.error(`错误: ${error.response.data.message}`);
            } else {
              message.error('请求参数错误，请检查数据格式');
            }
          } else {
            console.error('错误响应文本:', error.response.data);
            message.error(`服务器返回错误: ${error.response.data}`);
          }
        } else {
          message.error('请求参数错误 (400)');
        }
      } else {
        message.error(`服务器错误: ${error.response.status}`);
      }
    } else if (error.request) {
      message.error('网络错误，无法连接到服务器');
    } else {
      message.error('未知错误: ' + error.message);
    }
  }
};
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
        ]
      });
    }
  }
];

// 编辑最近招聘的函数
const handleEditRecent = (id) => {
  router.push(`/enterprise/recruitments/${id}/edit`)
};

// 在 script 中添加
const talentPoolCount = ref(0)

// 获取人才库统计
const fetchTalentPoolStats = async () => {
  try {
    const response = await axios.get('/talent_pool/')
    talentPoolCount.value = response.data.count || response.data.length || 0
  } catch (error) {
    console.error('获取人才库统计失败:', error)
  }
}

// 生命周期
onMounted(async () => {
  if (isLogin.value) {
    try {
      console.log('开始获取企业信息...');
      
      // 1. 获取企业信息
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
      
      // 2. 获取招聘信息
      await fetchRecentRecruitments();
      
      // 3. 获取真实的申请数据
      await fetchApplications();
      
      await fetchTalentPoolStats();
    } catch (error) {
      console.error('获取企业数据失败:', error);
    }
  } else {
    router.push('/login');
  }
});

// 新增：获取申请记录的函数
const fetchApplications = async () => {
  applicationsLoading.value = true;
  try {
    const response = await axios.get('/applications/');
    console.log('申请记录API响应:', response);
    
    if (response.data) {
      let data = response.data;
      
      // 处理不同的响应格式
      if (response.data.results) {
        data = response.data.results;
        console.log('从results字段获取申请数据:', data);
      }
      
      if (Array.isArray(data)) {
        applications.value = data;
        console.log('成功设置申请数据:', applications.value);
        
        // 更新统计数据
        receivedResumes.value = applications.value.length;
        pendingInterviews.value = applications.value.filter(app => 
          app.status === 'pending' || app.status === 'PENDING'
        ).length;
      } else {
        console.warn('申请数据不是数组格式:', data);
        applications.value = [];
      }
    }
  } catch (error) {
    console.error('获取申请记录失败:', error);
    // 可以保留模拟数据用于开发测试
    applications.value = getMockApplications();
  } finally {
    applicationsLoading.value = false;
  }
};

// 模拟数据函数（开发阶段使用）
const getMockApplications = () => {
  return [
    {
      id: 1,
      job_seeker: {
        id: 2, // 真实的求职者用户ID
        username: 'zhangsan',
        nickname: '张三',
        avatar: ''
      },
      resume_name: '张小明', // 简历中的真实姓名
      recruitment: {
        id: 201, // 真实的招聘信息ID
        title: '前端开发工程师'
      },
      status: 'pending',
      created_at: new Date().toISOString()
    }
  ];
};

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


const getStatusType = (status) => {
  const statusMap = {
    'pending': 'warning',
    'accepted': 'success',
    'rejected': 'error',
    'reviewed': 'info'
  }
  return statusMap[status] || 'default'
}

const getStatusText = (status) => {
  const textMap = {
    'pending': '待处理',
    'accepted': '已接受',
    'rejected': '已拒绝',
    'reviewed': '已查看'
  }
  return textMap[status] || status
}

// 添加时间格式化函数（复用聊天列表的格式）
const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 24 * 60 * 60 * 1000) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else if (diff < 7 * 24 * 60 * 60 * 1000) {
    const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    return days[date.getDay()]
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}


// 修复测试聊天函数
const testStartChat = async () => {
  try {
    console.log('=== 测试聊天功能 ===');
    console.log('当前用户:', currentUser.value);
    
    if (!currentUser.value) {
      message.error('请先登录');
      return;
    }

    // 使用更完整的测试数据
    const testApplication = {
      job_seeker: {
        id: 123,
        username: 'test_user',
        nickname: '测试用户'
      },
      recruitment: {
        id: 456,
        title: '测试职位'
      }
    };

    const response = await api.post('/api/chatrooms/start_chat/', {
      enterprise_user_id: currentUser.value.id,
      job_seeker_user_id: testApplication.job_seeker.id,
      recruitment_id: testApplication.recruitment.id
    });
    
    message.success('测试聊天室创建成功！');
    console.log('测试响应:', response.data);
    router.push(`/chat/${response.data.id}`);
  } catch (error) {
    console.error('测试创建聊天室失败:', error);
    message.error('测试失败: ' + (error.response?.data?.message || error.message));
  }
};

// 处理返回按钮点击
const handleBack = () => {
  message.info('[onBack]');
};

// 下拉菜单选项
const options = [
  {
    label: '企业设置',
    key: 'settings',
    onClick: () => $router.push('/enterprise/settings')
  },
  {
    label: '查看统计',
    key: 'statistics',
    onClick: () => $router.push('/enterprise/statistics')
  },
  {
    label: '关于我们',
    key: 'about',
    onClick: () => $router.push('/enterprise/about')
  }
];
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


.applications-section {
  margin-bottom: 20px;
}

.application-content {
  flex: 1;
  margin-left: 12px;
}

.application-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.applicant-name {
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.apply-time {
  font-size: 12px;
  color: #888;
}

.application-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.job-title {
  font-size: 13px;
  color: #666;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  color: #666;
}
</style>