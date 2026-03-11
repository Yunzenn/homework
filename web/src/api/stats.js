import { get } from '@/utils/request'

// 获取趋势数据
export const getTrendData = (params = {}) => {
  return get('/records/trend/', params)
}

// 获取实时数据
export const getRealTimeData = () => {
  return get('/records/realtime/')
}

// 获取历史统计
export const getHistoryStats = (params = {}) => {
  return get('/records/history_stats/', params)
}

// 获取报警统计
export const getAlertStats = () => {
  return get('/records/alert_stats/')
}
