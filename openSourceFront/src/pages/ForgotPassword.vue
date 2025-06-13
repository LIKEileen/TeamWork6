<template>
    <div class="forgot-password-container">
      <h2 class="title">重置密码</h2>
      <p class="sub-title">请输入您的邮箱，我们将发送验证码来重置密码</p>
  
      <el-form :model="form" :rules="rules" ref="resetForm" label-position="top">
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" clearable />
        </el-form-item>
  
        <el-form-item label="验证码" prop="code">
          <el-input v-model="form.code" placeholder="请输入验证码" clearable class="code-input">
            <template #append>
              <el-button
                :disabled="isDisabled"
                @click="sendVerificationCode"
                class="send-code-btn"
              >
                {{ buttonText }}
              </el-button>
            </template>
          </el-input>
        </el-form-item>
  
        <el-form-item label="新密码" prop="password">
          <el-input
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="请输入新密码"
            clearable
          >
            <template #suffix>
              <el-icon @click="togglePassword" class="cursor-pointer">
                <component :is="showPassword ? View : Hide" />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            :type="showConfirmPassword ? 'text' : 'password'"
            placeholder="请再次输入密码"
            clearable
          >
            <template #suffix>
              <el-icon @click="toggleConfirmPassword" class="cursor-pointer">
                <component :is="showConfirmPassword ? View : Hide" />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>

  
        <el-form-item>
          <el-row :gutter="10" style="width: 100%">
            <el-col :span="12">
              <el-button type="primary" block @click="handleResetPassword">提交</el-button>
            </el-col>
            <el-col :span="12">
              <el-button block @click="router.push('/login')">取消</el-button>
            </el-col>
          </el-row>
        </el-form-item>
      </el-form>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue'
  import { ElMessage } from 'element-plus'
  import { useRouter } from 'vue-router'
  import { View, Hide } from '@element-plus/icons-vue'
  import { sendVerificationCodeApi, resetPasswordApi } from '@/api/auth'
  import { IS_DEV } from '@/config'
  
  const router = useRouter()
  
  // 表单数据
  const form = ref({
    email: '',
    code: '',
    password: '',
    confirmPassword: ''
  })
  
  // 定时器控制按钮文字和禁用状态
  const buttonText = ref('发送验证码')
  const isDisabled = ref(false)
  let timer = null
  let countdown = 60

    // 密码确认校验
    const validatePasswordConfirm = (rule, value, callback) => {
    if (value && value !== form.value.password) {
        callback(new Error('两次密码输入不一致'))
    } else {
        callback()
    }
  }
  
  // 表单验证规则
  const rules = {
    email: [
      { required: true, message: '请输入邮箱', trigger: 'blur' },
      { type: 'email', message: '邮箱格式不正确', trigger: ['blur', 'change'] }
    ],
    code: [{ required: true, message: '请输入验证码', trigger: 'blur' }],
    password: [{ required: true, message: '请输入新密码', trigger: 'blur' }],
    confirmPassword: [
      { required: true, message: '请确认密码', trigger: 'blur' },
      { validator: validatePasswordConfirm, trigger: 'blur' }
    ]
  }
  
  // 显示/隐藏密码
  const showPassword = ref(false)
  const showConfirmPassword = ref(false)
  
  const togglePassword = () => {
    showPassword.value = !showPassword.value
  }
  
  const toggleConfirmPassword = () => {
    showConfirmPassword.value = !showConfirmPassword.value
  }
  
  // 发送验证码
  const sendVerificationCode = async () => {
  if (!form.value.email) {
    ElMessage.error('请输入邮箱')
    return
  }

  // 👉 mock 环境下只显示模拟成功提示，不实际请求
  if (IS_DEV) {
    ElMessage.success('【开发模式】验证码为 114514，请直接输入测试')
    startCountdown()
    return
  }

  try {
    const { data } = await sendVerificationCodeApi({ email: form.value.email })
    if (data.code === 200) {
      ElMessage.success('验证码已发送，请查收您的邮箱')
      startCountdown()
    } else {
      ElMessage.error(data.message || '验证码发送失败')
    }
  } catch (error) {
    ElMessage.error('网络错误，请稍后重试')
  }
}

  
  // 开始倒计时
  const startCountdown = () => {
    isDisabled.value = true
    timer = setInterval(() => {
      countdown--
      buttonText.value = `${countdown}s 后重发`
      if (countdown === 0) {
        clearInterval(timer)
        isDisabled.value = false
        buttonText.value = '发送验证码'
        countdown = 60
      }
    }, 1000)
  }
  
  // 重置密码
  const handleResetPassword = async () => {
  if (form.value.password !== form.value.confirmPassword) {
    ElMessage.error('两次密码不一致')
    return
  }

  // 👉 mock 验证逻辑
  if (IS_DEV) {
    if (form.value.code === '114514') {
      ElMessage.success('【开发模式】密码重置成功！')
      router.push('/login')
    } else {
      ElMessage.error('验证码错误，请输入 114514')
    }
    return
  }

  try {
    const payload = {
      email: form.value.email,
      code: form.value.code,
      password: form.value.password
    }

    const { data } = await resetPasswordApi(payload)
    if (data.code === 200) {
      ElMessage.success('密码重置成功，请重新登录')
      router.push('/login')
    } else {
      ElMessage.error(data.message || '密码重置失败')
    }
  } catch (error) {
    ElMessage.error('服务器异常，重置失败')
  }
}

  </script>
  
  <style scoped>
  .forgot-password-container {
    width: 100%;
    max-width: 450px;
    margin: 100px auto;
    padding: 20px;
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    text-align: center;
  }
  
  .title {
    font-size: 24px;
    margin-bottom: 10px;
    color: #333;
  }
  
  .sub-title {
    color: #888;
    font-size: 14px;
    margin-bottom: 30px;
  }
  
  .el-form-item {
    margin-bottom: 20px;
  }
  
  .el-button {
    width: 100%;
    font-size: 14px;
  }

  .el-form-item .el-input,
  .el-form-item .el-input-group {
    width: 100%;
  }

  .send-code-btn {
    padding: 0 20px;
    height: 32px;
    line-height: 32px;
    font-size: 13px;
  }

  .code-input .el-input__inner {
    height: 32px;
  }

  </style>
  