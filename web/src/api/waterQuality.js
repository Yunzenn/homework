import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url)
    return response.data
  },
  (error) => {
    console.error('API Error:', error.response?.status, error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// 水质记录API
export const waterQualityApi = {
  // 获取记录列表
  getRecords: (params = {}) => {
    return api.get('/records/', { params })
  },

  // 获取单条记录
  getRecord: (id) => {
    return api.get(`/records/${id}/`)
  },

  // 创建记录
  createRecord: (data) => {
    return api.post('/records/', data)
  },

  // 更新记录
  updateRecord: (id, data) => {
    return api.put(`/records/${id}/`, data)
  },

  // 删除记录
  deleteRecord: (id) => {
    return api.delete(`/records/${id}/`)
  },

  // 批量删除记录
  batchDeleteRecords: (recordIds) => {
    return api.post('/records/batch_delete/', { record_ids: recordIds })
  },

  // 导出记录
  exportRecords: (params = {}) => {
    return api.get('/records/export/', { params, responseType: 'blob' })
  },

  // 获取统计数据
  getStats: () => {
    return api.get('/stats/')
  },

  // 获取报警数据
  getAlerts: (params = {}) => {
    return api.get('/alerts/', { params })
  }
}

export default api
