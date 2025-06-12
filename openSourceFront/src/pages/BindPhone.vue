<template>
  <div class="bind-container">
    <el-card class="bind-card">
      <h2 class="title">绑定手机号</h2>

      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>

        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" placeholder="请输入昵称" />
        </el-form-item>

        <el-form-item label="设置密码" prop="password">
          <el-input v-model="form.password" placeholder="请输入密码" show-password />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" placeholder="请再次输入密码" show-password />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleBind" block>确认绑定</el-button>
          <el-button @click="router.push('/login')" style="margin-top: 10px" block>取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { bindPhone } from '@/api/auth'
import { IS_DEV } from '@/config'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref()
const form = ref({
  phone: '',
  nickname: '',
  password: '',
  confirmPassword: ''
})

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1\d{10}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
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

const handleBind = () => {
  formRef.value.validate(async valid => {
    if (!valid) return

    const payload = {
      phone: form.value.phone,
      nickname: form.value.nickname,
      password: form.value.password
    }

    // ------------------------
    // ✅ 开发模式 mock 流程
    // ------------------------
    if (IS_DEV) {
      const mockData = {
        token: 'mock-token-999',
        nickname: payload.nickname,
        phone: payload.phone,
        avatar: '',
        role: 'user',
        orgs: []
      }
      userStore.setUserInfo(mockData)
      ElMessage.success('绑定成功（本地模拟）')
      router.push('/dashboard')
      return
    }

    // ------------------------
    // ✅ 真实 API 流程
    // ------------------------
    try {
      const { data } = await bindPhone(payload)
      userStore.setUserInfo(data.data)
      ElMessage.success('绑定成功')
      router.push('/dashboard')
    } catch (err) {
      ElMessage.error('绑定失败，请稍后重试')
    }
  })
}
</script>

<style scoped>
.bind-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(to right, #eef1f5, #ffffff);
}

.bind-card {
  width: 460px;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
}

.title {
  text-align: center;
  font-size: 22px;
  margin-bottom: 24px;
}
</style>
