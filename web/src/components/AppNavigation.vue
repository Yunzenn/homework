<template>
  <div class="app-navigation">
    <el-menu 
      :default-active="activeIndex" 
      mode="horizontal" 
      :router="true"
      class="nav-menu"
    >
      <el-menu-item index="/dashboard">
        <el-icon><House /></el-icon>
        <span>主界面</span>
      </el-menu-item>
      
      <el-menu-item index="/records">
        <el-icon><Document /></el-icon>
        <span>数据查看</span>
      </el-menu-item>
      
      <el-menu-item index="/batch-input">
        <el-icon><Upload /></el-icon>
        <span>数据录入</span>
      </el-menu-item>
      
      <el-menu-item index="/query">
        <el-icon><Search /></el-icon>
        <span>数据查询</span>
      </el-menu-item>
      
      <div class="nav-right">
        <el-dropdown @command="handleUserMenu" class="user-dropdown">
          <span class="user-info">
            <el-icon><User /></el-icon>
            {{ user?.username || '管理员' }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon> 个人资料
              </el-dropdown-item>
              <el-dropdown-item command="settings">
                <el-icon><Setting /></el-icon> 系统设置
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <el-icon><SwitchButton /></el-icon> 退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-menu>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  House, 
  Document, 
  Upload, 
  Search, 
  User, 
  ArrowDown, 
  Setting, 
  SwitchButton 
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const user = computed(() => authStore.user)
const activeIndex = computed(() => route.path)

// 用户菜单处理
const handleUserMenu = async (command) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人资料功能开发中...')
      break
    case 'settings':
      ElMessage.info('系统设置功能开发中...')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm(
          '确定要退出登录吗？',
          '退出确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        await authStore.logout()
        ElMessage.success('已退出登录')
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('退出失败')
        }
      }
      break
  }
}
</script>

<style scoped>
.app-navigation {
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.nav-menu {
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.nav-right {
  margin-left: auto;
  display: flex;
  align-items: center;
}

.user-dropdown {
  margin-left: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-menu {
    padding: 0 10px;
  }
  
  .user-info span {
    display: none;
  }
}
</style>
