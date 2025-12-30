<template>
  <div class="resume-edit">
    <h2>编辑简历</h2>
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

      <!-- PDF文件操作区域 -->
      <n-form-item label="PDF简历">
        <div class="pdf-operations">
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
              <div class="upload-content">
                <n-icon size="48" class="upload-icon">
                  <CloudUploadOutline />
                </n-icon>
                <div class="upload-text">点击或拖拽PDF文件到此处上传</div>
                <div class="upload-hint">支持.pdf格式，最大10MB</div>
              </div>
            </n-upload>
          </div>
        </div>
      </n-form-item>

      <!-- 提交按钮 -->
      <n-form-item>
        <n-button type="primary" @click="handleSubmit" :loading="submitting">保存修改</n-button>
        <n-button @click="$router.push('/resumes')" style="margin-left: 16px;">取消</n-button>
      </n-form-item>
    </n-form>

    <!-- PDF预览模态框 -->
    <n-modal v-model:show="showPdfPreview" transform-origin="center">
      <n-card
        style="width: 90%; max-width: 1000px; height: 90vh;"
        :bordered="false"
        size="huge"
        role="dialog"
        aria-modal="true"
      >
        <template #header>
          <div class="modal-header">
            <span>PDF预览 - {{ currentPdfName }}</span>
            <n-button quaternary circle @click="showPdfPreview = false">
              <template #icon>
                <n-icon><CloseOutline /></n-icon>
              </template>
            </n-button>
          </div>
        </template>
        <div class="pdf-viewer-container">
          <iframe
            v-if="showPdfPreview"
            :src="pdfPreviewUrl"
            width="100%"
            height="100%"
            style="border: none;"
            title="PDF预览"
          ></iframe>
        </div>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useMessage } from 'naive-ui';
import { getResumeDetail, updateResume, deleteResumePdf } from '@/api/resume';
import { EyeOutline, CloudUploadOutline, CloseOutline } from '@vicons/ionicons5';

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
  internship_experience: '',
  work_experience: '',
  project_experience: '',
  school_experience: '',
  self_evaluation: '',
  Scholarships: '',
  skills: '',
  job_objective: '',
  status: 'draft',
  pdf_url: ''
});

const selectedFile = ref(null);
const showPdfPreview = ref(false);
const submitting = ref(false);
const deletingPdf = ref(false);

// 计算属性
const pdfPreviewUrl = computed(() => {
  if (!form.value.pdf_url) return '';
  // 确保URL是完整的（如果是相对路径，添加基础URL）
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
  return form.value.pdf_url.startsWith('http') ? form.value.pdf_url : `${baseUrl}${form.value.pdf_url}`;
});

const currentPdfName = computed(() => {
  return getFileName(form.value.pdf_url);
});

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
  
  // 直接在新窗口打开PDF链接
  window.open(pdfPreviewUrl.value, '_blank', 'width=1200,height=800,scrollbars=yes');
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
            const formData = new FormData();
            
            // 简化字段处理，只添加必要的字段
            const fields = ['name', 'sex', 'email', 'phone', 'education', 
                          'job_objective', 'internship_experience', 'skills'];
            
            fields.forEach(key => {
                if (form.value[key] !== undefined && form.value[key] !== null) {
                    formData.append(key, form.value[key]);
                }
            });

            formData.append('pdf_file', selectedFile.value);

            await updateResume(resumeId, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
        } else {
            await updateResume(resumeId, form.value);
        }

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
}

.form-container {
  max-width: 800px;
  margin-top: 24px;
}

n-form-item {
  margin-bottom: 16px;
}

/* PDF操作区域样式 */
.pdf-operations {
  width: 100%;
}

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
.upload-area {
  border: 2px dashed #4096ff;
  border-radius: 6px;
  background: #f9f9f9;
}

.upload-content {
  padding: 30px;
  text-align: center;
}

.upload-icon {
  color: #4096ff;
  margin-bottom: 8px;
}

.upload-text {
  color: #333;
  font-size: 16px;
  margin-bottom: 4px;
}

.upload-hint {
  color: #666;
  font-size: 12px;
}

.upload-area:hover {
  border-color: #1890ff;
  background: #f0f7ff;
}

/* 模态框样式 */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pdf-viewer-container {
  width: 100%;
  height: calc(90vh - 120px);
}
</style>