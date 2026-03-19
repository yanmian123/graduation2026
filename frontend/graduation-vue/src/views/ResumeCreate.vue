<template>
  <div class="resume-create">
    <h2>创建我的简历</h2>
    
    <!-- 基本信息 -->
    <n-card title="基本信息" class="section-card">
      <n-form ref="formRef" :model="form" :rules="rules" label-width="120px">
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

        <!-- 毕业院校 -->
        <n-form-item label="毕业院校" path="school">
          <n-input v-model:value="form.school" placeholder="请输入毕业院校" />
        </n-form-item>

        <!-- 专业 -->
        <n-form-item label="专业" path="major">
          <n-input v-model:value="form.major" placeholder="请输入专业（如计算机科学与技术）" />
        </n-form-item>

        <!-- 求职意向 -->
        <n-form-item label="求职意向" path="job_objective">
          <n-input v-model:value="form.job_objective" placeholder="请输入求职意向（如前端工程师）" />
        </n-form-item>
      </n-form>
    </n-card>

    <!-- 经历信息 -->
    <n-card title="经历信息" class="section-card">
      <n-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <!-- 实习经历（文本域） -->
        <n-form-item label="实习经历" path="internship_experience">
          <n-input
            v-model:value="form.internship_experience"
            type="textarea"
            rows="4"
            placeholder="请描述实习经历（如公司、职位、职责）"
          />
        </n-form-item>

        <!-- 工作经历（文本域） -->
        <n-form-item label="工作经历" path="work_experience">
          <n-input
            v-model:value="form.work_experience"
            type="textarea"
            rows="4"
            placeholder="请描述工作经历（如公司、职位、职责、成就）"
          />
        </n-form-item>

        <!-- 项目经历（文本域） -->
        <n-form-item label="项目经历" path="project_experience">
          <n-input
            v-model:value="form.project_experience"
            type="textarea"
            rows="4"
            placeholder="请描述项目经历（如项目名称、角色、技术栈、成果）"
          />
        </n-form-item>

        <!-- 校园经历（文本域） -->
        <n-form-item label="校园经历" path="school_experience">
          <n-input
            v-model:value="form.school_experience"
            type="textarea"
            rows="4"
            placeholder="请描述校园经历（如社团活动、学生会、志愿者经历）"
          />
        </n-form-item>
      </n-form>
    </n-card>

    <!-- 其他信息 -->
    <n-card title="其他信息" class="section-card">
      <n-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <!-- 奖学金（文本域） -->
        <n-form-item label="奖学金" path="scholarships">
          <n-input
            v-model:value="form.scholarships"
            type="textarea"
            rows="3"
            placeholder="请描述获得的奖学金（如国家奖学金、校级奖学金等）"
          />
        </n-form-item>

        <!-- 技能标签（文本域） -->
        <n-form-item label="技能标签" path="skills">
          <n-input
            v-model:value="form.skills"
            type="textarea"
            rows="3"
            placeholder="请填写技能标签（如：Java、Python、Vue.js、MySQL等，用逗号分隔）"
          />
        </n-form-item>

        <!-- 自我评价（文本域） -->
        <n-form-item label="自我评价" path="self_evaluation">
          <n-input
            v-model:value="form.self_evaluation"
            type="textarea"
            rows="4"
            placeholder="请进行自我评价（如性格特点、学习能力、团队协作等）"
          />
        </n-form-item>
      </n-form>
    </n-card>

    <!-- PDF上传 -->
    <n-card title="简历文件" class="section-card">
      <n-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <n-form-item label="PDF简历">
          <n-upload
            type="drag"
            accept=".pdf"
            :max-size="10 * 1024 * 1024"
            :auto-upload="false" 
            @change="handleFileChange"
            class="upload-area" 
          >
            <div class="upload-text">
              <n-icon :component="DocumentOutline" size="32" />
              <div>点击或拖拽上传PDF文件</div>
              <div class="upload-hint">支持 .pdf 格式，最大 10MB</div>
            </div>
          </n-upload>
        </n-form-item>
      </n-form>
    </n-card>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <n-button type="primary" size="large" @click="handleSubmit">创建简历</n-button>
      <n-button size="large" @click="$router.push('/userinfo')">取消</n-button>
      <n-button size="large" @click="$router.push('/resumes')">我的简历</n-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useMessage } from 'naive-ui';
import { NCard } from 'naive-ui';
import { DocumentOutline } from '@vicons/ionicons5';
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
  school: '',
  major: '',
  internship_experience: '',
  work_experience: '',
  project_experience: '',
  school_experience: '',
  self_evaluation: '',
  scholarships: '',
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
  max-width: 900px;
  margin: 0 auto;
}

.resume-create h2 {
  text-align: center;
  margin-bottom: 32px;
  color: #333;
  font-size: 28px;
  font-weight: 600;
}

.section-card {
  margin-bottom: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.section-card :deep(.n-card__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  font-size: 16px;
  padding: 16px 20px;
}

.section-card :deep(.n-card__content) {
  padding: 24px 20px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
}

.upload-area {
  border: 2px dashed #4096ff;
  padding: 24px 20px;
  border-radius: 8px;
  background: #f9f9f9;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-area:hover {
  border-color: #1890ff;
  background: #f0f7ff;
  transform: translateY(-2px);
}

.upload-text {
  color: #666;
  font-size: 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.upload-hint {
  color: #999;
  font-size: 12px;
  margin-top: 0;
}

.n-form-item {
  margin-bottom: 20px;
}

.n-form-item:last-child {
  margin-bottom: 0;
}

:deep(.n-input) {
  border-radius: 4px;
}

:deep(.n-input__textarea) {
  border-radius: 4px;
}

:deep(.n-select) {
  border-radius: 4px;
}
</style>