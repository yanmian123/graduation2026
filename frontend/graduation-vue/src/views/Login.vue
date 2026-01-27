<template>
  <div class="login-page">
    <n-card class="login-card">
      <n-tabs 
        class="card-tabs" 
        v-model:value="activeTab"
        size="large" 
        animated 
        pane-wrapper-style="margin: 0 -4px" 
        pane-style="padding-left: 4px; padding-right: 4px; box-sizing: border-box;" 
      >
        <!-- 用户登录 -->
        <n-tab-pane name="user-login" tab="用户登录">
          <n-form 
            ref="userLoginFormRef" 
            :model="userLoginForm" 
            :rules="userLoginRules"
            label-placement="top"
          >
            <n-form-item-row label="用户名">
              <n-input 
                v-model:value="userLoginForm.username" 
                placeholder="请输入用户名"
                autocomplete="username"
              >
                <template #prefix>
                  <n-icon :component="Person" />
                </template>
              </n-input>
            </n-form-item-row>
            <n-form-item-row label="密码">
              <n-input 
                v-model:value="userLoginForm.password" 
                type="password" 
                placeholder="请输入密码"
                show-password-on="mousedown"
                autocomplete="current-password"
              >
                <template #prefix>
                  <n-icon :component="LockClosed" />
                </template>
              </n-input>
            </n-form-item-row>
            <n-button 
              type="primary" 
              block 
              secondary 
              strong
              @click="handleUserLogin"
              :loading="loading"
            >
              <template v-if="!loading">登录</template>
              <template v-else>
                <n-spin size="small" />
                登录中...
              </template>
            </n-button>
            <div class="forgot-password">
              <n-button text type="primary" @click="showForgotPassword = true">
                忘记密码？
              </n-button>
              <span class="divider">|</span>
              <n-button text type="primary" @click="showUserRegister = true">
                注册
              </n-button>
            </div>
          </n-form>
        </n-tab-pane>

        <!-- 企业登录 -->
        <n-tab-pane name="enterprise-login" tab="企业登录">
          <n-form 
            ref="enterpriseLoginFormRef" 
            :model="enterpriseLoginForm" 
            :rules="enterpriseLoginRules"
            label-placement="top"
          >
            <n-form-item-row label="用户名">
              <n-input 
                v-model:value="enterpriseLoginForm.username" 
                placeholder="请输入企业用户名"
                autocomplete="username"
              >
                <template #prefix>
                  <n-icon :component="Person" />
                </template>
              </n-input>
            </n-form-item-row>
            <n-form-item-row label="密码">
              <n-input 
                v-model:value="enterpriseLoginForm.password" 
                type="password" 
                placeholder="请输入密码"
                show-password-on="mousedown"
                autocomplete="current-password"
              >
                <template #prefix>
                  <n-icon :component="LockClosed" />
                </template>
              </n-input>
            </n-form-item-row>
            <n-button 
              type="primary" 
              block 
              secondary 
              strong
              @click="handleEnterpriseLogin"
              :loading="loading"
            >
              <template v-if="!loading">登录</template>
              <template v-else>
                <n-spin size="small" />
                登录中...
              </template>
            </n-button>
            <div class="forgot-password">
              <n-button text type="primary" @click="showForgotPassword = true">
                忘记密码？
              </n-button>
              <span class="divider">|</span>
              <n-button text type="primary" @click="showEnterpriseRegister = true">
                注册
              </n-button>
            </div>
          </n-form>
        </n-tab-pane>
      </n-tabs>
    </n-card>

    <!-- 用户注册弹窗 -->
    <n-modal v-model:show="showUserRegister" preset="card" title="用户注册" style="width: 400px;">
      <n-form 
        ref="userRegisterFormRef" 
        :model="userRegisterForm" 
        :rules="userRegisterRules"
        label-placement="top"
      >
        <n-form-item label="用户名" path="username">
          <n-input 
            v-model:value="userRegisterForm.username" 
            placeholder="请输入用户名"
            autocomplete="username"
          >
            <template #prefix>
              <n-icon :component="Person" />
            </template>
          </n-input>
        </n-form-item>
        <n-form-item label="邮箱" path="email">
          <n-input 
            v-model:value="userRegisterForm.email" 
            placeholder="请输入邮箱"
            autocomplete="email"
          >
            <template #prefix>
              <n-icon :component="Mail" />
            </template>
          </n-input>
        </n-form-item>
        <n-form-item label="密码" path="password">
          <n-input 
            v-model:value="userRegisterForm.password" 
            type="password" 
            placeholder="请输入密码"
            show-password-on="mousedown"
            autocomplete="new-password"
          >
            <template #prefix>
              <n-icon :component="LockClosed" />
            </template>
          </n-input>
        </n-form-item>
        <n-form-item label="确认密码" path="confirmPassword">
          <n-input 
            v-model:value="userRegisterForm.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
            show-password-on="mousedown"
            autocomplete="new-password"
          >
            <template #prefix>
              <n-icon :component="LockClosed" />
            </template>
          </n-input>
        </n-form-item>
        <n-button 
          type="primary" 
          block 
          @click="handleUserRegister"
          :loading="loading"
        >
          <template v-if="!loading">注册</template>
          <template v-else>
            <n-spin size="small" />
            注册中...
          </template>
        </n-button>
      </n-form>
    </n-modal>

    <!-- 企业注册弹窗 -->
    <n-modal v-model:show="showEnterpriseRegister" preset="card" title="企业注册" style="width: 450px;">
      <n-form 
        ref="enterpriseRegisterFormRef" 
        :model="enterpriseRegisterForm" 
        :rules="enterpriseRegisterRules"
        label-placement="top"
      >
        <n-form-item label="用户名" path="username">
          <n-input 
            v-model:value="enterpriseRegisterForm.username" 
            placeholder="请输入用户名"
            autocomplete="username"
          >
            <template #prefix>
              <n-icon :component="Person" />
            </template>
          </n-input>
        </n-form-item>
        <n-form-item label="邮箱" path="contact_email">
          <n-input 
            v-model:value="enterpriseRegisterForm.contact_email" 
            placeholder="请输入邮箱"
            autocomplete="email"
          >
            <template #prefix>
              <n-icon :component="Mail" />
            </template>
          </n-input>
        </n-form-item>
        <n-form-item label="密码" path="password">
          <n-input 
            v-model:value="enterpriseRegisterForm.password" 
            type="password" 
            placeholder="请输入密码"
            show-password-on="mousedown"
            autocomplete="new-password"
          >
            <template #prefix>
              <n-icon :component="LockClosed" />
            </template>
          </n-input>
        </n-form-item>
        <n-form-item label="确认密码" path="confirmPassword">
          <n-input 
            v-model:value="enterpriseRegisterForm.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
            show-password-on="mousedown"
            autocomplete="new-password"
          >
            <template #prefix>
              <n-icon :component="LockClosed" />
            </template>
          </n-input>
        </n-form-item>
        <n-form-item label="企业名称" path="enterpriseName">
          <n-input 
            v-model:value="enterpriseRegisterForm.enterpriseName" 
            placeholder="请输入企业名称"
          />
        </n-form-item>
        <n-form-item label="企业地址" path="address">
          <n-input 
            v-model:value="enterpriseRegisterForm.address" 
            placeholder="请输入企业地址"
          />
        </n-form-item>
        <n-form-item label="企业简介" path="description">
          <n-input 
            v-model:value="enterpriseRegisterForm.description" 
            type="textarea"
            placeholder="请输入企业简介"
          />
        </n-form-item>
        <n-form-item label="联系人" path="contactPerson">
          <n-input 
            v-model:value="enterpriseRegisterForm.contactPerson" 
            placeholder="请输入联系人姓名"
          />
        </n-form-item>
        <n-form-item label="联系电话" path="contactPhone">
          <n-input 
            v-model:value="enterpriseRegisterForm.contactPhone" 
            placeholder="请输入联系电话"
          />
        </n-form-item>
        <n-button 
          type="primary" 
          block 
          @click="handleEnterpriseRegister"
          :loading="loading"
        >
          <template v-if="!loading">注册</template>
          <template v-else>
            <n-spin size="small" />
            注册中...
          </template>
        </n-button>
      </n-form>
    </n-modal>

    <!-- 找回密码弹窗 -->
    <n-modal v-model:show="showForgotPassword" preset="card" title="找回密码" style="width: 400px;">
      <n-form 
        ref="resetFormRef" 
        :model="resetForm" 
        :rules="resetRules"
        label-placement="top"
      >
        <n-form-item label="用户名" path="username">
          <n-input 
            v-model:value="resetForm.username" 
            placeholder="请输入用户名"
            autocomplete="username"
          />
        </n-form-item>
        <n-form-item label="绑定的邮箱" path="email">
          <n-input 
            v-model:value="resetForm.email" 
            placeholder="请输入绑定的邮箱"
            autocomplete="email"
          />
        </n-form-item>
        <n-form-item>
          <n-space>
            <n-input 
              v-model:value="resetForm.code" 
              placeholder="请输入验证码"
              autocomplete="one-time-code"
              style="width: 150px;"
            />
            <n-button 
              type="primary" 
              @click="sendResetCode"
              :loading="sendingCode"
              :disabled="countdown > 0"
            >
              {{ countdown > 0 ? `${countdown}秒后重试` : '发送验证码' }}
            </n-button>
          </n-space>
        </n-form-item>
        <n-form-item label="新密码" path="new_password">
          <n-input 
            v-model:value="resetForm.new_password" 
            type="password"
            placeholder="请输入新密码"
            autocomplete="new-password"
          />
        </n-form-item>
        <n-button 
          type="primary" 
          block 
          @click="handleResetPassword"
          :loading="resetting"
        >
          重置密码
        </n-button>
      </n-form>
    </n-modal>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { 
  NForm, NFormItem, NFormItemRow, NInput, NButton, NCard, NSpin, 
  NText, NTabs, NTabPane, NModal, NSpace, NIcon 
} from 'naive-ui'
import { Person, LockClosed, Mail } from '@vicons/ionicons5'
import axios from '@/utils/axios'

const router = useRouter()

// 用户登录表单
const userLoginForm = ref({
  username: '',
  password: ''
})

// 企业登录表单
const enterpriseLoginForm = ref({
  username: '',
  password: ''
})

// 用户注册表单
const userRegisterForm = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// 企业注册表单
const enterpriseRegisterForm = ref({
  username: '',
  contact_email: '',
  password: '',
  confirmPassword: '',
  enterpriseName: '',
  description: '',
  contactPerson: '',
  contactPhone: '',
  address: ''
})

// 找回密码表单
const resetForm = ref({
  username: '',
  email: '',
  code: '',
  new_password: ''
})

const userLoginFormRef = ref(null)
const enterpriseLoginFormRef = ref(null)
const userRegisterFormRef = ref(null)
const enterpriseRegisterFormRef = ref(null)
const resetFormRef = ref(null)

const loading = ref(false)
const sendingCode = ref(false)
const resetting = ref(false)
const countdown = ref(0)
const showForgotPassword = ref(false)
const showUserRegister = ref(false)
const showEnterpriseRegister = ref(false)
const activeTab = ref('user-login')

// 表单验证规则
const userLoginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const enterpriseLoginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const userRegisterRules = {
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
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value) => {
        return value === userRegisterForm.value.password
      },
      message: '两次输入的密码不一致',
      trigger: 'blur'
    }
  ]
}

const enterpriseRegisterRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3-20 个字符', trigger: 'blur' }
  ],
  contact_email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value) => {
        return value === enterpriseRegisterForm.value.password
      },
      message: '两次输入的密码不一致',
      trigger: 'blur'
    }
  ],
  enterpriseName: [
    { required: true, message: '请输入企业名称', trigger: 'blur' },
    { min: 2, max: 200, message: '企业名称长度在 2-200 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入企业简介', trigger: 'blur' }
  ],
  contactPerson: [
    { required: true, message: '请输入联系人', trigger: 'blur' }
  ],
  contactPhone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' }
  ],
  address: [
    { required: true, message: '请输入企业地址', trigger: 'blur' }
  ]
}

const resetRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' }
  ]
}

// 用户登录
const handleUserLogin = async () => {
  if (!userLoginFormRef.value) return
  
  try {
    await userLoginFormRef.value.validate()
    loading.value = true
    
    const response = await axios.post('/login/', {
      username: userLoginForm.value.username,
      password: userLoginForm.value.password
    })
    
    const { access, refresh } = response.data
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
    
    const userInfoResponse = await axios.get('/user/info/')
    const userInfo = userInfoResponse.data
    localStorage.setItem('userInfo', JSON.stringify(userInfo))
    
    router.push(userInfo.is_enterprise ? '/enterprise/home' : '/home')
  } catch (error) {
    console.error('登录失败:', error.response?.data || error.message)
  } finally {
    loading.value = false
  }
}

// 企业登录
const handleEnterpriseLogin = async () => {
  if (!enterpriseLoginFormRef.value) return
  
  try {
    await enterpriseLoginFormRef.value.validate()
    loading.value = true
    
    const response = await axios.post('/login/', {
      username: enterpriseLoginForm.value.username,
      password: enterpriseLoginForm.value.password
    })
    
    const { access, refresh } = response.data
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
    
    const userInfoResponse = await axios.get('/user/info/')
    const userInfo = userInfoResponse.data
    localStorage.setItem('userInfo', JSON.stringify(userInfo))
    
    router.push('/enterprise/home')
  } catch (error) {
    console.error('登录失败:', error.response?.data || error.message)
  } finally {
    loading.value = false
  }
}

// 用户注册
const handleUserRegister = async () => {
  if (!userRegisterFormRef.value) return
  
  try {
    await userRegisterFormRef.value.validate()
    loading.value = true
    
    const response = await axios.post('/register/', {
      username: userRegisterForm.value.username,
      email: userRegisterForm.value.email,
      password: userRegisterForm.value.password,
      password_confirm: userRegisterForm.value.confirmPassword
    })
    
    if (response.status === 201) {
      alert('注册成功！请登录')
      
      // 清空用户注册表单
      userRegisterForm.value = {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      }
      
      // 关闭注册弹窗
      showUserRegister.value = false
    }
  } catch (error) {
    console.error('注册失败:', error.response?.data || error.message)
    alert(error.response?.data?.username?.[0] || error.response?.data?.email?.[0] || '注册失败')
  } finally {
    loading.value = false
  }
}

// 企业注册
const handleEnterpriseRegister = async () => {
  if (!enterpriseRegisterFormRef.value) return
  
  try {
    await enterpriseRegisterFormRef.value.validate()
    loading.value = true
    
    // 先注册用户
    const userResponse = await axios.post('/register/', {
      username: enterpriseRegisterForm.value.username,
      email: enterpriseRegisterForm.value.contact_email,
      password: enterpriseRegisterForm.value.password,
      password_confirm: enterpriseRegisterForm.value.confirmPassword,
      is_enterprise: true
    })
    
    // 登录获取token
    const loginResponse = await axios.post('/login/', {
      username: enterpriseRegisterForm.value.username,
      password: enterpriseRegisterForm.value.password
    })
    
    // 存储 Token
    localStorage.setItem('accessToken', loginResponse.data.access);
    localStorage.setItem('refreshToken', loginResponse.data.refresh);
    
    // 创建企业信息
    const enterpriseResponse = await axios.post('/enterprises/', {
      name: enterpriseRegisterForm.value.enterpriseName,
      description: enterpriseRegisterForm.value.description,
      contact_person: enterpriseRegisterForm.value.contactPerson,
      contact_phone: enterpriseRegisterForm.value.contactPhone,
      contact_email: enterpriseRegisterForm.value.contact_email,
      address: enterpriseRegisterForm.value.address
    }, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('accessToken')}`
      }
    });

    alert('企业注册成功！')
    
    // 清空企业注册表单
    enterpriseRegisterForm.value = {
      username: '',
      contact_email: '',
      password: '',
      confirmPassword: '',
      enterpriseName: '',
      description: '',
      contactPerson: '',
      contactPhone: '',
      address: ''
    }
    
    // 关闭注册弹窗
    showEnterpriseRegister.value = false
  } catch (error) {
    console.error('注册失败:', error.response?.data || error.message)
    alert(error.response?.data?.username?.[0] || error.response?.data?.email?.[0] || '注册失败')
  } finally {
    loading.value = false
  }
}

// 发送重置验证码
const sendResetCode = async () => {
  if (!resetFormRef.value) return
  
  try {
    await resetFormRef.value.validate(['username', 'email'])
    sendingCode.value = true
    
    const response = await axios.post('/send-reset-code/', {
      username: resetForm.value.username,
      email: resetForm.value.email
    })
    
    alert(`验证码已发送：${response.data.code}`)
    
    // 开始倒计时
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  } catch (error) {
    console.error('发送验证码失败:', error.response?.data || error.message)
    alert(error.response?.data?.error || '发送失败')
  } finally {
    sendingCode.value = false
  }
}

// 重置密码
const handleResetPassword = async () => {
  if (!resetFormRef.value) return
  
  try {
    await resetFormRef.value.validate()
    resetting.value = true
    
    await axios.post('/reset-password/', {
      username: resetForm.value.username,
      code: resetForm.value.code,
      new_password: resetForm.value.new_password
    })
    
    alert('密码重置成功！请使用新密码登录')
    showForgotPassword.value = false
    
    // 清空表单
    resetForm.value = {
      username: '',
      email: '',
      code: '',
      new_password: ''
    }
  } catch (error) {
    console.error('重置密码失败:', error.response?.data || error.message)
    alert(error.response?.data?.error || '重置失败')
  } finally {
    resetting.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #bad2ce 0%, #9ddcd0 100%);
}

.login-card {
  width: 100%;
  max-width: 450px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.card-tabs :deep(.n-tabs-nav) {
  padding: 0;
  margin-bottom: 20px;
}

.card-tabs :deep(.n-tabs-tab) {
  font-size: 15px;
  font-weight: 500;
}

.card-tabs :deep(.n-tabs-tab--active) {
  color: #667eea;
  font-weight: 600;
}

.card-tabs :deep(.n-tabs-bar) {
  background: #667eea;
}

.n-form-item {
  margin-bottom: 16px;
}

.forgot-password {
  text-align: center;
  margin-top: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
}

.divider {
  color: #999;
  font-size: 14px;
}

.forgot-password button {
  font-size: 13px;
  padding: 0;
}
</style>