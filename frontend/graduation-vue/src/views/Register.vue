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

        <!-- 验证码 -->
        <n-form-item path="verificationCode" label="验证码">
          <div class="code-input-wrapper">
            <n-input 
              v-model:value="formData.verificationCode" 
              placeholder="请输入验证码"
              :prefix="Key"
              maxlength="6"
            />
            <n-button 
              type="primary" 
              ghost
              :disabled="codeSent || countdown > 0"
              :loading="sendingCode"
              @click="sendVerificationCode"
              class="send-code-btn"
            >
              {{ countdown > 0 ? `${countdown}秒后重发` : '发送验证码' }}
            </n-button>
          </div>
        </n-form-item>

        <!-- 密码 -->
        <n-form-item path="password" label="密码">
          <n-input 
            v-model:value="formData.password" 
            type="password" 
            placeholder="请输入密码"
            :prefix="LockClosed"
            show-password-on="mousedown"
            autocomplete="new-password"
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
            autocomplete="new-password"
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
import { NForm, NFormItem, NInput, NButton, NCard, NSpin, NText, useMessage } from 'naive-ui'
import { Person, LockClosed, Mail, Key } from '@vicons/ionicons5'
import axios from 'axios'

const formData = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  verificationCode: ''
})

const formRef = ref(null)
const loading = ref(false)
const sendingCode = ref(false)
const codeSent = ref(false)
const countdown = ref(0)
const router = useRouter()
const message = useMessage()

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3-20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  verificationCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位数字', trigger: 'blur' }
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

const sendVerificationCode = async () => {
  if (!formData.value.email) {
    message.warning('请先输入邮箱')
    return
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(formData.value.email)) {
    message.warning('请输入正确的邮箱格式')
    return
  }
  
  try {
    sendingCode.value = true
    const response = await axios.post('http://localhost:8000/api/send-register-code/', {
      email: formData.value.email
    })
    
    if (response.status === 200) {
      message.success(`验证码已发送到 ${formData.value.email}`)
      codeSent.value = true
      
      const code = response.data.code
      message.info(`开发环境验证码：${code}`)
      
      countdown.value = 60
      const timer = setInterval(() => {
        countdown.value--
        if (countdown.value <= 0) {
          clearInterval(timer)
          codeSent.value = false
        }
      }, 1000)
    }
  } catch (error) {
    console.error('发送验证码失败:', error)
    if (error.response?.data?.error) {
      message.error(error.response.data.error)
    } else {
      message.error('发送验证码失败，请稍后重试')
    }
  } finally {
    sendingCode.value = false
  }
}

const handleRegister = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    const response = await axios.post('http://localhost:8000/api/register/', {
      username: formData.value.username,
      email: formData.value.email,
      password: formData.value.password,
      password_confirm: formData.value.confirmPassword,
      verification_code: formData.value.verificationCode
    })
    
    if (response.status === 201) {
      message.success('注册成功！请登录')
      router.push('/login')
    }
  } catch (error) {
    console.error('注册失败:', error)
    if (error.response?.data?.error) {
      message.error(error.response.data.error)
    } else if (error.response?.data) {
      const errors = error.response.data
      const errorMessages = Object.values(errors).flat()
      message.error(errorMessages[0] || '注册失败，请检查输入信息')
    } else {
      message.error('注册失败，请稍后重试')
    }
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

.code-input-wrapper {
  display: flex;
  gap: 8px;
}

.code-input-wrapper .n-input {
  flex: 1;
}

.send-code-btn {
  white-space: nowrap;
  min-width: 100px;
}
</style>