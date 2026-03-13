<template>
  <div class="login-page">
    <a href="http://localhost:8000/admin/" class="admin-link" target="_blank">管理员入口</a>
    <h1 class="page-title">大学生就业信息共享平台</h1>
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
                :type="showUserLoginPassword ? 'text' : 'password'"
                placeholder="请输入密码"
                autocomplete="current-password"
              >
                <template #prefix>
                  <n-icon :component="LockClosed" />
                </template>
                <template #suffix>
                  <n-icon 
                    :component="showUserLoginPassword ? EyeOff : Eye"
                    style="cursor: pointer"
                    @click="showUserLoginPassword = !showUserLoginPassword"
                  />
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
                :type="showEnterpriseLoginPassword ? 'text' : 'password'"
                placeholder="请输入密码"
                autocomplete="current-password"
              >
                <template #prefix>
                  <n-icon :component="LockClosed" />
                </template>
                <template #suffix>
                  <n-icon 
                    :component="showEnterpriseLoginPassword ? EyeOff : Eye"
                    style="cursor: pointer"
                    @click="showEnterpriseLoginPassword = !showEnterpriseLoginPassword"
                  />
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
        <n-form-item label="密码" path="password">
          <n-input 
            v-model:value="userRegisterForm.password" 
            :type="showUserRegisterPassword ? 'text' : 'password'"
            placeholder="请输入密码"
            autocomplete="new-password"
          >
            <template #prefix>
              <n-icon :component="LockClosed" />
            </template>
            <template #suffix>
              <n-icon 
                :component="showUserRegisterPassword ? EyeOff : Eye"
                style="cursor: pointer"
                @click="showUserRegisterPassword = !showUserRegisterPassword"
              />
            </template>
          </n-input>
          <template #feedback>
            <div v-if="userRegisterForm.password" style="font-size: 12px;">
              <span :style="{ color: userRegisterPasswordStrength.color }">{{ userRegisterPasswordStrength.text }}</span>
            </div>
          </template>
        </n-form-item>
        <n-form-item label="确认密码" path="confirmPassword">
          <n-input 
            v-model:value="userRegisterForm.confirmPassword" 
            :type="showUserRegisterConfirmPassword ? 'text' : 'password'"
            placeholder="请再次输入密码"
            autocomplete="new-password"
          >
            <template #prefix>
              <n-icon :component="LockClosed" />
            </template>
            <template #suffix>
              <n-icon 
                :component="showUserRegisterConfirmPassword ? EyeOff : Eye"
                style="cursor: pointer"
                @click="showUserRegisterConfirmPassword = !showUserRegisterConfirmPassword"
              />
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
        <n-form-item label="验证码" path="verificationCode">
          <n-space>
            <n-input 
              v-model:value="userRegisterForm.verificationCode" 
              placeholder="请输入验证码"
              autocomplete="one-time-code"
              style="width: 150px;"
            />
            <n-button 
              type="primary" 
              @click="sendUserRegisterCode"
              :loading="sendingUserCode"
              :disabled="userCodeCountdown > 0"
            >
              {{ userCodeCountdown > 0 ? `${userCodeCountdown}秒后重试` : '发送验证码' }}
            </n-button>
          </n-space>
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
        <n-form-item label="密码" path="password">
          <n-input 
            v-model:value="enterpriseRegisterForm.password" 
            :type="showEnterpriseRegisterPassword ? 'text' : 'password'"
            placeholder="请输入密码"
            autocomplete="new-password"
          >
            <template #prefix>
              <n-icon :component="LockClosed" />
            </template>
            <template #suffix>
              <n-icon 
                :component="showEnterpriseRegisterPassword ? EyeOff : Eye"
                style="cursor: pointer"
                @click="showEnterpriseRegisterPassword = !showEnterpriseRegisterPassword"
              />
            </template>
          </n-input>
          <template #feedback>
            <div v-if="enterpriseRegisterForm.password" style="font-size: 12px;">
              <span :style="{ color: enterpriseRegisterPasswordStrength.color }">{{ enterpriseRegisterPasswordStrength.text }}</span>
            </div>
          </template>
        </n-form-item>
        <n-form-item label="确认密码" path="confirmPassword">
          <n-input 
            v-model:value="enterpriseRegisterForm.confirmPassword" 
            :type="showEnterpriseRegisterConfirmPassword ? 'text' : 'password'"
            placeholder="请再次输入密码"
            autocomplete="new-password"
          >
            <template #prefix>
              <n-icon :component="LockClosed" />
            </template>
            <template #suffix>
              <n-icon 
                :component="showEnterpriseRegisterConfirmPassword ? EyeOff : Eye"
                style="cursor: pointer"
                @click="showEnterpriseRegisterConfirmPassword = !showEnterpriseRegisterConfirmPassword"
              />
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
        <n-form-item label="验证码" path="verificationCode">
          <n-space>
            <n-input 
              v-model:value="enterpriseRegisterForm.verificationCode" 
              placeholder="请输入验证码"
              autocomplete="one-time-code"
              style="width: 150px;"
            />
            <n-button 
              type="primary" 
              @click="sendEnterpriseRegisterCode"
              :loading="sendingEnterpriseCode"
              :disabled="enterpriseCodeCountdown > 0"
            >
              {{ enterpriseCodeCountdown > 0 ? `${enterpriseCodeCountdown}秒后重试` : '发送验证码' }}
            </n-button>
          </n-space>
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
          >
            <template #prefix>
              <n-icon :component="Person" />
            </template>
          </n-input>
        </n-form-item>
        <n-form-item label="新密码" path="new_password">
          <n-input 
            v-model:value="resetForm.new_password" 
            :type="showResetPassword ? 'text' : 'password'"
            placeholder="请输入新密码"
            autocomplete="new-password"
          >
            <template #prefix>
              <n-icon :component="LockClosed" />
            </template>
            <template #suffix>
              <n-icon 
                :component="showResetPassword ? EyeOff : Eye"
                style="cursor: pointer"
                @click="showResetPassword = !showResetPassword"
              />
            </template>
          </n-input>
          <template #feedback>
            <div v-if="resetForm.new_password" style="font-size: 12px;">
              <span :style="{ color: resetPasswordStrength.color }">{{ resetPasswordStrength.text }}</span>
            </div>
          </template>
        </n-form-item>
        <n-form-item label="确认新密码" path="confirm_password">
          <n-input 
            v-model:value="resetForm.confirm_password" 
            :type="showResetPassword ? 'text' : 'password'"
            placeholder="请再次输入新密码"
            autocomplete="new-password"
          >
            <template #prefix>
              <n-icon :component="LockClosed" />
            </template>
            <template #suffix>
              <n-icon 
                :component="showResetPassword ? EyeOff : Eye"
                style="cursor: pointer"
                @click="showResetPassword = !showResetPassword"
              />
            </template>
          </n-input>
        </n-form-item>
        <n-form-item label="邮箱" path="email">
          <n-input 
            v-model:value="resetForm.email" 
            placeholder="请输入绑定的邮箱"
            autocomplete="email"
          >
            <template #prefix>
              <n-icon :component="Mail" />
            </template>
          </n-input>
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { 
  NForm, NFormItem, NFormItemRow, NInput, NButton, NCard, NSpin, 
  NText, NTabs, NTabPane, NModal, NSpace, NIcon, useMessage 
} from 'naive-ui'
import { Person, LockClosed, Mail, Eye, EyeOff } from '@vicons/ionicons5'
import axios from '@/utils/axios'

const router = useRouter()
const message = useMessage()

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
  verificationCode: '',
  password: '',
  confirmPassword: ''
})

// 企业注册表单
const enterpriseRegisterForm = ref({
  username: '',
  contact_email: '',
  verificationCode: '',
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
  new_password: '',
  confirm_password: ''
})

const userLoginFormRef = ref(null)
const enterpriseLoginFormRef = ref(null)
const userRegisterFormRef = ref(null)
const enterpriseRegisterFormRef = ref(null)
const resetFormRef = ref(null)

// 密码显示状态
const showUserLoginPassword = ref(false)
const showEnterpriseLoginPassword = ref(false)
const showUserRegisterPassword = ref(false)
const showUserRegisterConfirmPassword = ref(false)
const showEnterpriseRegisterPassword = ref(false)
const showEnterpriseRegisterConfirmPassword = ref(false)
const showResetPassword = ref(false)

const loading = ref(false)
const sendingCode = ref(false)
const sendingUserCode = ref(false)
const sendingEnterpriseCode = ref(false)
const resetting = ref(false)
const countdown = ref(0)
const userCodeCountdown = ref(0)
const enterpriseCodeCountdown = ref(0)
const showForgotPassword = ref(false)
const showUserRegister = ref(false)
const showEnterpriseRegister = ref(false)
const activeTab = ref('user-login')

// 计算密码强度
const calculatePasswordStrength = (password) => {
  if (!password) return { text: '', color: '#86909c' }
  
  let score = 0
  
  // 长度检查
  if (password.length >= 6) score += 1
  if (password.length >= 8) score += 1
  if (password.length >= 12) score += 1
  
  // 复杂度检查
  if (/[a-z]/.test(password)) score += 1
  if (/[A-Z]/.test(password)) score += 1
  if (/[0-9]/.test(password)) score += 1
  if (/[^a-zA-Z0-9]/.test(password)) score += 1
  
  // 根据分数返回强度信息
  if (score <= 2) return { text: '密码强度：弱', color: '#f53f3f' }
  if (score <= 4) return { text: '密码强度：中', color: '#ff7d00' }
  if (score <= 5) return { text: '密码强度：强', color: '#00b42a' }
  return { text: '密码强度：非常强', color: '#165dff' }
}

// 用户注册密码强度
const userRegisterPasswordStrength = computed(() => {
  return calculatePasswordStrength(userRegisterForm.value.password)
})

// 企业注册密码强度
const enterpriseRegisterPasswordStrength = computed(() => {
  return calculatePasswordStrength(enterpriseRegisterForm.value.password)
})

// 重置密码强度
const resetPasswordStrength = computed(() => {
  return calculatePasswordStrength(resetForm.value.new_password)
})

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
    { required: true, message: '请输入用户名', trigger: ['blur', 'input'] },
    { min: 3, max: 20, message: '用户名长度在 3-20 个字符', trigger: ['blur', 'input'] }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: ['blur', 'input'] },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: ['blur', 'input'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: ['blur', 'input'] },
    { min: 6, message: '密码长度至少 6 个字符', trigger: ['blur', 'input'] }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: ['blur', 'input'] },
    {
      validator: (rule, value) => {
        return value === userRegisterForm.value.password
      },
      message: '两次输入的密码不一致',
      trigger: ['blur', 'input']
    }
  ],
  verificationCode: [
    { required: true, message: '请输入验证码', trigger: ['blur', 'input'] },
    { len: 6, message: '验证码为6位数字', trigger: ['blur', 'input'] }
  ]
}

const enterpriseRegisterRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: ['blur', 'input'] },
    { min: 3, max: 20, message: '用户名长度在 3-20 个字符', trigger: ['blur', 'input'] }
  ],
  contact_email: [
    { required: true, message: '请输入邮箱', trigger: ['blur', 'input'] },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: ['blur', 'input'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: ['blur', 'input'] },
    { min: 6, message: '密码长度至少 6 个字符', trigger: ['blur', 'input'] }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: ['blur', 'input'] },
    {
      validator: (rule, value) => {
        return value === enterpriseRegisterForm.value.password
      },
      message: '两次输入的密码不一致',
      trigger: ['blur', 'input']
    }
  ],
  enterpriseName: [
    { required: true, message: '请输入企业名称', trigger: ['blur', 'input'] },
    { min: 2, max: 200, message: '企业名称长度在 2-200 个字符', trigger: ['blur', 'input'] }
  ],
  description: [
    { required: true, message: '请输入企业简介', trigger: ['blur', 'input'] }
  ],
  contactPerson: [
    { required: true, message: '请输入联系人', trigger: ['blur', 'input'] }
  ],
  contactPhone: [
    { required: true, message: '请输入联系电话', trigger: ['blur', 'input'] }
  ],
  address: [
    { required: true, message: '请输入企业地址', trigger: ['blur', 'input'] }
  ],
  verificationCode: [
    { required: true, message: '请输入验证码', trigger: ['blur', 'input'] },
    { len: 6, message: '验证码为6位数字', trigger: ['blur', 'input'] }
  ]
}

const resetRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: ['blur', 'input'] }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: ['blur', 'input'] },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: ['blur', 'input'] }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: ['blur', 'input'] },
    { len: 4, message: '验证码为4位数字', trigger: ['blur', 'input'] }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: ['blur', 'input'] }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: ['blur', 'input'] },
    {
      validator: (rule, value) => {
        return value === resetForm.value.new_password
      },
      message: '两次输入的密码不一致',
      trigger: ['blur', 'input']
    }
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
    sessionStorage.setItem('accessToken', access)
    sessionStorage.setItem('refreshToken', refresh)
    
    const userInfoResponse = await axios.get('/user/info/')
    const userInfo = userInfoResponse.data
    localStorage.setItem('userInfo', JSON.stringify(userInfo))
    sessionStorage.setItem('userInfo', JSON.stringify(userInfo))
    
    router.push(userInfo.is_enterprise ? '/enterprise/home' : '/home')
  } catch (error) {
    console.error('登录失败:', error.response?.data || error.message)
    
    // 提取错误信息
    let errorMessage = '登录失败'
    const errorData = error.response?.data
    
    if (errorData) {
      if (errorData.username) {
        errorMessage = errorData.username[0]
      } else if (errorData.password) {
        errorMessage = errorData.password[0]
      } else if (errorData.detail) {
        errorMessage = errorData.detail
      } else if (errorData.error) {
        errorMessage = errorData.error
      }
    }
    
    message.error(errorMessage)
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
    sessionStorage.setItem('accessToken', access)
    sessionStorage.setItem('refreshToken', refresh)
    
    const userInfoResponse = await axios.get('/user/info/')
    const userInfo = userInfoResponse.data
    localStorage.setItem('userInfo', JSON.stringify(userInfo))
    sessionStorage.setItem('userInfo', JSON.stringify(userInfo))
    
    router.push('/enterprise/home')
  } catch (error) {
    console.error('登录失败:', error.response?.data || error.message)
    
    // 提取错误信息
    let errorMessage = '登录失败'
    const errorData = error.response?.data
    
    if (errorData) {
      if (errorData.username) {
        errorMessage = errorData.username[0]
      } else if (errorData.password) {
        errorMessage = errorData.password[0]
      } else if (errorData.detail) {
        errorMessage = errorData.detail
      } else if (errorData.error) {
        errorMessage = errorData.error
      }
    }
    
    message.error(errorMessage)
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
      verification_code: userRegisterForm.value.verificationCode,
      password: userRegisterForm.value.password,
      password_confirm: userRegisterForm.value.confirmPassword
    })
    
    if (response.status === 201) {
      message.success('注册成功！请登录')
      
      // 清空用户注册表单
      userRegisterForm.value = {
        username: '',
        email: '',
        verificationCode: '',
        password: '',
        confirmPassword: ''
      }
      
      // 关闭注册弹窗
      showUserRegister.value = false
    }
  } catch (error) {
    console.error('注册失败:', error.response?.data || error.message)
    
    // 提取错误信息
    let errorMessage = '注册失败'
    const errorData = error.response?.data
    
    if (errorData) {
      if (errorData.username) {
        errorMessage = errorData.username[0]
      } else if (errorData.email) {
        errorMessage = errorData.email[0]
      } else if (errorData.password) {
        errorMessage = errorData.password[0]
      } else if (errorData.password_confirm) {
        errorMessage = errorData.password_confirm[0]
      } else if (errorData.verification_code) {
        errorMessage = errorData.verification_code[0]
      } else if (errorData.error) {
        errorMessage = errorData.error
      } else if (errorData.detail) {
        errorMessage = errorData.detail
      }
    }
    
    message.error(errorMessage)
  } finally {
    loading.value = false
  }
}

// 发送用户注册验证码
const sendUserRegisterCode = async () => {
  if (!userRegisterForm.value.email) {
    message.warning('请先输入邮箱')
    return
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(userRegisterForm.value.email)) {
    message.warning('请输入正确的邮箱格式')
    return
  }
  
  try {
    sendingUserCode.value = true
    const response = await axios.post('http://localhost:8000/api/send-register-code/', {
      email: userRegisterForm.value.email
    })
    
    if (response.status === 200) {
      message.success(`验证码已发送到 ${userRegisterForm.value.email}`)
      
      const code = response.data.code
      message.info(`开发环境验证码：${code}`)
      
      userCodeCountdown.value = 60
      const timer = setInterval(() => {
        userCodeCountdown.value--
        if (userCodeCountdown.value <= 0) {
          clearInterval(timer)
        }
      }, 1000)
    }
  } catch (error) {
    console.error('发送验证码失败:', error)
    message.error(error.response?.data?.error || '发送验证码失败，请稍后重试')
  } finally {
    sendingUserCode.value = false
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
      verification_code: enterpriseRegisterForm.value.verificationCode,
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

    message.success('企业注册成功！')
    
    // 清空企业注册表单
    enterpriseRegisterForm.value = {
      username: '',
      contact_email: '',
      verificationCode: '',
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
    
    // 提取错误信息
    let errorMessage = '注册失败'
    const errorData = error.response?.data
    
    if (errorData) {
      if (errorData.username) {
        errorMessage = errorData.username[0]
      } else if (errorData.email) {
        errorMessage = errorData.email[0]
      } else if (errorData.password) {
        errorMessage = errorData.password[0]
      } else if (errorData.password_confirm) {
        errorMessage = errorData.password_confirm[0]
      } else if (errorData.verification_code) {
        errorMessage = errorData.verification_code[0]
      } else if (errorData.error) {
        errorMessage = errorData.error
      } else if (errorData.detail) {
        errorMessage = errorData.detail
      }
    }
    
    message.error(errorMessage)
  } finally {
    loading.value = false
  }
}

// 发送企业注册验证码
const sendEnterpriseRegisterCode = async () => {
  if (!enterpriseRegisterForm.value.contact_email) {
    message.warning('请先输入邮箱')
    return
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(enterpriseRegisterForm.value.contact_email)) {
    message.warning('请输入正确的邮箱格式')
    return
  }
  
  try {
    sendingEnterpriseCode.value = true
    const response = await axios.post('http://localhost:8000/api/send-register-code/', {
      email: enterpriseRegisterForm.value.contact_email
    })
    
    if (response.status === 200) {
      message.success(`验证码已发送到 ${enterpriseRegisterForm.value.contact_email}`)
      
      const code = response.data.code
      message.info(`开发环境验证码：${code}`)
      
      enterpriseCodeCountdown.value = 60
      const timer = setInterval(() => {
        enterpriseCodeCountdown.value--
        if (enterpriseCodeCountdown.value <= 0) {
          clearInterval(timer)
        }
      }, 1000)
    }
  } catch (error) {
    console.error('发送验证码失败:', error)
    message.error(error.response?.data?.error || '发送验证码失败，请稍后重试')
  } finally {
    sendingEnterpriseCode.value = false
  }
}

// 发送重置验证码
const sendResetCode = async () => {
  if (!resetForm.value.username || !resetForm.value.email) {
    message.warning('请先输入用户名和邮箱')
    return
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(resetForm.value.email)) {
    message.warning('请输入正确的邮箱格式')
    return
  }
  
  try {
    sendingCode.value = true
    const response = await axios.post('http://localhost:8000/api/send-reset-code/', {
      username: resetForm.value.username,
      email: resetForm.value.email
    })
    
    if (response.status === 200) {
      message.success(`验证码已发送到 ${resetForm.value.email}`)
      
      const code = response.data.code
      message.info(`开发环境验证码：${code}`)
      
      countdown.value = 60
      const timer = setInterval(() => {
        countdown.value--
        if (countdown.value <= 0) {
          clearInterval(timer)
        }
      }, 1000)
    }
  } catch (error) {
    console.error('发送验证码失败:', error)
    message.error(error.response?.data?.error || '发送验证码失败，请稍后重试')
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
    
    await axios.post('http://localhost:8000/api/reset-password/', {
      username: resetForm.value.username,
      code: resetForm.value.code,
      new_password: resetForm.value.new_password,
      confirm_password: resetForm.value.confirm_password
    })
    
    message.success('密码重置成功！请使用新密码登录')
    showForgotPassword.value = false
    
    // 清空表单
    resetForm.value = {
      username: '',
      email: '',
      code: '',
      new_password: '',
      confirm_password: ''
    }
  } catch (error) {
    console.error('重置密码失败:', error.response?.data || error.message)
    
    // 提取错误信息
    let errorMessage = '重置失败'
    const errorData = error.response?.data
    
    if (errorData) {
      if (errorData.username) {
        errorMessage = errorData.username[0]
      } else if (errorData.email) {
        errorMessage = errorData.email[0]
      } else if (errorData.code) {
        errorMessage = errorData.code[0]
      } else if (errorData.new_password) {
        errorMessage = errorData.new_password[0]
      } else if (errorData.confirm_password) {
        errorMessage = errorData.confirm_password[0]
      } else if (errorData.error) {
        errorMessage = errorData.error
      } else if (errorData.detail) {
        errorMessage = errorData.detail
      }
    }
    
    message.error(errorMessage)
  } finally {
    resetting.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px 20px 60px;
  background: linear-gradient(135deg, #bad2ce 0%, #9ddcd0 100%);
  position: relative;
}

.admin-link {
  position: absolute;
  top: 20px;
  right: 20px;
  font-size: 14px;
  color: #ffffff;
  text-decoration: none;
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

.admin-link:hover {
  opacity: 1;
  text-decoration: underline;
}

.page-title {
  font-size: 36px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 10px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  letter-spacing: 2px;
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