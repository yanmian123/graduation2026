<template>
  <n-layout class="article-detail-layout">

    <!-- 主体内容 -->
    <n-layout-content class="main-content">
      <n-grid :x-gap="16" :y-gap="24" class="content-grid">
        <!-- 左侧文章详情 -->
        <n-grid-item span="19" class="article-content">
          <n-card bordered class="article-card">
            <!-- 作者信息 -->
            <div class="author-info">
              <n-avatar :src="article.authorAvatar" class="author-avatar" round @click="goToAuthorProfile" style="cursor: pointer;" />
              <div class="author-details">
                <div class="author-name" @click="goToAuthorProfile" style="cursor: pointer;">{{ article.authorName }}</div>
                <div class="author-identity">{{ article.authorIdentity }}</div>
              </div>
              
              <n-space>
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
                <n-dropdown :options="authorOptions" placement="bottom-start" @select="handleAuthorAction">
                  <n-button :bordered="false" style="padding: 0 4px">
                    ···
                  </n-button>
                </n-dropdown>
              </n-space>
            </div>

            <!-- 文章元信息 -->
            <div class="article-meta">
              <span class="publish-time">{{ article.publishTime }}</span>
              <span class="category-tag">{{ getCategoryText(article.category) }}</span>
            </div>

            <!-- 文章标题 -->
            <h1 class="article-title">{{ article.title }}</h1>

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
              <h2>评论区</h2>
            </div>

            <!-- 评论输入框 -->
            <div v-if="replyingToCommentId" class="reply-header">
              <span class="reply-to">回复 <span class="reply-username">{{ replyingToUsername }}</span>:</span>
              <n-button
                ghost
                size="small"
                class="cancel-reply-btn"
                @click="cancelReply"
              >
                取消回复
              </n-button>
            </div>
            <n-input
              v-model:value="newComment"
              type="textarea"
              :placeholder="replyingToCommentId ? `回复 ${replyingToUsername}...` : '写下你的评论...'"
              class="comment-input"
              :rows="3"
            />
            <n-button
              type="primary"
              class="submit-comment"
              @click="submitComment"
              :disabled="!newComment.trim()"
            >
              {{ replyingToCommentId ? '回复' : '发表评论' }}
            </n-button>

            <!-- 评论列表 -->
            <div id="comments" class="comments-list">
              <CommentItem
                v-for="comment in comments"
                :key="comment.id"
                :comment="comment"
                :article-author-id="article.authorId"
                :target-comment-id="targetCommentId"
                @like="likeComment"
                @reply="replyToComment"
                @delete="deleteComment"
                @report="reportComment"
              />
            </div>

            <!-- 评论控制按钮 -->
            <div v-if="totalComments > 5">
              <!-- 显示全部评论按钮 -->
              <n-button
                v-if="!showAllComments"
                ghost
                block
                class="load-more-comments"
                @click="() => { showAllComments = true; fetchComments(1, false); }"
              >
                显示全部 {{ totalComments }} 条评论
              </n-button>
              
              <!-- 收起评论按钮 -->
              <n-button
                v-else
                ghost
                block
                class="load-more-comments"
                @click="() => { showAllComments = false; fetchComments(1, false); }"
              >
                收起评论
              </n-button>
            </div>
            
            <!-- 加载更多评论按钮（仅当显示全部评论且还有更多时显示） -->
            <n-button
              v-if="showAllComments && hasMoreComments"
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
        <n-grid-item span="5" class="sidebar">
          <!-- 作者信息卡片 -->
          <n-card bordered class="author-card">
            <div class="author-card-header">
              <n-avatar :src="article.authorAvatar" class="author-card-avatar" round />
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

    <!-- 举报文章模态框 -->
    <n-modal v-model:show="showArticleReportModal" preset="card" title="举报文章" style="width: 500px">
      <n-form-item label="举报原因">
        <n-select
          v-model:value="articleReportForm.reason"
          :options="reportUserReasonOptions"
          placeholder="请选择举报原因"
        />
      </n-form-item>
      <n-form-item label="详细描述">
        <n-input
          v-model:value="articleReportForm.description"
          type="textarea"
          placeholder="请输入详细描述（选填）"
          :rows="4"
          maxlength="500"
          show-count
        />
      </n-form-item>
      <template #footer>
        <n-space justify="end">
          <n-button @click="cancelArticleReport">取消</n-button>
          <n-button type="primary" @click="submitArticleReport">提交举报</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 举报评论模态框 -->
    <n-modal v-model:show="showReportModal" preset="card" title="举报评论" style="width: 500px">
      <n-form-item label="举报原因">
        <n-select
          v-model:value="reportForm.reason"
          :options="reportReasonOptions"
          placeholder="请选择举报原因"
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
          <n-button @click="cancelReport">取消</n-button>
          <n-button type="primary" @click="submitCommentReport">提交举报</n-button>
        </n-space>
      </template>
    </n-modal>
  </n-layout>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router';
import { useMessage } from 'naive-ui';
import { ref, onMounted, computed,watch, nextTick } from 'vue';
import axios from '@/utils/axios';
import { getArticleComments, addComment } from '@/api/article';
import CommentItem from '@/components/CommentItem.vue'; 

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
  NSpace,
  NDropdown,
  NModal,
  NFormItem,
  NSelect
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

// 作者操作选项
const authorOptions = [
  {
    label: '举报',
    key: 'report'
  }
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
const totalComments = ref(0);
const showAllComments = ref(false);
const targetCommentId = ref(null);
const relatedPosts = ref([]);
const isFollowing = ref(false);
const currentUserFollowingCount = ref(0);
const searchQuery = ref('');
const loading = ref(true);
// 回复评论相关状态
const replyingToCommentId = ref(null);
const replyingToUsername = ref('');
// 举报评论相关状态
const showReportModal = ref(false);
const reportCommentId = ref(null);
const reportForm = ref({
  reason: '',
  description: ''
});
// 举报文章相关状态
const showArticleReportModal = ref(false);
const articleReportForm = ref({
  reason: '',
  description: ''
});

// 举报用户理由选项（用于举报文章作者）
const reportUserReasonOptions = [
  { label: '发布不良的内容或信息', value: '发布不良的内容或信息' },
  { label: '传播色情或引导私下交易', value: '传播色情或引导私下交易' },
  { label: '侵犯权益', value: '侵犯权益' },
  { label: '未成年相关', value: '未成年相关' },
  { label: '冒充他人', value: '冒充他人' },
  { label: '涉嫌欺诈', value: '涉嫌欺诈' },
  { label: '危害人身安全', value: '危害人身安全' },
  { label: '网络暴力', value: '网络暴力' },
  { label: '我不喜欢这个账号的内容', value: '我不喜欢这个账号的内容' },
  { label: '其它', value: '其它' }
];

// 举报评论理由选项（保持不变）
const reportReasonOptions = [
  { label: '谩骂攻击', value: '谩骂攻击' },
  { label: '色情低俗', value: '色情低俗' },
  { label: '违法违规', value: '违法违规' },
  { label: '广告营销', value: '广告营销' },
  { label: '价值观导向不良', value: '价值观导向不良' },
  { label: '政治敏感', value: '政治敏感' },
  { label: '虚假冒充', value: '虚假冒充' },
  { label: '其他', value: '其他' }
];

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
    
    // 处理头像URL，添加localhost:8000前缀（如果是相对路径）
    const rawAvatar = data.user_avatar || data.avatar || data.user?.avatar;
    const userAvatar = rawAvatar ? (rawAvatar.startsWith('http') ? rawAvatar : `http://localhost:8000${rawAvatar}`) : 'https://picsum.photos/id/237/40/40';
    
    // 处理昵称，优先使用data.nickname或data.user.nickname
    let authorName;
    if (data.nickname && data.nickname.trim()) {
      authorName = data.nickname;
    } else if (data.user?.nickname && data.user.nickname.trim()) {
      authorName = data.user.nickname;
    } else {
      // 如果没有昵称，使用用户名，并确保不显示'匿名用户'
      const rawUsername = data.username || data.user?.username || '用户';
      const namePart = rawUsername.replace(/\d+/g, '');
      if (namePart) {
        authorName = namePart.charAt(0).toUpperCase() + namePart.slice(1) + '同学';
      } else {
        authorName = '用户' + rawUsername;
      }
    }
    
    article.value = {
      id: data.id,
      title: data.title,
      authorId: data.user_id, 
      content: data.content,
      authorName: authorName,
      authorAvatar: userAvatar,
      authorIdentity: data.user?.profile?.identity || '职场前辈',
      publishTime: formatTimeAgo(data.created_at),
      category: data.category,
      tags: data.tags ? data.tags.split(',') : [],
      likeCount: data.like_count,
      collectCount: data.star_count || 0,
      viewCount: data.view_count,
      isLiked: data.is_liked || false,
      isCollected: data.is_collected || false,
      authorArticleCount: data.author_article_count || 0,
      authorLikeCount: data.author_total_likes || 0,
      authorFollowerCount: data.author_follower_count || 0
    };
    
    // 检查是否已关注
    isFollowing.value = data.is_followed || false;
    console.log("初始关注状态：", isFollowing.value);
    
    // 从localStorage同步关注状态
    syncFollowStateFromStorage();
    
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
// 格式化单个评论
const formatComment = (comment) => {
  const formattedComment = {
    id: comment.id,
    userId: comment.user_id,
    username: comment.nickname || comment.username || '匿名用户',
    userAvatar: comment.avatar ? (comment.avatar.startsWith('http') ? comment.avatar : `http://localhost:8000${comment.avatar}`) : 'https://picsum.photos/id/237/40/40',
    content: comment.content,
    createdAt: comment.created_at,
    likeCount: comment.like_count,
    isLiked: comment.is_liked || false,
    parentUsername: comment.parent_username || null,
    parentNickname: comment.parent_nickname || null,
    replies: []
  };
  
  // 递归格式化回复
  if (comment.replies && comment.replies.length > 0) {
    formattedComment.replies = comment.replies.map(reply => formatComment(reply));
  }
  
  return formattedComment;
};

const fetchComments = async (page = 1, loadMore = false) => {
  try {
    const pageSize = showAllComments.value ? 100 : 5;
    const response = await getArticleComments(articleId.value, page, pageSize);
    
    const formattedComments = response.data.results.map(comment => formatComment(comment));
    
    if (loadMore) {
      comments.value = [...comments.value, ...formattedComments];
    } else {
      comments.value = formattedComments;
    }
    
    hasMoreComments.value = response.data.next !== null;
    totalComments.value = response.data.count;
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
    let response;
    if (article.value.isLiked) {
      response = await axios.delete(`/posts/${articleId.value}/like/`);
    } else {
      response = await axios.post(`/posts/${articleId.value}/like/`);
    }
    
    // 根据后端返回的最新数据更新状态
    if (response.data) {
      article.value.isLiked = response.data.is_liked || false;
      article.value.likeCount = response.data.count || 0;
    } else {
      // 如果没有返回数据，手动更新状态
      article.value.isLiked = !article.value.isLiked;
      if (article.value.isLiked) {
        article.value.likeCount++;
      } else {
        article.value.likeCount--;
      }
    }
  } catch (error) {
    console.error('点赞失败:', error);
    message.error('操作失败，请重试');
  }
};

// 收藏文章
const handleCollect = async () => {
  try {
    // 显示加载状态
    loading.value = true;
    
    // 记录当前操作类型
    const isCollecting = !article.value.isCollected;
    
    let response;
    if (article.value.isCollected) {
      response = await axios.delete(`/posts/${articleId.value}/collect/`);
    } else {
      response = await axios.post(`/posts/${articleId.value}/collect/`);
    }
    
    // 检查响应数据
    if (response.data) {
      // 根据后端返回的最新数据更新状态
      article.value.isCollected = response.data.is_collected || false;
      article.value.collectCount = response.data.count || 0;
      
      // 根据操作类型显示提示
      message.success(isCollecting ? '收藏成功' : '取消收藏成功');
    } else {
      // 如果没有返回数据，手动更新状态
      article.value.isCollected = !article.value.isCollected;
      if (article.value.isCollected) {
        article.value.collectCount++;
        message.success('收藏成功');
      } else {
        article.value.collectCount--;
        message.success('取消收藏成功');
      }
    }
  } catch (error) {
    console.error('收藏失败:', error);
    console.error('错误详情:', error.response?.data || error.message);
    message.error('操作失败，请重试');
  } finally {
    loading.value = false;
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
      await axios.delete(`/user/users/${article.value.authorId}/follow/`);
      message.success('取消关注成功');
      isFollowing.value = false;
      article.value.authorFollowerCount--;
      currentUserFollowingCount.value--;
      
      // 同步关注状态到localStorage
      syncFollowState(article.value.authorId, false);
      
      // 更新localStorage中的用户信息
      const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
      if (userInfo.username) {
        localStorage.setItem('userInfo', JSON.stringify(userInfo));
      }
    } else {
      await axios.post(`/user/users/${article.value.authorId}/follow/`);
      message.success('关注成功');
      isFollowing.value = true;
      article.value.authorFollowerCount++;
      currentUserFollowingCount.value++;
      
      // 同步关注状态到localStorage
      syncFollowState(article.value.authorId, true);
      
      // 更新localStorage中的用户信息
      const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
      if (userInfo.username) {
        localStorage.setItem('userInfo', JSON.stringify(userInfo));
      }
    }
  } catch (error) {
    console.error('关注/取消关注失败:', error);
    message.error('操作失败，请重试');
  }
};

// 同步关注状态到localStorage
const syncFollowState = (userId, isFollowing) => {
  const followState = JSON.parse(localStorage.getItem('followState') || '{}');
  followState[userId] = isFollowing;
  localStorage.setItem('followState', JSON.stringify(followState));
};

// 从localStorage同步关注状态
const syncFollowStateFromStorage = () => {
  if (article.value.authorId) {
    const followState = JSON.parse(localStorage.getItem('followState') || '{}');
    if (followState[article.value.authorId] !== undefined) {
      isFollowing.value = followState[article.value.authorId];
    }
  }
};

// 提交评论
const submitComment = async () => {
  const content = newComment.value.trim();
  if (!content) return;
  
  try {
    // 准备评论数据
    const commentData = {
      content: content
    };
    
    // 如果是回复评论，添加parent_id
    if (replyingToCommentId.value) {
      commentData.parent_id = replyingToCommentId.value;
    }
    
    // 使用更新后的addComment方法
    await addComment(articleId.value, commentData);
    fetchComments(1);  // 重新加载评论
    newComment.value = '';
    
    // 提交成功后取消回复状态
    if (replyingToCommentId.value) {
      cancelReply();
    }
  } catch (error) {
    console.error('提交评论失败:', error);
  }
};

// 点赞评论
const likeComment = async (commentId) => {
  try {
    const findComment = (commentList, id) => {
      for (const comment of commentList) {
        if (comment.id === id) {
          return comment;
        }
        if (comment.replies && comment.replies.length > 0) {
          const found = findComment(comment.replies, id);
          if (found) return found;
        }
      }
      return null;
    };
    
    const comment = findComment(comments.value, commentId);
    if (!comment) {
      console.error('未找到评论:', commentId);
      return;
    }
    
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

// 获取当前用户ID
const getCurrentUserId = () => {
  const userInfo = localStorage.getItem('userInfo');
  if (userInfo) {
    try {
      const user = JSON.parse(userInfo);
      return user.id;
    } catch (e) {
      console.error('解析用户信息失败:', e);
    }
  }
  return null;
};

// 删除评论
const deleteComment = async (commentId) => {
  try {
    await axios.delete(`/comments/${commentId}/`);
    
    // 从评论列表中移除该评论
    const removeComment = (commentsList) => {
      const index = commentsList.findIndex(c => c.id === commentId);
      if (index !== -1) {
        commentsList.splice(index, 1);
        return true;
      }
      for (const comment of commentsList) {
        if (comment.replies && comment.replies.length > 0) {
          if (removeComment(comment.replies)) {
            return true;
          }
        }
      }
      return false;
    };
    
    removeComment(comments.value);
    totalComments.value--;
    message.success('删除成功');
  } catch (error) {
    console.error('删除评论失败:', error);
    if (error.response?.status === 403) {
      message.error('只能删除自己的评论');
    } else {
      message.error('删除失败，请重试');
    }
  }
};

// 递归查找评论（包括嵌套回复）
const findCommentById = (comments, commentId) => {
  for (const comment of comments) {
    if (comment.id === commentId) {
      return comment;
    }
    if (comment.replies && comment.replies.length > 0) {
      const found = findCommentById(comment.replies, commentId);
      if (found) return found;
    }
  }
  return null;
};

// 回复评论
const replyToComment = (commentId) => {
  // 递归查找要回复的评论（包括嵌套回复）
  const commentToReply = findCommentById(comments.value, commentId);
  if (commentToReply) {
    replyingToCommentId.value = commentId;
    replyingToUsername.value = commentToReply.username;
    // 聚焦到评论输入框
    setTimeout(() => {
      document.querySelector('.comment-input textarea')?.focus();
    }, 100);
  }
};

// 取消回复
const cancelReply = () => {
  replyingToCommentId.value = null;
  replyingToUsername.value = '';
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

// 跳转到作者主页
const goToAuthorProfile = () => {
  if (article.value.authorId) {
    router.push(`/user/profile/${article.value.authorId}`);
  }
};

// 处理作者操作
const handleAuthorAction = (key) => {
  switch (key) {
    case 'report':
      handleReport();
      break;
    default:
      break;
  }
};

// 举报功能
const handleReport = () => {
  if (!article.value.authorId) {
    message.error('无法获取作者信息');
    return;
  }
  
  showArticleReportModal.value = true;
};

// 提交文章举报
const submitArticleReport = async () => {
  if (!articleReportForm.value.reason) {
    message.warning('请选择举报原因');
    return;
  }
  
  try {
    await axios.post(`/user/users/${article.value.authorId}/report/`, {
      reason: articleReportForm.value.reason,
      description: articleReportForm.value.description,
      report_type: 'user'
    });
    message.success('举报提交成功，管理员会尽快处理');
    showArticleReportModal.value = false;
    articleReportForm.value = {
      reason: '',
      description: ''
    };
  } catch (error) {
    console.error('举报提交失败:', error);
    message.error('举报提交失败，请重试');
  }
};

// 取消文章举报
const cancelArticleReport = () => {
  showArticleReportModal.value = false;
  articleReportForm.value = {
    reason: '',
    description: ''
  };
};

// 举报评论
const reportComment = (commentId) => {
  reportCommentId.value = commentId;
  showReportModal.value = true;
};

// 提交评论举报
const submitCommentReport = async () => {
  if (!reportForm.value.reason) {
    message.warning('请选择举报理由');
    return;
  }
  
  try {
    await axios.post(`/comments/${reportCommentId.value}/report/`, {
      reason: reportForm.value.reason,
      description: reportForm.value.description
    });
    message.success('举报提交成功，管理员会尽快处理');
    showReportModal.value = false;
    reportForm.value = {
      reason: '',
      description: ''
    };
  } catch (error) {
    console.error('举报评论失败:', error);
    message.error('举报提交失败，请重试');
  }
};

// 取消举报
const cancelReport = () => {
  showReportModal.value = false;
  reportForm.value = {
    reason: '',
    description: ''
  };
};

// 滚动到评论区
const scrollToComments = (commentId = null) => {
  nextTick(() => {
    if (commentId) {
      const commentElement = document.getElementById(`comment-${commentId}`);
      if (commentElement) {
        commentElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        commentElement.classList.add('highlight-comment');
        setTimeout(() => {
          commentElement.classList.remove('highlight-comment');
        }, 3000);
      }
    } else {
      const commentsElement = document.getElementById('comments');
      if (commentsElement) {
        commentsElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  });
};

// 初始化
onMounted(async () => {
  const commentId = route.query.commentId;
  
  if (route.hash === '#comments' && commentId) {
    targetCommentId.value = parseInt(commentId);
    showAllComments.value = true;
  }
  
  await fetchArticleDetail();
  await fetchComments();
  
  if (route.hash === '#comments') {
    if (commentId) {
      setTimeout(() => {
        scrollToComments(parseInt(commentId));
      }, 500);
    } else {
      scrollToComments();
    }
  }
});

// 监听文章ID变化（适用于同页面路由切换）
watch(
  () => route.params.id,
  (newId) => {
    articleId.value = newId;
    targetCommentId.value = null;
    fetchArticleDetail();
    fetchComments();
    commentPage.value = 1;
  }
);

// 监听hash和query变化
watch(
  () => [route.hash, route.query.commentId],
  ([newHash, newCommentId]) => {
    if (newHash === '#comments') {
      if (newCommentId) {
        targetCommentId.value = parseInt(newCommentId);
        setTimeout(() => {
          scrollToComments(parseInt(newCommentId));
        }, 500);
      } else {
        targetCommentId.value = null;
        scrollToComments();
      }
    }
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
  padding: 16px 8px;
}

.content-grid {
  max-width: 1600px;
  margin: 0 auto;
}

.article-content {
  padding: 8px;
}

.article-card {
  padding: 16px;
  margin-bottom: 16px;
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
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.article-body img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 16px auto;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.article-body p {
  margin: 12px 0;
}

.article-body h1,
.article-body h2,
.article-body h3,
.article-body h4,
.article-body h5,
.article-body h6 {
  margin: 20px 0 12px 0;
  font-weight: 600;
  line-height: 1.4;
}

.article-body h1 {
  font-size: 28px;
}

.article-body h2 {
  font-size: 24px;
}

.article-body h3 {
  font-size: 20px;
}

.article-body ul,
.article-body ol {
  margin: 12px 0;
  padding-left: 24px;
}

.article-body li {
  margin: 6px 0;
}

.article-body blockquote {
  margin: 16px 0;
  padding: 12px 16px;
  border-left: 4px solid #667eea;
  background-color: #f7f8fa;
  color: #4a5568;
}

.article-body pre {
  margin: 16px 0;
  padding: 16px;
  background-color: #f7f8fa;
  border-radius: 8px;
  overflow-x: auto;
}

.article-body code {
  background-color: #f7f8fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
}

.article-body a {
  color: #667eea;
  text-decoration: none;
}

.article-body a:hover {
  text-decoration: underline;
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
  padding: 1px;
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
  gap: 0px;
}

.reply-info-inline {
  margin-left: 8px;
  font-size: 13px;
}

.reply-label {
  color: #86909c;
}

.reply-target {
  color: #165dff;
  font-weight: 500;
}

.reply-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f2f3f5;
}

.reply-to {
  color: #86909c;
  font-size: 14px;
}

.reply-username {
  color: #2d8cf0;
  font-weight: 500;
}

.cancel-reply-btn {
  padding: 4px 8px;
  font-size: 12px;
}

.load-more-comments {
  margin-top: 16px;
}

.sidebar {
  padding: 8px;
}

.author-card {
  margin-bottom: 16px;
  padding: 16px;
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
  padding: 12px;
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

/* 评论高亮样式 */
:deep(.highlight-comment) {
  animation: highlightPulse 3s ease-in-out;
}

@keyframes highlightPulse {
  0% {
    background-color: rgba(16, 185, 129, 0.3);
    box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
  }
  100% {
    background-color: transparent;
    box-shadow: none;
  }
}
</style>