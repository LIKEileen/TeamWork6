<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2 class="title">登 录</h2>

      <el-tabs v-model="activeTab" stretch>
        <el-tab-pane label="手机号登录" name="phone">
          <el-form
            ref="loginForm"
            :model="form"
            :rules="commonRules"
            label-position="top"
          >
            <el-form-item label="手机号" prop="phone">
              <el-input
                v-model="form.phone"
                placeholder="请输入手机号"
                clearable
              />
            </el-form-item>

            <el-form-item label="密码" prop="password">
              <el-input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="请输入密码"
              >
                <template #suffix>
                  <el-icon @click="togglePassword" class="cursor-pointer">
                    <component :is="showPassword ? View : Hide" />
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>

            <!-- 登录和学校认证按钮排在同一行 -->
            <div class="button-container">
              <el-button type="primary" @click="handleLogin('phone')" class="button-item">登 录</el-button>
              <el-button type="success" plain @click="goToSchoolAuth" class="button-item">学校认证登录</el-button>
            </div>

            <!-- 忘记密码链接 -->
            <div class="forgot-password">
              <router-link to="/forgot-password">忘记密码？</router-link>
            </div>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="邮箱登录" name="email">
          <el-form
            ref="loginForm"
            :model="form"
            :rules="commonRules"
            label-position="top"
          >
            <el-form-item label="邮箱" prop="email">
              <el-input
                v-model="form.email"
                placeholder="请输入邮箱"
                clearable
              />
            </el-form-item>

            <el-form-item label="密码" prop="password">
              <el-input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="请输入密码"
              >
                <template #suffix>
                  <el-icon @click="togglePassword" class="cursor-pointer">
                    <component :is="showPassword ? View : Hide" />
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>

            <!-- 登录和学校认证按钮排在同一行 -->
            <div class="button-container">
              <el-button type="primary" @click="handleLogin('email')" class="button-item">登 录</el-button>
              <el-button type="success" plain @click="goToSchoolAuth" class="button-item">学校认证登录</el-button>
            </div>

            <!-- 忘记密码链接 -->
            <div class="forgot-password">
              <router-link to="/forgot-password">忘记密码？</router-link>
            </div>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <div class="register-link">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { View, Hide } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { login } from '@/api/auth'
import { IS_DEV } from '@/config'
import { computed } from 'vue'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('phone')
const showPassword = ref(false)

const form = ref({
  phone: '',
  email: '',
  password: ''
})

const commonRules = computed(() => {
  const rules = {
    password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
  }

  if (activeTab.value === 'phone') {
    rules.phone = [
      { required: true, message: '请输入手机号', trigger: 'blur' },
      { pattern: /^1\d{10}$/, message: '手机号格式不正确', trigger: 'blur' }
    ]
  } else {
    rules.email = [
      { required: true, message: '请输入邮箱', trigger: 'blur' },
      {
        type: 'email',
        message: '邮箱格式不正确',
        trigger: ['blur', 'change']
      }
    ]
  }

  return rules
})

const loginForm = ref(null)

const togglePassword = () => {
  showPassword.value = !showPassword.value
}

const handleLogin = async (type) => {
  loginForm.value.validate(async valid => {
    if (!valid) return

    const payload = {
      phone: type === 'phone' ? form.value.phone : '',
      email: type === 'email' ? form.value.email : '',
      password: form.value.password
    }

    // -------------------------
    // 本地开发模拟登录逻辑
    // -------------------------
    if (IS_DEV) {
      const mockData = {
        token: 'mock-token-abc123',
        nickname: type === 'phone' ? '手机用户' : '邮箱用户',
        avatar: new URL('@/assets/default_icon.jpg', import.meta.url).href,
        email: payload.email === '' ? payload.email : '1@q.cc',
        phone: payload.phone,
        role: 'user',
        orgs: ['开发组', '测试组']
      }
      userStore.setUserInfo(mockData)
      ElMessage.success('模拟登录成功')
      router.push('/dashboard')
      return
    }

    // -------------------------
    // 正式联调请求逻辑
    // -------------------------
    try {
      const { data } = await login(payload)
      if (data && data.code === 1) {
        userStore.setUserInfo(data.data)
        ElMessage.success('登录成功')
        router.push('/dashboard')
      } else {
        console.log(data)
        ElMessage.error(data.message || '登录失败')
      }
    } catch (err) {
      console.log(err)
      ElMessage.error('网络错误或服务器异常')
    }
  })
}

const goToSchoolAuth = () => {
  // 真实流程应为学校统一认证跳转 + 回调
  // 这里暂时模拟跳转
  router.push('/bind-phone')
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(to right, #f1f5f9, #ffffff);
}

.login-card {
  width: 420px;
  padding: 32px;
  border-radius: 18px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
}

.title {
  text-align: center;
  margin-bottom: 20px;
  font-size: 22px;
  color: #333;
}

.forgot-password {
  text-align: center;
  margin-top: 10px;
}

.forgot-password a {
  color: #409EFF;
  font-size: 14px;
}

.register-link {
  margin-top: 16px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.button-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
}

.button-item {
  width: 48%; /* 两个按钮占据等宽的空间 */
}

.extra-options {
  margin-top: 20px;
}
</style>
