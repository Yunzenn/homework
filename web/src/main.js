import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 创建应用实例
const app = createApp(App)

// 创建Pinia实例
const pinia = createPinia()

// 按正确顺序注册插件
app.use(pinia)  // 先注册Pinia
app.use(router)
app.use(ElementPlus)

// 挂载应用
app.mount('#app')
