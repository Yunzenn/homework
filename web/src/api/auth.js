import { request } from '@/utils/request'

// 认证相关API
export const authApi = {
  // 用户登录
  login: (credentials) => {
    return request({
      url: '/auth/login/',
      method: 'POST',
      data: credentials
    })
  },

  // 用户注册
  register: (userData) => {
    return request({
      url: '/auth/register',
      method: 'POST',
      data: userData
    })
  },

  // 用户退出
  logout: () => {
    return request({
      url: '/auth/logout',
      method: 'POST'
    })
  },

  // 刷新token
  refreshToken: (refreshToken) => {
    return request({
      url: '/auth/refresh',
      method: 'POST',
      data: { refresh_token: refreshToken }
    })
  },

  // 获取用户资料
  getProfile: () => {
    return request({
      url: '/profile',
      method: 'GET'
    })
  },

  // 更新用户资料
  updateProfile: (userData) => {
    return request({
      url: '/profile',
      method: 'PUT',
      data: userData
    })
  },

  // 修改密码
  changePassword: (passwordData) => {
    return request({
      url: '/auth/change-password',
      method: 'POST',
      data: passwordData
    })
  },

  // 忘记密码
  forgotPassword: (email) => {
    return request({
      url: '/auth/forgot-password',
      method: 'POST',
      data: { email }
    })
  },

  // 重置密码
  resetPassword: (token, newPassword) => {
    return request({
      url: '/auth/reset-password',
      method: 'POST',
      data: {
        token,
        new_password: newPassword,
        confirm_password: newPassword
      }
    })
  },

  // 上传头像
  uploadAvatar: (file) => {
    const formData = new FormData()
    formData.append('avatar', file)
    
    return request({
      url: '/profile/avatar',
      method: 'POST',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}

// 用户管理API（管理员）
export const userApi = {
  // 获取用户列表
  getUsers: (params) => {
    return request({
      url: '/users',
      method: 'GET',
      params
    })
  },

  // 获取用户详情
  getUser: (id) => {
    return request({
      url: `/users/${id}`,
      method: 'GET'
    })
  },

  // 创建用户
  createUser: (userData) => {
    return request({
      url: '/users',
      method: 'POST',
      data: userData
    })
  },

  // 更新用户
  updateUser: (id, userData) => {
    return request({
      url: `/users/${id}`,
      method: 'PUT',
      data: userData
    })
  },

  // 删除用户
  deleteUser: (id) => {
    return request({
      url: `/users/${id}`,
      method: 'DELETE'
    })
  },

  // 分配角色
  assignRole: (userId, roleId) => {
    return request({
      url: `/users/${userId}/role`,
      method: 'PUT',
      data: { role_id: roleId }
    })
  },

  // 更新用户状态
  updateUserStatus: (userId, isActive, lockReason = '') => {
    return request({
      url: `/users/${userId}/status`,
      method: 'PUT',
      data: {
        is_active: isActive,
        lock_reason: lockReason
      }
    })
  }
}

// 角色管理API（管理员）
export const roleApi = {
  // 获取角色列表
  getRoles: (params) => {
    return request({
      url: '/roles',
      method: 'GET',
      params
    })
  },

  // 获取角色详情
  getRole: (id) => {
    return request({
      url: `/roles/${id}`,
      method: 'GET'
    })
  },

  // 创建角色
  createRole: (roleData) => {
    return request({
      url: '/roles',
      method: 'POST',
      data: roleData
    })
  },

  // 更新角色
  updateRole: (id, roleData) => {
    return request({
      url: `/roles/${id}`,
      method: 'PUT',
      data: roleData
    })
  },

  // 删除角色
  deleteRole: (id) => {
    return request({
      url: `/roles/${id}`,
      method: 'DELETE'
    })
  },

  // 获取权限列表
  getPermissions: () => {
    return request({
      url: '/permissions',
      method: 'GET'
    })
  }
}

// 日志管理API（管理员）
export const logApi = {
  // 获取登录日志
  getLoginLogs: (params) => {
    return request({
      url: '/logs/login',
      method: 'GET',
      params
    })
  },

  // 获取操作日志
  getOperationLogs: (params) => {
    return request({
      url: '/logs/operation',
      method: 'GET',
      params
    })
  },

  // 获取用户操作日志
  getUserOperationLogs: (userId, params) => {
    return request({
      url: `/logs/user/${userId}`,
      method: 'GET',
      params
    })
  }
}
