import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const refreshToken = ref(localStorage.getItem('refreshToken') || null)
  const permissions = ref([])
  const roles = ref([])
  const loading = ref(false)
  const loginError = ref('')

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.is_staff || false)
  const userPermissions = computed(() => permissions.value)
  const userRoles = computed(() => roles.value)

  // 检查权限
  const hasPermission = (permission) => {
    if (isAdmin.value) return true
    return permissions.value.includes(permission) || permissions.value.includes('*')
  }

  // 检查角色
  const hasRole = (role) => {
    if (isAdmin.value) return true
    return roles.value.some(r => r.code === role)
  }

  // 检查任意权限
  const hasAnyPermission = (permissionList) => {
    if (isAdmin.value) return true
    return permissionList.some(permission => hasPermission(permission))
  }

  // 检查任意角色
  const hasAnyRole = (roleList) => {
    if (isAdmin.value) return true
    return roleList.some(role => hasRole(role))
  }

  // 登录
  const login = async (credentials) => {
    try {
      loading.value = true
      loginError.value = ''
      
      const response = await authApi.login(credentials)
      
      // 保存用户信息和token
      user.value = response.user
      token.value = response.token
      permissions.value = response.user.permissions || []
      roles.value = response.user.roles || []
      
      // 根据记住密码选择存储位置
      const storage = credentials.remember ? localStorage : sessionStorage
      storage.setItem('token', response.token)
      storage.setItem('user', JSON.stringify(response.user))
      storage.setItem('permissions', JSON.stringify(response.user.permissions || []))
      storage.setItem('roles', JSON.stringify(response.user.roles || []))
      
      // 如果有refresh token，也保存
      if (response.refreshToken) {
        refreshToken.value = response.refreshToken
        storage.setItem('refreshToken', response.refreshToken)
      }
      
      return { success: true, data: response }
    } catch (error) {
      loginError.value = error.message || '登录失败'
      return { success: false, error: error.message || '登录失败' }
    } finally {
      loading.value = false
    }
  }

  // 注册
  const register = async (userData) => {
    try {
      loading.value = true
      
      const response = await authApi.register(userData)
      
      return { success: true, data: response }
    } catch (error) {
      return { success: false, error: error.message || '注册失败' }
    } finally {
      loading.value = false
    }
  }

  // 退出登录
  const logout = async () => {
    try {
      if (token.value) {
        await authApi.logout()
      }
    } catch (error) {
      console.error('退出登录失败:', error)
    } finally {
      // 清除状态
      user.value = null
      token.value = null
      refreshToken.value = null
      permissions.value = []
      roles.value = []
      loginError.value = ''
      
      // 清除localStorage
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
      localStorage.removeItem('permissions')
      localStorage.removeItem('roles')
      
      // 跳转到登录页
      router.push('/enhanced-login')
    }
  }

  // 刷新token
  const refreshAuthToken = async () => {
    try {
      if (!refreshToken.value) {
        throw new Error('No refresh token')
      }
      
      const response = await authApi.refreshToken(refreshToken.value)
      
      token.value = response.token
      localStorage.setItem('token', response.token)
      
      return response.token
    } catch (error) {
      // 刷新失败，退出登录
      await logout()
      throw error
    }
  }

  // 获取用户信息
  const fetchUserProfile = async () => {
    try {
      loading.value = true
      
      const response = await authApi.getProfile()
      
      user.value = response
      permissions.value = response.permissions || []
      roles.value = response.roles || []
      
      // 更新localStorage
      localStorage.setItem('user', JSON.stringify(response))
      localStorage.setItem('permissions', JSON.stringify(response.permissions || []))
      localStorage.setItem('roles', JSON.stringify(response.roles || []))
      
      return response
    } catch (error) {
      console.error('获取用户信息失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新用户信息
  const updateUserProfile = async (userData) => {
    try {
      loading.value = true
      
      const response = await authApi.updateProfile(userData)
      
      user.value = { ...user.value, ...response }
      localStorage.setItem('user', JSON.stringify(user.value))
      
      return response
    } catch (error) {
      console.error('更新用户信息失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 修改密码
  const changePassword = async (passwordData) => {
    try {
      loading.value = true
      
      const response = await authApi.changePassword(passwordData)
      
      return { success: true, data: response }
    } catch (error) {
      return { success: false, error: error.message || '修改密码失败' }
    } finally {
      loading.value = false
    }
  }

  // 忘记密码
  const forgotPassword = async (email) => {
    try {
      loading.value = true
      
      const response = await authApi.forgotPassword(email)
      
      return { success: true, data: response }
    } catch (error) {
      return { success: false, error: error.message || '发送重置邮件失败' }
    } finally {
      loading.value = false
    }
  }

  // 重置密码
  const resetPassword = async (token, newPassword) => {
    try {
      loading.value = true
      
      const response = await authApi.resetPassword(token, newPassword)
      
      return { success: true, data: response }
    } catch (error) {
      return { success: false, error: error.message || '重置密码失败' }
    } finally {
      loading.value = false
    }
  }

  // 上传头像
  const uploadAvatar = async (file) => {
    try {
      loading.value = true
      
      const response = await authApi.uploadAvatar(file)
      
      if (user.value) {
        user.value.avatar = response.avatar
        localStorage.setItem('user', JSON.stringify(user.value))
      }
      
      return { success: true, data: response }
    } catch (error) {
      return { success: false, error: error.message || '上传头像失败' }
    } finally {
      loading.value = false
    }
  }

  // 初始化用户状态（从localStorage恢复）
  const initializeAuth = () => {
    try {
      const savedUser = localStorage.getItem('user')
      const savedPermissions = localStorage.getItem('permissions')
      const savedRoles = localStorage.getItem('roles')
      
      if (savedUser) {
        user.value = JSON.parse(savedUser)
      }
      
      if (savedPermissions) {
        permissions.value = JSON.parse(savedPermissions)
      }
      
      if (savedRoles) {
        roles.value = JSON.parse(savedRoles)
      }
    } catch (error) {
      console.error('初始化认证状态失败:', error)
      // 清除损坏的数据
      logout()
    }
  }

  // 检查token是否过期
  const isTokenExpired = () => {
    if (!token.value) return true
    
    try {
      // 简单的token过期检查（实际应该解析JWT）
      const payload = JSON.parse(atob(token.value.split('.')[1]))
      const currentTime = Date.now() / 1000
      
      return payload.exp < currentTime
    } catch (error) {
      return true
    }
  }

  // 清除错误
  const clearError = () => {
    loginError.value = ''
  }

  return {
    // 状态
    user,
    token,
    refreshToken,
    permissions,
    roles,
    loading,
    loginError,
    
    // 计算属性
    isAuthenticated,
    isAdmin,
    userPermissions,
    userRoles,
    
    // 方法
    hasPermission,
    hasRole,
    hasAnyPermission,
    hasAnyRole,
    login,
    register,
    logout,
    refreshAuthToken,
    fetchUserProfile,
    updateUserProfile,
    changePassword,
    forgotPassword,
    resetPassword,
    uploadAvatar,
    initializeAuth,
    isTokenExpired,
    clearError
  }
})
