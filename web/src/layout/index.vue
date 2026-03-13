<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="sidebarWidth" class="sidebar">
      <div class="logo-container">
        <div class="logo">
          <el-icon size="24" color="#409EFF"><TrendCharts /></el-icon>
          <span v-show="!sidebarCollapsed" class="logo-text">水质监控</span>
        </div>
      </div>
      
      <el-menu
        :default-active="$route.path"
        :collapse="sidebarCollapsed"
        :unique-opened="true"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>
        
        <el-menu-item index="/records">
          <el-icon><List /></el-icon>
          <template #title>数据管理</template>
        </el-menu-item>
        
        <el-menu-item index="/query">
          <el-icon><Search /></el-icon>
          <template #title>高级查询</template>
        </el-menu-item>
        
        <el-menu-item index="/alerts">
          <el-icon><Warning /></el-icon>
          <template #title>报警监控</template>
        </el-menu-item>
        
        <el-menu-item index="/ai-chat">
          <el-icon><ChatDotRound /></el-icon>
          <template #title>AI智能助手</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部栏 -->
      <el-header height="60px" class="header">
        <div class="header-left">
          <el-button
            type="text"
            :icon="sidebarCollapsed ? Expand : Fold"
            @click="toggleSidebar"
            class="sidebar-toggle"
          />
          
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentRoute.meta?.title">
              {{ currentRoute.meta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <!-- 主题切换 -->
          <el-button
            type="text"
            :icon="Sunny"
            @click="toggleTheme"
            class="theme-toggle"
          />
          
          <!-- 用户信息 -->
          <el-dropdown @command="handleUserAction">
            <div class="user-info">
              <el-avatar :size="32" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
              <span class="username">管理员</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="settings">系统设置</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主要内容 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  DataBoard,
  List,
  Search,
  Warning,
  Expand,
  Fold,
  Sunny,
  Moon,
  ArrowDown,
  TrendCharts
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 简单的状态管理
const sidebarCollapsed = ref(false)
const isDark = ref(false)

const currentRoute = computed(() => route)
const sidebarWidth = computed(() => {
  return sidebarCollapsed.value ? '64px' : '200px'
})

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  ElMessage.success(isDark.value ? '已切换到深色主题' : '已切换到浅色主题')
}

const handleUserAction = (command) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人信息功能待开发')
      break
    case 'settings':
      ElMessage.info('系统设置功能待开发')
      break
    case 'logout':
      ElMessage.success('已退出登录')
      router.push('/login')
      break
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  background-color: #f5f5f5;
}

.sidebar {
  background-color: #fff;
  border-right: 1px solid #e6e6e6;
  transition: width 0.3s ease;
  overflow: hidden;
  
  .logo-container {
    height: 60px;
    display: flex;
    align-items: center;
    padding: 0 16px;
    border-bottom: 1px solid #e6e6e6;
    
    .logo {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .logo-text {
        font-size: 18px;
        font-weight: 600;
        color: #333;
        white-space: nowrap;
      }
    }
  }
  
  .el-menu {
    border-right: none;
    padding: 8px 0;
  }
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;
    
    .sidebar-toggle {
      font-size: 18px;
      color: #666;
      
      &:hover {
        color: #409eff;
      }
    }
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;
    
    .theme-toggle {
      font-size: 18px;
      color: #666;
      
      &:hover {
        color: #409eff;
      }
    }
    
    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      padding: 4px 8px;
      border-radius: 4px;
      transition: background-color 0.3s ease;
      
      &:hover {
        background-color: #f5f5f5;
      }
      
      .username {
        font-size: 13px;
        color: #666;
      }
    }
  }
}

.main-content {
  padding: 24px;
  background-color: #f5f5f5;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
