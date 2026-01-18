import axios from '@/utils/axios';

// 获取文章列表（首页展示用）
export const getArticleList = () => {
  return axios.get('/api/articles/', {
    params: {
      ordering: '-created_at', // 最新发布的在前
      page_size: 4 // 首页显示4篇
    }
  });
};

// 获取文章详情
export const getArticleDetail = (id: number) => {
  return axios.get(`/posts/${id}/`);
};

// 增加阅读量
export const increaseViewCount = (id: number) => {
  return axios.post(`/posts/${id}/view/`);
};

// 文章点赞
export const likeArticle = (id: number) => {
  return axios.post(`/posts/${id}/like/`);
};

// 取消文章点赞
export const unlikeArticle = (id: number) => {
  return axios.delete(`/posts/${id}/like/`);
};

// 收藏文章
export const collectArticle = (id: number) => {
  return axios.post(`/posts/${id}/collect/`);
};

// 取消收藏
export const uncollectArticle = (id: number) => {
  return axios.delete(`/posts/${id}/collect/`);
};

// 获取文章评论
export const getArticleComments = (id: number, page: number = 1, page_size: number = 5) => {
  return axios.get(`/posts/${id}/get_comments/`, {
    params: {
      page,
      page_size
    }
  });
};

// 发表评论
export const addComment = (id: number, data: { content: string }) => {
  return axios.post(`/posts/${id}/add_comment/`, data);
};

// 评论点赞
export const likeComment = (commentId: number) => {
  return axios.post(`/comments/${commentId}/like/`);
};

// 关注作者
export const followUser = (userId: number) => {
  return axios.post(`/users/${userId}/follow/`);
};