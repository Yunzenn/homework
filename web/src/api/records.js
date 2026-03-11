import { get, post, put, del } from '@/utils/request'

// 获取记录列表
export const getRecordsList = (params) => {
  return get('/records/', params)
}

// 获取单条记录
export const getRecord = (id) => {
  return get(`/records/${id}/`)
}

// 创建记录
export const createRecord = (data) => {
  return post('/records/', data)
}

// 更新记录
export const updateRecord = (id, data) => {
  return put(`/records/${id}/`, data)
}

// 删除记录
export const deleteRecord = (id) => {
  return del(`/records/${id}/`)
}

// 高级查询
export const queryRecords = (data) => {
  return post('/records/query/', data)
}

// 获取报警记录
export const getAlerts = (params = {}) => {
  return get('/records/alerts/', params)
}

// 获取统计数据
export const getStatistics = () => {
  return get('/records/stats/')
}

// 获取仪表盘数据
export const getDashboardData = () => {
  return get('/records/dashboard_data/')
}

// 批量删除
export const batchDeleteRecords = (data) => {
  return post('/records/batch_delete/', data)
}

// 导出数据
export const exportRecords = (params = {}) => {
  return get('/records/export/', params)
}
