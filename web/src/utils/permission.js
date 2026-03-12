import { useAuthStore } from '@/stores/auth'

// 权限检查函数
export const checkPermission = (permission) => {
  const authStore = useAuthStore()
  return authStore.hasPermission(permission)
}

// 角色检查函数
export const checkRole = (role) => {
  const authStore = useAuthStore()
  return authStore.hasRole(role)
}

// 检查任意权限
export const checkAnyPermission = (permissions) => {
  const authStore = useAuthStore()
  return authStore.hasAnyPermission(permissions)
}

// 检查任意角色
export const checkAnyRole = (roles) => {
  const authStore = useAuthStore()
  return authStore.hasAnyRole(roles)
}

// 权限指令
export const permissionDirective = {
  mounted(el, binding) {
    const { value } = binding
    
    if (!value) {
      console.warn('权限指令需要指定权限值')
      return
    }
    
    const hasPermission = checkPermission(value)
    
    if (!hasPermission) {
      // 隐藏元素
      el.style.display = 'none'
      // 或者移除元素
      // el.parentNode && el.parentNode.removeChild(el)
    }
  },
  
  updated(el, binding) {
    const { value, oldValue } = binding
    
    if (value !== oldValue) {
      const hasPermission = checkPermission(value)
      
      if (!hasPermission) {
        el.style.display = 'none'
      } else {
        el.style.display = ''
      }
    }
  }
}

// 角色指令
export const roleDirective = {
  mounted(el, binding) {
    const { value } = binding
    
    if (!value) {
      console.warn('角色指令需要指定角色值')
      return
    }
    
    const hasRole = checkRole(value)
    
    if (!hasRole) {
      el.style.display = 'none'
    }
  },
  
  updated(el, binding) {
    const { value, oldValue } = binding
    
    if (value !== oldValue) {
      const hasRole = checkRole(value)
      
      if (!hasRole) {
        el.style.display = 'none'
      } else {
        el.style.display = ''
      }
    }
  }
}

// 任意权限指令
export const anyPermissionDirective = {
  mounted(el, binding) {
    const { value } = binding
    
    if (!value || !Array.isArray(value)) {
      console.warn('任意权限指令需要指定权限数组')
      return
    }
    
    const hasAnyPermission = checkAnyPermission(value)
    
    if (!hasAnyPermission) {
      el.style.display = 'none'
    }
  },
  
  updated(el, binding) {
    const { value, oldValue } = binding
    
    if (value !== oldValue && Array.isArray(value)) {
      const hasAnyPermission = checkAnyPermission(value)
      
      if (!hasAnyPermission) {
        el.style.display = 'none'
      } else {
        el.style.display = ''
      }
    }
  }
}

// 任意角色指令
export const anyRoleDirective = {
  mounted(el, binding) {
    const { value } = binding
    
    if (!value || !Array.isArray(value)) {
      console.warn('任意角色指令需要指定角色数组')
      return
    }
    
    const hasAnyRole = checkAnyRole(value)
    
    if (!hasAnyRole) {
      el.style.display = 'none'
    }
  },
  
  updated(el, binding) {
    const { value, oldValue } = binding
    
    if (value !== oldValue && Array.isArray(value)) {
      const hasAnyRole = checkAnyRole(value)
      
      if (!hasAnyRole) {
        el.style.display = 'none'
      } else {
        el.style.display = ''
      }
    }
  }
}

// 权限常量
export const PERMISSIONS = {
  // 仪表盘权限
  DASHBOARD_VIEW: 'dashboard:view',
  
  // 数据管理权限
  DATA_VIEW: 'data:view',
  DATA_CREATE: 'data:create',
  DATA_UPDATE: 'data:update',
  DATA_DELETE: 'data:delete',
  DATA_IMPORT: 'data:import',
  DATA_EXPORT: 'data:export',
  
  // 报警管理权限
  ALERT_VIEW: 'alert:view',
  ALERT_CONFIRM: 'alert:confirm',
  ALERT_CONFIG: 'alert:config',
  
  // 用户管理权限
  USER_VIEW: 'user:view',
  USER_CREATE: 'user:create',
  USER_UPDATE: 'user:update',
  USER_DELETE: 'user:delete',
  USER_ROLE: 'user:role',
  
  // 角色管理权限
  ROLE_VIEW: 'role:view',
  ROLE_CREATE: 'role:create',
  ROLE_UPDATE: 'role:update',
  ROLE_DELETE: 'role:delete',
  
  // 日志管理权限
  LOG_VIEW: 'log:view',
  
  // 数据分析权限
  ANALYSIS_VIEW: 'analysis:view'
}

// 角色常量
export const ROLES = {
  ADMIN: 'admin',
  SUPERVISOR: 'supervisor',
  OPERATOR: 'operator',
  VIEWER: 'viewer'
}

// 权限组
export const PERMISSION_GROUPS = {
  // 数据管理权限组
  DATA_MANAGEMENT: [
    PERMISSIONS.DATA_VIEW,
    PERMISSIONS.DATA_CREATE,
    PERMISSIONS.DATA_UPDATE,
    PERMISSIONS.DATA_DELETE,
    PERMISSIONS.DATA_IMPORT,
    PERMISSIONS.DATA_EXPORT
  ],
  
  // 用户管理权限组
  USER_MANAGEMENT: [
    PERMISSIONS.USER_VIEW,
    PERMISSIONS.USER_CREATE,
    PERMISSIONS.USER_UPDATE,
    PERMISSIONS.USER_DELETE,
    PERMISSIONS.USER_ROLE
  ],
  
  // 角色管理权限组
  ROLE_MANAGEMENT: [
    PERMISSIONS.ROLE_VIEW,
    PERMISSIONS.ROLE_CREATE,
    PERMISSIONS.ROLE_UPDATE,
    PERMISSIONS.ROLE_DELETE
  ],
  
  // 报警管理权限组
  ALERT_MANAGEMENT: [
    PERMISSIONS.ALERT_VIEW,
    PERMISSIONS.ALERT_CONFIRM,
    PERMISSIONS.ALERT_CONFIG
  ]
}

// 权限检查工具函数
export const canViewDashboard = () => checkPermission(PERMISSIONS.DASHBOARD_VIEW)
export const canManageData = () => checkAnyPermission(PERMISSION_GROUPS.DATA_MANAGEMENT)
export const canCreateData = () => checkPermission(PERMISSIONS.DATA_CREATE)
export const canUpdateData = () => checkPermission(PERMISSIONS.DATA_UPDATE)
export const canDeleteData = () => checkPermission(PERMISSIONS.DATA_DELETE)
export const canImportData = () => checkPermission(PERMISSIONS.DATA_IMPORT)
export const canExportData = () => checkPermission(PERMISSIONS.DATA_EXPORT)
export const canManageUsers = () => checkAnyPermission(PERMISSION_GROUPS.USER_MANAGEMENT)
export const canManageRoles = () => checkAnyPermission(PERMISSION_GROUPS.ROLE_MANAGEMENT)
export const canViewLogs = () => checkPermission(PERMISSIONS.LOG_VIEW)
export const canManageAlerts = () => checkAnyPermission(PERMISSION_GROUPS.ALERT_MANAGEMENT)
export const canViewAnalysis = () => checkPermission(PERMISSIONS.ANALYSIS_VIEW)

// 角色检查工具函数
export const isAdmin = () => checkRole(ROLES.ADMIN)
export const isSupervisor = () => checkRole(ROLES.SUPERVISOR)
export const isOperator = () => checkRole(ROLES.OPERATOR)
export const isViewer = () => checkRole(ROLES.VIEWER)

// 获取用户权限列表
export const getUserPermissions = () => {
  const authStore = useAuthStore()
  return authStore.userPermissions
}

// 获取用户角色列表
export const getUserRoles = () => {
  const authStore = useAuthStore()
  return authStore.userRoles
}

// 检查是否为管理员或主管
export const isManager = () => checkAnyRole([ROLES.ADMIN, ROLES.SUPERVISOR])

// 检查是否为操作员或以上
export const isOperatorOrAbove = () => checkAnyRole([ROLES.ADMIN, ROLES.SUPERVISOR, ROLES.OPERATOR])

// 检查是否为只读用户
export const isReadOnly = () => checkRole(ROLES.VIEWER)

// 权限映射表（用于菜单显示）
export const MENU_PERMISSIONS = {
  dashboard: PERMISSIONS.DASHBOARD_VIEW,
  records: PERMISSIONS.DATA_VIEW,
  batchInput: PERMISSIONS.DATA_CREATE,
  query: PERMISSIONS.DATA_VIEW,
  alert: PERMISSIONS.ALERT_VIEW,
  analysis: PERMISSIONS.ANALYSIS_VIEW,
  userManagement: PERMISSIONS.USER_VIEW,
  roleManagement: PERMISSIONS.ROLE_VIEW,
  auditLog: PERMISSIONS.LOG_VIEW
}

// 检查菜单权限
export const canAccessMenu = (menuKey) => {
  const permission = MENU_PERMISSIONS[menuKey]
  if (!permission) return true
  return checkPermission(permission)
}
