<template>
  <div class="user-profile-container">
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
          <n-statistic label="关注的企业" :value="stats.followingEnterpriseCount" />
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
          <n-button @click="handleFollow" :type="isFollowing ? 'default' : 'primary'">
            {{ isFollowing ? '已关注' : '关注' }}
          </n-button>
          <n-dropdown :options="options" placement="bottom-start" @select="handleDropdownSelect">
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

    <n-divider />
    <n-tabs type="segment" animated v-model:value="activeTab">
      <n-tab-pane name="publish" tab="发布">
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
      <n-tab-pane name="comments" tab="评论">
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

    <n-modal v-model:show="showReportModal" preset="card" title="举报用户" style="width: 500px">
      <n-form-item label="举报原因">
        <n-input
          v-model:value="reportForm.reason"
          type="text"
          placeholder="请输入举报原因"
          maxlength="100"
          show-count
        />
      </n-form-item>
      <n-form-item label="详细描述">
        <n-input
          v-model:value="reportForm.description"
          type="textarea"
          placeholder="请输入详细描述（选填）"
          :rows="4"
          maxlength="500"
          show-count
        />
      </n-form-item>
      <template #footer>
        <n-space justify="end">
          <n-button @click="handleReportCancel">取消</n-button>
          <n-button type="primary" @click="handleReportSubmit">提交举报</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from '@/utils/axios';
import { articleApi } from '@/services/api';
import { 
  NButton, NAvatar, NIcon, NSpace, useMessage, NPageHeader, NGrid, NGi, NStatistic, 
  NBreadcrumb, NBreadcrumbItem, NDivider, NTabs, NTabPane, 
  NEmpty, NCard, NDropdown, NModal, NInput, NFormItem
} from 'naive-ui';
import { Person } from '@vicons/ionicons5';

const message = useMessage();
const router = useRouter();
const route = useRoute();

const activeTab = ref('publish');
const isFollowing = ref(false);

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
const favorites = ref([]);

const form = ref({
  id: null,
  nickname: '',
  username: '',
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

const previewAvatarUrl = ref('');

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

const showReportModal = ref(false);
const reportForm = ref({
  reason: '',
  description: ''
});

const handleBack = () => {
  router.back();
};

const handleDropdownSelect = (key) => {
  const userId = route.params.id;
  switch (key) {
    case '1':
      message.info('私信功能开发中');
      break;
    case '2':
      message.info('催更功能开发中');
      break;
    case '3':
      showReportModal.value = true;
      break;
    default:
      break;
  }
};

const syncFollowState = (userId, isFollowing) => {
  const followState = JSON.parse(localStorage.getItem('followState') || '{}');
  followState[userId] = isFollowing;
  localStorage.setItem('followState', JSON.stringify(followState));
};

const handleFollow = async () => {
  try {
    const userId = route.params.id;
    if (isFollowing.value) {
      await axios.delete(`/user/users/${userId}/follow/`);
      message.success('取消关注成功');
      isFollowing.value = false;
      
      syncFollowState(userId, false);
    } else {
      await axios.post(`/user/users/${userId}/follow/`);
      message.success('关注成功');
      isFollowing.value = true;
      
      syncFollowState(userId, true);
    }
    await loadStats();
  } catch (error) {
    message.error('操作失败，请重试');
    console.error(error);
  }
};

onMounted(async () => {
  try {
    const userId = route.params.id;
    
    const response = await axios.get(`/user/users/${userId}/`);
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
    
    const followStatusRes = await axios.get(`/user/users/${userId}/follow_status/`);
    isFollowing.value = followStatusRes.data.is_following;
    
    loadStats();
  } catch (error) {
    message.error('获取用户信息失败，请重试');
    console.error(error);
  }
});

watch(activeTab, (newTab) => {
  if (newTab === 'comments' && comments.value.length === 0) {
    loadComments();
  } else if (newTab === 'favorites' && favorites.value.length === 0) {
    loadFavorites();
  }
});

const loadStats = async () => {
  try {
    const userId = route.params.id;
    
    const articlesRes = await articleApi.getUserArticles(userId);
    const articles = articlesRes.data;
    
    const userResponse = await axios.get(`/user/users/${userId}/`);
    const userData = userResponse.data;
    
    stats.value = {
      articleCount: articles.length,
      likeCount: articles.reduce((sum, article) => sum + (article.like_count || 0), 0),
      followerCount: userData.follower_count || 0,
      followingCount: userData.following_count || 0,
      followingEnterpriseCount: userData.following_enterprise_count || 0
    };
    
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
    const userId = route.params.id;
    const res = await articleApi.getUserComments(userId);
    comments.value = res.data.map(comment => ({
      id: comment.id,
      content: comment.content,
      created_at: comment.created_at
    }));
  } catch (error) {
    console.error('加载评论失败:', error);
  }
};

const loadFavorites = async () => {
  try {
    const userId = route.params.id;
    const res = await articleApi.getUserCollections(userId);
    favorites.value = res.data.map(item => ({
      id: item.id,
      title: item.title,
      description: item.description,
      created_at: item.created_at
    }));
  } catch (error) {
    console.error('加载收藏失败:', error);
  }
};

const handleReportSubmit = async () => {
  if (!reportForm.value.reason.trim()) {
    message.warning('请输入举报原因');
    return;
  }
  try {
    const userId = route.params.id;
    await axios.post(`/user/users/${userId}/report/`, {
      reason: reportForm.value.reason,
      description: reportForm.value.description
    });
    message.success('举报提交成功');
    showReportModal.value = false;
    reportForm.value = {
      reason: '',
      description: ''
    };
  } catch (error) {
    message.error('举报提交失败，请重试');
    console.error(error);
  }
};

const handleReportCancel = () => {
  showReportModal.value = false;
  reportForm.value = {
    reason: '',
    description: ''
  };
};
</script>

<style scoped>
.user-profile-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.form-item {
  margin-bottom: 20px;
}

.form-item label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.tab-content {
  min-height: 400px;
}

.article-list,
.comment-list,
.favorite-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.article-card,
.comment-card,
.favorite-card {
  transition: all 0.3s ease;
}

.article-card:hover,
.comment-card:hover,
.favorite-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.article-meta,
.comment-meta,
.favorite-meta {
  display: flex;
  justify-content: space-between;
  color: #999;
  font-size: 14px;
  margin-top: 12px;
}

.article-card h3 {
  margin: 0 0 8px 0;
  color: #333;
}

.article-card p {
  color: #666;
  line-height: 1.6;
}

.comment-card p {
  color: #666;
  line-height: 1.6;
}

.favorite-card h3 {
  margin: 0 0 8px 0;
  color: #333;
}

.favorite-card p {
  color: #666;
  line-height: 1.6;
}
</style>
