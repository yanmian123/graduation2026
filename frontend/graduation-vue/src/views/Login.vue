<template>
  <div class="login-page">
    <n-card class="login-card" title="用户登录">
      <n-form 
        ref="formRef" 
        :model="formData" 
        :rules="rules"
        label-placement="top"
      >
        <!-- 用户名 -->
        <n-form-item path="username" label="用户名">
          <n-input 
            v-model:value="formData.username" 
            placeholder="请输入用户名"
            :prefix="Person" 
          />
        </n-form-item>

        <!-- 密码 -->
        <n-form-item path="password" label="密码">
          <n-input 
            v-model:value="formData.password" 
            type="password" 
            placeholder="请输入密码"
            :prefix="LockClosed"
            show-password-on="mousedown"
          />
        </n-form-item>

        <!-- 操作按钮 -->
        <n-form-item>
          <n-button 
            type="primary" 
            block 
            @click="handleLogin"
            :loading="loading"
          >
            <template v-if="!loading">登录</template>
            <template v-else>
              <n-spin size="small" />
              登录中...
            </template>
          </n-button>
        </n-form-item>
      </n-form>

      <div style="text-align: center; margin-top: 16px;">
        <n-text>还没有账号？</n-text>
        <n-button 
          text 
          type="primary" 
          @click="goToRegister"
          style="padding: 0 8px;"
        >
          立即注册
        </n-button>
      </div>
    </n-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NForm, NFormItem, NInput, NButton, NCard, NSpin, NText } from 'naive-ui'
import { Person, LockClosed } from '@vicons/ionicons5'
// import axios from 'axios'
import axios from '@/utils/axios'

const formData = ref({
  username: '',
  password: ''
})

const formRef = ref(null)
const loading = ref(false)
const router = useRouter()

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

// 处理登录逻辑
const handleLogin = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    // 调用后端登录接口
    const response = await axios.post('/login/', {// 不需要完整URL，使用相对路径>>>为什么
      username: formData.value.username,
      password: formData.value.password
    })
    
    // 登录成功：保存令牌到本地存储
    const { access, refresh } = response.data
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
    
    // 跳转到首页（根据你的需求修改路径）
    // router.push('/api/user/info')
    router.push('/home')
  } catch (error) {
    console.error('登录失败:', error.response?.data || error.message)
    // 显示错误提示（可根据需求添加UI提示）
  } finally {
    loading.value = false
  }
}

// 跳转到注册页面
const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background-color: #f5f7fa;
}

.login-card {
  width: 100%;
  max-width: 400px;
}

.n-form-item {
  margin-bottom: 16px;
}
</style>