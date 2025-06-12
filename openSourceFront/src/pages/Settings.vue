<template>
  <div class="settings-container">
    <el-card class="settings-card">
      <h2 class="section-title">个人设置</h2>

      <!-- 头像设置 -->
      <div class="avatar-wrapper">
        <img :src="userAvatar" class="avatar" />
        <div class="avatar-actions">
          <el-button size="small" @click="openCropper">更换头像</el-button>
          <div class="qq-input-group">
            <el-input v-model="qqNumber" placeholder="输入QQ号" size="small" class="qq-input" :style="inputStyle" />
            <el-button size="small" @click="useQQAvatar">使用QQ头像</el-button>
          </div>
        </div>
      </div>

      <!-- 基本信息表单 -->
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" :style="inputStyle" />
        </el-form-item>

        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="updateInfo">保存信息</el-button>
        </el-form-item>
      </el-form>

      <!-- 修改密码 -->
      <el-form :model="form" :rules="passwordRules" ref="passwordForm" label-width="100px">
        <el-form-item label="原密码" prop="oldPassword">
          <el-input v-model="form.oldPassword" :type="showOldPassword ? 'text' : 'password'" placeholder="请输入原密码" clearable>
            <template #suffix>
              <el-icon @click="toggleOldPassword" class="cursor-pointer">
                <component :is="showOldPassword ? View : Hide" />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="新密码" prop="password">
          <el-input v-model="form.password" :type="showPassword ? 'text' : 'password'" placeholder="请输入新密码" clearable>
            <template #suffix>
              <el-icon @click="togglePassword" class="cursor-pointer">
                <component :is="showPassword ? View : Hide" />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" :type="showConfirmPassword ? 'text' : 'password'" placeholder="请再次输入密码" clearable>
            <template #suffix>
              <el-icon @click="toggleConfirmPassword" class="cursor-pointer">
                <component :is="showConfirmPassword ? View : Hide" />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" block @click="handleChangePassword">修改密码</el-button>
        </el-form-item>
      </el-form>

      <!-- 大模型配置 -->
      <h3 class="section-subtitle">大模型 API 配置
        <el-tooltip effect="dark" placement="right">
          <template #content>
            在这里绑定你的大语言模型接口，例如 OpenAI 服务：<br/>
            - base_url: 模型 API 地址<br/>
            - model_name: gpt-3.5-turbo 等<br/>
            - api_key: 授权密钥<br/>
            - 系统提示词: 模型初始化行为引导语
          </template>
          <el-icon style="margin-left: 4px; cursor: help"><QuestionFilled /></el-icon>
        </el-tooltip>
      </h3>

      <el-form :model="llmConfig" ref="llmForm" label-width="110px">
        <el-form-item label="Base URL">
          <el-input v-model="llmConfig.base_url" placeholder="https://your-api.com" />
        </el-form-item>
        <el-form-item label="Model Name">
          <el-input v-model="llmConfig.model_name" placeholder="如 gpt-4" />
        </el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="llmConfig.api_key" placeholder="sk-xxxxx" show-password />
        </el-form-item>
        <el-form-item label="系统提示词">
          <el-input v-model="llmConfig.system_prompt" type="textarea" rows="2" placeholder="你是会易助手..." />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveLLMConfig">保存配置</el-button>
        </el-form-item>
      </el-form>

      <!-- 主题设置 -->
      <h3 class="section-subtitle">主题设置</h3>
      <el-form :model="theme" label-width="110px">
        <el-form-item>
          <el-select v-model="theme" @change="changeTheme">
            <el-option label="日间模式" value="light" />
            <el-option label="夜间模式" value="dark" />
          </el-select>
        </el-form-item>
      </el-form>

      <AvatarCropper v-if="cropperVisible" @success="setAvatar" @cancel="cropperVisible = false" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import AvatarCropper from '@/components/AvatarCropper.vue'
import defaultIcon from '@/assets/default_icon.jpg'
import { updateUserInfo } from '@/api/user'
import { saveLLMConfigApi, getLLMConfigApi } from '@/api/llm'
import { uploadAvatarApi, useQQAvatarApi } from '@/api/user'
import { IS_DEV } from '@/config'
import { changePasswordApi } from '@/api/user'

const userStore = useUserStore()
const cropperVisible = ref(false)
const formRef = ref()
const llmForm = ref()
const theme = ref(userStore.theme)
const qqNumber = ref('')
const showOldPassword = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const form = ref({
  nickname: userStore.nickname,
  phone: userStore.phone,
  email: userStore.email,
  oldPassword: '',
  password: '',
  confirmPassword: ''
})

const llmConfig = ref({
  base_url: 'https://xxx.com/api/xxx',  // Mock 默认链接
  model_name: 'gpt-4',
  api_key: 'sk-xxxxx',
  system_prompt: '你是会议的二把手...'
})

const uploadAvatar = async (file) => {
  if (IS_DEV) {
    // 模拟上传头像（开发模式）
    userStore.avatar = '@/assets/demo_icon.jpg'  // 设置 mock 头像地址
    ElMessage.success('【开发模式】头像上传成功！')
    return
  }

  // 正式请求头像上传
  const formData = new FormData()
  formData.append('avatar', file)
  formData.append('token', userStore.token)

  try {
    const { data } = await uploadAvatarApi(formData)
    if (data.code === 1) {
      ElMessage.success('头像上传成功')
      userStore.avatar = data.avatarUrl  // 更新用户头像
    } else {
      ElMessage.error(data.message || '头像上传失败')
    }
  } catch (err) {
    ElMessage.error('头像上传失败')
  }
}

const useQQAvatar = async () => {
  if (!qqNumber.value) return ElMessage.warning('请输入QQ号')

  if (IS_DEV) {
    // 模拟 QQ 头像获取
    userStore.avatar = `http://q.qlogo.cn/headimg_dl?dst_uin=${qqNumber.value}&spec=640&img_type=jpg`
    ElMessage.success('【开发模式】QQ头像已更新')
    return
  }

  // 正式请求使用 QQ 头像
  const payload = {
      token: userStore.token,
      avatar: `http://q.qlogo.cn/headimg_dl?dst_uin=${qqNumber.value}&spec=640&img_type=jpg`
    }

    try {
      const { data } = await useQQAvatarApi(payload)
      if (data.code === 1) {
        userStore.avatar = payload.avatar
        ElMessage.success('QQ头像已更新')
      } else {
        ElMessage.error(data.message || 'QQ头像更新失败')
      }
    } catch (err) {
      ElMessage.error('QQ头像更新失败')
    }
}

const rules = {
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1\d{10}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ]
}

const updateInfo = async () => {
  formRef.value.validate(async (valid) => {
    if (!valid) return

    // 模拟开发模式下保存信息（Mock）
    if (IS_DEV) {
      userStore.nickname = form.value.nickname
      userStore.phone = form.value.phone
      userStore.email = form.value.email
      ElMessage.success('【开发模式】用户信息已保存！')
      return
    }

    // 正式保存用户信息（请求后端）
    try {
      const payload = {
        nickname: form.value.nickname,
        phone: form.value.phone,
        email: form.value.email,
        token: userStore.token
      }

      const { data } = await updateUserInfo(payload)
      if (data.code === 1) {
        userStore.nickname = form.value.nickname
        userStore.phone = form.value.phone
        userStore.email = form.value.email
        ElMessage.success('信息已保存')
      } else {
        ElMessage.error(data.message || '信息保存失败')
      }
    } catch (err) {
      ElMessage.error('网络错误，请稍后重试')
    }
  })
}

const toggleOldPassword = () => {
  showOldPassword.value = !showOldPassword.value
}

const togglePassword = () => {
  showPassword.value = !showPassword.value
}

const toggleConfirmPassword = () => {
  showConfirmPassword.value = !showConfirmPassword.value
}

const validatePasswordConfirm = (rule, value, callback) => {
  if (value && value !== form.value.password) {
    callback(new Error('两次密码输入不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  password: [{ required: true, message: '请输入新密码', trigger: 'blur' }],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validatePasswordConfirm, trigger: 'blur' }
  ]
}

const userAvatar = computed(() => userStore.avatar || defaultIcon)

const openCropper = () => {
  cropperVisible.value = true
}

const setAvatar = (url) => {
  userStore.avatar = url
  cropperVisible.value = false
}

const changeTheme = (val) => {
  userStore.theme = val
  localStorage.setItem('theme', val)
  document.body.setAttribute('data-theme', val)
}

const saveLLMConfig = () => {
  localStorage.setItem('llm_config', JSON.stringify(llmConfig.value))
  ElMessage.success('大模型配置已保存')
  if (IS_DEV) {
    // 模拟保存配置（开发模式）
    ElMessage.success('【开发模式】大模型配置已保存！')
    return
  }
  // 模拟调用后端接口
  saveLLMConfigApi(llmConfig.value).then(() => {
    ElMessage.success('大模型配置已保存')
  }).catch(() => {
    ElMessage.error('保存失败')
  })
}

// 修改密码功能
const handleChangePassword = async () => {
  if (form.value.password !== form.value.confirmPassword) {
    ElMessage.error('两次密码不一致')
    return
  }

  if (IS_DEV) {
    ElMessage.success('【开发模式】密码修改成功！')
    return
  }

  try {
    const payload = {
      oldPassword: form.value.oldPassword,
      newPassword: form.value.password,
      token: userStore.token
    }

    const { data } = await changePasswordApi(payload)
    if (data.code === 1) {
      ElMessage.success('密码修改成功')
    } else {
      ElMessage.error(data.message || '密码修改失败')
    }
  } catch (err) {
    ElMessage.error('网络错误或服务器异常')
  }
}

onMounted(() => {
  const local = localStorage.getItem('llm_config')
  if (local) llmConfig.value = JSON.parse(local)
  getLLMConfigApi().then(({ data }) => {
    if (data) {
      llmConfig.value = data
      localStorage.setItem('llm_config', JSON.stringify(data))
    }
  })
})

const inputStyle = computed(() => {
  return {
    backgroundColor: 'var(--input-bg)',
    color: 'var(--input-text-color)',
    borderColor: 'var(--input-border-color)'
  }
})
</script>

<style scoped>
.settings-container {
  padding: 24px;
  background-color: var(--bg-color);  /* 使用动态背景颜色 */
}

.settings-card {
  max-width: 700px;
  margin: auto;
  padding: 32px;
  background-color: var(--card-bg);  /* 使用动态卡片背景颜色 */
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0);
  border: 1px solid var(--input-border-color);  /* 统一边框颜色 */
}

.avatar-wrapper {
  display: flex;
  gap: 20px;
  align-items: center;
  margin-bottom: 20px;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--input-border-color);  /* 边框颜色 */
}
.section-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 20px;
  color: var(--text-color);
}
.section-subtitle {
  margin-top: 32px;
  font-size: 16px;
  font-weight: bold;
  color: var(--text-color);
}
.avatar-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.qq-input-group {
  display: flex;
  gap: 8px;
  align-items: center;
}
.el-input__inner {
  background-color: var(--input-bg) !important;  /* 输入框背景色 */
  color: var(--input-text-color) !important;  /* 输入框文字颜色 */
  border-color: var(--input-border-color) !important;  /* 输入框边框颜色 */
}

/* 清除默认的边框和阴影 */
.el-input__inner:focus {
  border-color: var(--primary-color) !important;
  box-shadow: none !important;
}

/* 输入框背景色、文字色和边框色 */
.el-input {
  background-color: var(--input-bg) !important;
  color: var(--input-text-color) !important;
  border-color: var(--input-border-color) !important;
}

/* 在夜间模式下，按钮和其他元素的颜色 */
.el-button {
  background-color: var(--primary-color) !important;
  border-color: var(--primary-color) !important;
  color: #fff;
}
</style>
