<template>
  <n-layout class="community-layout">
    <!-- 主体内容 -->
    <n-layout-content class="main-content">
      <n-grid :x-gap="24" :y-gap="24" class="content-grid">
        <!-- 左侧筛选栏 -->
<n-grid-item span="5" class="sidebar">
    <n-card title="内容筛选" bordered>
      <!-- 主题分类 -->
      <div class="filter-section">
        <h3 class="section-title">主题分类</h3>
        <n-radio-group
          v-model:value="topicFilter"
          type="button"
          button-style="outline"
          @update:value="handleFilterChange"
          class="radio-group"
        >
          <n-radio-button value="all">全部</n-radio-button>
          <n-radio-button value="interview">面试经验</n-radio-button>
          <n-radio-button value="resume">简历技巧</n-radio-button>
          <n-radio-button value="career">行业选择</n-radio-button>
          <n-radio-button value="exam">笔试攻略</n-radio-button>
          <n-radio-button value="others">其他</n-radio-button>
        </n-radio-group>
      </div>

      <!-- 排序方式 -->
        <div class="filter-section">
          <h3 class="section-title2">排序方式</h3>
          <n-space vertical>
            <n-select
              v-model:value="sortType"
              size="small"
              @update:value="handleFilterChange"
              class="sort-select"
              :options="sortOptions"
            />
          </n-space>
        </div>

      <!-- 热门标签 -->
      <div class="filter-section">
        <h3 class="section-title">热门标签</h3>
        <n-space wrap class="tag-space">
          <n-tag
            v-for="tag in hotTags"
            :key="tag.id"
            checkable
            :checked="selectedTags.includes(tag.id)"
            @update:checked="(checked) => handleTagCheck(tag.id, checked)"
            size="small"
          >
            {{ tag.name }}
          </n-tag>
        </n-space>
      </div>
    </n-card>
  </n-grid-item>

        <!-- 中间帖子列表 -->
        <n-grid-item span="13" class="post-list">
          <!-- 搜索结果标题（仅在搜索状态显示） -->
          <div v-if="isSearching" class="search-result-header">
            <h2>
              搜索 "{{ searchQuery }}" 找到 {{ totalResults }} 条结果
              <n-button 
                size="small" 
                ghost 
                @click="resetSearch"
              >
                清除搜索
              </n-button>
            </h2>
          </div>


          <!-- 加载状态     当 loading 为真时，显示 <n-skeleton> 骨架屏
骨架屏高度 240px，重复显示 3 个，用于数据加载时的占位展示 -->
            
          <n-skeleton
            v-if="loading"
            width="100%"
            height="240px"
            class="post-skeleton"
            :repeat="3"
          />
          <!-- 帖子列表渲染：根据状态显示搜索结果或普通列表 -->
            <n-card
             v-for="post in isSearching ? searchResults : posts"
            :key="post.id"
            bordered
            hoverable
            class="post-card"
            @click="$router.push(`/community/post/${post.id}`)"
          >
            <!-- 作者信息 -->
            <n-avatar-group size="small" class="author-info">
              <n-avatar :src="post.authorAvatar" />
              <span class="author-name">{{ post.authorName }}</span>
              <n-tag size="small" type="info">{{ post.authorIdentity }}</n-tag>
              <span class="publish-time">{{ post.publishTime }}</span>
            </n-avatar-group>

            <!-- 帖子内容 -->
            <template #header>
              <div class="post-header">
                <div class="post-title">{{ post.title }}</div>
              </div>
            </template>
            <div class="post-content">
              <div class="post-excerpt" v-html="post.excerpt"></div>

              <n-space wrap class="post-tags">
                <n-tag
                  v-for="tag in post.tags"
                  :key="tag"
                  size="small"
                  type="outline"
                  round
                >
                  {{ tag }}
                </n-tag>
              </n-space>
            </div>

            <!-- 互动数据 -->
            <template #footer>
              <div class="post-meta">
                <n-space size="large">
                  <n-space align="center">
                    <n-icon size="16" :color="'#8c8c8c'">
                      <Eye />
                    </n-icon>
                    <n-text type="secondary" size="small">{{ post.viewCount }} 浏览</n-text>
                  </n-space>
                  <n-space align="center">
                    <n-icon size="16" :color="'#ff4d4f'">
                      <Heart />
                    </n-icon>
                    <n-text type="secondary" size="small">{{ post.likeCount }} 点赞</n-text>
                  </n-space>
                  <n-space align="center">
                    <n-icon size="16" :color="'#1890ff'">
                      <Chatbubble />
                    </n-icon>
                    <n-text type="secondary" size="small">{{ post.commentCount }} 评论</n-text>
                  </n-space>
                </n-space>
              </div>
            </template>
          </n-card>
          <!-- 空状态 -->
      <n-empty
          v-if="!loading && (isSearching ? searchResults.length === 0 : posts.length === 0)"
          :description="isSearching ? '没有找到相关内容' : '暂无相关经验分享'"
        >
          <template #extra>
            <n-button 
              type="primary" 
              @click="$router.push('/community/articlescreate')"
            >
              发布第一篇经验
            </n-button>
          </template>
        </n-empty>


          <!-- 分页器 -->
          <div class="pagination-container">
            <n-pagination
              v-if="!loading && totalResults > 0"
              :page="currentPage"
              :page-size="pageSize"
              :page-count="Math.ceil(totalResults / pageSize)"
              :show-size-picker="true"
              :page-sizes="[5, 10, 20]"
              @update:page="handlePageChange"
              @update:page-size="handlePageSizeChange"
              show-quick-jumper
              show-total
              :total="totalResults"
              align="center"
            />
          </div>
        </n-grid-item>

        <!-- 右侧热门推荐 -->
        <n-grid-item span="6" class="right-sidebar">
          <!-- 热门帖子 -->
          <n-card title="热门帖子" bordered class="sidebar-card">
            <n-list>
              <n-list-item
                v-for="(hotPost, index) in hotPosts"
                :key="hotPost.id"
                class="hot-post-item"
                @click="$router.push(`/community/post/${hotPost.id}`)"
              >
                <n-avatar
                  :size="20"
                  :style="{
                    backgroundColor: index < 3 ? '#ff6b6b' : '#ccc',
                    color: '#fff',
                    fontSize: '12px'
                  }"
                  class="hot-rank"
                >
                  {{ index + 1 }}
                </n-avatar>
                <div class="hot-post-content">
                  <n-text strong class="hot-post-title">{{ hotPost.title }}</n-text>
                  <n-space size="small" class="hot-post-meta">
                    <n-space size="small" align="center">
                      <n-icon size="12">
                        <Heart />
                      </n-icon>
                      <n-text type="secondary" size="small">{{ hotPost.likeCount }}</n-text>
                    </n-space>
                    <n-space size="small" align="center">
                      <n-icon size="12">
                        <Chatbubble />
                      </n-icon>
                      <n-text type="secondary" size="small">{{ hotPost.commentCount }}</n-text>
                    </n-space>
                  </n-space>
                </div>
              </n-list-item>
            </n-list>
          </n-card>

          <!-- 活跃用户 -->
          <n-card title="活跃学长学姐" bordered class="sidebar-card" style="margin-top: 16px;">
            <n-list>
              <n-list-item
                v-for="user in activeUsers"
                :key="user.id"
                class="active-user-item"
              >
                <n-avatar :src="user.avatar" size="small" />
                <div class="user-info">
                  <n-text strong>{{ user.name }}</n-text>
                  <n-text type="secondary" size="small">{{ user.desc }}</n-text>
                </div>
                <n-button
                  size="small"
                  type="primary"
                  ghost
                  class="follow-btn"
                >
                  关注
                </n-button>
              </n-list-item>
            </n-list>
          </n-card>

          <!-- 社区公告 -->
          <n-card title="社区公告" bordered class="sidebar-card" style="margin-top: 16px;">
            <n-space vertical>
              <n-card title="欢迎新同学" size="small" bordered>
                <n-text type="secondary" size="small">
                  欢迎加入职享圈，分享你的职场经验！
                </n-text>
              </n-card>
              <n-card title="内容规范" size="small" bordered>
                <n-text type="secondary" size="small">
                  请遵守社区规范，发布有价值的内容
                </n-text>
              </n-card>
            </n-space>
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
import { useRouter } from 'vue-router';
import { useMessage } from 'naive-ui';
import { ref, onMounted } from 'vue';
import axios from '@/utils/axios';

// 图标使用 @vicons/ionicons5，确保已安装
import {
  Briefcase,
  Search,
//   Pen,
  Eye,
  Heart,
  Chatbubble,
  
} from '@vicons/ionicons5';
// Naive UI 组件导入（移除 NListItemMain 等废弃组件）
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
  NRadioGroup,
  NRadioButton,
  NForm,
  NFormItem,
  NSelect,
  NTag,
  NSpace,
  NList,
  NListItem,  // 仅保留 NListItem
  NText,
  NIcon,
  NAvatar,
  NAvatarGroup,
  NSkeleton  // 添加骨架屏组件
  
} from 'naive-ui';

const router = useRouter();
const message = useMessage();

// 导航菜单
const menuOptions = [
  { key: 'home', label: '首页' },
  { key: 'jobs', label: '招聘信息' },
  { key: 'community', label: '经验社区', disabled: true },
  { key: 'resources', label: '就业资源' }
];

// 搜索与筛选状态
const isSearching = ref(false);// 搜索状态
const searchResults = ref([]);// 搜索结果
const totalResults = ref(0);// 总结果数
const searchQuery = ref('');
const topicFilter = ref('all');
const sortType = ref('latest');
const selectedTags = ref([]);
const posts = ref([]);
const hotPosts = ref([]);
const activeUsers = ref([]);
const hasMore = ref(true);
const loading = ref(false);
const currentPage = ref(1);
const pageSize = ref(5);
const sortOptions = [
  {
    label: "最新发布",
    value: "latest"
  },
  {
    label: "热门推荐",
    value: "hot"
  },
  {
    label: "点赞最多",
    value: "mostLiked"
  }
];
const hotTags = ref([
  { id: 1, name: '字节跳动' },
  { id: 2, name: '前端开发' },
  { id: 3, name: '群面技巧' },
  { id: 4, name: '秋招' }
]);


// 格式化日期（多久前）
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

// 获取文章列表
const fetchPosts = async (isLoadMore = false) => {
  if (!isLoadMore) {
    currentPage.value = 1;
    loading.value = true;
  }
  try {
      // 构建查询参数
      const params = {
        page: currentPage.value,
        page_size: pageSize.value,
        ordering: sortType.value === 'latest' ? '-created_at' : 
                  sortType.value === 'mostLiked' ? '-like_count' : '-view_count',
      };

      // 添加分类筛选
      if (topicFilter.value !== 'all') {
        params.category = topicFilter.value;
      }

      // 添加标签筛选
      if (selectedTags.value.length > 0) {
        params.tags = selectedTags.value.join(',');
      }

      // 发送请求
      const response = await axios.get('/posts/', { params });
      console.log('后端返回数据:', response.data);
      
      // 处理响应数据（根据后端返回的数据结构调整）
      let data = response.data;
      let total = 0;
      
      // 检查后端返回的数据结构
      if (Array.isArray(data)) {
        // 如果直接返回数组，则没有分页信息，使用所有数据的长度作为总数
        total = data.length;
      } else if (data.results && Array.isArray(data.results)) {
        // 如果返回的是分页对象
        data = data.results;
        total = data.count || 0;
      }
      
      // 处理响应数据
      const formattedPosts = data.map(post => ({
        id: post.id,
        title: post.title,
        authorName: post.user?.username || '匿名用户',
        authorAvatar: post.user?.avatar || 'https://picsum.photos/id/237/40/40',
        authorIdentity: post.user?.profile?.identity || '职场前辈',
        excerpt: post.content.substring(0, 50) + (post.content.length > 50 ? '...' : ''),
        tags: post.tags.split(','),
        viewCount: post.view_count,
        likeCount: post.like_count,
        commentCount: post.comment_count,
        publishTime: formatTimeAgo(post.created_at)
      }));

      // 如果后端返回了所有数据（没有分页），则在前端进行分页
      let paginatedPosts = formattedPosts;
      if (Array.isArray(response.data)) {
        // 计算分页的起始和结束索引
        const startIndex = (currentPage.value - 1) * pageSize.value;
        const endIndex = startIndex + pageSize.value;
        paginatedPosts = formattedPosts.slice(startIndex, endIndex);
      }

    // 更新数据
      posts.value = isLoadMore ? [...posts.value, ...paginatedPosts] : paginatedPosts;
    
      // 更新总数据条数
      totalResults.value = total;
      
      // 检查是否还有更多数据
      hasMore.value = currentPage.value * pageSize.value < total;
    } catch (error) {
      console.error('获取文章列表失败:', error);
      message.error('加载内容失败，请重试');
    } finally {
      loading.value = false;
    }
  };


// 获取热门数据
const fetchHotData = async () => {
  try {
    // 获取热门帖子，设置page_size为10，获取前10个热门帖子
    const hotResponse = await axios.get('/posts/', {
      params: { ordering: '-like_count', page_size: 10 }
    });
    
    // 处理响应数据
    let data = hotResponse.data;
    
    // 如果后端返回的是分页对象，获取results
    if (data.results && Array.isArray(data.results)) {
      data = data.results;
    }
    
    // 只取前10个热门帖子
    const top10Posts = data.slice(0, 10);
    
    hotPosts.value = top10Posts.map(post => ({
      id: post.id,
      title: post.title,
      likeCount: post.like_count,
      commentCount: post.comment_count
    }));

    // 获取活跃用户
    // const usersResponse = await axios.get('/user/active/');
    // activeUsers.value = usersResponse.data.map(user => ({
    //   id: user.id,
    //   name: user.username,
    //   avatar: user.avatar || 'https://picsum.photos/id/237/40/40',
    //   desc: `分享${user.article_count}篇经验 · 帮助${user.help_count|| 0}人`
    // }));
  } catch (error) {
    console.error('获取热门数据失败:', error);
  }
};

// 分页器事件处理
const handlePageChange = (page) => {
  currentPage.value = page;
  fetchPosts();
};

const handlePageSizeChange = (newPageSize) => {
  pageSize.value = newPageSize;
  currentPage.value = 1;
  fetchPosts();
};

// 初始化加载
onMounted(() => {
  fetchPosts();
  fetchHotData();
});


const value = ref(null);
const options = [
  {
    label: "最新",
    value: "latest",
    disabled: true
  },
  {
    label: "最热",
    value: "hot"
  },
  {
    label: "最多点赞",
    value: "mostLiked"
  },
  
];


const handleSearch = async ()=>{
  const keyword = searchQuery.value.trim(); // 提前处理关键词，代码更简洁
  if (!keyword) {
    message.warning('请输入搜索关键词~'); // 提示用户输入
    return;
  }
  
  isSearching.value = true; // 设置搜索状态
  loading.value = true; // 显示加载状态 
  try {
    const response = await axios.get('/posts/searching/', {
      params: { keyword,
       page: 1, 
       page_size: pageSize.value } 
    });
     // 格式化搜索结果（复用已有的格式化逻辑）
    searchResults.value = response.data.results.map(post => formatPost(post)); 
    totalResults.value = response.data.count; // 假设返回的结果数组
    hasMore.value = response.data.next !== null; // 根据后端分页判断
  } catch (error) {
        console.error('搜索请求失败:', error);
    console.error('错误状态码:', error.response?.status);
    console.error('请求的完整 URL:', error.config?.url);
    message.error('搜索失败，请重试');
  } finally {
    loading.value = false; // 隐藏加载状态
  }
}

const formatPost = (post) => ({
  id: post.id,
  title: post.title,
  authorName: post.user?.username || '匿名用户',
  authorAvatar: post.user?.avatar || 'https://picsum.photos/id/237/40/40',
  authorIdentity: post.user?.profile?.identity || '职场前辈',
  excerpt: post.content.substring(0, 50) + (post.content.length > 50 ? '...' : ''),
  tags: post.tags.split(','),
  viewCount: post.view_count,
  likeCount: post.like_count,
  commentCount: post.comment_count,
  publishTime: formatTimeAgo(post.created_at)
});


const handleFilterChange = (value) => {
  fetchPosts(); 
  console.log('筛选条件变化：', value);
};

const handleTagCheck = (tagId, checked) => {
  if (checked) {
    selectedTags.value.push(tagId);
  } else {
    selectedTags.value = selectedTags.value.filter(id => id !== tagId);
  }
  fetchPosts(); // 标签变化时重新加载
};


const handleMenuSelect = (key) => {
  switch (key) {
    case 'home':
      router.push('/home');
      break;
    case 'jobs':
      router.push('/jobs');
      break;
    case 'resources':
      router.push('/resources');
      break;
    case 'community':
      router.push('/community');
      break;
    case 'events':
      router.push('/events');
      break;
  }
};


const loadMorePosts = () => {
  if (loading.value) return;
  currentPage.value++;
  fetchPosts(true);
};

// 重置搜索状态
const resetSearch = () => {
  isSearching.value = false;
  searchQuery.value = '';
  searchResults.value = [];
  // 恢复显示原始列表
  fetchPosts();
};

// 加载更多搜索结果
const loadMoreSearch = async () => {
  if (loading.value) return;
  
  const keyword = searchQuery.value.trim();
  currentPage.value++;
  loading.value = true;
  
  try {
    const response = await axios.get('posts/searching/', {
      params: {
        keyword,
        page: currentPage.value,
        page_size: pageSize.value
      }
    });

    const newResults = response.data.results.map(post => formatPost(post));
    searchResults.value = [...searchResults.value, ...newResults];
    hasMore.value = response.data.next !== null;
  } catch (error) {
    console.error('加载更多搜索结果失败:', error);
    message.error('加载失败，请重试');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.community-layout {
  min-height: 100vh;
}

.filter-section {
  margin-bottom: 20px;
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

.community-layout.content-grid {
  display: grid !important;
  grid-template-columns: 20% 50% 30% !important;
  gap: 24px !important;
  width: 100% !important;
}

/* 确保网格项不被压缩 */
.community-layout .n-grid-item {
  min-width: 0 !important; /* 允许内容收缩 */
  width: 100% !important;
}

/* 侧边栏最小宽度保护 */
.community-layout .sidebar {
  min-width: 250px !important;
  max-width: 300px !important;
}

.filter-group {
  margin-bottom: 16px;
}

.community-layout .post-list {
  min-width: 400px !important;
  flex: 1 !important;
}

.post-card {
  cursor: pointer;
  transition: all 0.2s;
}

.post-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.author-info {
  padding: 8px 16px;
  align-items: center;
  gap: 8px;
}

.author-name {
  font-weight: 500;
}

.publish-time {
  margin-left: auto;
  color: #86909c;
  font-size: 14px;
}

.post-title {
  font-size: 18px;
  transition: color 0.2s;
}

.post-card:hover .post-title {
  color: #2d8cf0;
}

.post-excerpt {
  color: #4e5969;
  display: -webkit-box;
  overflow: hidden;
  margin-bottom: 12px;
}

.post-tags {
  margin-top: 8px;
}

.load-more-btn {
  margin-top: 16px;
}

.community-layout .right-sidebar {
  min-width: 250px !important;
  max-width: 300px !important;
}


.radio-group {
  display: flex;
  flex-wrap: wrap;
}


.search-result-header {
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-result-header h2 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.section-title2 {
  font-size: 16px;
  font-weight: 600;
  margin-top: 70px;
  margin-bottom: 8px;
}

.sidebar-card {
  width: 100%;
}

.sort-select {
  width: 100%;
  max-width: 200px;
}


.tag-space {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hot-post-item {
  cursor: pointer;
  padding: 8px 0;
  transition: background-color 0.2s;
}

.hot-post-item:hover {
  background-color: #f7f8fa;
}

.hot-post-meta {
  margin-top: 4px;
}

.active-user-item {
  cursor: pointer;
  padding: 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  flex: 1;
}

.footer {
  padding: 24px;
  background-color: #f7f8fa;
}
</style>