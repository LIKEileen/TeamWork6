<template>
  <div class="dashboard-container">
    <!-- 左侧 Sidebar -->
    <Sidebar />

    <!-- 右侧主内容区域 -->
    <div class="main-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import Sidebar from '@/components/Sidebar.vue'
</script>

<style scoped>
.dashboard-container {
  display: flex;
  height: 100vh;
  width: 100%;
  overflow: hidden;
  background-color: var(--bg-color);
  color: var(--text-color);
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  box-sizing: border-box;
  background-color: var(--bg-color);
  color: var(--text-color);
}
</style>
