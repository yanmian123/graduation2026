<template>
  <n-layout class="create-layout">
    <!-- 顶部导航（复用平台导航） -->
    <n-layout-header bordered class="header">
      <!-- 导航内容同首页，省略 -->
    </n-layout-header>

    <n-layout-content class="main-content">
      <n-card title="发布经验分享" bordered class="create-card">
        <n-form
          ref="formRef"
          :model="formData"
          :rules="formRules"
          label-placement="top"
          label-width="auto"
          label-align="left"
        >
          <!-- 标题输入 -->
          <n-form-item label="帖子标题" path="title" required>
            <n-input
              v-model:value="formData.title"
              placeholder="请输入标题（如“我的秋招面试全记录”）"
              :maxlength="80"
              show-count
              size="large"
              class="title-input"
            />
          </n-form-item>

          <!-- 分类和标签一行显示 -->
          <div class="form-row">
            <n-form-item label="内容分类" path="category" required class="form-item-inline">
              <n-select
                v-model:value="formData.category"
                placeholder="选择分类"
                clearable
                :options="categoryOptions"
                size="large"
              />
            </n-form-item>

            <n-form-item label="标签" path="tags" class="form-item-inline">
              <n-dynamic-input
                v-model:value="formData.tags"
                placeholder="输入标签后按回车/点击+号添加"
                :min="0"  
                :max="5"  
                :autocomplete-options="tagOptions"  
                @search="handleTagSearch"
                size="large"
              />
            </n-form-item>
          </div>

          <n-text type="secondary" class="tips" depth="3" size="small">
            最多添加5个标签，有助于内容曝光
          </n-text>

          <!-- 富文本编辑 -->
          <n-form-item label="经验内容" path="content" required>
            <div class="editor-container">
              <quill-editor
                ref="quillRef"  
                v-model:content="formData.content"
                :options="editorOptions"
                @text-change="handleContentChange"
              />
            </div>
          </n-form-item>

          <!-- 附件上传 -->
          <n-form-item label="附件（可选）">
            <n-upload
              action="/api/upload/file"  
              accept=".pdf,.doc,.docx,.zip"
              :max-size="10 * 1024 * 1024" 
              :on-success="handleFileSuccess"
              :on-error="handleFileError"
              :file-list="fileList"
              @remove="handleFileRemove"
              multiple
            >
              <n-button>
                <template #icon>
                  <n-icon><Document /></n-icon>
                </template>
                选择文件上传
              </n-button>
            </n-upload>
            <n-text type="secondary" depth="3" size="small" style="margin-top: 8px;">
              支持上传面经文档、笔试题库等（最大10MB）
            </n-text>
          </n-form-item>

          <!-- 操作按钮 -->
          <n-form-item :show-label="false">
            <n-space size="large">
              <n-button size="large" @click="handlePreview">
                <template #icon>
                  <n-icon><Eye /></n-icon>
                </template>
                预览
              </n-button>
              <n-button type="primary" size="large" @click="handleSubmit">
                <template #icon>
                  <n-icon><Send /></n-icon>
                </template>
                发布
              </n-button>
              <n-button size="large" @click="$router.push('/community')">
                取消
              </n-button>
            </n-space>
          </n-form-item>
        </n-form>
      </n-card>
    </n-layout-content>
  </n-layout>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useMessage } from 'naive-ui';
// 富文本编辑器
import { QuillEditor } from '@vueup/vue-quill';
import '@vueup/vue-quill/dist/vue-quill.snow.css';
// Naive UI 组件
import {
  NLayout,
  NLayoutHeader,
  NLayoutContent,
  NCard,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  NUpload,
  NButton,
  NText,
  NDynamicInput,
  NSpace,
  NIcon
} from 'naive-ui';
import { Document, Eye, Send } from '@vicons/ionicons5';
// 接口请求
import axios from '@/utils/axios';

const router = useRouter();
const message = useMessage();
const formRef = ref(null);

// 表单数据
const formData = reactive({
  title: '',
  category: '',
  tags: [],
  content: '',  // 富文本内容（HTML格式）
  attachments: []  // 附件ID列表（后端返回）
});

// 分类选项
const categoryOptions = [
  { label: "面试经验", value: "interview" },
  { label: "简历技巧", value: "resume" },
  { label: "行业选择", value: "career" },
  { label: "笔试攻略", value: "exam" },
  { label: "其他", value: "others" }
];

// 表单验证规则
const formRules = {
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 5, message: '标题至少5个字符', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  content: [
    { 
      required: true, 
      validator: (rule, value, callback) => {
        // 检查富文本内容是否为空
        if (!value || !value.ops || value.ops.length === 0) {
          callback(new Error('请输入经验内容'));
          return;
        }

        // 从Delta格式中提取纯文本
        const text = value.ops.reduce((str, op) => {
          if (typeof op.insert === 'string') {
            return str + op.insert;
          }
          return str;
        }, '').trim();

        // if (text.length < 50) {
        //   callback(new Error('内容至少50个字符'));
        // } else {
        //   callback();
        // }
      },
      trigger: 'change'
    }
  ]
};

// 富文本编辑器配置
const editorOptions = {
  modules: {
    toolbar: [
      [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
      [{ 'size': ['small', false, 'large', 'huge'] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'align': [] }],
      [{ 'list': 'ordered' }, { 'list': 'bullet' }],
      [{ 'indent': '-1' }, { 'indent': '+1' }],
      ['link', 'image'],
      ['clean']
    ]
  },
  placeholder: '请分享你的经验...（建议包含具体经历、方法技巧和个人感悟）'
};

const quillRef = ref(null);

// 标签联想功能
const tagOptions = ref([]);
const handleTagSearch = async (keyword) => {
  if (keyword.length < 2) return;
  try {
    const res = await axios.get(`/api/tags/suggest?keyword=${keyword}`);
    tagOptions.value = res.data.map(tag => tag.name);
  } catch (error) {
    message.error('标签联想获取失败');
  }
};

// 附件上传
const fileList = ref([]);
const handleFileSuccess = (response, file) => {
  formData.attachments.push(response.data.fileId);
  message.success('文件上传成功');
};
const handleFileError = (error) => {
  message.error('文件上传失败：' + error.message);
};
const handleFileRemove = (file) => {
  const index = formData.attachments.findIndex(id => id === file.response?.data?.fileId);
  if (index > -1) {
    formData.attachments.splice(index, 1);
  }
};

// 内容变化监听
const handleContentChange = () => {
  // 可调用接口保存草稿
};

// 预览功能
const handlePreview = () => {
  formRef.value.validate((errors) => {
    if (!errors) {
      router.push({
        path: '/community/preview',
        query: { data: JSON.stringify(formData) }
      });
    } else {
      // 显示验证错误
      Object.keys(errors).forEach(field => {
        message.error(`${getFieldLabel(field)}: ${errors[field][0].message}`);
      });
    }
  });
};

// 辅助函数：获取字段显示标签
const getFieldLabel = (field) => {
  const labels = {
    title: "帖子标题",
    category: "内容分类",
    content: "经验内容"
  };
  return labels[field] || field;
};

// 提交发布
const handleSubmit = () => {
  console.log('开始提交');
  formRef.value.validate((errors) => {
    if (errors) {
      // 显示所有验证错误
      Object.keys(errors).forEach(field => {
        console.log(`字段 ${field} 验证失败:`, errors[field][0].message);
        message.error(`${getFieldLabel(field)}: ${errors[field][0].message}`);
      });
      return;
    }

    // 验证通过，执行提交逻辑
    submitForm();
  });
};

// 实际提交表单的函数
const submitForm = async () => {
  try {
    const res = await axios.post('/posts/', {
      title: formData.title,
      category: formData.category,
      tags: formData.tags.join(','), // 数组转逗号分隔字符串
      content: quillRef.value.getHTML(),
      attachmentIds: formData.attachments
    });

    message.success('发布成功！');
    router.push(`/community/post/${res.data.postId}`);
  } catch (error) {
    console.log('后端错误详情:', error.response.data); // 重点查看这里
    message.error('发布失败：' + (error.response?.data?.message || error.message));
    console.log('发布错误详情:', error);
  }
};
</script>

<style scoped>
.create-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
}

.main-content {
  padding: 24px;
  max-width: 1000px;
  margin: 0 auto;
}

.create-card {
  padding: 32px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.create-card :deep(.n-card__header) {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  font-size: 18px;
  font-weight: 600;
  padding: 20px 24px;
  border-radius: 16px 16px 0 0;
}

.title-input {
  border-radius: 12px;
}

.title-input :deep(.n-input__border) {
  border: 2px solid #e8e8e8;
  transition: all 0.3s ease;
}

.title-input:focus-within :deep(.n-input__border) {
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.form-row {
  display: flex;
  gap: 24px;
  margin-bottom: 8px;
}

.form-item-inline {
  flex: 1;
}

.form-item-inline :deep(.n-form-item-label) {
  min-width: 80px;
}

.editor-container {
  height: 500px;
  border: 2px solid #e8e8e8;
  border-radius: 12px;
  overflow: hidden;
}

.editor-container :deep(.ql-toolbar) {
  border: 2px solid #e8e8e8;
  border-bottom: none;
  border-radius: 12px 12px 0 0;
  background: #fafafa;
  padding: 12px;
}

.editor-container :deep(.ql-editor) {
  font-size: 16px;
  line-height: 1.8;
  padding: 20px;
}

.editor-container :deep(.ql-editor.ql-blank::before) {
  color: #999;
  font-style: italic;
}

.tips {
  color: #666;
  background: rgba(16, 185, 129, 0.05);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 8px;
  padding: 8px 12px;
  display: inline-block;
  margin-top: 4px;
}

@media screen and (max-width: 768px) {
  .main-content {
    padding: 16px;
  }

  .create-card {
    padding: 20px;
  }

  .form-row {
    flex-direction: column;
    gap: 16px;
  }

  .form-item-inline {
    width: 100%;
  }

  .editor-container {
    height: 400px;
  }
}
</style>