// src/api/user.js
import axios from '@/utils/axios'; // 导入配置好的实例

// 获取当前用户信息
export const getUserInfo = () => {
  return axios.get('/user/info/', {
    params: {
      _t: Date.now()
    }
  });
};

// 更新用户信息
export const updateUserInfo = (data) => {
  return axios.put('/user/info/', data);
};

// 上传用户头像（使用PUT方法更新用户信息）
export const uploadUserAvatar = (formData) => {
  return axios.put('/user/info/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};