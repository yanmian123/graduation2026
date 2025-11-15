<template>
  <div class="user-info-container">
    <h2>个人信息</h2>
    <form @submit.prevent="handleSave">
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
import { getUserInfo, updateUserInfo } from '@/api/user';
import { NInput, NSelect, NInputNumber,NButton, useMessage } from 'naive-ui';
// Naive UI 消息提示
const message = useMessage();

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
});

// 页面加载时获取用户信息
onMounted(async () => {
  try {
    const response = await getUserInfo();
    form.value = response.data;  // 回显用户信息到表单
  } catch (error) {
    message.error('获取用户信息失败，请重试');
    console.error(error);
  }
});


const handleSave = async () => {
  console.log('保存按钮被点击，开始执行保存逻辑'); // 确认事件触发
  try {
    console.log('提交的数据:', form.value); // 打印提交数据
    await updateUserInfo(form.value);
    message.success('信息更新成功');
  } catch (error) {
    message.error('更新失败，请检查输入');
    console.error('保存失败原因:', error);
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
</style>