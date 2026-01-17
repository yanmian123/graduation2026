import { createRouter, createWebHistory } from 'vue-router'
import Register from '../views/Register.vue'  // 假设新建了注册页面   // 假设新建了登录页面
import Login from '../views/Login.vue'
import UserInfo from '@/views/UserInfo.vue'
// 新增：导入简历页面（后续需创建这些组件）
import ResumeList from '@/views/ResumeList.vue'; // 简历列表
import ResumeCreate from '@/views/ResumeCreate.vue'; // 创建简历
import ResumeEdit from '@/views/ResumeEdit.vue'; // 编辑简历
import Home from '@/views/Home.vue';
import Home1 from '@/views/Home1.vue'
import Jobs from '@/views/Job.vue'
import CommunityIndex from '@/views/CommunityIndex.vue';
// import ResumeDetail from '@/views/ResumeDetail.vue'; // 查看简历
import CommunityCreate from '@/views/CommunityCreate.vue'; // 创建帖子
import articlesdetail from '@/views/articlesdetail.vue'; //帖子详情
import EnterpriseRegister from '@/views/EnterpriseRegister.vue'; //企业注册
import EnterpriseEdit from '@/views/EnterpriseEdit.vue'; //企业信息编辑
import RecruitmentList from '@/views/RecruitmentList.vue'; //招聘信息列表
import RecruitmentCreate from '@/views/RecruitmentCreate.vue'; //创建招聘信息
import RecruitmentEdit from '@/views/RecruitmentEdit.vue'; //编辑招聘信息
import Enterprisehome from '@/views/Enterprise-home.vue'; //企业首页
import Enterpriselogin from '@/views/Enterpriselogin.vue'; //企业登录
import ApplicationList from '@/views/ApplicationList.vue';//应聘者简历接收列表
import ChatView from '@/views/ChatView.vue'; //聊天页面
import NotificationCenter from '@/views/NotificationCenter.vue'; //通知中心页面
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/register', name: 'Register', component: Register,meta: { requiresAuth: false, layout:'empty'} },  // 注册页面路由,添加隐藏布局标识(隐藏导航和页脚)
    { path: '/login', name: 'Login', component: Login,meta: { requiresAuth: false, layout:'empty' }  },  // 登录页面路由,添加隐藏布局标识(隐藏导航和页脚)
    {path:'/userinfo',name:'UserInfo',component: UserInfo,meta: { requiresAuth: true,layout:'default' }}, //用户信息页面路由(标记需要登录才能访问)
    {path:'/notifications',name:'NotificationCenter',component: NotificationCenter,meta: { requiresAuth: true,layout:'default' }}, //通知中心页面路由
    // 新增：简历路由
    { path: '/resumes', name: 'ResumeList', component: ResumeList, meta: { requiresAuth: true,layout:'default' } },
    { path: '/resumes/create', name: 'ResumeCreate', component: ResumeCreate, meta: { requiresAuth: true,layout:'default' } },
    { path: '/resumes/:id/edit', name: 'ResumeEdit', component: ResumeEdit, meta: { requiresAuth: true ,layout:'default'} },
    // { path: '/resumes/:id', name: 'ResumeDetail', component: ResumeDetail, meta: { requiresAuth: true } },
    {path:'/home',name:'Home',component:Home, meta: { requiresAuth: true,layout: 'default'  }},
    {path: '/home1',name: 'Home1',component: Home1},
    {path: '/jobs',name: 'jobs',component: Jobs ,meta: { requiresAuth: true ,layout: 'default'  }},
    {path:'/community',name:'CommunityIndex',component:CommunityIndex, meta: { requiresAuth: true,layout:'default' }},
    {path:'/community/articlescreate',name:'CommunityCreate',component:CommunityCreate, meta: { requiresAuth: true,layout:'default' }},
    {path:'/community/post/:id',name: 'ArticlesDetail',component: () => import('@/views/ArticlesDetail.vue'),meta: { requiresAuth: true,layout:'default' }},
    {path: '/enterprise/register', name: 'EnterpriseRegister', component:EnterpriseRegister,meta: { requiresAuth: false, layout:'empty' }},
    {path: '/enterprise',name: 'Enterprise',redirect: '/enterprise/home',meta: { layout: 'enterprise', requiresAuth: true }
  },
    {path: '/enterprise/edit', name: 'EnterpriseEdit', component: EnterpriseEdit,meta: { layout: 'enterprise', requiresAuth: true}},
    {path: '/enterprise/recruitments', name: 'RecruitmentList', component:RecruitmentList,meta: { layout: 'enterprise', requiresAuth: true }},
    {path: '/enterprise/recruitments/create', name: 'RecruitmentCreate', component:RecruitmentCreate,meta: { layout: 'enterprise', requiresAuth: true}},
    {path: '/enterprise/home', name: 'Enterprise-home', component:Enterprisehome,meta: { requiresAuth: true ,layout: 'enterprise'}},
    {path: '/enterprise/login', name: 'Enterpriselogin', component:Enterpriselogin,meta: { requiresAuth: false, layout:'empty' }},
    {path: '/enterprise/applications', name: 'ApplicationList', component:ApplicationList,meta: { layout: 'enterprise', requiresAuth: true }},
    {
  path: '/enterprise/talent-pool',
  name: 'TalentPool',
  component: () => import('@/views/TalentPool.vue'),
  meta: { 
    requiresAuth: true, 
    layout: 'enterprise',
    title: '人才库管理'
  }
},
{path: '/chat/:roomId?', // 添加roomId作为可选参数
  name: 'Chat', 
  component: ChatView,
  meta: { requiresAuth: true }
},
    {path: '/enterprise/recruitments/:id/edit', name: 'RecruitmentEdit', component:RecruitmentEdit,meta: { layout: 'enterprise', requiresAuth: true }},
  ],
})


// 路由守卫：未登录用户访问需登录的页面时，跳转到登录页
router.beforeEach((to, from, next) => {

  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('accessToken');  // 假设 token 存在 localStorage 中
    if (token) {
      next();
    } else {
      next('/login');  // 未登录则跳转到登录页
    }
  } else {
    next();
  }
});



export default router
