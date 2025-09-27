<template>
  <div class="register-page">
    <n-card class="register-card" title="用户注册">
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

        <!-- 邮箱 -->
        <n-form-item path="email" label="邮箱">
          <n-input 
            v-model:value="formData.email" 
            placeholder="请输入邮箱"
            :prefix="Mail"
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

        <!-- 确认密码 -->
        <n-form-item path="confirmPassword" label="确认密码">
          <n-input 
            v-model:value="formData.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
            :prefix="LockClosed"
            show-password-on="mousedown"
          />
        </n-form-item>

        <!-- 操作按钮 -->
        <n-form-item>
          <n-button 
            type="primary" 
            block 
            @click="handleRegister"
            :loading="loading"
          >
            <template v-if="!loading">注册</template>
            <template v-else>
              <n-spin size="small" />
              注册中...
            </template>
          </n-button>
        </n-form-item>
      </n-form>

      <div style="text-align: center; margin-top: 16px;">
        <n-text>已有账号？</n-text>
        <n-button 
          text 
          type="primary" 
          @click="goToLogin"
          style="padding: 0 8px;"
        >
          立即登录
        </n-button>
      </div>
    </n-card>
  </div>



  
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NForm, NFormItem, NInput, NButton, NCard, NSpin, NText } from 'naive-ui'
// 修正图标导入，将User改为Person
import { Person, LockClosed, Mail } from '@vicons/ionicons5'
import axios from 'axios'

// 其余代码保持不变...
const formData = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const formRef = ref(null)
const loading = ref(false)
const router = useRouter()

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3-20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { 
      validator(rule, value) {
        if (value !== formData.value.password) {
          return new Error('两次输入的密码不一致')
        }
        return true
      },
      trigger: 'blur'
    }
  ]
}

const handleRegister = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    // 与settings.py中的配置对应，使用正确的API地址
    const response = await axios.post('http://localhost:8000/api/register/', {
      username: formData.value.username,
      email: formData.value.email,
      password: formData.value.password,
      password_confirm: formData.value.confirmPassword 
    })
    
    if (response.status === 201) {
      router.push('/login')
    }
  } catch (error) {
    console.error('注册失败:', error)
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}


</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background-color: #f5f7fa;
}

.register-card {
  width: 100%;
  max-width: 400px;
}

.n-form-item {
  margin-bottom: 16px;
}
</style>