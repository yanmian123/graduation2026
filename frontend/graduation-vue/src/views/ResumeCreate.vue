<template>
  <div class="resume-create">
    <h2>创建我的简历</h2>
    <n-form ref="formRef" :model="form" :rules="rules" label-width="120px" class="form-container">
      <!-- 姓名 -->
      <n-form-item label="姓名" path="name">
        <n-input v-model:value="form.name" placeholder="请输入姓名" />
      </n-form-item>

      <!-- 性别 -->
      <n-form-item label="性别" path="sex">
        <n-select v-model:value="form.sex" :options="sexOptions" placeholder="请选择性别" />
      </n-form-item>

      <!-- 邮箱（必填） -->
      <n-form-item label="邮箱" path="email">
        <n-input v-model:value="form.email" type="email" placeholder="请输入邮箱（如xxx@test.com）" />
      </n-form-item>

      <!-- 电话 -->
      <n-form-item label="电话" path="phone">
        <n-input v-model:value="form.phone" placeholder="请输入手机号（可含国家代码）" />
      </n-form-item>

      <!-- 学历 -->
      <n-form-item label="学历" path="education">
        <n-select v-model:value="form.education" :options="educationOptions" placeholder="请选择学历" />
      </n-form-item>

      <!-- 求职意向 -->
      <n-form-item label="求职意向" path="job_objective">
        <n-input v-model:value="form.job_objective" placeholder="请输入求职意向（如前端工程师）" />
      </n-form-item>

      <!-- 实习经历（文本域） -->
      <n-form-item label="实习经历" path="internship_experience">
        <n-input
          v-model:value="form.internship_experience"
          type="textarea"
          rows="4"
          placeholder="请描述实习经历（如公司、职位、职责）"
        />
      </n-form-item>

            <!-- PDF上传组件 -->
      <n-form-item label="PDF简历" >
        <n-upload
          type="drag"
          accept=".pdf"
          :max-size="10 * 1024 * 1024"
          :auto-upload="false" 
          
          @change="handleFileChange"
          class="upload-area" 
        >
          <div >选择PDF文件</div>
        </n-upload>
      </n-form-item>

      <!-- 提交按钮 -->
      <n-form-item>
        <n-button type="primary" @click="handleSubmit">创建简历</n-button>
                <n-button @click="$router.push('/api/user/info')" style="margin-left: 16px;">取消</n-button>
        <n-button @click="$router.push('/resumes')" style="margin-left: 16px;">我的简历</n-button>

      </n-form-item>
    </n-form>
  </div>

</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useMessage} from 'naive-ui';
import { createResume } from '@/api/resume';
import axios from '@/utils/axios';


// const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
// 获取环境变量（在脚本中可以安全使用import.meta）

// 1. 表单数据（与后端 Resume 模型字段对应）
const form = ref({
  name: '',
  sex: '',
  email: '',
  phone: '',
  education: '',
  internship_experience: '',
  work_experience: '',
  project_experience: '',
  school_experience: '',
  self_evaluation: '',
  Scholarships: '',
  skills: '',
  job_objective: '',
  status: 'draft' // 默认草稿状态
});

// 2. 下拉选项（与模型选择字段对应）
const sexOptions = [
  { label: '男', value: 'M' },
  { label: '女', value: 'F' }
];
const educationOptions = [
  { label: '博士', value: '博士' },
  { label: '硕士', value: '硕士' },
  { label: '本科', value: '本科' },
  { label: '专科', value: '专科' },
  { label: '高中', value: '高中' },
  { label: '中专/中技', value: '中专/中技' },
  { label: '初中及以下', value: '初中及以下' }
];

// 3. 表单验证规则（与后端序列化器验证逻辑对应）
const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式（如xxx@test.com）', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^\+?1?\d{9,15}$/, message: '手机号格式不正确（9-15位数字，可含国家代码）', trigger: 'blur' }
  ]
};

// 4. 提交逻辑
const formRef = ref(null);
const message = useMessage();
const router = useRouter();
const selectedFile = ref(null);

const handleSubmit = async () => {
  if (!formRef.value) return;
  try {
    await formRef.value.validate();


        // 提交前再次验证文件（如果有文件）
    if (selectedFile.value) {
      const isPdf = selectedFile.value.type === 'application/pdf' && 
                   selectedFile.value.name.toLowerCase().endsWith('.pdf');
      if (!isPdf) {
        message.error('请上传PDF格式的文件（.pdf）');
        return; // 终止提交
      }
    }
    // 使用 FormData 处理文件上传
    const formData = new FormData();

    // 添加表单字段
    Object.keys(form.value).forEach(key => {
      if (form.value[key] !== '') {
        formData.append(key, form.value[key]);
      }
    });

    // 关键：确认文件已被正确添加
    if (selectedFile.value) {
      formData.append('pdf_file', selectedFile.value);  // 字段名必须与后端一致
      console.log('文件已添加到FormData：', selectedFile.value.name);
      console.log("FormData中的pdf_file：", formData.get('pdf_file'));
      console.log("selectedFile是否有效：", selectedFile.value instanceof File); // 检查selectedFile是否为File对象
    } else {
      console.warn('未选择文件，跳过文件上传');
    }

    // 提交表单（包含文件）
    await axios.post('/resumes/', formData, {
      headers: { 
        // 'Content-Type': 'multipart/form-data' ,
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}` 
      }  // 显式指定表单类型
    });

    message.success('简历创建成功！');
    router.push('/resumes');
  } catch (error) {
    // 错误处理
  }
};

// 定义上传接口的完整URL（基于Axios的baseURL）
const uploadAction = ref(`${axios.defaults.baseURL}/resumes/upload-pdf/`);

const uploadHeaders = ref({
  Authorization: `Bearer ${localStorage.getItem('accessToken') || ''}`
});

// 修正简历pdf上传前验证函数
// const handleBeforeUpload = (params) => {
//   const file = params.file; 
//   console.log('准备上传文件：', file);
//   if (!file) {
//     message.error('文件格式错误');
//     return false;
//   }

//   // 验证文件MIME类型（主验证）
//   const isPdfType = file.type === 'application/pdf';
//   // 验证文件后缀（辅助验证，防止MIME类型被篡改）
//   const isPdfSuffix = file.name.toLowerCase().endsWith('.pdf');

//   if (!isPdfType || !isPdfSuffix) {
//     message.error('请上传PDF格式的文件（.pdf）');
//     return false; // 阻止文件被选中
//   }
//   return true; // 验证通过，允许文件被选中
// };

// 3. 简化文件选择逻辑
const handleFileChange = (params) => {
  // params是包含file和fileList的对象，而非文件数组
  console.log('文件选择事件参数：', params);
  
  // 从fileList中提取文件（fileList是真正的文件数组）
  if (params.fileList && params.fileList.length > 0) {
    // 从文件项中获取原生File对象（naive-ui中文件对象在raw属性）
    const fileItem = params.fileList[0];
    selectedFile.value = fileItem.raw || fileItem.file; // 兼容不同版本
    
    // 验证文件对象
    if (selectedFile.value instanceof File) {
      console.log('成功获取文件：', selectedFile.value.name);
    } else {
      console.error('获取的不是有效的File对象', selectedFile.value);
      selectedFile.value = null;
    }
  } else {
    console.log('未选择任何文件');
    selectedFile.value = null;
  }
};
// 上传进度
const handleProgress = (progress) => {
  console.log('上传进度：', progress);
};

// 上传成功
const handleUploadSuccess = (response) => {
  message.success('PDF上传成功');
  // 可在这里获取后端返回的PDF URL，保存到表单
  form.value.pdf_url = response.pdf_url;
};

// 上传失败
const handleUploadError = (error) => {
  message.error('上传失败');
};
</script>

<style scoped>
.resume-create {
  padding: 24px;
}
.form-container {
  max-width: 800px;
  margin-top: 24px;
}
n-form-item {
  margin-bottom: 16px;
}

/* 在原style标签内添加 */
.upload-area {
  border: 2px dashed #4096ff; /* 蓝色虚线边框 */
  padding: 30px;
  border-radius: 6px;
  background: #f9f9f9;
  text-align: center;
  cursor: pointer;
}

.upload-text {
  color: #666;
  font-size: 14px;
}

/* 悬停效果 */
.upload-area:hover {
  border-color: #1890ff;
  background: #f0f7ff;
}
</style>