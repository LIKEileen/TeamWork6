<template>
  <li class="member-item">
    <div class="avatar">
      <img :src="member.avatarUrl || defaultAvatar" alt="用户头像" />
    </div>
    <div class="info">
      <div class="name">
        <span v-if="member.role === 'creator'" class="tag tag-creator">创建者</span>
        <span v-if="member.role === 'admin'" class="tag tag-admin">管理员</span>
        {{ member.name }}
      </div>
    </div>
  </li>
</template>

<script setup>
import { defineProps } from 'vue'
import defaultAvatar from '@/assets/default_icon.jpg'

const props = defineProps({
  member: {
    type: Object,
    required: true
  }
})
</script>

<style scoped>
.member-item {
  display: flex;
  align-items: center;
  padding: 8px;
  gap: 10px;
}

.avatar {
  width: 30px;
  height: 30px;
  overflow: hidden;
  border-radius: 50%;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.info {
  flex: 1;
}

.name {
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tag {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.tag-creator {
  background-color: #F56C6C; /* 红色 */
  color: #fff;
}

.tag-admin {
  background-color: #409EFF; /* 蓝色 */
  color: #fff;
}
</style>
