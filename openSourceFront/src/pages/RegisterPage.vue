<template>
  <div class="register-container">
    <el-card class="register-card">
      <h2 class="title">注册会易账号</h2>

      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" placeholder="请输入昵称" />
        </el-form-item>

        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" placeholder="请输入密码" show-password />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" placeholder="请再次输入密码" show-password />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" block @click="handleRegister">注册</el-button>
        </el-form-item>
      </el-form>

      <div class="login-link">
        已有账号？<router-link to="/login">返回登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { register } from '@/api/auth'
import { IS_DEV } from '@/config'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref()
const form = ref({
  nickname: '',
  phone: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const rules = {
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1\d{10}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value) => value === form.value.password,
      message: '两次输入密码不一致',
      trigger: 'blur'
    }
  ]
}

const handleRegister = () => {
  formRef.value.validate(async valid => {
    if (!valid) return

    const payload = {
      nickname: form.value.nickname,
      phone: form.value.phone,
      email: form.value.email,
      password: form.value.password
    }

    // -------------------------
    // ✅ 开发 mock 模式
    // -------------------------
    if (IS_DEV) {
      const mockData = {
        token: 'mock-token-999',
        nickname: payload.nickname,
        phone: payload.phone,
        email: payload.email,
        avatar: '',
        role: 'user',
        orgs: []
      }
      userStore.setUserInfo(mockData)
      ElMessage.success('注册成功（本地模拟）')
      router.push('/dashboard')
      return
    }

    // -------------------------
    // ✅ 实际接口请求
    // -------------------------
    try {
      const { data } = await register(payload)
      userStore.setUserInfo(data.data)
      // console.log(data)
      ElMessage.success('注册成功')
      router.push('/dashboard')
    } catch (err) {
      console.log(err)
      ElMessage.error('注册失败，请重试')
    }
  })
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(to right, #f5f7fa, #ffffff);
}

.register-card {
  width: 460px;
  padding: 30px;
  border-radius: 18px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.title {
  text-align: center;
  font-size: 22px;
  margin-bottom: 24px;
}

.login-link {
  margin-top: 16px;
  text-align: center;
  font-size: 14px;
  color: #666;
}
</style>
