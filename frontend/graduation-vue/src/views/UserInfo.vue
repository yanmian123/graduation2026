<template>
  <div class="user-profile-container">
    <!-- 页头 -->
    <n-page-header :subtitle="form.personal_profile || '暂无个性签名'" @back="handleBack">
      <n-grid :cols="5">
        <n-gi>
          <n-statistic label="文章发布数" :value="stats.articleCount" />
        </n-gi>
        <n-gi>
          <n-statistic label="文章获赞数" :value="stats.likeCount" />
        </n-gi>
        <n-gi>
          <n-statistic label="粉丝数" :value="stats.followerCount">
            <template #suffix>
              <n-button text type="primary" @click="showFollowersModal = true" style="margin-left: 8px;">查看</n-button>
            </template>
          </n-statistic>
        </n-gi>
        <n-gi>
          <n-statistic label="关注数" :value="stats.followingCount">
            <template #suffix>
              <n-button text type="primary" @click="showFollowingModal = true" style="margin-left: 8px;">查看</n-button>
            </template>
          </n-statistic>
        </n-gi>
        <n-gi>
          <n-statistic label="关注的企业" :value="stats.followingEnterpriseCount">
            <template #suffix>
              <n-button text type="primary" @click="showFollowingEnterprisesModal = true" style="margin-left: 8px;">查看</n-button>
            </template>
          </n-statistic>
        </n-gi>
      </n-grid>
      <template #title>
        <a href="#" style="text-decoration: none; color: inherit">{{ form.nickname || '用户昵称' }}</a>
      </template>
      <template #header>
        <n-breadcrumb>
          <n-breadcrumb-item v-for="skill in skills" :key="skill">{{ skill }}</n-breadcrumb-item>
          <n-breadcrumb-item>{{ form.nickname || '用户昵称' }}</n-breadcrumb-item>
        </n-breadcrumb>
      </template>
      <template #avatar>
        <n-avatar
          :src="previewAvatarUrl"
          :size="80"
        />
      </template>
      <template #extra>
        <n-space>
          <n-button v-if="form.is_staff || form.is_superuser" type="warning" @click="goToAdminVerification">管理员审核</n-button>
          <n-button v-if="form.is_staff || form.is_superuser" type="error" @click="goToAdminReports">举报管理</n-button>
          <n-button type="primary" @click="goToChat">私信与求职沟通</n-button>
          <n-button @click="showEditModal = true">编辑个人信息</n-button>
        </n-space>
      </template>
      <template #footer>
        截止到 {{ new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' }) }}
      </template>
    </n-page-header>

    <!-- 标签页 -->
    <n-divider />
    <n-tabs type="segment" animated v-model:value="activeTab">
      <n-tab-pane name="publish" tab="我的发布">
        <div class="tab-content">
          <n-empty v-if="publishedArticles.length === 0" description="暂无发布内容" />
          <div v-else class="article-list">
            <n-card v-for="article in publishedArticles" :key="article.id" class="article-card" hoverable @click="openArticleDetail(article.id)">
              <h3>{{ article.title }}</h3>
              <p class="article-content">{{ stripHtmlTags(article.content) }}</p>
              <div class="article-meta">
                <span>发布时间: {{ article.created_at }}</span>
                <span>点赞数: {{ article.likes }}</span>
              </div>
            </n-card>
          </div>
        </div>
      </n-tab-pane>
      <n-tab-pane name="comments" tab="我的评论">
        <div class="tab-content">
          <n-empty v-if="comments.length === 0" description="暂无评论" />
          <div v-else class="comment-list">
            <n-card v-for="comment in comments" :key="comment.id" class="comment-card" hoverable @click="openArticleWithComment(comment)">
              <p class="article-content">{{ stripHtmlTags(comment.content) }}</p>
              <div class="comment-meta">
                <span>评论时间: {{ comment.created_at }}</span>
              </div>
            </n-card>
          </div>
        </div>
      </n-tab-pane>
      <n-tab-pane name="applications" tab="投递记录">
        <div class="tab-content">
          <n-empty v-if="applications.length === 0" description="暂无投递记录" />
          <div v-else class="application-list">
            <n-card v-for="app in applications" :key="app.id" class="application-card" hoverable @click="goToApplications">
              <h3>{{ app.position }}</h3>
              <p>公司: {{ app.company }}</p>
              <div class="application-meta">
                <span>投递时间: {{ app.created_at }}</span>
                <span>状态: {{ app.status }}</span>
              </div>
            </n-card>
          </div>
        </div>
      </n-tab-pane>
      <n-tab-pane name="favorites" tab="收藏">
        <div class="tab-content">
          <n-empty v-if="favorites.length === 0" description="暂无收藏" />
          <div v-else class="favorite-list">
            <n-card v-for="item in favorites" :key="item.id" class="favorite-card" hoverable @click="openArticleDetail(item.article_id)">
              <h3>{{ item.title }}</h3>
              <p class="article-content">{{ stripHtmlTags(item.description) }}</p>
              <div class="favorite-meta">
                <span>收藏时间: {{ item.created_at }}</span>
              </div>
            </n-card>
          </div>
        </div>
      </n-tab-pane>
    </n-tabs>

    <!-- 编辑信息弹窗 -->
    <n-modal v-model:show="showEditModal" preset="card" title="编辑个人信息" style="width: 600px;">
      <form @submit.prevent="handleSave">
        <!-- 头像上传 -->
        <div class="form-item avatar-upload">
          <label>头像：</label>
          <div class="avatar-container">
            <n-space vertical>
              <n-image 
                :src="previewAvatarUrl" 
                class="preview-avatar" 
                v-if="previewAvatarUrl"
              />
              <n-avatar size="large" v-else class="preview-avatar">
                <template #fallback>
                  <n-icon><Person /></n-icon>
                </template>
              </n-avatar>
              <n-upload
                :default-file-list="avatarFileList"
                @change="handleAvatarChange"
                :max="1"
                type="select"
              >
                <n-button type="primary" size="small">上传头像</n-button>
              </n-upload>
            </n-space>
            <div class="avatar-hint">支持 JPG、PNG 格式，大小不超过 2MB</div>
          </div>
        </div>

        <!-- 昵称 -->
        <div class="form-item">
          <label>昵称：</label>
          <n-input 
            type="text" 
            v-model:value="form.nickname" 
            placeholder="请输入昵称"
            style="width: 300px;"
          />
        </div>

        <!-- 性别 -->
        <div class="form-item">
          <label>性别：</label>
          <n-select 
            v-model:value="form.sex" 
            style="width: 300px;"
            :options="[
              { label: '男', value: 'M' },
              { label: '女', value: 'F' }
            ]"
          />
        </div>

        <!-- 年龄 -->
        <div class="form-item">
          <label>年龄：</label>
          <n-input-number 
            v-model:value="form.age" 
            placeholder="请输入年龄"
            :min="16" 
            :max="60"
            style="width: 300px;"
          />
        </div>

        <!-- 毕业院校 -->
        <div class="form-item">
          <label>毕业院校：</label>
          <n-input 
            type="text" 
            v-model:value="form.graduation_school" 
            placeholder="请输入毕业院校"
            style="width: 300px;"
          />
        </div>

        <!-- 学历 -->
        <div class="form-item">
          <label>学历：</label>
          <n-select 
            v-model:value="form.education_level" 
            style="width: 300px;"
            :options="[
              { label: '博士', value: '博士' },
              { label: '硕士', value: '硕士' },
              { label: '本科', value: '本科' },
              { label: '专科', value: '专科' },
              { label: '高中', value: '高中' },
              { label: '中专/中技', value: '中专/中技' },
              { label: '初中及以下', value: '初中及以下' }
            ]"
          />
        </div>

        <!-- 专业 -->
        <div class="form-item">
          <label>专业：</label>
          <n-input 
            type="text" 
            v-model:value="form.major" 
            placeholder="请输入专业"
            style="width: 300px;"
          />
        </div>

        <!-- 毕业年份 -->
        <div class="form-item">
          <label>毕业年份：</label>
          <n-input-number 
            v-model:value="form.graduation_year" 
            placeholder="毕业年份"
            :min="1950" 
            :max="2100"
            style="width: 300px;"
          />
        </div>

        <!-- 手机号 -->
        <div class="form-item">
          <label>手机号：</label>
          <n-input 
            type="text" 
            v-model:value="form.phone_number" 
            placeholder="请输入手机号"
            pattern="^\+?1?\d{9,15}$"
            style="width: 300px;"
          />
        </div>

        <!-- 目前状态 -->
        <div class="form-item">
          <label>目前状态：</label>
          <n-select 
            v-model:value="form.current_status" 
            style="width: 300px;"
            :options="[
              { label: '应届毕业生', value: '应届毕业生' },
              { label: '在找工作', value: '在找工作' },
              { label: '在职', value: '在职' },
              { label: '离职', value: '离职' },
              { label: '实习', value: '实习' },
              { label: '在校', value: '在校' },
              { label: '其他', value: '其他' }
            ]"
          />
        </div>

        <!-- 意向职位 -->
        <div class="form-item">
          <label>意向职位：</label>
          <n-input 
            type="text" 
            v-model:value="form.intended_position" 
            placeholder="请输入意向职位"
            style="width: 300px;"
          />
        </div>

        <!-- 期望薪资 -->
        <div class="form-item">
          <label>意向年薪：</label>
          <n-input-number 
            v-model:value="form.intended_salary" 
            placeholder="请输入意向年薪"
            :min="0"
            style="width: 300px;"
          />
        </div>

        <!-- 住址 -->
        <div class="form-item">
          <label>住址：</label>
          <n-input 
            type="text" 
            v-model:value="form.address" 
            placeholder="请输入住址"
            style="width: 300px;"
          />   
        </div>

        <!-- 意向城市 -->
        <div class="form-item">
          <label>意向城市：</label>
          <n-input 
            type="text" 
            v-model:value="form.intended_city" 
            placeholder="请输入意向城市"
            style="width: 300px;"
          /> 
        </div>

        <!-- 个人简介 -->
        <div class="form-item">
          <label>个人简介：</label>
          <n-input
            type="textarea" 
            v-model:value="form.personal_profile" 
            placeholder="请输入个人简介"
            :rows="4"
            :cols="50"
            style="width: 300px;"
          />    
        </div>

        <div class="form-actions">
          <n-button @click="showEditModal = false">取消</n-button>
          <n-button type="primary" @click="handleSave">保存修改</n-button>
        </div>
      </form>
    </n-modal>

    <!-- 粉丝列表弹窗 -->
    <n-modal v-model:show="showFollowersModal" preset="card" title="粉丝列表" style="width: 600px;">
      <n-spin :show="loadingFollowers">
        <n-empty v-if="followers.length === 0 && !loadingFollowers" description="暂无粉丝" />
        <div v-else class="user-list">
          <n-card v-for="user in followers" :key="user.id" class="user-card" hoverable @click="goToUserProfile(user.id)">
            <div class="user-info">
              <n-avatar :src="user.avatar" :size="40" />
              <div class="user-details">
                <div class="user-name">{{ user.username }}</div>
                <div class="user-nickname">{{ user.nickname || '暂无昵称' }}</div>
              </div>
            </div>
          </n-card>
        </div>
      </n-spin>
    </n-modal>

    <!-- 关注列表弹窗 -->
    <n-modal v-model:show="showFollowingModal" preset="card" title="关注列表" style="width: 600px;">
      <n-spin :show="loadingFollowing">
        <n-empty v-if="following.length === 0 && !loadingFollowing" description="暂无关注" />
        <div v-else class="user-list">
          <n-card v-for="user in following" :key="user.id" class="user-card" hoverable @click="goToUserProfile(user.id)">
            <div class="user-info">
              <n-avatar :src="user.avatar" :size="40" />
              <div class="user-details">
                <div class="user-name">{{ user.username }}</div>
                <div class="user-nickname">{{ user.nickname || '暂无昵称' }}</div>
              </div>
            </div>
          </n-card>
        </div>
      </n-spin>
    </n-modal>

    <!-- 关注的企业列表弹窗 -->
    <n-modal v-model:show="showFollowingEnterprisesModal" preset="card" title="关注的企业" style="width: 600px;">
      <n-spin :show="loadingFollowingEnterprises">
        <n-empty v-if="followingEnterprises.length === 0 && !loadingFollowingEnterprises" description="暂无关注的企业" />
        <div v-else class="enterprise-list">
          <n-card v-for="enterprise in followingEnterprises" :key="enterprise.id" class="enterprise-card" hoverable @click="goToEnterpriseProfile(enterprise.id)">
            <div class="enterprise-info">
              <n-avatar :src="enterprise.logo ? `http://localhost:8000${enterprise.logo}` : ''" :size="40" round>
                <template #fallback>
                  <n-icon><Business /></n-icon>
                </template>
              </n-avatar>
              <div class="enterprise-details">
                <div class="enterprise-name">{{ enterprise.name }}</div>
                <div class="enterprise-meta">
                  <span>{{ getIndustryText(enterprise.industry) }}</span>
                  <span>{{ getScaleText(enterprise.scale) }}</span>
                </div>
              </div>
            </div>
          </n-card>
        </div>
      </n-spin>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import axios from '@/utils/axios';
import { getUserInfo, updateUserInfo, uploadUserAvatar } from '@/api/user';
import { articleApi, applicationApi } from '@/services/api';
import { 
  NInput, NSelect, NInputNumber, NButton, NAvatar, NIcon, NUpload, 
  NSpace, useMessage, NImage, NPageHeader, NGrid, NGi, NStatistic, 
  NBreadcrumb, NBreadcrumbItem, NDivider, NTabs, NTabPane, 
  NEmpty, NCard, NModal, NSpin
} from 'naive-ui';
import { Person, Business } from '@vicons/ionicons5';

const message = useMessage();
const router = useRouter();

const showEditModal = ref(false);
const activeTab = ref('publish');

const skills = ref(['Python', 'Vue.js', 'Django']);

const stats = ref({
  articleCount: 0,
  likeCount: 0,
  followerCount: 0,
  followingCount: 0,
  followingEnterpriseCount: 0
});

const publishedArticles = ref([]);
const comments = ref([]);
const applications = ref([]);
const favorites = ref([]);

const showFollowersModal = ref(false);
const showFollowingModal = ref(false);
const showFollowingEnterprisesModal = ref(false);
const followers = ref([]);
const following = ref([]);
const followingEnterprises = ref([]);
const loadingFollowers = ref(false);
const loadingFollowing = ref(false);
const loadingFollowingEnterprises = ref(false);

const form = ref({
  nickname: '',
  sex: '',
  age: null,
  major: '',
  phone_number: '',
  graduation_school: '',
  education_level: '',
  graduation_year: null,
  current_status: '',
  intended_position: '',
  intended_salary: null,
  address: '',
  intended_city: '',
  personal_profile: '',
  avatar: '',
  is_staff: false,
  is_superuser: false,
});

const avatarFileList = ref([]);
const previewAvatarUrl = ref('');

const handleAvatarChange = (data) => {
  console.log('handleAvatarChange called with:', data);
  avatarFileList.value = data.fileList;
  
  if (avatarFileList.value.length > 0 && avatarFileList.value[0].file) {
    const file = avatarFileList.value[0].file;
    const reader = new FileReader();
    reader.onload = (e) => {
      previewAvatarUrl.value = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

const validateAvatarFile = (file) => {
  const isJPG = file.type === 'image/jpeg' || file.type === 'image/png';
  const isLt2M = file.size / 1024 / 1024 < 2;
  
  if (!isJPG) {
    message.error('只能上传 JPG/PNG 格式的图片');
    return false;
  }
  if (!isLt2M) {
    message.error('图片大小不能超过 2MB');
    return false;
  }
  
  return true;
};

const handleBack = () => {
  message.info('[onBack]');
};

onMounted(async () => {
  try {
    const response = await getUserInfo();
    const userData = response.data;
    
    if (userData.age) userData.age = Number(userData.age);
    if (userData.graduation_year) userData.graduation_year = Number(userData.graduation_year);
    if (userData.intended_salary) userData.intended_salary = Number(userData.intended_salary);
    
    form.value = userData;
    
    let avatarUrl = form.value.avatar || '';
    if (avatarUrl && !avatarUrl.startsWith('http')) {
      avatarUrl = `http://localhost:8000${avatarUrl}`;
    }
    
    previewAvatarUrl.value = avatarUrl;
    form.value.avatar = avatarUrl;
    
    if (avatarUrl) {
      avatarFileList.value = [{
        id: 'avatar',
        name: 'avatar.png',
        url: avatarUrl
      }];
    }
    
    const userInfo = {
      id: form.value.id,
      username: form.value.username,
      avatar: avatarUrl
    };
    localStorage.setItem('userInfo', JSON.stringify(userInfo));
    
    // 加载统计数据和文章
    loadStats();
  } catch (error) {
    message.error('获取用户信息失败，请重试');
    console.error(error);
  }
});

// 监听标签页切换，加载对应数据
watch(activeTab, (newTab) => {
  if (newTab === 'comments' && comments.value.length === 0) {
    loadComments();
  } else if (newTab === 'applications' && applications.value.length === 0) {
    loadApplications();
  } else if (newTab === 'favorites' && favorites.value.length === 0) {
    loadFavorites();
  }
});

const loadStats = async () => {
  try {
    // 重新获取用户信息以获取最新的follower_count和following_count
    const userResponse = await getUserInfo();
    const userData = userResponse.data;
    
    // 更新form.value中的用户信息
    form.value.follower_count = userData.follower_count || 0;
    form.value.following_count = userData.following_count || 0;
    form.value.following_enterprise_count = userData.following_enterprise_count || 0;
    
    // 获取我的文章
    const articlesRes = await articleApi.getMyArticles();
    const articles = articlesRes.data;
    
    // 计算统计数据
    stats.value = {
      articleCount: articles.length,
      likeCount: articles.reduce((sum, article) => sum + (article.like_count || 0), 0),
      followerCount: form.value.follower_count || 0,
      followingCount: form.value.following_count || 0,
      followingEnterpriseCount: form.value.following_enterprise_count || 0
    };
    
    // 设置文章数据
    publishedArticles.value = articles.map(article => ({
      id: article.id,
      title: article.title,
      content: article.content,
      created_at: article.created_at,
      likes: article.like_count
    }));
  } catch (error) {
    console.error('加载统计数据失败:', error);
  }
};

const loadComments = async () => {
  try {
    const res = await articleApi.getMyComments();
    comments.value = res.data.map(comment => ({
      id: comment.id,
      article_id: comment.article_id,
      comment_id: comment.id,
      content: comment.content,
      created_at: comment.created_at
    }));
  } catch (error) {
    console.error('加载评论失败:', error);
  }
};

const loadApplications = async () => {
  try {
    const res = await applicationApi.getMyApplications();
    applications.value = res.data.map(app => ({
      id: app.id,
      position: app.recruitment_title || '未知职位',
      company: app.enterprise_name || '未知公司',
      created_at: app.created_at,
      status: app.status
    }));
  } catch (error) {
    console.error('加载投递记录失败:', error);
  }
};

const loadFavorites = async () => {
  try {
    const res = await articleApi.getMyCollections();
    favorites.value = res.data.map(fav => ({
      id: fav.id,
      article_id: fav.article_id,
      title: fav.article_title || '未知标题',
      description: fav.article_content?.substring(0, 100) || '暂无描述',
      created_at: fav.created_at
    }));
  } catch (error) {
    console.error('加载收藏失败:', error);
  }
};

const handleSave = async () => {
  console.log('保存按钮被点击，开始执行保存逻辑');
  try {
    const submitData = { ...form.value }
    delete submitData.avatar
    delete submitData.id
    delete submitData.username

    console.log('提交的基本信息:', submitData);
    
    await updateUserInfo(submitData)
    
    if (avatarFileList.value.length > 0 && avatarFileList.value[0].file) {
      console.log('检测到头像文件，开始上传...');
      
      if (!validateAvatarFile(avatarFileList.value[0].file)) {
        return;
      }
      
      const uploadFormData = new FormData();
      uploadFormData.append('avatar', avatarFileList.value[0].file);
      
      const avatarResponse = await uploadUserAvatar(uploadFormData);
      console.log('头像上传成功，原始URL:', avatarResponse.data.avatar);
      
      let avatarUrl = avatarResponse.data.avatar;
      if (avatarUrl && !avatarUrl.startsWith('http')) {
        avatarUrl = `http://localhost:8000${avatarUrl}`;
        console.log('处理后的完整URL:', avatarUrl);
      }
      
      form.value.avatar = avatarUrl;
      previewAvatarUrl.value = avatarUrl;
      
      avatarFileList.value = [{
        id: 'avatar',
        name: 'avatar.png',
        url: avatarUrl
      }];
      
      const userInfo = {
        id: form.value.id,
        username: form.value.username,
        avatar: avatarUrl
      };
      localStorage.setItem('userInfo', JSON.stringify(userInfo));
    }
    
    message.success('信息更新成功');
    showEditModal.value = false;
  } catch (error) {
    message.error('更新失败，请检查输入');
    console.error('保存失败原因:', error);
    console.error('错误响应:', error.response);
  }
};

const loadFollowers = async () => {
  try {
    loadingFollowers.value = true;
    const res = await axios.get('/user/followers/');
    followers.value = res.data.map(user => ({
      id: user.id,
      username: user.username,
      nickname: user.nickname,
      avatar: user.avatar ? `http://localhost:8000${user.avatar}` : ''
    }));
  } catch (error) {
    console.error('加载粉丝列表失败:', error);
    followers.value = [];
  } finally {
    loadingFollowers.value = false;
  }
};

const loadFollowing = async () => {
  try {
    loadingFollowing.value = true;
    const res = await axios.get('/user/following/');
    following.value = res.data.map(user => ({
      id: user.id,
      username: user.username,
      nickname: user.nickname,
      avatar: user.avatar ? `http://localhost:8000${user.avatar}` : ''
    }));
  } catch (error) {
    console.error('加载关注列表失败:', error);
    following.value = [];
  } finally {
    loadingFollowing.value = false;
  }
};

const loadFollowingEnterprises = async () => {
  try {
    loadingFollowingEnterprises.value = true;
    const res = await axios.get('/user/following-enterprises/');
    followingEnterprises.value = res.data;
  } catch (error) {
    console.error('加载关注企业列表失败:', error);
    followingEnterprises.value = [];
  } finally {
    loadingFollowingEnterprises.value = false;
  }
};

const goToUserProfile = (userId) => {
  router.push(`/user/${userId}`);
};

const goToEnterpriseProfile = (enterpriseUserId) => {
  router.push(`/enterprise/${enterpriseUserId}`);
};

const goToChat = () => {
  router.push('/chat');
};

const goToAdminVerification = () => {
  router.push('/admin/verification');
};

const goToAdminReports = () => {
  router.push('/admin/reports');
};

const stripHtmlTags = (html) => {
  if (!html) return '';
  const div = document.createElement('div');
  div.innerHTML = html;
  return div.textContent || div.innerText || '';
};

const openArticleDetail = (articleId) => {
  window.open(`/community/post/${articleId}`, '_blank');
};

const openArticleWithComment = (comment) => {
  window.open(`/community/post/${comment.article_id}?commentId=${comment.comment_id}#comments`, '_blank');
};

const goToApplications = () => {
  router.push('/applications');
};

const getIndustryText = (industry) => {
  const industryMap = {
    'IT': '信息技术',
    'FINANCE': '金融',
    'EDUCATION': '教育',
    'MEDIA': '传媒',
    'MANUFACTURING': '制造业',
    'SERVICE': '服务业',
    'OTHER': '其他'
  };
  return industryMap[industry] || industry;
};

const getScaleText = (scale) => {
  const scaleMap = {
    'MICRO': '微型企业（<10人）',
    'SMALL': '小型企业（10-99人）',
    'MEDIUM': '中型企业（100-999人）',
    'LARGE': '大型企业（1000人以上）'
  };
  return scaleMap[scale] || scale;
};

watch(showFollowersModal, (newVal) => {
  if (newVal && followers.value.length === 0) {
    loadFollowers();
  }
});

watch(showFollowingModal, (newVal) => {
  if (newVal && following.value.length === 0) {
    loadFollowing();
  }
});

watch(showFollowingEnterprisesModal, (newVal) => {
  if (newVal && followingEnterprises.value.length === 0) {
    loadFollowingEnterprises();
  }
});
</script>

<style scoped>
.user-profile-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.form-item {
  margin: 15px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

label {
  width: 100px;
  text-align: right;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}

.avatar-upload {
  align-items: flex-start;
  padding-top: 10px;
}

.avatar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.preview-avatar {
  width: 120px;
  height: 120px;
}

.avatar-hint {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.tab-content {
  padding: 20px 0;
}

.article-card,
.comment-card,
.application-card,
.favorite-card {
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 8px;
}

.article-card:hover,
.favorite-card:hover,
.comment-card:hover,
.application-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.article-card h3,
.comment-card h3,
.application-card h3,
.favorite-card h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  line-height: 1.4;
}

.comment-card p {
  margin: 0 0 10px 0;
  color: #666;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: 60px;
}

.article-content {
  margin: 0 0 10px 0;
  color: #666;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: 60px;
}

.article-card p,
.application-card p,
.favorite-card p {
  margin: 0 0 10px 0;
  color: #666;
  line-height: 1.6;
}

.article-meta,
.comment-meta,
.application-meta,
.favorite-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
}

.user-list {
  max-height: 400px;
  overflow-y: auto;
}

.user-card {
  margin-bottom: 12px;
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-details {
  flex: 1;
}

.user-name {
  font-weight: 500;
  font-size: 14px;
}

.user-nickname {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.enterprise-list {
  max-height: 400px;
  overflow-y: auto;
}

.enterprise-card {
  margin-bottom: 12px;
  cursor: pointer;
}

.enterprise-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.enterprise-details {
  flex: 1;
}

.enterprise-name {
  font-weight: 500;
  font-size: 14px;
}

.enterprise-meta {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  display: flex;
  gap: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-details {
  flex: 1;
}

.user-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.user-nickname {
  font-size: 14px;
  color: #666;
}
</style>
