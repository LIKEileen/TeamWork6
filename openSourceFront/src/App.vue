<!-- <script setup>
import HelloWorld from './components/HelloWorld.vue'
</script> -->

<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
  import { watchEffect } from 'vue'
  import { useUserStore } from '@/store/user'

  const userStore = useUserStore()

  watchEffect(() => {
    document.body.setAttribute('data-theme', userStore.theme || 'light')
})
</script>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
