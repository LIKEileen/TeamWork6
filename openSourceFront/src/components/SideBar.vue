<template>
  <div
    class="sidebar"
    :class="{ collapsed: isCollapsed }"
    @keydown.esc="closeMenu"
  >
    <!-- 展开按钮 -->
    <div class="toggle-btn" @click="toggleSidebar">
      <el-icon><component :is="isCollapsed ? Expand : Fold" /></el-icon>
    </div>

    <!-- 产品名（展开时显示） -->
    <div class="logo" v-if="!isCollapsed">会易</div>

    <!-- 菜单项 -->
    <el-menu
      :default-active="activeMenu"
      class="nav-menu themed-menu"
      :collapse="isCollapsed"
      router
    >
      <el-menu-item index="/dashboard/board">
        <el-icon><Grid /></el-icon>
        <template #title>组织看板</template>
      </el-menu-item>
      <el-menu-item index="/dashboard/schedule">
        <el-icon><Calendar /></el-icon>
        <template #title>我的日程</template>
      </el-menu-item>
      <el-menu-item index="/dashboard/create">
        <el-icon><Plus /></el-icon>
        <template #title>创建会议</template>
      </el-menu-item>
      <el-menu-item index="/dashboard/org">
        <el-icon><UserFilled /></el-icon>
        <template #title>我的组织</template>
      </el-menu-item>
      <el-menu-item index="/dashboard/settings">
        <el-icon><Setting /></el-icon>
        <template #title>个人设置</template>
      </el-menu-item>
    </el-menu>

    <!-- 大模型协作入口 -->
    <div class="nav-item" @click="toggleAssistant">
      <el-icon><ChatDotRound /></el-icon>
      <span v-if="!isCollapsed">AI 协作</span>
    </div>

    <!-- 用户头像 -->
    <div class="avatar-section" @click.stop="toggleUserMenu">
      <img :src="userAvatar" class="avatar" />
      <transition name="fade">
        <div class="user-menu" v-if="userMenuVisible" ref="menuRef">
          <div class="user-header">{{ userStore.nickname }}（{{ userStore.phone }}）</div>
          <el-button link type="danger" @click="logout">退出</el-button>
        </div>
      </transition>
    </div>

    <!-- 预留大模型聊天窗口 -->
    <ChatAssistant v-if="showAssistant" @close="showAssistant = false" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'
import defaultIcon from '@/assets/default_icon.jpg'
import { logout as logoutApi } from '@/api/auth'
import { IS_DEV } from '@/config'
import { ElMessage } from 'element-plus'
import { Grid, Calendar, Plus, UserFilled, Setting, Fold, Expand, ChatDotRound } from '@element-plus/icons-vue'
import ChatAssistant from '@/components/ChatAssistant.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isCollapsed = ref(false)
const userMenuVisible = ref(false)
const menuRef = ref(null)
const showAssistant = ref(false)

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
  closeMenu()
}

const toggleUserMenu = () => {
  userMenuVisible.value = !userMenuVisible.value
}

const closeMenu = () => {
  userMenuVisible.value = false
}

const onClickOutside = (e) => {
  if (userMenuVisible.value && menuRef.value && !menuRef.value.contains(e.target)) {
    closeMenu()
  }
}

const toggleAssistant = () => {
  showAssistant.value = !showAssistant.value
}

watch(() => route.path, () => {
  closeMenu()
})

const userAvatar = computed(() => {
  return userStore.avatar || defaultIcon
})

const activeMenu = computed(() => route.path)

const logout = async () => {
  if (IS_DEV) {
    userStore.clearUser()
    ElMessage.success('已退出（mock 模拟）')
    router.push('/login')
    return
  }
  try {
    const { data } = await logoutApi()
    if (data.code === 200) {
      userStore.clearUser()
      ElMessage.success('退出成功')
      router.push('/login')
    } else {
      ElMessage.error(data.message || '退出失败')
    }
  } catch (err) {
    ElMessage.error('网络异常，退出失败')
  }
}

onMounted(() => {
  document.addEventListener('click', onClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', onClickOutside)
})
</script>

<style scoped>
.sidebar {
  width: 220px;
  background-color: var(--card-bg);
  color: var(--text-color);
  height: 100vh;
  border-right: 1px solid var(--input-border-color);
  display: flex;
  flex-direction: column;
  position: relative;
  transition: width 0.3s ease;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 64px;
}

.toggle-btn {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-bottom: 1px solid var(--input-border-color);
}

.logo {
  text-align: center;
  font-size: 18px;
  font-weight: bold;
  padding: 12px 0;
  color: var(--text-color);
  border-bottom: 1px solid var(--input-border-color);
}

.nav-menu {
  flex: 1;
  border-right: none;
  transition: all 0.2s ease;
  background-color: var(--card-bg); /* ✅ 适配主题 */
}

.nav-menu.themed-menu :deep(.el-menu-item) {
  background-color: var(--card-bg);
  color: var(--text-color);
}

.nav-menu.themed-menu :deep(.el-menu-item.is-active) {
  background-color: var(--input-bg);
  color: var(--el-color-primary);
}

.nav-menu.themed-menu :deep(.el-menu-item:hover) {
  background-color: var(--input-bg);
}

.avatar-section {
  padding: 12px;
  text-align: center;
  position: relative;
  transition: all 0.3s;
  background-color: var(--card-bg); /* ✅ 确保下方底色一致 */
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--input-border-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.avatar:hover {
  border-color: var(--el-color-primary);
}

.user-menu {
  position: absolute;
  bottom: 60px;
  left: 50%;
  transform: translateX(-50%);
  background-color: var(--card-bg);
  border: 1px solid var(--input-border-color);
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  padding: 8px 12px;
  z-index: 10;
  min-width: 140px;
  text-align: center;
  color: var(--text-color);
}

.user-header {
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: bold;
  word-break: break-word;
  line-height: 1.4;
}

.user-header span {
  display: block;
  font-weight: normal;
  font-size: 13px;
  margin-top: 4px;
  opacity: 0.8;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  cursor: pointer;
  color: var(--text-color);
  background-color: var(--card-bg); /* ✅ 保持底部 AI 区一致 */
  transition: background-color 0.3s ease, padding 0.3s ease;
}

.sidebar.collapsed .nav-item span {
  display: none;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 12px 0;
}

.nav-item:hover {
  background-color: var(--input-bg);
}
</style>
