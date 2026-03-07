import { createRouter, createWebHistory } from 'vue-router'
import Register from '../views/Register.vue'
import Login from '../views/Login.vue'
import UserInfo from '@/views/UserInfo.vue'
import OtherUserProfile from '@/views/OtherUserProfile.vue'
import ResumeList from '@/views/ResumeList.vue'
import ResumeCreate from '@/views/ResumeCreate.vue'
import ResumeEdit from '@/views/ResumeEdit.vue'
import Home from '@/views/Home.vue'
import Jobs from '@/views/Job.vue'
import CommunityIndex from '@/views/CommunityIndex.vue'
import CommunityCreate from '@/views/CommunityCreate.vue'
import ArticlesDetail from '@/views/ArticlesDetail.vue'
import EnterpriseRegister from '@/views/EnterpriseRegister.vue'
import EnterpriseEdit from '@/views/EnterpriseEdit.vue'
import RecruitmentList from '@/views/RecruitmentList.vue'
import RecruitmentCreate from '@/views/RecruitmentCreate.vue'
import RecruitmentEdit from '@/views/RecruitmentEdit.vue'
import Enterprisehome from '@/views/Enterprise-home.vue'
import Enterpriselogin from '@/views/Enterpriselogin.vue'
import ApplicationList from '@/views/ApplicationList.vue'
import MyApplications from '@/views/MyApplications.vue'
import ChatView from '@/views/ChatView.vue'
import NotificationCenter from '@/views/NotificationCenter.vue'
import JobDetail from '@/views/JobDetail.vue'
import EnterpriseProfile from '@/views/EnterpriseProfile.vue'
import EnterpriseVerification from '@/views/EnterpriseVerification.vue'
import UserVerification from '@/views/UserVerification.vue'
import AdminVerification from '@/views/AdminVerification.vue'
import AdminReportManagement from '@/views/AdminReportManagement.vue'
import TalentPool from '@/views/TalentPool.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/register', name: 'Register', component: Register,meta: { requiresAuth: false, layout:'empty'} },
    { path: '/login', name: 'Login', component: Login,meta: { requiresAuth: false, layout:'empty' } },
    {path:'/userinfo',name:'UserInfo',component: UserInfo,meta: { requiresAuth: true,layout:'default' }},
    {path:'/user/:id',name:'OtherUserProfile',component: OtherUserProfile,meta: { requiresAuth: true,layout:'default' }},
    {path:'/notifications',name:'NotificationCenter',component: NotificationCenter,meta: { requiresAuth: true,layout:'default' }},
    {path:'/applications',name:'MyApplications',component: MyApplications,meta: { requiresAuth: true,layout:'default' }},
    { path: '/resumes', name: 'ResumeList', component: ResumeList, meta: { requiresAuth: true,layout:'default' } },
    { path: '/resumes/create', name: 'ResumeCreate', component: ResumeCreate, meta: { requiresAuth: true,layout:'default' } },
    { path: '/resumes/:id/edit', name: 'ResumeEdit', component: ResumeEdit, meta: { requiresAuth: true ,layout:'default'} },
    {path:'/home',name:'Home',component:Home, meta: { requiresAuth: true,layout: 'default' }},
    {path: '/jobs',name:'jobs',component: Jobs ,meta: { requiresAuth: true ,layout: 'default' }},
    {path: '/jobs/:id',name: 'JobDetail',component: JobDetail,meta: { requiresAuth: true ,layout: 'default' }},
    {path: '/enterprise/:id',name: 'EnterpriseProfile',component: EnterpriseProfile,meta: { requiresAuth: true ,layout: 'default' }},
    {path:'/community',name:'CommunityIndex',component:CommunityIndex, meta: { requiresAuth: true,layout:'default' }},
    {path:'/community/articlescreate',name:'CommunityCreate',component:CommunityCreate, meta: { requiresAuth: true,layout:'default' }},
    {path:'/community/post/:id',name: 'ArticlesDetail',component: ArticlesDetail,meta: { requiresAuth: true,layout:'default' }},
    {path: '/enterprise/register', name: 'EnterpriseRegister', component:EnterpriseRegister,meta: { requiresAuth: false, layout:'empty' }},
    {path: '/enterprise',name: 'Enterprise',redirect: '/enterprise/home',meta: { layout: 'enterprise', requiresAuth: true }},
    {path: '/enterprise/edit', name: 'EnterpriseEdit', component: EnterpriseEdit,meta: { layout: 'enterprise', requiresAuth: true}},
    {path: '/enterprise/recruitments', name: 'RecruitmentList', component:RecruitmentList,meta: { layout: 'enterprise', requiresAuth: true }},
    {path: '/enterprise/recruitments/create', name: 'RecruitmentCreate', component:RecruitmentCreate,meta: { layout: 'enterprise', requiresAuth: true}},
    {path: '/enterprise/home', name: 'Enterprise-home', component:Enterprisehome,meta: { requiresAuth: true ,layout: 'enterprise'}},
    {path: '/enterprise/login', name: 'Enterpriselogin', component:Enterpriselogin,meta: { requiresAuth: false, layout:'empty' }},
    {path: '/enterprise/applications', name: 'ApplicationList', component:ApplicationList,meta: { layout: 'enterprise', requiresAuth: true }},
    {path: '/enterprise/verification', name: 'EnterpriseVerification', component:EnterpriseVerification,meta: { layout: 'enterprise', requiresAuth: true }},
    {path: '/user/verification', name: 'UserVerification', component:UserVerification,meta: { layout: 'default', requiresAuth: true }},
    {path: '/admin/verification', name: 'AdminVerification', component:AdminVerification,meta: { layout: 'default', requiresAuth: true }},
    {path: '/admin/reports', name: 'AdminReportManagement', component:AdminReportManagement,meta: { layout: 'default', requiresAuth: true }},
    {
      path: '/enterprise/talent-pool',
      name: 'TalentPool',
      component: TalentPool,
      meta: { 
        requiresAuth: true, 
        layout: 'enterprise',
        title: '人才库管理'
      }
    },
    {
      path: '/chat/:roomId?',
      name: 'Chat', 
      component: ChatView,
      meta: { requiresAuth: true }
    },
    {path: '/enterprise/recruitments/:id/edit', name: 'RecruitmentEdit', component:RecruitmentEdit,meta: { layout: 'enterprise', requiresAuth: true }},
  ],
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('accessToken');
    if (token) {
      next();
    } else {
      next('/login');
    }
  } else {
    next();
  }
});

export default router
