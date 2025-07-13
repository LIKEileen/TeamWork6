import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './assets/theme.css'

const app = createApp(App)
app.use(router)
app.use(createPinia())
app.use(ElementPlus)
app.mount('#app')

// router.afterEach((to) => {
//     // 优先取路由 meta.title，没有则用默认标题
//     document.title = to.meta.title || 'Ciallo～ (∠・ω< )⌒★';
//   });
