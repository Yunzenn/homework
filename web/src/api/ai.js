/**
 * AI Agent API服务
 */

import { get, post } from '@/utils/request'

const aiApi = {
  // AI智能对话
  chat: (data) => {
    // 添加用户配置到请求中
    const config = this.getAIConfig()
    return post('/ai/chat/', {
      ...data,
      ai_config: config
    })
  },

  // 数据查询
  query: (data) => {
    const config = this.getAIConfig()
    return post('/ai/query/', {
      ...data,
      ai_config: config
    })
  },

  // 数据分析
  analysis: (data) => {
    const config = this.getAIConfig()
    return post('/ai/analysis/', {
      ...data,
      ai_config: config
    })
  },

  // 趋势预测
  prediction: (data) => {
    const config = this.getAIConfig()
    return post('/ai/prediction/', {
      ...data,
      ai_config: config
    })
  },

  // 异常检测
  anomaly: (data) => {
    const config = this.getAIConfig()
    return post('/ai/anomaly/', {
      ...data,
      ai_config: config
    })
  },

  // 报告生成
  report: (data) => {
    const config = this.getAIConfig()
    return post('/ai/report/', {
      ...data,
      ai_config: config
    })
  },

  // 决策建议
  advisory: (data) => {
    const config = this.getAIConfig()
    return post('/ai/advisory/', {
      ...data,
      ai_config: config
    })
  },

  // 获取AI配置
  getAIConfig: () => {
    try {
      const config = localStorage.getItem('aiConfig')
      return config ? JSON.parse(config) : null
    } catch (e) {
      console.error('获取AI配置失败:', e)
      return null
    }
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
