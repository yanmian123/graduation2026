<template>
  <div class="user-info-container">
    <h2>个人信息</h2>
    <form @submit.prevent="handleSave">
      <!-- 头像上传 -->
      <div class="form-item avatar-upload">
        <label>头像：</label>
        <div class="avatar-container">
          <n-space vertical>
            <n-image 
              :src="previewAvatarUrl" 
              class="preview-avatar" 
              v-if="previewAvatarUrl"
            />
            <n-avatar size="large" v-else class="preview-avatar">
              <template #fallback>
                <n-icon><Person /></n-icon>
              </template>
            </n-avatar>
            <n-upload
              :default-file-list="avatarFileList"
              @change="handleAvatarChange"
              :max="1"
              type="select"
            >
              <n-button type="primary" size="small">上传头像</n-button>
            </n-upload>
          </n-space>
          <div class="avatar-hint">支持 JPG、PNG 格式，大小不超过 2MB</div>
        </div>
      </div>

      <!-- 昵称 -->
      <div class="form-item">
        <label>昵称：</label>
        <n-input 
          type="text" 
          v-model:value="form.nickname" 
          placeholder="请输入昵称"
          style="width: 300px;"
        />
      </div>

      <!-- 性别 -->
      <div class="form-item">
        <label>性别：</label>
        <n-select 
        v-model:value="form.sex" 
        style="width: 300px;"
        :options="[
            { label: '男', value: 'M' },
            { label: '女', value: 'F' }
        ]"
        />
      </div>

      <!-- 年龄 -->
      <div class="form-item">
        <label>年龄：</label>
        <n-input-number 
          v-model:value="form.age" 
          placeholder="请输入年龄"
          :min="16" 
          :max="60"
          style="width: 300px;"
        />
      </div>

      <!-- 毕业院校 -->
      <div class="form-item">
        <label>毕业院校：</label>
        <n-input 
          type="text" 
          v-model:value="form.graduation_school" 
          placeholder="请输入毕业院校"
          style="width: 300px;"
        />
      </div>

      <!-- 学历 -->
        <div class="form-item">
        <label>学历：</label>
        <n-select 
            v-model:value="form.education_level" 
            style="width: 300px;"
            :options="[
            { label: '博士', value: '博士' },
            { label: '硕士', value: '硕士' },
            { label: '本科', value: '本科' },
            { label: '专科', value: '专科' },
            { label: '高中', value: '高中' },
            { label: '中专/中技', value: '中专/中技' },
            { label: '初中及以下', value: '初中及以下' }
            ]"
        />
        </div>

      <!-- 专业 -->
      <div class="form-item">
        <label>专业：</label>
        <n-input 
          type="text" 
          v-model:value="form.major" 
          placeholder="请输入专业"
          style="width: 300px;"
        />
      </div>

      <!-- 毕业年份 -->
      <div class="form-item">
        <label>毕业年份：</label>
        <n-input-number 
          v-model:value="form.graduation_year" 
          placeholder="毕业年份"
          :min="1950" 
          :max="2100"
          style="width: 300px;"
        />
      </div>

      <!-- 手机号 -->
      <div class="form-item">
        <label>手机号：</label>
        <n-input 
          type="text" 
          v-model:value="form.phone_number" 
          placeholder="请输入手机号"
          pattern="^\+?1?\d{9,15}$"
          style="width: 300px;"
        />
      </div>

        <!-- 目前状态 -->
        <div class="form-item">
        <label>目前状态：</label>
        <n-select 
            v-model:value="form.current_status" 
            style="width: 300px;"
            :options="[
            { label: '应届毕业生', value: '应届毕业生' },
            { label: '在找工作', value: '在找工作' },
            { label: '在职', value: '在职' },
            { label: '离职', value: '离职' },
            { label: '实习', value: '实习' },
            { label: '在校', value: '在校' },
            { label: '其他', value: '其他' }
            ]"
        />
        </div>

      <!-- 意向职位 -->
      <div class="form-item">
        <label>意向职位：</label>
        <n-input 
          type="text" 
          v-model:value="form.intended_position" 
          placeholder="请输入意向职位"
          style="width: 300px;"
        />
      </div>

      <!-- 期望薪资 -->
      <div class="form-item">
        <label>意向年薪：</label>
        <n-input-number 
          v-model:value="form.intended_salary" 
          placeholder="请输入意向年薪"
          :min="0"
          style="width: 300px;"
        />
      </div>

      <!-- 住址 -->
      <div class="form-item">
        <label>住址：</label>
        <n-input 
          type="text" 
          v-model:value="form.address" 
          placeholder="请输入住址"
          style="width: 300px;"
        />   
      </div>

      <!-- 意向城市 -->
      <div class="form-item">
        <label>意向城市：</label>
        <n-input 
          type="text" 
          v-model:value="form.intended_city" 
          placeholder="请输入意向城市"
          style="width: 300px;"
        /> 
      </div>

      <!-- 个人简介 -->
      <div class="form-item">
        <label>个人简介：</label>
        <n-input
          type="textarea" 
          v-model:value="form.personal_profile" 
          placeholder="请输入个人简介"
          :rows="4"
          :cols="50"
          style="width: 300px;"
        />    
      </div>

      <n-button type="submit" @click="handleSave">保存修改</n-button>
            <n-button type="primary" @click="$router.push('/resumes/create')">
        + 新建简历
      </n-button>
              
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getUserInfo, updateUserInfo, uploadUserAvatar } from '@/api/user';
import { NInput, NSelect, NInputNumber, NButton, NAvatar, NIcon, NUpload, NSpace, useMessage, NImage } from 'naive-ui';
import { Person } from '@vicons/ionicons5';
// Naive UI 消息提示
const message = useMessage();
// 路由实例
const router = useRouter();

// 表单数据
const form = ref({
  nickname: '',
  sex: '',
  age: null,
  major: '',
  phone_number: '',
  graduation_school: '',
  education_level: '',
  graduation_year: null,
  current_status: '',
  intended_position: '',
  intended_salary: null,
  address: '',
  intended_city: '',
  personal_profile: '',
  avatar: '',
});

// 头像上传相关
const avatarFileList = ref([]);
// 头像预览URL
const previewAvatarUrl = ref('');

// 处理头像文件变化
const handleAvatarChange = (data) => {
  console.log('handleAvatarChange called with:', data);
  avatarFileList.value = data.fileList;
  
  // 如果有文件，创建本地预览
  if (avatarFileList.value.length > 0 && avatarFileList.value[0].file) {
    const file = avatarFileList.value[0].file;
    const reader = new FileReader();
    reader.onload = (e) => {
      previewAvatarUrl.value = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

// 校验头像文件
const validateAvatarFile = (file) => {
  const isJPG = file.type === 'image/jpeg' || file.type === 'image/png';
  const isLt2M = file.size / 1024 / 1024 < 2;
  
  if (!isJPG) {
    message.error('只能上传 JPG/PNG 格式的图片');
    return false;
  }
  if (!isLt2M) {
    message.error('图片大小不能超过 2MB');
    return false;
  }
  
  return true;
};

// 页面加载时获取用户信息
onMounted(async () => {
  try {
    const response = await getUserInfo();
    const userData = response.data;
    
    // 类型转换：确保数字字段为Number类型
    if (userData.age) userData.age = Number(userData.age);
    if (userData.graduation_year) userData.graduation_year = Number(userData.graduation_year);
    if (userData.intended_salary) userData.intended_salary = Number(userData.intended_salary);
    
    form.value = userData;  // 回显用户信息到表单
    
    // 处理头像URL，确保是完整URL
    let avatarUrl = form.value.avatar || '';
    if (avatarUrl && !avatarUrl.startsWith('http')) {
      avatarUrl = `http://localhost:8000${avatarUrl}`;
      console.log('初始化时处理的完整URL:', avatarUrl);
    }
    
    // 初始化头像预览URL
    previewAvatarUrl.value = avatarUrl;
    
    // 更新表单中的头像URL
    form.value.avatar = avatarUrl;
    
    // 初始化头像文件列表（与EnterpriseEdit.vue保持一致）
    if (avatarUrl) {
      avatarFileList.value = [{
        id: 'avatar',
        name: 'avatar.png',
        url: avatarUrl
      }];
    }
    
    // 更新本地存储的用户信息
    const userInfo = {
      id: form.value.id,
      username: form.value.username,
      avatar: avatarUrl
    };
    localStorage.setItem('userInfo', JSON.stringify(userInfo));
  } catch (error) {
    message.error('获取用户信息失败，请重试');
    console.error(error);
  }
});


const handleSave = async () => {
  console.log('保存按钮被点击，开始执行保存逻辑'); // 确认事件触发
  try {
    // 1. 先保存基本信息（排除头像）
    const submitData = { ...form.value }
    // 移除头像字段，单独处理
    delete submitData.avatar
    // 移除后端不接受的字段
    delete submitData.id
    delete submitData.username

    console.log('提交的基本信息:', submitData); // 打印提交数据
    
    // 调用API保存基本信息
    await updateUserInfo(submitData)
    
    // 2. 如果有头像文件，上传头像
    if (avatarFileList.value.length > 0 && avatarFileList.value[0].file) {
      console.log('检测到头像文件，开始上传...');
      
      // 校验头像文件
      if (!validateAvatarFile(avatarFileList.value[0].file)) {
        return;
      }
      
      const uploadFormData = new FormData();
      uploadFormData.append('avatar', avatarFileList.value[0].file);
      
      const avatarResponse = await uploadUserAvatar(uploadFormData);
      console.log('头像上传成功，原始URL:', avatarResponse.data.avatar);
      
      // 处理URL，确保是完整URL
      let avatarUrl = avatarResponse.data.avatar;
      if (avatarUrl && !avatarUrl.startsWith('http')) {
        // 如果是相对路径，添加完整前缀
        avatarUrl = `http://localhost:8000${avatarUrl}`;
        console.log('处理后的完整URL:', avatarUrl);
      }
      
      // 更新表单数据和预览URL
      form.value.avatar = avatarUrl;
      previewAvatarUrl.value = avatarUrl;
      
      // 更新文件列表（与EnterpriseEdit.vue完全一致）
      avatarFileList.value = [{
        id: 'avatar',
        name: 'avatar.png',
        url: avatarUrl
      }];
      
      // 更新本地存储的用户信息（与Header.vue保持一致）
      const userInfo = {
        id: form.value.id,
        username: form.value.username,
        avatar: avatarUrl
      };
      localStorage.setItem('userInfo', JSON.stringify(userInfo));
    }
    
    message.success('信息更新成功');
    
    // 保存成功后跳转到首页
    router.push('/home');
  } catch (error) {
    message.error('更新失败，请检查输入');
    console.error('保存失败原因:', error);
    console.error('错误响应:', error.response);
  }
};
</script>

<style scoped>
.form-item {
  margin: 15px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

label {
  width: 100px;
  text-align: right;
}

.n-button {
  margin-top: 20px;
  margin-left: 110px;
}

/* 头像上传样式 */
.avatar-upload {
  align-items: flex-start;
  padding-top: 10px;
}

.avatar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.preview-avatar {
  width: 120px;
  height: 120px;
}

.avatar-hint {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.avatar-uploader {
  display: flex;
  flex-direction: column;
  align-items: center;
}
</style>