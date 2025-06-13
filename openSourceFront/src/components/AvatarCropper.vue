<template>
  <el-dialog
    v-model="visible"
    title="裁剪头像"
    width="600px"
    :close-on-click-modal="false"
    class="cropper-dialog"
  >
    <div class="cropper-wrapper">
      <input type="file" accept="image/*" @change="onFileChange" />
      <div v-if="imageUrl" class="preview-area">
        <vue-cropper
          ref="cropper"
          :src="imageUrl"
          :aspect-ratio="1"
          :view-mode="1"
          :autoCrop="true"
          :responsive="true"
          :autoCropArea="0.8"
          background
          style="max-width: 100%; max-height: 400px;"
        />
      </div>
    </div>

    <template #footer>
      <el-button @click="cancel">取消</el-button>
      <el-button type="primary" @click="confirmCrop">确认</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, defineEmits } from 'vue'
import VueCropper from 'vue-cropperjs'
import 'cropperjs/dist/cropper.css'
import { ElMessage } from 'element-plus'
import { IS_DEV } from '@/config'
import { useUserStore } from '@/store/user'
import { uploadAvatarApi } from '@/api/user'

const emit = defineEmits(['success', 'cancel'])

const userStore = useUserStore()
const visible = ref(true)
const imageUrl = ref('')
const cropper = ref(null)

const onFileChange = (e) => {
  const file = e.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = () => {
    imageUrl.value = reader.result
  }
  reader.readAsDataURL(file)
}

const confirmCrop = async () => {
  try {
    const canvas = cropper.value.getCroppedCanvas({ width: 200, height: 200 })
    const blob = await new Promise((resolve) =>
      canvas.toBlob(resolve, 'image/jpeg')
    )

    if (IS_DEV) {
      const demoUrl = new URL('@/assets/demo_icon.jpg', import.meta.url).href
      emit('success', demoUrl)
      ElMessage.success('【开发模式】模拟上传成功')
      return
    }

    const formData = new FormData()
    formData.append('file', blob, 'avatar.jpg')
    formData.append('token', userStore.token)

    const { data } = await uploadAvatarApi(formData)
    if (data.code === 1) {
      ElMessage.success('头像上传成功')
      emit('success', data.avatarUrl)
    } else {
      ElMessage.error(data.message || '头像上传失败')
    }
  } catch (err) {
    ElMessage.error('裁剪失败，请重试')
  }
}

const cancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.cropper-dialog :deep(.el-dialog) {
  background-color: var(--card-bg);  /* 卡片背景适配主题 */
  color: var(--text-color);
}

.cropper-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
  color: var(--text-color);
}

.preview-area {
  width: 100%;
  max-height: 400px;
  border: 1px solid var(--input-border-color);
  border-radius: 8px;
  background-color: var(--input-bg);
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
