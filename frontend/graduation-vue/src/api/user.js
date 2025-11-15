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