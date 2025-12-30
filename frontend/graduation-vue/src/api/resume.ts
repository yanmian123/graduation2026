import axios from '@/utils/axios';//每次请求都会携带token

// 1. 创建简历
export const createResume = (data: any) => {
  return axios.post('/resumes/', data); // 对应后端 /api/resumes/（Axios基础路径已含 /api）
};

// 2. 获取当前用户所有简历
export const getResumeList = () => {
  return axios.get('/resumes/');
};

// 3. 获取单个简历详情
export const getResumeDetail = (id: number | string) => {
  return axios.get(`/resumes/${id}/`);
};

// 4. 部分更新简历（推荐：无需传所有字段）
export const updateResume = (id: number | string, data: any) => {
  return axios.patch(`/resumes/${id}/`, data);
};

// 5. 删除简历
export const deleteResume = (id: number | string) => {
  return axios.delete(`/resumes/${id}/`, { data: { pdf_url: null } });
};

// 专门删除PDF文件的API
export const deleteResumePdf = (id: number | string) => {
  return axios.post(`/resumes/${id}/delete-pdf/`);
}