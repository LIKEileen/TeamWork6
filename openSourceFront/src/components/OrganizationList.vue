<template>
    <ul class="org-list">
      <li
        v-for="org in organizations"
        :key="org.id"
        @click="toggleExpand(org.id)"
        @contextmenu.prevent="$emit('context', $event, org)"
        :class="{ active: expandedOrgId === org.id }"
      >
        <span class="arrow" :class="{ expanded: expandedOrgId === org.id }">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
            <path d="M8 5v14l11-7z" />
          </svg>
        </span>
        {{ org.name }}
  
        <transition name="fade-expand">
          <ul v-if="expandedOrgId === org.id" class="member-list">
            <MemberItem
              v-for="member in org.members"
              :key="member.id"
              :member="member"
            />
          </ul>
        </transition>
      </li>
    </ul>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import MemberItem from './MemberItem.vue'
  
  const props = defineProps({
    organizations: Array
  })
  const emit = defineEmits(['context'])
  
  const expandedOrgId = ref(null)
  const toggleExpand = (id) => {
    expandedOrgId.value = expandedOrgId.value === id ? null : id
  }
  </script>
  
  <style scoped>
  .org-list {
    list-style: none;
    padding-left: 0;
  }
  
  .org-list li {
    cursor: pointer;
    padding: 8px 12px;
    border-bottom: 1px solid #eee;
    user-select: none;
    font-weight: bold;
  }
  
  .org-list li.active {
    background-color: #f0f4f8;
  }
  
  .member-list {
    margin-top: 6px;
    margin-left: 24px;
    padding-left: 4px;
  }
  
  .arrow {
    display: inline-block;
    transition: transform 0.2s ease;
    margin-right: 6px;
    color: #666;
  }
  .arrow.expanded {
    transform: rotate(90deg);
  }
  
  /* 过渡动画 */
  .fade-expand-enter-from,
  .fade-expand-leave-to {
    max-height: 0;
    opacity: 0;
    transform: scaleY(0.95);
  }
  .fade-expand-enter-to,
  .fade-expand-leave-from {
    max-height: 500px;
    opacity: 1;
    transform: scaleY(1);
  }
  .fade-expand-enter-active,
  .fade-expand-leave-active {
    transition: all 0.2s ease;
    overflow: hidden;
  }
  </style>
  