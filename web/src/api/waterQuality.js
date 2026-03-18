import { request, get, post, put, del } from '@/utils/request'

// 水质记录API
export const waterQualityApi = {
  // 获取记录列表
  getRecords: (params = {}) => {
    return request({
      url: '/records/',
      method: 'GET',
      params
    })
  },

  // 获取单条记录
  getRecord: (id) => {
    return request({
      url: `/records/${id}/`,
      method: 'GET'
    })
  },

  // 创建记录
  createRecord: (data) => {
    return request({
      url: '/records/',
      method: 'POST',
      data
    })
  },

  // 更新记录
  updateRecord: (id, data) => {
    return request({
      url: `/records/${id}/`,
      method: 'PUT',
      data
    })
  },

  // 删除记录
  deleteRecord: (id) => {
    return request({
      url: `/records/${id}/`,
      method: 'DELETE'
    })
  },

  // 批量删除记录
  batchDeleteRecords: (recordIds) => {
    return request({
      url: '/records/batch_delete/',
      method: 'POST',
      data: { record_ids: recordIds }
    })
  },

  // 导出记录
  exportRecords: (params = {}) => {
    return request({
      url: '/records/export/',
      method: 'GET',
      params,
      responseType: 'blob'
    })
  },

  // 获取统计数据
  getStats: () => {
    return request({
      url: '/stats/',
      method: 'GET'
    })
  },

  // 获取报警数据
  getAlerts: (params = {}) => {
    return request({
      url: '/alerts/',
      method: 'GET',
      params
    })
  }
}

export default request
