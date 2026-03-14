<template>
  <div class="resume-edit">
    <h2>编辑简历</h2>
    
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
          <!-- 已上传PDF预览 -->
          <div v-if="form.pdf_url" class="pdf-preview">
            <div class="preview-header">
              <span class="preview-title">已上传的PDF简历</span>
              <n-button type="error" size="small" @click="handleDeletePdf" :loading="deletingPdf">
                删除PDF
              </n-button>
            </div>
            <div class="preview-content">
              <n-button type="primary" @click="previewPdf" class="preview-btn">
                <template #icon>
                  <n-icon><EyeOutline /></n-icon>
                </template>
                预览PDF
              </n-button>
              <span class="file-name">{{ getFileName(form.pdf_url) }}</span>
            </div>
          </div>

          <!-- PDF上传组件 -->
          <div class="upload-section">
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
          </div>
        </n-form-item>
      </n-form>
    </n-card>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <n-button type="primary" size="large" @click="handleSubmit" :loading="submitting">保存修改</n-button>
      <n-button size="large" @click="$router.push('/resumes')">取消</n-button>
      <n-button size="large" @click="$router.push('/resumes')">我的简历</n-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useMessage } from 'naive-ui';
import { NCard } from 'naive-ui';
import { EyeOutline, DocumentOutline } from '@vicons/ionicons5';
import { getResumeDetail, updateResume, deleteResumePdf } from '@/api/resume';
import axios from '@/utils/axios';

// 路由相关
const router = useRouter();
const route = useRoute();
const resumeId = route.params.id;

// 响应式数据
const form = ref({
  name: '',
  sex: '',
  email: '',
  phone: '',
  education: '',
  school: '',
  internship_experience: '',
  work_experience: '',
  project_experience: '',
  school_experience: '',
  self_evaluation: '',
  scholarships: '',
  skills: '',
  job_objective: '',
  status: 'draft',
  pdf_url: ''
});

const selectedFile = ref(null);
const submitting = ref(false);
const deletingPdf = ref(false);

// 下拉选项
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

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^\+?1?\d{9,15}$/, message: '手机号格式不正确', trigger: 'blur' }
  ]
};

// 表单引用和消息提示
const formRef = ref(null);
const message = useMessage();

// 获取简历详情并回显
const fetchResumeDetail = async () => {
  try {
    const response = await getResumeDetail(resumeId);
    form.value = response.data;
    console.log('PDF URL:', form.value.pdf_url);
  } catch (error) {
    message.error('获取简历详情失败');
    console.error(error);
  }
};

// 文件处理
const handleFileChange = (params) => {
  if (params.fileList && params.fileList.length > 0) {
    const fileItem = params.fileList[0];
    selectedFile.value = fileItem.raw || fileItem.file;
    
    if (selectedFile.value instanceof File) {
      console.log('选择新文件：', selectedFile.value.name);
    } else {
      console.error('无效的文件对象');
      selectedFile.value = null;
    }
  } else {
    selectedFile.value = null;
  }
};

// 获取文件名
const getFileName = (url) => {
  if (!url) return '';
  return url.split('/').pop() || '简历.pdf';
};

// PDF预览 - 新窗口打开
const previewPdf = () => {
  if (!form.value.pdf_url) {
    message.warning('暂无PDF文件可预览');
    return;
  }
  
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
  const pdfUrl = form.value.pdf_url.startsWith('http') ? form.value.pdf_url : `${baseUrl}${form.value.pdf_url}`;
  
  window.open(pdfUrl, '_blank', 'width=1200,height=800,scrollbars=yes');
};

// 删除PDF
const handleDeletePdf = async () => {
  if (!form.value.pdf_url) {
    message.warning('暂无PDF文件可删除');
    return;
  }
  
  try {
    deletingPdf.value = true;
    await deleteResumePdf(resumeId);
    form.value.pdf_url = '';
    message.success('PDF文件删除成功');
  } catch (error) {
    message.error('删除PDF失败');
    console.error(error);
  } finally {
    deletingPdf.value = false;
  }
};

const handleSubmit = async () => {
  if (!formRef.value) return;
  
  try {
    submitting.value = true;
    await formRef.value.validate();

    if (selectedFile.value) {
      const isPdf = selectedFile.value.type === 'application/pdf' && 
                   selectedFile.value.name.toLowerCase().endsWith('.pdf');
      if (!isPdf) {
        message.error('请上传PDF格式的文件（.pdf）');
        return;
      }
    }

    const formData = new FormData();

    Object.keys(form.value).forEach(key => {
      if (form.value[key] !== undefined && form.value[key] !== null && form.value[key] !== '') {
        formData.append(key, form.value[key]);
      }
    });

    if (selectedFile.value) {
      formData.append('pdf_file', selectedFile.value);
      console.log('文件已添加到FormData：', selectedFile.value.name);
    }

    await updateResume(resumeId, formData, {
      headers: { 
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}` 
      }
    });

    message.success('简历更新成功！');
    router.push('/resumes');
  } catch (error) {
    const errorMsg = error.response?.data?.message || '更新失败，请检查输入';
    message.error(errorMsg);
    console.error('更新错误详情:', error);
  } finally {
    submitting.value = false;
  }
};

// 页面加载时获取简历数据
onMounted(fetchResumeDetail);
</script>

<style scoped>
.resume-edit {
  padding: 24px;
  max-width: 900px;
  margin: 0 auto;
}

.resume-edit h2 {
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

/* PDF预览样式 */
.pdf-preview {
  margin-bottom: 16px;
  padding: 16px;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  background: #f9f9f9;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.preview-title {
  font-weight: bold;
  color: #333;
}

.preview-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.preview-btn {
  flex-shrink: 0;
}

.file-name {
  color: #666;
  font-size: 14px;
}

/* 上传区域样式 */
.upload-section {
  width: 100%;
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