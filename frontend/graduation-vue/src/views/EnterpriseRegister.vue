<template>
  <div class="register-page">
    <n-card class="register-card" title="企业用户注册">
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
            v-model:value="formData.contact_email" 
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

        <!-- 企业名称 -->
        <n-form-item path="enterpriseName" label="企业名称">
          <n-input 
            v-model:value="formData.enterpriseName" 
            placeholder="请输入企业名称"
          />
        </n-form-item>

        <n-form-item path="address" label="企业地址">
    <n-input v-model:value="formData.address" placeholder="请输入企业地址" />
  </n-form-item>

  <n-form-item path="description" label="企业简介">
    <n-input 
      v-model:value="formData.description" 
      type="textarea" 
      placeholder="请输入企业简介" 
    />
  </n-form-item>

    <n-form-item path="contactPerson" label="联系人">
        <n-input v-model:value="formData.contactPerson" placeholder="请输入联系人姓名" />
    </n-form-item>

    <n-form-item path="contactPhone" label="联系电话">
        <n-input v-model:value="formData.contactPhone" placeholder="请输入联系电话" />
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
import { Person, LockClosed, Mail } from '@vicons/ionicons5'
import axios from '@/utils/axios'

const formData = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  enterpriseName: '',
  description: '',          // 新增
  contactPerson: '',        // 新增
  contactPhone: '',         // 新增
  contact_email: '',        // 新增
  address: '' 
})

const formRef = ref(null)
const loading = ref(false)
const router = useRouter()

const rules = {
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

const handleRegister = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    // 先注册用户
    const userResponse = await axios.post('/register/', {
      username: formData.value.username,
      email: formData.value.email,
      password: formData.value.password,
      password_confirm: formData.value.confirmPassword,
      is_enterprise: true  // 标记为企业用户
    }) 
    

    // const enterpriseResponse = await axios.post('/enterprises/', {
    //   name: formData.value.enterpriseName,
    //   description: formData.value.description,
    //   contact_person: formData.value.contactPerson,
    //   contact_phone: formData.value.contactPhone,
    //   address: formData.value.address
    // }, {
    //   headers: {
    //     Authorization: `Bearer ${localStorage.getItem('accessToken')}`
    //   }
    // });
    // console.log('企业信息创建成功:', enterpriseResponse.data);

    // 再创建企业信息
    if (userResponse.status === 201) {
      // 登录获取token
      const loginResponse = await axios.post('/login/', {
        username: formData.value.username,
        password: formData.value.password
      })
      
      // 存储 Token
      localStorage.setItem('accessToken', loginResponse.data.access);
      localStorage.setItem('refreshToken', loginResponse.data.refresh);
      // 保存token
      // const { access, refresh } = loginResponse.data
      // localStorage.setItem('accessToken', access)
      // localStorage.setItem('refreshToken', refresh)
      
      const enterpriseResponse = await axios.post('/enterprises/', {
        name: formData.value.enterpriseName,
        description: formData.value.description,
        contact_person: formData.value.contactPerson,
        contact_phone: formData.value.contactPhone,
        contact_email: formData.value.contact_email,
        address: formData.value.address
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`
        }
      });

      router.push('/home')
    }
  } catch (error) {
    
    console.error('注册失败:', error.response.data) // 输出后端返回的错误信息
    console.log('注册失败:', error.message)
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