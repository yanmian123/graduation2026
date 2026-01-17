// src/api/user.js
import axios from '@/utils/axios'; // 导入配置好的实例

// 获取当前用户信息
export const getUserInfo = () => {
  return axios.get('/user/info/');
};

// 更新用户信息
export const updateUserInfo = (data) => {
  return axios.put('/user/info/', data);
};

// 上传用户头像
export const uploadUserAvatar = (formData) => {
  // 不手动设置Content-Type，让axios自动处理
  // axios会自动设置正确的Content-Type，包括boundary信息
  return axios.post('/user/info/', formData);
};