/**
 * AI Agent API服务
 */

import { get, post } from '@/utils/request'

const aiApi = {
  // AI智能对话
  chat: (data) => {
    // 添加用户配置到请求中
    const config = aiApi.getAIConfig()
    return post('/ai/chat/', {
      ...data,
      ai_config: config
    })
  },

  // 数据查询
  query: (data) => {
    const config = aiApi.getAIConfig()
    return post('/ai/query/', {
      ...data,
      ai_config: config
    })
  },

  // 数据分析
  analysis: (data) => {
    const config = aiApi.getAIConfig()
    return post('/ai/analysis/', {
      ...data,
      ai_config: config
    })
  },

  // 趋势预测
  prediction: (data) => {
    const config = aiApi.getAIConfig()
    return post('/ai/prediction/', {
      ...data,
      ai_config: config
    })
  },

  // 异常检测
  anomaly: (data) => {
    const config = aiApi.getAIConfig()
    return post('/ai/anomaly/', {
      ...data,
      ai_config: config
    })
  },

  // 报告生成
  report: (data) => {
    const config = aiApi.getAIConfig()
    return post('/ai/report/', {
      ...data,
      ai_config: config
    })
  },

  // 决策建议
  advisory: (data) => {
    const config = aiApi.getAIConfig()
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
  },

  // Vercel AI SDK流式对话（失败时由调用方回退到普通接口）
  streamChat: async (data, handlers = {}) => {
    // Vite开发环境下 /api 通常代理到Django，Vercel函数不可直接访问
    if (import.meta.env.DEV) {
      throw new Error('DEV环境禁用Vercel流式接口，自动回退到Django接口')
    }

    const { onChunk, onComplete } = handlers
    const config = aiApi.getAIConfig()
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')

    const response = await fetch('/api/vercel-ai/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: JSON.stringify({
        ...data,
        ai_config: config
      })
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(errorText || `流式请求失败: ${response.status}`)
    }

    if (!response.body) {
      throw new Error('流式响应为空')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let fullText = ''

    const processLine = (line) => {
      const trimmed = line.trim()
      if (!trimmed || !trimmed.startsWith('data:')) return

      const payloadText = trimmed.slice(5).trim()
      if (!payloadText || payloadText === '[DONE]') return

      try {
        const payload = JSON.parse(payloadText)
        if (payload.type === 'text-delta' && typeof payload.delta === 'string') {
          fullText += payload.delta
          if (onChunk) onChunk(fullText, payload.delta)
        }
      } catch {
        // ignore non-json chunks
      }
    }

    while (true) {
      const { value, done } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        processLine(line)
      }
    }

    if (buffer) {
      processLine(buffer)
    }

    if (onComplete) onComplete(fullText)

    return {
      success: true,
      data: {
        message: fullText
      }
    }
  }
}

export { aiApi }
