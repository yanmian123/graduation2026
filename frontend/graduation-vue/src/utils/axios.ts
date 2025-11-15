// 新建src/utils/axios.ts
import axios from 'axios'

const instance = axios.create({
  baseURL: 'http://localhost:8000/api',  // 基础路径
})
// 新增：打印基础路径
console.log('axios 基础路径:', instance.defaults.baseURL);
// 请求拦截器：添加令牌到请求头
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken')
    if (token && config.url && !config.url.includes('/register/'))  {
      config.headers.Authorization = `Bearer ${token}`  // JWT标准格式
    }
    return config
  },
  (error) => Promise.reject(error)
)

export default instance