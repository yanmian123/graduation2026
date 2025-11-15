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

      <!-- 提交按钮 -->
      <n-form-item>
        <n-button type="primary" @click="handleSubmit">保存修改</n-button>
        <n-button @click="$router.push('/resumes')" style="margin-left: 16px;">取消</n-button>

      </n-form-item>
    </n-form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useMessage } from 'naive-ui';
import { getResumeDetail, updateResume } from '@/api/resume';

// 路由相关
const router = useRouter();
const route = useRoute();
const resumeId = route.params.id; // 获取当前简历ID

// 表单数据（与创建页保持一致）
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
  status: 'draft'
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

// 表单验证规则（与创建页一致）
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
    form.value = response.data; // 填充表单数据
  } catch (error) {
    message.error('获取简历详情失败');
    console.error(error);
  }
};

// 提交修改
const handleSubmit = async () => {
  if (!formRef.value) return;
  try {
    await formRef.value.validate();
    await updateResume(resumeId, form.value);
    message.success('简历更新成功！');
    router.push('/resumes'); // 跳回列表页
  } catch (error) {
    const errorMsg = error.response?.data?.message || '更新失败，请检查输入';
    message.error(errorMsg);
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
</style>