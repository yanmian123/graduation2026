<template>
  <n-layout class="create-layout">
    <!-- 顶部导航（复用平台导航） -->
    <n-layout-header bordered class="header">
      <!-- 导航内容同首页，省略 -->
    </n-layout-header>

    <n-layout-content class="main-content">
      <!-- 草稿箱 -->
      <n-card v-if="showDraftBox" title="草稿箱" bordered class="create-card">
        <n-empty v-if="drafts.length === 0" description="暂无草稿" />
        <div v-else class="draft-list">
          <n-card v-for="draft in drafts" :key="draft.id" class="draft-card" hoverable>
            <h3>{{ draft.title }}</h3>
            <p class="draft-content">{{ stripHtmlTags(draft.content) }}</p>
            <div class="draft-meta">
              <span>保存时间: {{ draft.updated_at }}</span>
            </div>
            <div class="draft-actions">
              <n-button size="small" type="primary" @click="editDraft(draft)">
                编辑
              </n-button>
              <n-button size="small" type="success" @click="publishDraft(draft)">
                重新发布
              </n-button>
              <n-button size="small" type="error" @click="deleteDraft(draft.id)">
                删除
              </n-button>
            </div>
          </n-card>
        </div>
        <div class="draft-box-actions">
          <n-button @click="showDraftBox = false; resetForm()">新建文章</n-button>
        </div>
      </n-card>

      <!-- 编辑/发布表单 -->
      <n-card v-else :title="isEditMode ? '编辑文章' : '发布经验分享'" bordered class="create-card">
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

          <!-- 操作按钮 -->
          <n-form-item :show-label="false">
            <n-space size="large">
              <n-button size="large" @click="handlePreview">
                <template #icon>
                  <n-icon><Eye /></n-icon>
                </template>
                预览
              </n-button>
              <n-button type="default" size="large" @click="handleSaveDraft">
                <template #icon>
                  <n-icon><Save /></n-icon>
                </template>
                保存草稿
              </n-button>
              <n-button type="primary" size="large" @click="handleSubmit">
                <template #icon>
                  <n-icon><Send /></n-icon>
                </template>
                {{ isEditMode ? '更新' : '发布' }}
              </n-button>
              <n-button size="large" @click="showDraftBox = true; loadDrafts()">
                查看草稿箱
              </n-button>
              <n-button size="large" @click="goBack">
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
import { ref, reactive, onMounted } from 'vue';
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
  NButton,
  NText,
  NDynamicInput,
  NSpace,
  NIcon,
  NEmpty
} from 'naive-ui';
import { Eye, Send, Save } from '@vicons/ionicons5';
// 接口请求
import axios from '@/utils/axios';
import { useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();
const message = useMessage();
const formRef = ref(null);

// 编辑模式和草稿箱
const isEditMode = ref(false);
const showDraftBox = ref(false);
const editingArticleId = ref(null);
const drafts = ref([]);

// 表单数据
const formData = reactive({
  title: '',
  category: '',
  tags: [],
  content: ''  // 富文本内容（HTML格式）
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
    ],
    clipboard: {
      matchVisual: false
    }
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

// 内容变化监听
const handleContentChange = () => {
  // 自动调整图片大小，防止溢出
  if (quillRef.value && quillRef.value.root) {
    const editor = quillRef.value.root;
    const images = editor.querySelectorAll('img');
    
    images.forEach(img => {
      // 如果图片没有设置样式，则添加样式
      if (!img.style.maxWidth) {
        img.style.maxWidth = '100%';
        img.style.height = 'auto';
        img.style.display = 'block';
        img.style.margin = '10px auto';
      }
    });
  }
  
  // 可调用接口保存草稿
};

// 保存草稿
const handleSaveDraft = async () => {
  // 检查是否有内容
  if (!formData.title && !formData.content) {
    message.warning('请先输入标题或内容');
    return;
  }

  try {
    // 获取富文本编辑器的HTML内容
    let contentHTML = '';
    if (quillRef.value) {
      // 尝试多种方式获取内容
      if (quillRef.value.getHTML) {
        contentHTML = quillRef.value.getHTML();
      } else if (quillRef.value.root) {
        contentHTML = quillRef.value.root.innerHTML;
      }
    }

    const draftData = {
      title: formData.title,
      category: formData.category,
      tags: formData.tags,
      content: contentHTML,
      isDraft: true
    };

    console.log('保存草稿数据:', draftData);

    // 保存到localStorage
    localStorage.setItem('community_draft', JSON.stringify(draftData));
    
    message.success('草稿已保存');
  } catch (error) {
    console.error('保存草稿失败:', error);
    message.error('保存草稿失败');
  }
};

// 加载草稿
const loadDraft = () => {
  try {
    const draftData = localStorage.getItem('community_draft');
    if (draftData) {
      const draft = JSON.parse(draftData);
      console.log('加载草稿数据:', draft);
      
      formData.title = draft.title || '';
      formData.category = draft.category || '';
      formData.tags = draft.tags || [];
      
      // 延迟加载富文本内容，确保编辑器已初始化
      setTimeout(() => {
        if (quillRef.value && draft.content) {
          console.log('设置富文本内容:', draft.content);
          // 尝试多种方式设置内容
          if (quillRef.value.setHTML) {
            quillRef.value.setHTML(draft.content);
          } else if (quillRef.value.root) {
            quillRef.value.root.innerHTML = draft.content;
          }
          // 在编辑器内容设置后再更新formData.content
          if (quillRef.value.getHTML) {
            formData.content = quillRef.value.getHTML();
          } else if (quillRef.value.root) {
            formData.content = quillRef.value.root.innerHTML;
          }
        }
      }, 500);
      
      message.info('已加载上次保存的草稿');
    }
  } catch (error) {
    console.error('加载草稿失败:', error);
  }
};

// 清除草稿
const clearDraft = () => {
  localStorage.removeItem('community_draft');
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
const handleSubmit = async () => {
  console.log('开始提交');
  
  // 先刷新用户认证状态，确保获取最新状态
  try {
    const userInfoResponse = await axios.get('/user/info/')
    const userInfo = userInfoResponse.data
    localStorage.setItem('userInfo', JSON.stringify(userInfo))
    sessionStorage.setItem('userInfo', JSON.stringify(userInfo))
  } catch (error) {
    console.error('刷新用户信息失败:', error)
  }
  
  // 检查用户实名认证状态
  const userInfo = JSON.parse(localStorage.getItem('userInfo'))
  if (!userInfo || !userInfo.is_verified) {
    message.warning('请先完成个人实名认证后再发布文章')
    router.push('/user/verification')
    return
  }
  
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
    // 获取HTML内容并处理图片
    let htmlContent = quillRef.value.getHTML();
    
    // 创建临时DOM来处理图片
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = htmlContent;
    
    // 处理所有图片，添加样式防止溢出
    const images = tempDiv.querySelectorAll('img');
    images.forEach(img => {
      img.style.maxWidth = '100%';
      img.style.height = 'auto';
      img.style.display = 'block';
      img.style.margin = '10px auto';
    });
    
    // 使用处理后的HTML
    htmlContent = tempDiv.innerHTML;
    
    // 检查敏感词
    const contentToCheck = [formData.title, formData.content].filter(Boolean).join(' ')
    if (contentToCheck.trim()) {
      try {
        const checkResponse = await axios.get('/user/sensitive_words/check_content/', {
          params: { content: contentToCheck }
        })
        
        if (checkResponse.data.has_sensitive) {
          message.error(`内容包含敏感词：${checkResponse.data.sensitive_words.join('、')}，请修改后重新发布`)
          return
        }
      } catch (error) {
        console.error('敏感词检测失败:', error)
      }
    }
    
    let res;
    if (isEditMode.value && editingArticleId.value) {
      // 更新文章
      res = await axios.patch(`/posts/${editingArticleId.value}/`, {
        title: formData.title,
        category: formData.category,
        tags: formData.tags.join(','),
        content: htmlContent
      });
      message.success('更新成功！');
      
      // 编辑模式下返回到用户信息页面
      router.push('/userinfo');
    } else {
      // 创建新文章
      res = await axios.post('/posts/', {
        title: formData.title,
        category: formData.category,
        tags: formData.tags.join(','),
        content: htmlContent
      });
      message.success('发布成功！');
      
      // 清除草稿
      clearDraft();
      
      // 跳转到文章详情页
      const postId = res.data.data?.postId || res.data.postId || res.data.id;
      if (postId) {
        router.push(`/community/post/${postId}`);
      } else {
        message.error('获取文章ID失败');
        console.error('响应数据结构:', res.data);
      }
    }
  } catch (error) {
    console.log('后端错误详情:', error.response?.data);
    message.error((isEditMode.value ? '更新' : '发布') + '失败：' + (error.response?.data?.message || error.message));
    console.log('操作错误详情:', error);
  }
};

// 加载草稿列表
const loadDrafts = async () => {
  try {
    const res = await axios.get('/posts/', {
      params: { is_draft: true }
    });
    drafts.value = res.data.map(draft => ({
      id: draft.id,
      title: draft.title,
      content: draft.content,
      updated_at: draft.updated_at
    }));
  } catch (error) {
    console.error('加载草稿失败:', error);
    message.error('加载草稿失败');
  }
};

// 编辑草稿
const editDraft = (draft) => {
  showDraftBox.value = false;
  isEditMode.value = true;
  editingArticleId.value = draft.id;
  
  formData.title = draft.title;
  
  // 延迟设置编辑器内容，确保编辑器已初始化
  setTimeout(() => {
    if (quillRef.value && draft.content) {
      if (quillRef.value.setHTML) {
        quillRef.value.setHTML(draft.content);
      } else if (quillRef.value.root) {
        quillRef.value.root.innerHTML = draft.content;
      }
      // 在编辑器内容设置后再更新formData.content
      if (quillRef.value.getHTML) {
        formData.content = quillRef.value.getHTML();
      } else if (quillRef.value.root) {
        formData.content = quillRef.value.root.innerHTML;
      }
    }
  }, 500);
};

// 发布草稿
const publishDraft = async (draft) => {
  try {
    await axios.patch(`/posts/${draft.id}/`, { is_draft: false });
    message.success('发布成功！');
    loadDrafts();
  } catch (error) {
    console.error('发布草稿失败:', error);
    message.error('发布失败：' + (error.response?.data?.message || error.message));
  }
};

// 删除草稿
const deleteDraft = async (draftId) => {
  try {
    await axios.delete(`/posts/${draftId}/`);
    message.success('删除成功');
    loadDrafts();
  } catch (error) {
    console.error('删除草稿失败:', error);
    message.error('删除失败：' + (error.response?.data?.message || error.message));
  }
};

// 重置表单
const resetForm = () => {
  formData.title = '';
  formData.category = '';
  formData.tags = [];
  formData.content = '';
  isEditMode.value = false;
  editingArticleId.value = null;
};

// 返回
const goBack = () => {
  if (isEditMode.value) {
    router.push('/user-info');
  } else {
    router.push('/community');
  }
};

// 去除HTML标签
const stripHtmlTags = (html) => {
  if (!html) return '';
  const div = document.createElement('div');
  div.innerHTML = html;
  return div.textContent || div.innerText || '';
};

// 页面加载时
onMounted(async () => {
  // 刷新用户信息以获取最新的认证状态
  try {
    const userInfoResponse = await axios.get('/user/info/')
    const userInfo = userInfoResponse.data
    localStorage.setItem('userInfo', JSON.stringify(userInfo))
    sessionStorage.setItem('userInfo', JSON.stringify(userInfo))
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
  
  // 检查是否是编辑模式
  const articleId = route.query.articleId;
  if (articleId) {
    isEditMode.value = true;
    editingArticleId.value = articleId;
    loadArticle(articleId);
  } else {
    // 加载本地草稿
    loadDraft();
  }
});

// 加载文章（编辑模式）
const loadArticle = async (articleId) => {
  try {
    const res = await axios.get(`/posts/${articleId}/`);
    const article = res.data;
    
    formData.title = article.title;
    formData.category = article.category;
    formData.tags = article.tags ? article.tags.split(',') : [];
    
    // 延迟设置编辑器内容，确保编辑器已初始化
    setTimeout(() => {
      if (quillRef.value && article.content) {
        if (quillRef.value.setHTML) {
          quillRef.value.setHTML(article.content);
        } else if (quillRef.value.root) {
          quillRef.value.root.innerHTML = article.content;
        }
        // 在编辑器内容设置后再更新formData.content
        if (quillRef.value.getHTML) {
          formData.content = quillRef.value.getHTML();
        } else if (quillRef.value.root) {
          formData.content = quillRef.value.root.innerHTML;
        }
      }
    }, 500);
  } catch (error) {
    console.error('加载文章失败:', error);
    message.error('加载文章失败');
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
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.editor-container :deep(.ql-editor img) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 10px auto;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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

.draft-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.draft-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.draft-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.draft-card h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  line-height: 1.4;
}

.draft-content {
  margin: 0 0 10px 0;
  color: #666;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: 60px;
}

.draft-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
  margin-bottom: 12px;
}

.draft-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #f2f3f5;
}

.draft-actions .n-button {
  flex: 1;
}

.draft-box-actions {
  display: flex;
  justify-content: center;
  margin-top: 20px;
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