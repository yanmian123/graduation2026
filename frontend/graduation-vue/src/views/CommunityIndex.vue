<template>
  <n-layout class="community-layout">
    <!-- 主体内容 -->
    <n-layout-content class="main-content">
      <n-grid :x-gap="16" :y-gap="24" class="content-grid">
        <!-- 左侧列：包含筛选栏和帖子列表 -->
        <n-grid-item span="18">
          <!-- 筛选栏：放在帖子列表上方 -->
          <n-card title="内容筛选" bordered class="filter-card">
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
          </n-card>

          <!-- 帖子列表 -->
          <n-card title="" bordered style="margin-top: 24px;" class="post-list-container">
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
          <n-list hoverable clickable class="post-list">
            <n-list-item
              v-for="post in isSearching ? searchResults : posts"
              :key="post.id"
              @click="$router.push(`/community/post/${post.id}`)"
              class="post-item"
            >
              <!-- 作者信息：显示在标题上方 -->
              <n-space align="center" size="small" class="author-info-section">
                <!-- 头像悬停效果 -->
                <n-dropdown trigger="hover" :options="getUserDropdownOptions(post)" @select="handleUserDropdownSelect">
                  <n-avatar :src="post.authorAvatar" size="medium" round />
                </n-dropdown>
                <span class="author-name">{{ post.authorName }}</span>
                <n-tag size="small" type="info">{{ post.authorIdentity }}</n-tag>
                <span class="publish-time">{{ post.publishTime }}</span>
              </n-space>
              
              <n-thing
                :title="post.title"
                content-style="margin-top: 0;"
              >
                <div class="post-excerpt" v-html="post.excerpt"></div>
                                  <n-space wrap class="post-tags" style="margin-top: 4px">
                    <n-tag
                      v-for="tag in post.tags"
                      :key="tag"
                      size="small"
                      :bordered="false"
                      type="info"
                    >
                      {{ tag }}
                    </n-tag>
                  </n-space>
                <div class="post-meta" style="margin-top: 8px">
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
              </n-thing>
            </n-list-item>
          </n-list>
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
        </n-card> <!-- 结束帖子列表卡片 -->
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
import { ref, onMounted, h } from 'vue';
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
  NText,
  NIcon,
  NAvatar,
  NAvatarGroup,
  NSkeleton,
  NDropdown
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
  // 只有在加载更多时不重置currentPage，其他情况（包括翻页）都不重置
  if (!isLoadMore) {
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

      // 发送请求
      const response = await axios.get('/posts/', { params });
      console.log('当前页码:', currentPage.value, '每页条数:', pageSize.value);
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
      const formattedPosts = data.map(post => {
        // 详细日志记录每个帖子的用户信息
        console.log('单个帖子数据:', post);
        
        // 从帖子对象的顶层属性获取用户信息
        // 优先使用后端返回的nickname字段，如果没有或为空，则从username生成
        let authorName;
        if (post.nickname && post.nickname.trim()) {
            authorName = post.nickname;
        } else {
            const rawUsername = post.username || '匿名用户';
            const namePart = rawUsername.replace(/\d+/g, '');
            if (namePart) {
                authorName = namePart.charAt(0).toUpperCase() + namePart.slice(1) + '同学';
            } else {
                authorName = '用户' + rawUsername;
            }
        }
        
        // 为头像URL添加localhost:8000前缀（如果是相对路径）
        const rawAvatar = post.user_avatar || post.avatar || post.user?.avatar;
        const userAvatar = rawAvatar ? (rawAvatar.startsWith('http') ? rawAvatar : `http://localhost:8000${rawAvatar}`) : 'https://picsum.photos/id/237/40/40';
        
        return {
          id: post.id,
          title: post.title,
          authorName: authorName, // 直接使用后端返回的nickname，没有则使用username
          authorId: post.user_id || post.user?.id || Math.floor(Math.random() * 1000),
          authorAvatar: userAvatar,
          authorIdentity: post.identity || post.user?.profile?.identity || '职场前辈',
          authorSchool: post.user?.profile?.school || '未填写',
          isFollowing: Math.random() > 0.5,
          postCount: Math.floor(Math.random() * 100) + 10,
          excerpt: post.content.substring(0, 50) + (post.content.length > 50 ? '...' : ''),
          tags: post.tags.split(','),
          viewCount: post.view_count || post.viewCount,
          likeCount: post.like_count || post.likeCount,
          commentCount: post.comment_count || post.commentCount,
          publishTime: formatTimeAgo(post.created_at)
        };
      });

      // 如果后端返回了所有数据（没有分页），则在前端进行分页
      let paginatedPosts = formattedPosts;
      if (Array.isArray(response.data)) {
        // 计算分页的起始和结束索引
        const startIndex = (currentPage.value - 1) * pageSize.value;
        const endIndex = startIndex + pageSize.value;
        console.log('分页范围:', startIndex, '-', endIndex);
        paginatedPosts = formattedPosts.slice(startIndex, endIndex);
        console.log('分页后数据条数:', paginatedPosts.length);
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

const formatPost = (post) => {
  // 从帖子对象的顶层属性获取用户信息
  // 优先使用后端返回的nickname字段，如果没有或为空，则从username生成
  let authorName;
  if (post.nickname && post.nickname.trim()) {
      authorName = post.nickname;
  } else {
      const rawUsername = post.username || '匿名用户';
      const namePart = rawUsername.replace(/\d+/g, '');
      if (namePart) {
          authorName = namePart.charAt(0).toUpperCase() + namePart.slice(1) + '同学';
      } else {
          authorName = '用户' + rawUsername;
      }
  }
  
  // 为头像URL添加localhost:8000前缀（如果是相对路径）
  const rawAvatar = post.user_avatar || post.avatar || post.user?.avatar || post.author?.avatar;
  const userAvatar = rawAvatar ? (rawAvatar.startsWith('http') ? rawAvatar : `http://localhost:8000${rawAvatar}`) : 'https://picsum.photos/id/237/40/40';
  const userId = post.user_id || post.user?.id || post.author?.id || Math.floor(Math.random() * 1000);
  
  return {
    id: post.id,
    title: post.title,
    authorName: authorName, // 直接使用后端返回的nickname，没有则使用username
    authorId: userId,
    authorAvatar: userAvatar,
    authorIdentity: post.identity || post.user?.profile?.identity || '职场前辈',
    authorSchool: post.user?.profile?.school || post.author?.school || '未填写',
    isFollowing: Math.random() > 0.5,
    postCount: Math.floor(Math.random() * 100) + 10,
    excerpt: post.content.substring(0, 50) + (post.content.length > 50 ? '...' : ''),
    tags: post.tags.split(','),
    viewCount: post.view_count || post.viewCount,
    likeCount: post.like_count || post.likeCount,
    commentCount: post.comment_count || post.commentCount,
    publishTime: formatTimeAgo(post.created_at)
  };
};


const handleFilterChange = (value) => {
  fetchPosts(); 
  console.log('筛选条件变化：', value);
};

// 用户头像悬停下拉菜单配置
function getUserDropdownOptions(post) {
  // 渲染用户信息头部
  function renderUserHeader() {
    return h(
      'div',
      {
        style: 'display: flex; align-items: center; padding: 12px 16px;'
      },
      [
        h(NAvatar, {
          round: true,
          style: 'margin-right: 16px; width: 64px; height: 64px;',
          src: post.authorAvatar
        }),
        h('div', null, [
          h('div', { style: 'font-weight: bold; margin-bottom: 4px;' }, post.authorName),
          h('div', { style: 'font-size: 12px; color: #999;' }, post.authorIdentity || '未设置身份'),
          h('div', { style: 'font-size: 12px; color: #999; margin-top: 4px;' }, '毕业院校：' + (post.authorSchool || '未填写'))
        ])
      ]
    );
  }

  // 渲染统计数据
  function renderStats() {
    return h(
      'div',
      {
        style: 'padding: 8px 16px; background-color: #f7f7f7; display: flex; justify-content: space-around;'
      },
      [
        h('div', { style: 'text-align: center;' }, [
          h('div', { style: 'font-weight: bold;' }, post.postCount || 0),
          h('div', { style: 'font-size: 12px; color: #999;' }, '发帖数')
        ]),
        h('div', { style: 'text-align: center;' }, [
          h('div', { style: 'font-weight: bold;' }, post.likeCount || 0),
          h('div', { style: 'font-size: 12px; color: #999;' }, '获赞数')
        ])
      ]
    );
  }

  // 渲染操作按钮
  function renderActions() {
    return h(
      'div',
      {
        style: 'padding: 12px 16px; display: flex; gap: 8px; justify-content: center;'
      },
      [
        h(NButton, {
          type: post.isFollowing ? 'default' : 'primary',
          size: 'small',
          round: true,
          onClick: () => handleFollow(post.authorId)
        }, { default: () => (post.isFollowing ? '已关注' : '关注') }),
        h(NButton, {
          type: 'default',
          size: 'small',
          round: true,
          onClick: () => handleMessage(post.authorId)
        }, { default: () => '私信' })
      ]
    );
  }

  return [
    {
      key: 'user-header',
      type: 'render',
      render: renderUserHeader
    },
    {
      key: 'stats',
      type: 'render',
      render: renderStats
    },
    {
      key: 'actions',
      type: 'render',
      render: renderActions
    }
  ];
}

// 处理用户下拉菜单选择
function handleUserDropdownSelect(key) {
  console.log('用户菜单选择：', key);
}

// 处理关注用户
function handleFollow(userId) {
  const isLogin = !!localStorage.getItem('accessToken')
  if (!isLogin) {
    message.warning('请先登录后再关注用户')
    router.push('/login')
    return
  }

  const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
  if (currentUser.id === userId) {
    message.error('不能关注自己')
    return
  }

  const post = posts.value.find(p => p.authorId === userId)
  if (!post) return

  if (post.isFollowing) {
    axios.delete(`/users/${userId}/follow/`)
      .then(() => {
        post.isFollowing = false
        message.success('已取消关注')
      })
      .catch(error => {
        console.error('取消关注失败:', error)
        message.error('操作失败，请稍后重试')
      })
  } else {
    axios.post(`/users/${userId}/follow/`)
      .then(() => {
        post.isFollowing = true
        message.success('关注成功')
      })
      .catch(error => {
        console.error('关注失败:', error)
        message.error('操作失败，请稍后重试')
      })
  }
}

// 处理私信用户
function handleMessage(userId) {
  message.info('私信功能待实现');
}


// 重置搜索状态
const resetSearch = () => {
  isSearching.value = false;
  searchQuery.value = '';
  searchResults.value = [];
  // 恢复显示原始列表
  fetchPosts();
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
  padding: 10px;
}

.community-layout.content-grid {
  display: grid !important;
  grid-template-columns: 20% 50% 30% !important;
  gap: 16px !important;
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

/* 筛选栏和帖子列表的上下布局样式 */
.filter-card {
  margin-bottom: 16px;
}



/* 帖子列表容器样式 */
.post-list-container {
  padding: 1px;
}

.post-skeleton {
  margin: 0;
}

.pagination-container {
  padding-left: 20px;
}

/* 响应式布局调整 */
@media screen and (max-width: 992px) {
  .filter-row {
    flex-direction: column;
    gap: 16px;
  }
  
  .sort-section {
    width: 100%;
  }
  
  .sort-select {
    width: 100%;
  }
}

.author-name {
  font-weight: 500;
}

.author-info-section {
  width: 100%;
  padding: 8px 0;
}

.post-item {
  padding: 12px;
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
  margin-top: 16px;
  margin-bottom: 8px;
}

.sidebar-card {
  width: 100%;
  margin-bottom: 12px;
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
  padding: 24x;
  background-color: #f7f8fa;
}
</style>


