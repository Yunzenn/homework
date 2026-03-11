<template>
  <div class="simple-layout">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-left">
        <h1 class="logo">水质监控系统</h1>
      </div>
      <div class="header-right">
        <button class="theme-btn" @click="toggleTheme">🌙</button>
        <div class="user-info">
          <span>管理员</span>
        </div>
      </div>
    </header>

    <!-- 主体内容区 -->
    <div class="main-container">
      <!-- 侧边栏 -->
      <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="menu-toggle" @click="toggleSidebar">
          <span>☰</span>
        </div>
        <nav class="menu">
          <a href="#" class="menu-item" :class="{ active: currentPath === '/dashboard' }" @click="navigate('/dashboard')">
            <span class="icon">📊</span>
            <span class="text" v-show="!sidebarCollapsed">仪表盘</span>
          </a>
          <a href="#" class="menu-item" :class="{ active: currentPath === '/records' }" @click="navigate('/records')">
            <span class="icon">📝</span>
            <span class="text" v-show="!sidebarCollapsed">数据管理</span>
          </a>
          <a href="#" class="menu-item" :class="{ active: currentPath === '/batch-input' }" @click="navigate('/batch-input')">
            <span class="icon">📥</span>
            <span class="text" v-show="!sidebarCollapsed">批量输入</span>
          </a>
          <a href="#" class="menu-item" :class="{ active: currentPath === '/query' }" @click="navigate('/query')">
            <span class="icon">🔍</span>
            <span class="text" v-show="!sidebarCollapsed">高级查询</span>
          </a>
          <a href="#" class="menu-item" :class="{ active: currentPath === '/analysis' }" @click="navigate('/analysis')">
            <span class="icon">📊</span>
            <span class="text" v-show="!sidebarCollapsed">数据分析</span>
          </a>
          <a href="#" class="menu-item" :class="{ active: currentPath === '/test-form' }" @click="navigate('/test-form')">
            <span class="icon">🧪</span>
            <span class="text" v-show="!sidebarCollapsed">测试表单</span>
          </a>
          <a href="#" class="menu-item" :class="{ active: currentPath === '/api-test' }" @click="navigate('/api-test')">
            <span class="icon">🔧</span>
            <span class="text" v-show="!sidebarCollapsed">API测试</span>
          </a>
          <a href="#" class="menu-item" :class="{ active: currentPath === '/alerts' }" @click="navigate('/alerts')">
            <span class="icon">⚠️</span>
            <span class="text" v-show="!sidebarCollapsed">报警监控</span>
          </a>
        </nav>
      </aside>

      <!-- 内容区域 -->
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSimpleStore } from '@/stores/simple'

const router = useRouter()
const route = useRoute()
const simpleStore = useSimpleStore()

const sidebarCollapsed = ref(false)
const currentPath = ref('/dashboard')
const isDark = ref(false)

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
  simpleStore.increment()
  console.log('Pinia store count:', simpleStore.count)
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  simpleStore.setMessage(`主题已切换到${isDark.value ? '深色' : '浅色'}模式`)
}

const navigate = (path) => {
  currentPath.value = path
  router.push(path)
}

onMounted(() => {
  currentPath.value = route.path
  console.log('Pinia store message:', simpleStore.message)
})
</script>

<style scoped>
.simple-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.header {
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-left .logo {
  font-size: 20px;
  font-weight: 600;
  color: #1890ff;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.theme-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.theme-btn:hover {
  background-color: #f5f5f5;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
}

.main-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sidebar {
  width: 200px;
  background: #fff;
  border-right: 1px solid #e6e6e6;
  transition: width 0.3s ease;
  display: flex;
  flex-direction: column;
}

.sidebar.collapsed {
  width: 60px;
}

.menu-toggle {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-bottom: 1px solid #e6e6e6;
  font-size: 18px;
}

.menu-toggle:hover {
  background-color: #f5f5f5;
}

.menu {
  flex: 1;
  padding: 10px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: #666;
  text-decoration: none;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.menu-item:hover {
  background-color: #f5f5f5;
  color: #1890ff;
}

.menu-item.active {
  background-color: #e6f7ff;
  color: #1890ff;
  border-left-color: #1890ff;
}

.collapsed .menu-item {
  justify-content: center;
  padding: 12px 0;
}

.menu-item .icon {
  font-size: 16px;
  margin-right: 10px;
  min-width: 16px;
}

.collapsed .menu-item .icon {
  margin-right: 0;
}

.menu-item .text {
  white-space: nowrap;
}

.content {
  flex: 1;
  background: #f5f5f5;
  overflow-y: auto;
  padding: 20px;
}

/* 深色主题 */
.dark .simple-layout {
  background-color: #141414;
  color: #fff;
}

.dark .header {
  background: #1f1f1f;
  border-bottom-color: #4c4d4f;
}

.dark .sidebar {
  background: #1f1f1f;
  border-right-color: #4c4d4f;
}

.dark .menu-toggle:hover,
.dark .menu-item:hover {
  background-color: #2a2a2a;
}

.dark .menu-item.active {
  background-color: #111b26;
  color: #1890ff;
}

.dark .content {
  background: #141414;
}
</style>
