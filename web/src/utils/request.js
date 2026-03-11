import axios from 'axios'
import { ElMessage, ElLoading } from 'element-plus'

// 创建axios实例
const service = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

let loading = null
let loadingCount = 0

// 显示loading
const showLoading = () => {
  if (loadingCount === 0) {
    loading = ElLoading.service({
      lock: true,
      text: '加载中...',
      background: 'rgba(0, 0, 0, 0.7)'
    })
  }
  loadingCount++
}

// 隐藏loading
const hideLoading = () => {
  loadingCount--
  if (loadingCount <= 0 && loading) {
    loading.close()
    loading = null
    loadingCount = 0
  }
}

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 可以在这里添加token等认证信息
    // config.headers['Authorization'] = 'Bearer ' + getToken()
    
    // 显示loading（可选）
    if (config.showLoading !== false) {
      showLoading()
    }
    
    return config
  },
  error => {
    hideLoading()
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    hideLoading()
    
    const { data, status } = response
    
    // 根据状态码处理
    if (status >= 200 && status < 300) {
      return data
    } else {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message || '请求失败'))
    }
  },
  error => {
    hideLoading()
    
    const { response } = error
    
    if (response) {
      const { status, data } = response
      
      switch (status) {
        case 400:
          ElMessage.error(data.error || '请求参数错误')
          break
        case 401:
          ElMessage.error('未授权，请重新登录')
          // 可以在这里处理登录跳转
          break
        case 403:
          ElMessage.error('拒绝访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(data.error || `请求失败，状态码：${status}`)
      }
    } else {
      ElMessage.error('网络连接失败')
    }
    
    return Promise.reject(error)
  }
)

// 封装GET请求
export const get = (url, params = {}, config = {}) => {
  return service.get(url, { params, ...config })
}

// 封装POST请求
export const post = (url, data = {}, config = {}) => {
  return service.post(url, data, config)
}

// 封装PUT请求
export const put = (url, data = {}, config = {}) => {
  return service.put(url, data, config)
}

// 封装DELETE请求
export const del = (url, config = {}) => {
  return service.delete(url, config)
}

// 封装PATCH请求
export const patch = (url, data = {}, config = {}) => {
  return service.patch(url, data, config)
}

export default service
