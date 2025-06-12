<template>
  <div
    class="chat-window"
    :style="{ top: position.top + 'px', left: position.left + 'px', width: size.width + 'px', height: size.height + 'px' }"
    @mousedown.stop="startDrag"
  >
    <div class="chat-header" @mousedown.stop.prevent="startResizeOrDrag($event, 'move')">
      <span>AI 协作助手</span>
      <div class="chat-controls">
        <el-switch v-model="useWebSearch" size="small" inline-prompt active-text="联网" inactive-text="本地" />
        <el-button link @click="$emit('close')">
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
    </div>
    <div class="chat-body">
      <div class="messages">
        <div
          v-for="(msg, index) in chatHistory"
          :key="index"
          :class="['message', msg.role === 'user' ? 'user-message' : 'assistant-message']"
          v-html="renderMarkdown(msg.content)"
        ></div>
        <div v-if="isStreaming" class="assistant-message" v-html="renderMarkdown(streamingText)"></div>
      </div>
    </div>
    <div class="chat-footer">
      <div class="upload-box">
        <input type="file" @change="onFileUpload" />
      </div>
      <div class="input-box">
        <el-input
          v-model="inputText"
          type="textarea"
          rows="3"
          resize="none"
          placeholder="输入你的问题..."
          @keydown.enter.exact.prevent="sendMessage"
        />
        <el-button type="primary" style="margin-top: 8px" @click="sendMessage">发送</el-button>
      </div>
    </div>
    <div
      class="resize-handle"
      @mousedown.stop.prevent="startResizeOrDrag($event, 'resize')"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { fetchEventSource } from '@microsoft/fetch-event-source'
import { marked } from 'marked'
import { Close } from '@element-plus/icons-vue'

const emit = defineEmits(['close'])
const userStore = useUserStore()

const chatHistory = ref([])
const inputText = ref('')
const streamingText = ref('')
const isStreaming = ref(false)
const useWebSearch = ref(false)

const position = reactive({ top: 60, left: 300 })
const size = reactive({ width: 500, height: 400 })
let dragType = null
let startX, startY, startTop, startLeft, startWidth, startHeight

const startResizeOrDrag = (e, type) => {
  dragType = type
  startX = e.clientX
  startY = e.clientY
  startTop = position.top
  startLeft = position.left
  startWidth = size.width
  startHeight = size.height
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', stopDrag)
}

const handleMouseMove = (e) => {
  const dx = e.clientX - startX
  const dy = e.clientY - startY
  if (dragType === 'move') {
    position.top = startTop + dy
    position.left = startLeft + dx
  } else if (dragType === 'resize') {
    size.width = Math.max(300, startWidth + dx)
    size.height = Math.max(200, startHeight + dy)
  }
}

const stopDrag = () => {
  dragType = null
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', stopDrag)
}

const sendMessage = async () => {
  if (!inputText.value.trim()) return
  const message = inputText.value
  inputText.value = ''
  chatHistory.value.push({ role: 'user', content: message })
  streamingText.value = ''
  isStreaming.value = true

  const config = JSON.parse(localStorage.getItem('llm_config') || '{}')
  
  try {
    // 使用 fetchEventSource 而不是普通的 fetch 来处理 SSE
    // const url = new URL('/chat/completions', config.base_url || 'https://api.deepseek.com')
    const url = (config.base_url || 'https://api.deepseek.com') + '/chat/completions'
    fetchEventSource(url.toString(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${config.api_key}`,
      },
      body: JSON.stringify({
        model: config.model_name || 'gpt-3.5-turbo',
        stream: true,
        messages: [
          ...(config.system_prompt ? [{ role: 'system', content: config.system_prompt }] : []),
          ...chatHistory.value,
          { role: 'user', content: message }
        ]
      }),
      onmessage(msg) {
        if (msg.data === '[DONE]') {
          chatHistory.value.push({ role: 'assistant', content: streamingText.value })
          isStreaming.value = false
        } else {
          try {
            const delta = JSON.parse(msg.data).choices[0].delta.content
            if (delta) streamingText.value += delta
          } catch (err) {}
        }
      },
      onopen() {
        // 连接开启
      },
      onerror(err) {
        ElMessage.error('响应失败：' + err.message)
        isStreaming.value = false
      }
    })
  } catch (err) {
    ElMessage.error('连接失败: ' + err.message)
    isStreaming.value = false
  }
}

const onFileUpload = (e) => {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    chatHistory.value.push({ role: 'user', content: `上传了文件：${file.name}\n\n${reader.result}` })
  }
  reader.readAsText(file)
}

onMounted(() => {
  window.addEventListener('resize', syncSize)
})

const syncSize = () => {
  // 防止 resize 后被重置：保持 size 状态
  const el = document.querySelector('.chat-window')
  if (el) {
    const rect = el.getBoundingClientRect()
    size.width = rect.width
    size.height = rect.height
  }
}

onBeforeUnmount(() => {
  chatHistory.value = [] // 清空对话历史
  window.removeEventListener('resize', syncSize)
})

const renderMarkdown = (text) => {
  return marked(text || '')
}
</script>

<style scoped>
.chat-window {
  position: fixed;
  z-index: 9999;
  background-color: var(--card-bg);
  color: var(--text-color);
  border: 1px solid var(--input-border-color);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  user-select: none;
  max-width: 700px;
  min-width: 360px;
}

.chat-header {
  background-color: var(--input-bg);
  padding: 8px 12px;
  font-weight: bold;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: move;
}

.chat-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.chat-controls .el-button {
  padding: 0;
  min-width: 24px;
  width: 24px;
  height: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.chat-controls .el-button :deep(svg) {
  width: 14px;
  height: 14px;
}

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  background-color: var(--bg-color);
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  max-width: 80%;
  padding: 6px 10px;
  border-radius: 10px;
  line-height: 1.5;
  word-break: break-word;
  white-space: pre-wrap;
  font-size: 14px;
}

.user-message {
  align-self: flex-end;
  background-color: var(--el-color-primary);
  color: white;
}

.assistant-message {
  align-self: flex-start;
  background-color: var(--input-bg);
  color: var(--text-color);
}

.chat-footer {
  padding: 10px 12px;
  background-color: var(--bg-color);
  border-top: 1px solid var(--input-border-color);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.upload-box input[type="file"] {
  display: block;
  margin-bottom: 8px;
}

.input-box .el-textarea {
  min-height: 80px !important;
}

.resize-handle {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 16px;
  height: 16px;
  cursor: nwse-resize;
  background: transparent;
}
</style>
