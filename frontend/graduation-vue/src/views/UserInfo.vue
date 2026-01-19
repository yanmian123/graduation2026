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
          <n-statistic label="粉丝数" :value="stats.followerCount" />
        </n-gi>
        <n-gi>
          <n-statistic label="关注数" :value="stats.followingCount" />
        </n-gi>
        <n-gi>
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
          <n-button @click="showEditModal = true">编辑个人信息</n-button>
          <n-dropdown :options="options" placement="bottom-start">
            <n-button :bordered="false" style="padding: 0 4px">
              ···
            </n-button>
          </n-dropdown>
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
            <n-card v-for="article in publishedArticles" :key="article.id" class="article-card">
              <h3>{{ article.title }}</h3>
              <p>{{ article.content }}</p>
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
            <n-card v-for="comment in comments" :key="comment.id" class="comment-card">
              <p>{{ comment.content }}</p>
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
            <n-card v-for="app in applications" :key="app.id" class="application-card">
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
            <n-card v-for="item in favorites" :key="item.id" class="favorite-card">
              <h3>{{ item.title }}</h3>
              <p>{{ item.description }}</p>
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
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { getUserInfo, updateUserInfo, uploadUserAvatar } from '@/api/user';
import { articleApi, applicationApi } from '@/services/api';
import { 
  NInput, NSelect, NInputNumber, NButton, NAvatar, NIcon, NUpload, 
  NSpace, useMessage, NImage, NPageHeader, NGrid, NGi, NStatistic, 
  NBreadcrumb, NBreadcrumbItem, NDropdown, NDivider, NTabs, NTabPane, 
  NEmpty, NCard, NModal 
} from 'naive-ui';
import { Person } from '@vicons/ionicons5';

const message = useMessage();
const router = useRouter();

const showEditModal = ref(false);
const activeTab = ref('publish');

const skills = ref(['Python', 'Vue.js', 'Django']);

const stats = ref({
  articleCount: 0,
  likeCount: 0,
  followerCount: 0,
  followingCount: 0
});

const publishedArticles = ref([]);
const comments = ref([]);
const applications = ref([]);
const favorites = ref([]);

const options = [
  {
    label: '私信',
    key: '1'
  },
  {
    label: '催更',
    key: '2'
  },
  {
    label: '举报',
    key: '3'
  }
];

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
    // 获取我的文章
    const articlesRes = await articleApi.getMyArticles();
    const articles = articlesRes.data;
    
    // 计算统计数据
    stats.value = {
      articleCount: articles.length,
      likeCount: articles.reduce((sum, article) => sum + (article.like_count || 0), 0),
      followerCount: form.value.follower_count || 0,
      followingCount: form.value.following_count || 0
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
}

.article-card h3,
.comment-card h3,
.application-card h3,
.favorite-card h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
}

.article-card p,
.comment-card p,
.application-card p,
.favorite-card p {
  margin: 0 0 10px 0;
  color: #666;
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
</style>
