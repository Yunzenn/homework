// API统一出口
export * from './records'
export * from './stats'

// API基础配置
export const API_BASE_URL = '/api'

// 通用响应处理
export const handleApiResponse = (response, successCallback, errorCallback) => {
  if (response && response.data !== undefined) {
    successCallback && successCallback(response.data)
  } else {
    errorCallback && errorCallback(response || '请求失败')
  }
}
