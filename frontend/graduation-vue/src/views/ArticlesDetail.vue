<template>
  <n-layout class="article-detail-layout">
    <!-- 顶部导航 -->
    <n-layout-header bordered class="header">
      <n-grid :x-gap="24" class="header-grid">
        <n-grid-item span="4">
          <div class="logo" @click="$router.push('/home')">
            <n-icon size="28" class="logo-icon">
              <Briefcase />
            </n-icon>
            <span class="logo-text">职享圈</span>
          </div>
        </n-grid-item>

        <n-grid-item span="12">
          <n-menu mode="horizontal" :options="menuOptions" class="main-menu" />
        </n-grid-item>

        <n-grid-item span="7">
          <div class="header-actions">
            <n-input
              v-model:value="searchQuery"
              placeholder="搜索经验分享..."
              size="small"
              class="search-input"
              :prefix="Search"
              @keyup.enter="handleSearch"
            />
            <n-button
              type="primary"
              size="small"
              class="post-btn"
              @click="$router.push('/community/articlescreate')"
            >
              发布经验
            </n-button>
          </div>
        </n-grid-item>
      </n-grid>
    </n-layout-header>

    <!-- 主体内容 -->
    <n-layout-content class="main-content">
      <n-grid :x-gap="24" :y-gap="24" class="content-grid">
        <!-- 左侧文章详情 -->
        <n-grid-item span="16" class="article-content">
          <n-card bordered class="article-card">
            <!-- 文章标题 -->
            <h1 class="article-title">{{ article.title }}</h1>

            <!-- 作者信息 -->
            <div class="author-info">
              <n-avatar :src="article.authorAvatar" class="author-avatar" />
              <div class="author-details">
                <div class="author-name">{{ article.authorName }}</div>
                <div class="author-identity">{{ article.authorIdentity }}</div>
              </div>
              <n-button
                v-if="!isFollowing"
                size="small"
                type="primary"
                @click="handleFollow"
                class="follow-btn"
              >
                关注
              </n-button>
              <n-button
                v-else
                size="small"
                ghost
                @click="handleFollow"
                class="follow-btn"
              >
                已关注
              </n-button>
            </div>

            <!-- 文章元信息 -->
            <div class="article-meta">
              <span class="publish-time">{{ article.publishTime }}</span>
              <span class="category-tag">{{ getCategoryText(article.category) }}</span>
            </div>

            <!-- 文章内容 -->
            <div class="article-body" v-html="article.content"></div>

            <!-- 文章标签 -->
            <div class="article-tags">
              <n-tag
                v-for="tag in article.tags"
                :key="tag"
                size="small"
                type="outline"
              >
                {{ tag }}
              </n-tag>
            </div>

            <!-- 互动按钮 -->
            <div class="action-buttons">
              <n-button
                v-if="!article.isLiked"
                ghost
                size="medium"
                class="action-btn"
                @click="handleLike"
              >
                <n-icon size="18" class="action-icon">
                  <Heart />
                </n-icon>
                <span>{{ article.likeCount }}</span>
              </n-button>
              <n-button
                v-else
                ghost
                size="medium"
                class="action-btn liked"
                @click="handleLike"
              >
                <n-icon size="18" class="action-icon">
                  <Heart />
                </n-icon>
                <span>{{ article.likeCount }}</span>
              </n-button>

              <n-button
                v-if="!article.isCollected"
                ghost
                size="medium"
                class="action-btn"
                @click="handleCollect"
              >
                <n-icon size="18" class="action-icon">
                  <Bookmark />
                </n-icon>
                <span>{{ article.collectCount }}</span>
              </n-button>
              <n-button
                v-else
                ghost
                size="medium"
                class="action-btn collected"
                @click="handleCollect"
              >
                <n-icon size="18" class="action-icon">
                  <Bookmark />
                </n-icon>
                <span>{{ article.collectCount }}</span>
              </n-button>

              <n-button
                ghost
                size="medium"
                class="action-btn"
                @click="handleShare"
              >
                <n-icon size="18" class="action-icon">
                  <Share />
                </n-icon>
                <span>分享</span>
              </n-button>
            </div>
          </n-card>

          <!-- 评论区 -->
          <n-card bordered class="comments-card">
            <div class="comments-header">
              <h2>评论 ({{ comments.length }})</h2>
            </div>

            <!-- 评论输入框 -->
            <n-textarea
              v-model:value="newComment"
              placeholder="写下你的评论..."
              class="comment-input"
              rows="3"
            />
            <n-button
              type="primary"
              class="submit-comment"
              @click="submitComment"
              :disabled="!newComment.trim()"
            >
              发表评论
            </n-button>

            <!-- 评论列表 -->
            <div class="comments-list">
              <n-card
                v-for="comment in comments"
                :key="comment.id"
                bordered
                class="comment-item"
              >
                <div class="comment-header">
                  <n-avatar :src="comment.userAvatar" size="small" />
                  <div class="comment-user-info">
                    <div class="comment-username">{{ comment.username }}</div>
                    <div class="comment-time">{{ formatTimeAgo(comment.createdAt) }}</div>
                  </div>
                </div>
                <div class="comment-content">{{ comment.content }}</div>
                <div class="comment-actions">
                  <n-button
                    v-if="!comment.isLiked"
                    ghost
                    size="tiny"
                    class="comment-action-btn"
                    @click="likeComment(comment.id)"
                  >
                    <Heart size="14" />
                    <span>{{ comment.likeCount }}</span>
                  </n-button>
                  <n-button
                    v-else
                    ghost
                    size="tiny"
                    class="comment-action-btn liked"
                    @click="likeComment(comment.id)"
                  >
                    <Heart size="14" />
                    <span>{{ comment.likeCount }}</span>
                  </n-button>
                  <n-button
                    ghost
                    size="tiny"
                    class="comment-action-btn"
                    @click="replyToComment(comment.id)"
                  >
                    回复
                  </n-button>
                </div>
              </n-card>
            </div>

            <!-- 加载更多评论 -->
            <n-button
              v-if="hasMoreComments"
              ghost
              block
              class="load-more-comments"
              @click="loadMoreComments"
            >
              加载更多评论
            </n-button>
          </n-card>
        </n-grid-item>

        <!-- 右侧边栏 -->
        <n-grid-item span="8" class="sidebar">
          <!-- 作者信息卡片 -->
          <n-card bordered class="author-card">
            <div class="author-card-header">
              <n-avatar :src="article.authorAvatar" class="author-card-avatar" />
              <div class="author-card-name">{{ article.authorName }}</div>
              <div class="author-card-identity">{{ article.authorIdentity }}</div>
            </div>
            <div class="author-stats">
              <div class="stat-item">
                <div class="stat-value">{{ article.authorArticleCount }}</div>
                <div class="stat-label">发布文章</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ article.authorLikeCount }}</div>
                <div class="stat-label">获得点赞</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ article.authorFollowerCount }}</div>
                <div class="stat-label">粉丝数</div>
              </div>
            </div>
          </n-card>

          <!-- 相关推荐 -->
          <n-card bordered class="related-posts">
            <div class="related-posts-header">相关推荐</div>
            <div
              v-for="post in relatedPosts"
              :key="post.id"
              class="related-post-item"
              @click="$router.push(`/community/post/${post.id}`)"
            >
              <div class="related-post-title">{{ post.title }}</div>
              <div class="related-post-meta">
                <span>{{ post.likeCount }} 赞</span>
                <span>{{ formatTimeAgo(post.createdAt) }}</span>
              </div>
            </div>
          </n-card>
        </n-grid-item>
      </n-grid>
    </n-layout-content>

    <!-- 页脚 -->
    <n-layout-footer class="footer">
      <n-text type="secondary" align="center">
        © 2024 职享圈 - 大学生就业经验社区
      </n-text>
    </n-layout-footer>
  </n-layout>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router';
import { useMessage } from 'naive-ui';
import { ref, onMounted, computed,watch } from 'vue';
import axios from '@/utils/axios';
import { getArticleComments } from '@/api/article'; 

// 图标
import {
  Briefcase,
  Search,
  Heart,
  Bookmark,
  Share
} from '@vicons/ionicons5';

// Naive UI 组件
import {
  NLayout,
  NLayoutHeader,
  NLayoutContent,
  NLayoutFooter,
  NGrid,
  NGridItem,
  NMenu,
  NInput,
  NButton,
  NCard,
  NTag,
  NText,
  NIcon,
  NAvatar,
  // NTextarea
} from 'naive-ui';

const router = useRouter();
const route = useRoute();
const message = useMessage();

// 导航菜单
const menuOptions = [
  { key: 'home', label: '首页' },
  { key: 'jobs', label: '招聘信息' },
  { key: 'community', label: '经验社区', disabled: true },
  { key: 'resources', label: '就业资源' }
];

// 状态管理
const articleId = ref(route.params.id);
const article = ref({
  id: '',
  title: '',
  content: '',
  authorName: '',
  authorAvatar: '',
  authorIdentity: '',
  publishTime: '',
  category: '',
  tags: [],
  likeCount: 0,
  collectCount: 0,
  viewCount: 0,
  isLiked: false,
  isCollected: false,
  authorArticleCount: 0,
  authorLikeCount: 0,
  authorFollowerCount: 0
});
const comments = ref([]);
const newComment = ref('');
const hasMoreComments = ref(true);
const commentPage = ref(1);
const relatedPosts = ref([]);
const isFollowing = ref(false);
const searchQuery = ref('');
const loading = ref(true);

// 分类文本映射
const categoryMap = {
  'interview': '面试经验',
  'resume': '简历技巧',
  'career': '行业选择',
  'exam': '笔试攻略',
  'others': '其他'
};

// 获取分类文本
const getCategoryText = (category) => {
  return categoryMap[category] || category;
};

// 格式化日期
const formatTimeAgo = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 60) return `${diffMins}分钟前`;
  if (diffHours < 24) return `${diffHours}小时前`;
  if (diffDays < 30) return `${diffDays}天前`;
  
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
};

// 获取文章详情
const fetchArticleDetail = async () => {
  try {
    loading.value = true;
    const response = await axios.get(`/posts/${articleId.value}/`);
    const data = response.data;
    
    article.value = {
      id: data.id,
      title: data.title,
      authorId: data.user_id, 
      content: data.content,
      authorName: data.user?.username || '匿名用户',
      authorAvatar: data.user?.avatar || 'https://picsum.photos/id/237/40/40',
      authorIdentity: data.user?.profile?.identity || '职场前辈',
      publishTime: formatTimeAgo(data.created_at),
      category: data.category,
      tags: data.tags ? data.tags.split(',') : [],
      likeCount: data.like_count,
      collectCount: data.star_count || 0,
      viewCount: data.view_count,
      isLiked: data.is_liked || false,
      isCollected: data.is_collected || false,
      authorArticleCount: data.user?.article_count || 0,
      authorLikeCount: data.user?.total_likes || 0,
      authorFollowerCount: data.user?.follower_count || 0
    };
    
    // 检查是否已关注
    isFollowing.value = data.user?.is_followed || false;
    console.log("初始关注状态：", isFollowing.value); 
    // 增加阅读量
    await axios.post(`/posts/${articleId.value}/view/`);
  } catch (error) {
    console.error('获取文章详情失败:', error);
    message.error('加载文章失败，请重试');
  } finally {
    loading.value = false;
  }
};

// 获取评论
const fetchComments = async (page = 1, loadMore = false) => {
  try {
    const response = await getArticleComments(articleId.value, page, 10);
    
    const formattedComments = response.data.map(comment => ({
      id: comment.id,
      username: comment.user?.username || '匿名用户',
      userAvatar: comment.user?.avatar || 'https://picsum.photos/id/237/40/40',
      content: comment.content,
      createdAt: comment.created_at,
      likeCount: comment.like_count,
      isLiked: comment.is_liked || false
    }));
    
    if (loadMore) {
      comments.value = [...comments.value, ...formattedComments];
    } else {
      comments.value = formattedComments;
    }
    
    hasMoreComments.value = response.data.next !== null;
  } catch (error) {
    console.error('获取评论失败:', error);
    message.error('加载评论失败，请重试');
  }
};

// 获取相关推荐
const fetchRelatedPosts = async () => {
  try {
    const response = await axios.get('/posts/', {
      params: {
        category: article.value.category,
        page_size: 5,
        ordering: '-created_at'
      }
    });
    
    relatedPosts.value = response.data
      .filter(post => post.id !== article.value.id)
      .map(post => ({
        id: post.id,
        title: post.title,
        likeCount: post.like_count,
        createdAt: post.created_at
      }));
  } catch (error) {
    console.error('获取相关推荐失败:', error);
  }
};

// 点赞文章
const handleLike = async () => {
  try {
    if (article.value.isLiked) {
      await axios.delete(`/posts/${articleId.value}/like/`);
      article.value.likeCount--;
    } else {
      await axios.post(`/posts/${articleId.value}/like/`);
      article.value.likeCount++;
    }
    article.value.isLiked = !article.value.isLiked;
  } catch (error) {
    console.error('点赞失败:', error);
    message.error('操作失败，请重试');
  }
};

// 收藏文章
const handleCollect = async () => {
  try {
    if (article.value.isCollected) {
      await axios.delete(`/posts/${articleId.value}/collect/`);
      article.value.collectCount--;
    } else {
      await axios.post(`/posts/${articleId.value}/collect/`);
      article.value.collectCount++;
    }
    article.value.isCollected = !article.value.isCollected;
  } catch (error) {
    console.error('收藏失败:', error);
    message.error('操作失败，请重试');
  }
};

// 分享文章
const handleShare = () => {
  // 实际项目中可以调用分享API或复制链接
  navigator.clipboard.writeText(window.location.href)
    .then(() => {
      message.success('链接已复制到剪贴板');
    })
    .catch(() => {
      message.error('复制失败，请手动复制链接');
    });
};

// 关注作者
const handleFollow = async () => {
  if (!article.value.authorId) {
    message.error('无法获取作者信息');
    return;
  }
  try {
    console.log('关注操作 - 当前用户token:', localStorage.getItem('accessToken'));
    console.log('关注目标ID:', article.value.authorId);
    if (isFollowing.value) {
      await axios.delete(`/users/${article.value.authorId}/follow/`);
      message.success('取消关注成功');
      isFollowing.value = false; // 补充状态更新
      article.value.authorFollowerCount--;
    } else {
      await axios.post(`/users/${article.value.authorId}/follow/`);
      message.success('关注成功');
      isFollowing.value = true;
      article.value.authorFollowerCount++;
    }
  } catch (error) {
    console.error('关注/取消关注失败:', error);
    message.error('操作失败，请重试');
  }
};

// 提交评论
const submitComment = async () => {
  const content = newComment.value.trim();
  if (!content) return;
  
  try {
    // 使用更新后的addComment方法
    await addComment(articleId.value, { content });
    fetchComments(1);  // 重新加载评论
    newComment.value = '';
  } catch (error) {
    console.error('提交评论失败:', error);
  }
};

// 点赞评论
const likeComment = async (commentId) => {
  try {
    const comment = comments.value.find(c => c.id === commentId);
    if (comment.isLiked) {
      await axios.delete(`/comments/${commentId}/like/`);
      comment.likeCount--;
    } else {
      await axios.post(`/comments/${commentId}/like/`);
      comment.likeCount++;
    }
    comment.isLiked = !comment.isLiked;
  } catch (error) {
    console.error('评论点赞失败:', error);
    message.error('操作失败，请重试');
  }
};

// 回复评论
const replyToComment = (commentId) => {
  // 实际项目中可以实现回复功能
  message.info('回复功能待实现');
};

// 加载更多评论
const loadMoreComments = () => {
  commentPage.value++;
  fetchComments(commentPage.value, true);
};

// 搜索功能
const handleSearch = async () => {
  const keyword = searchQuery.value.trim();
  if (!keyword) {
    message.warning('请输入搜索关键词~');
    return;
  }
  
  // 跳转到社区首页并执行搜索
  router.push('/community');
  // 在实际项目中可以使用pinia或事件总线传递搜索关键词
  setTimeout(() => {
    window.dispatchEvent(new CustomEvent('search', { detail: keyword }));
  }, 100);
};

// 初始化
onMounted(() => {
  fetchArticleDetail();
  fetchComments();
});

// 监听文章ID变化（适用于同页面路由切换）
watch(
  () => route.params.id,
  (newId) => {
    articleId.value = newId;
    fetchArticleDetail();
    fetchComments();
    commentPage.value = 1;
  }
);
</script>

<style scoped>
.article-detail-layout {
  min-height: 100vh;
}

.header {
  background-color: #fff;
}

.header-grid {
  height: 100%;
  align-items: center;
  padding: 0 24px;
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
}

.main-menu {
  width: 100%;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: flex-end;
}

.search-input {
  width: 240px;
}

.post-btn {
  white-space: nowrap;
}

.main-content {
  padding: 24px;
}

.content-grid {
  max-width: 1440px;
  margin: 0 auto;
}

.article-content {
  padding: 16px;
}

.article-card {
  padding: 24px;
  margin-bottom: 24px;
}

.article-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
  color: #1d2129;
}

.author-info {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.author-avatar {
  width: 48px;
  height: 48px;
  margin-right: 12px;
}

.author-details {
  flex: 1;
}

.author-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.author-identity {
  font-size: 14px;
  color: #86909c;
}

.follow-btn {
  margin-left: auto;
}

.article-meta {
  display: flex;
  align-items: center;
  color: #86909c;
  font-size: 14px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f2f3f5;
}

.publish-time {
  margin-right: 16px;
}

.category-tag {
  background-color: #f2f3f5;
  padding: 4px 8px;
  border-radius: 4px;
}

.article-body {
  font-size: 16px;
  line-height: 1.8;
  color: #1d2129;
  margin-bottom: 32px;
}

.article-body img {
  max-width: 100%;
  margin: 16px 0;
}

.article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 24px;
  padding-top: 16px;
  border-top: 1px solid #f2f3f5;
}

.action-buttons {
  display: flex;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid #f2f3f5;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #86909c;
}

.action-btn.liked,
.action-btn.collected {
  color: #f53f3f;
}

.action-icon {
  vertical-align: middle;
}

.comments-card {
  padding: 24px;
}

.comments-header {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f2f3f5;
}

.comments-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.comment-input {
  margin-bottom: 16px;
}

.submit-comment {
  margin-bottom: 24px;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-item {
  padding: 16px;
}

.comment-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.comment-user-info {
  margin-left: 8px;
}

.comment-username {
  font-weight: 500;
  font-size: 14px;
}

.comment-time {
  font-size: 12px;
  color: #86909c;
}

.comment-content {
  margin-bottom: 8px;
  line-height: 1.6;
}

.comment-actions {
  display: flex;
  gap: 16px;
}

.comment-action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #86909c;
  padding: 0;
  height: auto;
}

.comment-action-btn.liked {
  color: #f53f3f;
}

.load-more-comments {
  margin-top: 16px;
}

.sidebar {
  padding: 16px;
}

.author-card {
  margin-bottom: 24px;
  padding: 24px;
  text-align: center;
}

.author-card-avatar {
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
}

.author-card-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
}

.author-card-identity {
  color: #86909c;
  margin-bottom: 16px;
}

.author-stats {
  display: flex;
  justify-content: space-around;
  border-top: 1px solid #f2f3f5;
  padding-top: 16px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #86909c;
}

.related-posts {
  padding: 16px;
}

.related-posts-header {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f2f3f5;
}

.related-post-item {
  padding: 12px 0;
  border-bottom: 1px solid #f2f3f5;
  cursor: pointer;
  transition: background-color 0.2s;
}

.related-post-item:last-child {
  border-bottom: none;
}

.related-post-item:hover {
  background-color: #f7f8fa;
}

.related-post-title {
  font-size: 14px;
  margin-bottom: 4px;
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.related-post-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #86909c;
}

.footer {
  padding: 24px;
  background-color: #f7f8fa;
}

/* 加载状态样式 */
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}
</style>