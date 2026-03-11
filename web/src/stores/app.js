import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 主题
  const theme = ref(localStorage.getItem('theme') || 'light')
  
  // 侧边栏状态
  const sidebarCollapsed = ref(false)
  
  // 面包屑导航
  const breadcrumb = ref([])
  
  // 设置主题
  const setTheme = (newTheme) => {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    document.documentElement.className = newTheme === 'dark' ? 'dark' : ''
  }
  
  // 切换侧边栏
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
  
  // 设置面包屑
  const setBreadcrumb = (items) => {
    breadcrumb.value = items
  }
  
  return {
    theme,
    sidebarCollapsed,
    breadcrumb,
    setTheme,
    toggleSidebar,
    setBreadcrumb
  }
})
