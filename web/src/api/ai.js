/**
 * AI Agent API服务
 */

import { get, post } from '@/utils/request'

const aiApi = {
  // AI智能对话
  chat: (data) => {
    return post('/ai/chat/', data)
  },

  // 数据查询
  query: (data) => {
    return post('/ai/query/', data)
  },

  // 数据分析
  analysis: (data) => {
    return post('/ai/analysis/', data)
  },

  // 趋势预测
  prediction: (data) => {
    return post('/ai/prediction/', data)
  },

  // 异常检测
  anomaly: (data) => {
    return post('/ai/anomaly/', data)
  },

  // 建议生成
  advisory: (data) => {
    return post('/ai/advisory/', data)
  },

  // 报告生成
  report: (data) => {
    return post('/ai/report/', data)
  },

  // 获取对话历史
  getHistory: (params) => {
    return get('/ai/history/', params)
  },

  // 清空对话历史
  clearHistory: (params) => {
    return post('/ai/history/clear/', params)
  }
}

export { aiApi }
