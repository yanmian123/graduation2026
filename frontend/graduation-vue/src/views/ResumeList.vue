<template>
  <div class="resume-list-container">
    <div class="header">
      <h2>我的简历</h2>
      <button class="new-btn" @click="$router.push('/resumes/create')">
        + 新建简历
      </button>
    </div>

    <!-- 卡片列表 -->
    <div class="card-list">
      <div class="resume-card" v-for="resume in resumeList" :key="resume.id">
        <div class="card-header">
          <h3>{{ resume.name }} - {{ resume.job_objective }}</h3>
          <span class="education">{{ resume.education }}</span>
        </div>
        <div class="card-body">
          <p><strong>邮箱：</strong>{{ resume.email }}</p>
          <p><strong>电话：</strong>{{ resume.phone }}</p>
          <p><strong>更新时间：</strong>{{ resume.updated_at }}</p>
        </div>
        <div class="card-actions">
          <button @click="handleEdit(resume.id)" class="edit-btn">编辑</button>
          <button @click="handleDelete(resume.id)" class="delete-btn">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 逻辑与方案一完全相同，省略（复用 fetchResumes、handleEdit 等方法）
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getResumeList, deleteResume } from '@/api/resume';
import { useMessage } from 'naive-ui';
const resumeList = ref([]);
const router = useRouter();
const message = useMessage();


// 分页配置
const pagination = {
  pageSize: 5,
  showSizePicker: true,
  pageSizes: [5, 10, 20]
};

// 获取简历列表
const fetchResumes = async () => {
  try {
    const response = await getResumeList();
    console.log('获取到的简历数据：', response.data); // 查看控制台输出
    resumeList.value = response.data;
    
    console.log('获取到的简历个数：',  resumeList.value.length ); 
  } catch (error) {
    message.error('获取简历列表失败');
    console.error(error);
  }
};

// 编辑简历
const handleEdit = (id) => {
  router.push(`/resumes/${id}/edit`);
};

// 删除简历
const handleDelete = async (id) => {
  if (window.confirm('确定要删除这份简历吗？此操作不可恢复')) {
    try {
      await deleteResume(id);
      message.success('简历删除成功');
      fetchResumes(); // 重新获取列表
    } catch (error) {
      message.error('删除失败，请重试');
      console.error(error);
    }
  }
};

// 页面加载时获取数据
onMounted(fetchResumes);
</script>

<style scoped>
.resume-list-container {
  padding: 24px;
}

.header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.new-btn {
  padding: 8px 16px;
  background: #2d8cf0;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.card-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.resume-card {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #e8e8e8;
}

.education {
  background: #f5f5f5;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 14px;
}

.card-body p {
  margin: 8px 0;
  font-size: 14px;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 16px;
  padding-top: 8px;
  border-top: 1px dashed #e8e8e8;
}

.edit-btn, .delete-btn {
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.edit-btn {
  color: #2d8cf0;
  border: 1px solid #2d8cf0;
  background: transparent;
}

.delete-btn {
  color: #f53f3f;
  border: 1px solid #f53f3f;
  background: transparent;
}
</style>