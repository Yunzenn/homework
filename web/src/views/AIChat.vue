<template>
  <div class="ai-chat-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">
            <span class="title-icon">🤖</span>
            AI智能助手
          </h1>
          <p class="page-subtitle">水质监控智能分析，即问即答</p>
        </div>
        <div class="header-right">
          <el-button @click="showConfigDialog" :icon="Setting" circle title="AI配置" />
          <el-button @click="clearHistory" :icon="Delete" circle title="清空对话" />
          <el-button @click="exportChat" :icon="Download" circle title="导出对话" />
        </div>
      </div>
    </div>

    <!-- 聊天界面 -->
    <div class="chat-container">
      <!-- 对话区域 -->
      <div class="chat-messages" ref="messagesContainer">
        <div v-if="messages.length === 0" class="welcome-message">
          <div class="welcome-content">
            <div class="welcome-icon">👋</div>
            <h3>欢迎使用AI智能助手</h3>
            
            <!-- AI配置状态 -->
            <div class="ai-status">
              <el-alert 
                :title="getAIStatusText()" 
                :type="aiConfigStatus.type"
                :closable="false"
                show-icon
                class="status-alert"
              >
                <template #default>
                  <div class="status-content">
                    <span>{{ aiConfigStatus.message }}</span>
                    <el-button 
                      v-if="!aiConfigStatus.configured"
                      type="primary" 
                      size="small" 
                      @click="showConfigDialog"
                      style="margin-left: 10px;"
                    >
                      立即配置
                    </el-button>
                  </div>
                </template>
              </el-alert>
            </div>
            
            <p>我可以帮您：</p>
            <ul class="capability-list">
              <li>📊 查询水质数据：如"P-042今天pH值多少？"</li>
              <li>📈 分析数据趋势：如"最近一周浊度变化趋势？"</li>
              <li>🔍 异常原因诊断：如"为什么余氯突然升高？"</li>
              <li>🔮 预测未来趋势：如"明天水质会超标吗？"</li>
              <li>💡 提供治理建议：如"pH超标怎么办？"</li>
              <li>📋 生成分析报告：如"生成今天的水质日报"</li>
            </ul>
            <div class="quick-actions">
              <h4>快速开始：</h4>
              <div class="action-buttons">
                <el-button 
                  v-for="example in quickExamples" 
                  :key="example.text"
                  type="primary" 
                  plain
                  size="small"
                  @click="sendMessage(example.text)"
                >
                  {{ example.text }}
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 消息列表 -->
        <div v-for="(message, index) in messages" :key="index" class="message-item" :class="message.type">
          <div class="message-avatar">
            <div v-if="message.type === 'user'" class="user-avatar">👤</div>
            <div v-else class="ai-avatar">🤖</div>
          </div>
          <div class="message-content">
            <div class="message-header">
              <span class="message-sender">
                {{ message.type === 'user' ? '您' : 'AI助手' }}
              </span>
              <span class="message-time">{{ formatTime(message.timestamp) }}</span>
            </div>
            <div class="message-body">
              <div v-if="message.type === 'user'" class="user-message">
                {{ message.content }}
              </div>
              <div v-else class="ai-message">
                <!-- AI回复内容 -->
                <div v-if="message.loading" class="loading-message">
                  <el-icon class="is-loading"><Loading /></el-icon>
                  正在思考中...
                </div>
                <div v-else>
                  <!-- 主要回答 -->
                  <div class="ai-response" v-html="formatAIResponse(message.content)"></div>
                  
                  <!-- 结构化数据展示 -->
                  <div v-if="message.data" class="structured-data">
                    <!-- 数据查询结果 -->
                    <div v-if="message.data.agent === '数据查询Agent'" class="data-result">
                      <el-collapse v-model="activeCollapse">
                        <el-collapse-item title="📊 查询结果" name="data">
                          <div class="data-summary">
                            <p>{{ message.data.summary }}</p>
                          </div>
                          <div v-if="message.data.data?.records" class="data-table">
                            <el-table :data="message.data.data.records.slice(0, 5)" size="small">
                              <el-table-column prop="point_id" label="监测点" width="100" />
                              <el-table-column prop="date" label="日期" width="100" />
                              <el-table-column prop="time" label="时间" width="80" />
                              <el-table-column prop="ph" label="pH值" width="80" />
                              <el-table-column prop="chlorine" label="余氯" width="80" />
                              <el-table-column prop="turbidity" label="浊度" width="80" />
                            </el-table>
                            <div v-if="message.data.data.records.length > 5" class="more-data">
                              还有 {{ message.data.data.records.length - 5 }} 条数据...
                            </div>
                          </div>
                        </el-collapse-item>
                      </el-collapse>
                    </div>

                    <!-- 分析结果 -->
                    <div v-if="message.data.agent === '数据分析Agent'" class="analysis-result">
                      <el-collapse v-model="activeCollapse">
                        <el-collapse-item title="📈 分析结果" name="analysis">
                          <div class="quality-assessment">
                            <h4>水质评估</h4>
                            <div class="grade-display">
                              <span class="grade-label">综合评分：</span>
                              <span class="grade-value" :class="getGradeClass(message.data.quality_assessment?.grade)">
                                {{ message.data.quality_assessment?.grade || '未知' }}
                              </span>
                              <span class="grade-score">
                                ({{ message.data.quality_assessment?.overall_score || 0 }}分)
                              </span>
                            </div>
                          </div>
                          
                          <div v-if="message.data.trends?.length" class="trends-section">
                            <h4>趋势分析</h4>
                            <div class="trend-list">
                              <div v-for="trend in message.data.trends" :key="trend.indicator" class="trend-item">
                                <span class="trend-indicator">{{ getIndicatorName(trend.indicator) }}</span>
                                <span class="trend-direction" :class="trend.trend">
                                  {{ trend.trend }}
                                </span>
                                <span class="trend-rate">
                                  ({{ trend.change_rate > 0 ? '+' : '' }}{{ trend.change_rate?.toFixed(1) }}%)
                                </span>
                              </div>
                            </div>
                          </div>

                          <div v-if="message.data.anomalies?.length" class="anomalies-section">
                            <h4>异常检测</h4>
                            <div class="anomaly-list">
                              <div v-for="anomaly in message.data.anomalies" :key="anomaly.indicator" class="anomaly-item">
                                <el-tag :type="getAnomalyTagType(anomaly.severity)" size="small">
                                  {{ getIndicatorName(anomaly.indicator) }}{{ anomaly.anomaly_type }}
                                </el-tag>
                                <span class="anomaly-desc">{{ anomaly.description }}</span>
                              </div>
                            </div>
                          </div>
                        </el-collapse-item>
                      </el-collapse>
                    </div>

                    <!-- 建议结果 -->
                    <div v-if="message.data.agent === '建议Agent'" class="advisory-result">
                      <el-collapse v-model="activeCollapse">
                        <el-collapse-item title="💡 智能建议" name="advisory">
                          <div v-if="message.data.recommendations?.length" class="recommendations">
                            <h4>处理建议</h4>
                            <div class="recommendation-list">
                              <div v-for="rec in message.data.recommendations" :key="rec.title" class="recommendation-item">
                                <div class="rec-header">
                                  <el-tag :type="getPriorityTagType(rec.priority)" size="small">
                                    {{ rec.priority }}
                                  </el-tag>
                                  <span class="rec-title">{{ rec.title }}</span>
                                </div>
                                <p class="rec-description">{{ rec.description }}</p>
                                <div v-if="rec.action_steps?.length" class="rec-steps">
                                  <h5>行动步骤：</h5>
                                  <ul>
                                    <li v-for="step in rec.action_steps" :key="step">{{ step }}</li>
                                  </ul>
                                </div>
                              </div>
                            </div>
                          </div>

                          <div v-if="message.data.risk_assessment" class="risk-assessment">
                            <h4>风险评估</h4>
                            <div class="risk-level">
                              <span class="risk-label">风险等级：</span>
                              <el-tag :type="getRiskTagType(message.data.risk_assessment.risk_level)">
                                {{ message.data.risk_assessment.risk_level }}
                              </el-tag>
                            </div>
                          </div>
                        </el-collapse-item>
                      </el-collapse>
                    </div>

                    <!-- 预测结果 -->
                    <div v-if="message.data.agent === '预测Agent'" class="prediction-result">
                      <el-collapse v-model="activeCollapse">
                        <el-collapse-item title="🔮 趋势预测" name="prediction">
                          <div v-if="message.data.predictions?.length" class="predictions">
                            <div v-for="prediction in message.data.predictions" :key="prediction.indicator" class="prediction-item">
                              <h5>{{ getIndicatorName(prediction.indicator) }}预测</h5>
                              <div class="prediction-chart">
                                <div class="prediction-values">
                                  <div v-for="(value, index) in prediction.predicted_values" :key="index" class="value-point">
                                    <span class="time-label">{{ prediction.time_points[index] }}</span>
                                    <span class="predicted-value">{{ value?.toFixed(2) }}</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>

                          <div v-if="message.data.risk_assessment" class="prediction-risk">
                            <h4>风险评估</h4>
                            <el-alert 
                              :title="`预测风险等级：${message.data.risk_assessment.overall_risk}`"
                              :type="getRiskAlertType(message.data.risk_assessment.overall_risk)"
                              :closable="false"
                            />
                          </div>
                        </el-collapse-item>
                      </el-collapse>
                    </div>
                  </div>

                  <!-- 置信度显示 -->
                  <div v-if="message.data?.confidence" class="confidence-indicator">
                    <span class="confidence-label">置信度：</span>
                    <el-progress 
                      :percentage="Math.round(message.data.confidence * 100)"
                      :stroke-width="6"
                      :show-text="true"
                      :format="format => `${format}%`"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input">
        <div class="input-container">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="请输入您的问题，如：P-042今天水质怎么样？"
            @keydown.ctrl.enter="sendMessage"
            :disabled="loading"
            resize="none"
          />
          <div class="input-actions">
            <div class="input-tips">
              <span class="tip-text">按 Ctrl+Enter 发送</span>
            </div>
            <el-button 
              type="primary" 
              @click="sendMessage"
              :loading="loading"
              :disabled="!inputMessage.trim()"
            >
              <el-icon><ChatDotRound /></el-icon>
              发送
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- AI配置对话框 -->
    <el-dialog 
      v-model="configDialogVisible" 
      title="AI模型配置" 
      width="600px"
      :before-close="handleConfigClose"
    >
      <el-form :model="aiConfig" :rules="configRules" ref="configForm" label-width="120px">
        <!-- 模型类型选择 -->
        <el-form-item label="模型类型" prop="modelType">
          <el-radio-group v-model="aiConfig.modelType" @change="handleModelTypeChange">
            <el-radio label="local">本地模型</el-radio>
            <el-radio label="openai">OpenAI API</el-radio>
            <el-radio label="claude">Claude API</el-radio>
            <el-radio label="custom">自定义API</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 本地模型配置 -->
        <template v-if="aiConfig.modelType === 'local'">
          <el-form-item label="服务地址" prop="localUrl">
            <el-input 
              v-model="aiConfig.localUrl" 
              placeholder="http://localhost:11434/v1"
            />
          </el-form-item>
          <el-form-item label="模型名称" prop="localModel">
            <el-input 
              v-model="aiConfig.localModel" 
              placeholder="qwen2.5-coder:7b"
            />
          </el-form-item>
        </template>

        <!-- OpenAI配置 -->
        <template v-if="aiConfig.modelType === 'openai'">
          <el-form-item label="API密钥" prop="openaiApiKey">
            <el-input 
              v-model="aiConfig.openaiApiKey" 
              type="password"
              placeholder="sk-..."
              show-password
            />
          </el-form-item>
          <el-form-item label="模型名称" prop="openaiModel">
            <el-select v-model="aiConfig.openaiModel" placeholder="选择模型">
              <el-option label="GPT-3.5 Turbo" value="gpt-3.5-turbo" />
              <el-option label="GPT-4" value="gpt-4" />
              <el-option label="GPT-4 Turbo" value="gpt-4-turbo" />
            </el-select>
          </el-form-item>
        </template>

        <!-- Claude配置 -->
        <template v-if="aiConfig.modelType === 'claude'">
          <el-form-item label="API密钥" prop="claudeApiKey">
            <el-input 
              v-model="aiConfig.claudeApiKey" 
              type="password"
              placeholder="sk-ant-..."
              show-password
            />
          </el-form-item>
          <el-form-item label="模型名称" prop="claudeModel">
            <el-select v-model="aiConfig.claudeModel" placeholder="选择模型">
              <el-option label="Claude 3 Sonnet" value="claude-3-sonnet-20240229" />
              <el-option label="Claude 3 Haiku" value="claude-3-haiku-20240307" />
              <el-option label="Claude 3 Opus" value="claude-3-opus-20240229" />
            </el-select>
          </el-form-item>
        </template>

        <!-- 自定义API配置 -->
        <template v-if="aiConfig.modelType === 'custom'">
          <el-form-item label="API地址" prop="customUrl">
            <el-input 
              v-model="aiConfig.customUrl" 
              placeholder="http://your-api.com/v1"
            />
          </el-form-item>
          <el-form-item label="API密钥" prop="customApiKey">
            <el-input 
              v-model="aiConfig.customApiKey" 
              type="password"
              placeholder="可选"
              show-password
            />
          </el-form-item>
          <el-form-item label="模型名称" prop="customModel">
            <el-input 
              v-model="aiConfig.customModel" 
              placeholder="your-model-name"
            />
          </el-form-item>
        </template>

        <!-- 通用配置 -->
        <el-form-item label="温度参数" prop="temperature">
          <el-slider 
            v-model="aiConfig.temperature" 
            :min="0" 
            :max="2" 
            :step="0.1"
            show-input
            :show-input-controls="false"
          />
          <div class="form-help">
            <small>控制生成文本的随机性，值越高越随机</small>
          </div>
        </el-form-item>

        <el-form-item label="最大Token数" prop="maxTokens">
          <el-input-number 
            v-model="aiConfig.maxTokens" 
            :min="100" 
            :max="4000" 
            :step="100"
          />
          <div class="form-help">
            <small>限制AI回复的最大长度</small>
          </div>
        </el-form-item>
      </el-form>

      <!-- 连接测试 -->
      <div class="config-test">
        <el-button 
          @click="testConnection" 
          :loading="testingConnection"
          type="primary"
          plain
        >
          测试连接
        </el-button>
        <span v-if="testResult" :class="['test-result', testResult.success ? 'success' : 'error']">
          {{ testResult.message }}
        </span>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="configDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveConfig">保存配置</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Download, Loading, ChatDotRound, Setting } from '@element-plus/icons-vue'
import { aiApi } from '@/api/ai'

// 响应式数据
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)
const activeCollapse = ref(['data', 'analysis', 'advisory', 'prediction'])

// 快速示例
const quickExamples = ref([
  { text: 'P-042今天水质怎么样？' },
  { text: '最近一周pH值变化趋势？' },
  { text: '为什么余氯突然升高？' },
  { text: '明天水质会超标吗？' },
  { text: 'pH超标怎么办？' }
])

// AI配置相关
const configDialogVisible = ref(false)
const configForm = ref(null)
const testingConnection = ref(false)
const testResult = ref(null)

// AI配置数据
const aiConfig = reactive({
  modelType: 'local',
  localUrl: 'http://localhost:11434/v1',
  localModel: 'qwen2.5-coder:7b',
  openaiApiKey: '',
  openaiModel: 'gpt-3.5-turbo',
  claudeApiKey: '',
  claudeModel: 'claude-3-sonnet-20240229',
  customUrl: '',
  customApiKey: '',
  customModel: '',
  temperature: 0.7,
  maxTokens: 2000
})

// AI配置状态
const aiConfigStatus = reactive({
  configured: false,
  type: 'warning',
  message: '尚未配置AI模型'
})

// 配置验证规则
const configRules = {
  modelType: [{ required: true, message: '请选择模型类型', trigger: 'change' }],
  localUrl: [{ required: true, message: '请输入本地服务地址', trigger: 'blur' }],
  localModel: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  openaiApiKey: [{ required: true, message: '请输入OpenAI API密钥', trigger: 'blur' }],
  openaiModel: [{ required: true, message: '请选择OpenAI模型', trigger: 'change' }],
  claudeApiKey: [{ required: true, message: '请输入Claude API密钥', trigger: 'blur' }],
  claudeModel: [{ required: true, message: '请选择Claude模型', trigger: 'change' }],
  customUrl: [{ required: true, message: '请输入自定义API地址', trigger: 'blur' }],
  customModel: [{ required: true, message: '请输入模型名称', trigger: 'blur' }]
}

// 发送消息
const sendMessage = async (messageText = null) => {
  const text = messageText || inputMessage.value.trim()
  if (!text || loading.value) return

  // 添加用户消息
  const userMessage = {
    type: 'user',
    content: text,
    timestamp: new Date()
  }
  messages.value.push(userMessage)

  // 清空输入框
  if (!messageText) {
    inputMessage.value = ''
  }

  // 添加加载中的AI消息
  const aiMessage = {
    type: 'ai',
    content: '',
    timestamp: new Date(),
    loading: true,
    data: null
  }
  messages.value.push(aiMessage)

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  try {
    loading.value = true
    
    // 调用AI接口
    const response = await aiApi.chat({
      message: text,
      context: {
        user_id: 'current_user',
        session_id: 'chat_session'
      }
    })

    if (response.success) {
      // 更新AI消息
      const messageIndex = messages.value.length - 1
      messages.value[messageIndex] = {
        type: 'ai',
        content: response.data.synthesis?.summary || '处理完成',
        timestamp: new Date(),
        loading: false,
        data: response.data
      }
    } else {
      throw new Error(response.error || '处理失败')
    }

  } catch (error) {
    console.error('AI对话错误:', error)
    
    // 更新为错误消息
    const messageIndex = messages.value.length - 1
    messages.value[messageIndex] = {
      type: 'ai',
      content: '抱歉，处理您的问题时遇到了错误。请稍后重试。',
      timestamp: new Date(),
      loading: false,
      data: null,
      error: true
    }
    
    ElMessage.error('AI助手暂时无法响应，请稍后重试')
  } finally {
    loading.value = false
    await nextTick()
    scrollToBottom()
  }
}

// 格式化AI回复
const formatAIResponse = (content) => {
  if (!content) return ''
  
  // 简单的文本格式化
  return content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) {
    return '刚刚'
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 获取指标名称
const getIndicatorName = (indicator) => {
  const names = {
    ph: 'pH值',
    chlorine: '余氯',
    turbidity: '浊度',
    conductivity: '电导率',
    orp: 'ORP'
  }
  return names[indicator] || indicator
}

// 获取等级样式类
const getGradeClass = (grade) => {
  const classes = {
    '优': 'grade-excellent',
    '良': 'grade-good',
    '中': 'grade-medium',
    '及格': 'grade-pass',
    '差': 'grade-poor'
  }
  return classes[grade] || 'grade-unknown'
}

// 获取异常标签类型
const getAnomalyTagType = (severity) => {
  const types = {
    '严重': 'danger',
    '中等': 'warning',
    '轻微': 'info'
  }
  return types[severity] || 'info'
}

// 获取优先级标签类型
const getPriorityTagType = (priority) => {
  const types = {
    'high': 'danger',
    'medium': 'warning',
    'low': 'info'
  }
  return types[priority] || 'info'
}

// 获取风险标签类型
const getRiskTagType = (risk) => {
  const types = {
    '高': 'danger',
    '中': 'warning',
    '低': 'success'
  }
  return types[risk] || 'info'
}

// 获取风险警告类型
const getRiskAlertType = (risk) => {
  const types = {
    '高': 'error',
    '中': 'warning',
    '低': 'success'
  }
  return types[risk] || 'info'
}

// 清空对话历史
const clearHistory = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有对话记录吗？', '清空对话', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    messages.value = []
    ElMessage.success('对话记录已清空')
  } catch {
    // 用户取消
  }
}

// 导出对话
const exportChat = () => {
  if (messages.value.length === 0) {
    ElMessage.warning('没有对话记录可导出')
    return
  }

  const chatContent = messages.value.map(msg => {
    const sender = msg.type === 'user' ? '用户' : 'AI助手'
    const time = formatTime(msg.timestamp)
    return `[${time}] ${sender}:\n${msg.content}\n`
  }).join('\n---\n')

  const blob = new Blob([chatContent], { type: 'text/plain;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `AI对话记录_${new Date().toLocaleDateString()}.txt`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)

  ElMessage.success('对话记录已导出')
}

// AI配置相关方法
const showConfigDialog = () => {
  configDialogVisible.value = true
  loadConfig()
}

const loadConfig = () => {
  // 从localStorage加载配置
  const savedConfig = localStorage.getItem('aiConfig')
  if (savedConfig) {
    try {
      const config = JSON.parse(savedConfig)
      Object.assign(aiConfig, config)
    } catch (e) {
      console.error('加载AI配置失败:', e)
    }
  }
  checkAIStatus()
}

const saveConfig = async () => {
  try {
    // 验证表单
    await configForm.value.validate()
    
    // 保存到localStorage
    localStorage.setItem('aiConfig', JSON.stringify(aiConfig))
    
    // 更新状态
    checkAIStatus()
    
    ElMessage.success('AI配置已保存')
    configDialogVisible.value = false
  } catch (error) {
    console.error('保存配置失败:', error)
  }
}

const handleModelTypeChange = (type) => {
  // 清空测试结果
  testResult.value = null
  
  // 根据类型更新验证规则
  nextTick(() => {
    configForm.value.clearValidate()
  })
}

const testConnection = async () => {
  testingConnection.value = true
  testResult.value = null
  
  try {
    let apiUrl, headers, testData
    
    switch (aiConfig.modelType) {
      case 'local':
        // 使用专门的Ollama测试接口
        apiUrl = '/api/ai/test-ollama/'
        testData = {
          model: aiConfig.localModel,
          prompt: '你好，请回复一个简单的问候'
        }
        headers = {}
        break
      case 'openai':
        apiUrl = 'https://api.openai.com/v1/models'
        headers = {
          'Authorization': `Bearer ${aiConfig.openaiApiKey}`
        }
        break
      case 'claude':
        apiUrl = 'https://api.anthropic.com/v1/messages'
        headers = {
          'x-api-key': aiConfig.claudeApiKey,
          'anthropic-version': '2023-06-01'
        }
        testData = {
          model: aiConfig.claudeModel,
          max_tokens: 10,
          messages: [{ role: 'user', content: 'test' }]
        }
        break
      case 'custom':
        apiUrl = `${aiConfig.customUrl}/models`
        headers = aiConfig.customApiKey ? {
          'Authorization': `Bearer ${aiConfig.customApiKey}`
        } : {}
        break
      default:
        throw new Error('不支持的模型类型')
    }
    
    let response
    if (aiConfig.modelType === 'local') {
      // 使用POST请求测试Ollama
      response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...headers
        },
        body: JSON.stringify(testData)
      })
    } else {
      // 其他模型使用GET请求
      response = await fetch(apiUrl, { headers })
    }
    
    if (response.ok) {
      const data = await response.json()
      
      if (aiConfig.modelType === 'local') {
        // Ollama测试成功
        if (data.success) {
          testResult.value = {
            type: 'success',
            message: `连接成功！模型: ${data.data.model}, 响应: ${data.data.response.substring(0, 50)}...`
          }
        } else {
          testResult.value = {
            type: 'error',
            message: `连接失败: ${data.error}`
          }
        }
      } else {
        testResult.value = {
          type: 'success',
          message: '连接测试成功！'
        }
      }
    } else {
      const errorText = await response.text()
      testResult.value = {
        type: 'error',
        message: `连接失败: ${response.status} - ${errorText}`
      }
    }
  } catch (error) {
    testResult.value = {
      type: 'error',
      message: `连接测试失败: ${error.message}`
    }
  } finally {
    testingConnection.value = false
  }
}

const checkAIStatus = () => {
  // 检查AI配置状态
  const hasConfig = (
    (aiConfig.modelType === 'local' && aiConfig.localUrl && aiConfig.localModel) ||
    (aiConfig.modelType === 'openai' && aiConfig.openaiApiKey && aiConfig.openaiModel) ||
    (aiConfig.modelType === 'claude' && aiConfig.claudeApiKey && aiConfig.claudeModel) ||
    (aiConfig.modelType === 'custom' && aiConfig.customUrl && aiConfig.customModel)
  )
  
  if (hasConfig) {
    aiConfigStatus.configured = true
    aiConfigStatus.type = 'success'
    aiConfigStatus.message = `已配置${getModelTypeName()}`
  } else {
    aiConfigStatus.configured = false
    aiConfigStatus.type = 'warning'
    aiConfigStatus.message = '尚未配置AI模型'
  }
}

const getModelTypeName = () => {
  const names = {
    'local': '本地模型',
    'openai': 'OpenAI API',
    'claude': 'Claude API',
    'custom': '自定义API'
  }
  return names[aiConfig.modelType] || '未知模型'
}

const getAIStatusText = () => {
  if (aiConfigStatus.configured) {
    return 'AI模型已就绪'
  } else {
    return '需要配置AI模型'
  }
}

const handleConfigClose = () => {
  configDialogVisible.value = false
  testResult.value = null
}

// 组件挂载
onMounted(() => {
  scrollToBottom()
  loadConfig()
})
</script>

<style lang="scss" scoped>
.ai-chat-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.page-header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 20px 30px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  color: white;
}

.page-title {
  margin: 0 0 5px 0;
  font-size: 1.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-icon {
  font-size: 2rem;
}

.page-subtitle {
  margin: 0;
  opacity: 0.8;
  font-size: 0.9rem;
}

.header-right {
  display: flex;
  gap: 10px;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin: 20px;
  gap: 20px;
  max-height: calc(100vh - 120px);
}

.chat-messages {
  flex: 1;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 30px;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.welcome-message {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.welcome-content {
  text-align: center;
  max-width: 600px;
}

.welcome-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.welcome-content h3 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.capability-list {
  text-align: left;
  margin: 20px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 10px;
}

.capability-list li {
  margin-bottom: 10px;
  color: #495057;
}

.quick-actions {
  margin-top: 30px;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  margin-top: 15px;
}

.message-item {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
  animation: fadeInUp 0.3s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-avatar {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.user-avatar {
  background: #007bff;
  color: white;
}

.ai-avatar {
  background: #28a745;
  color: white;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.message-sender {
  font-weight: 600;
  color: #2c3e50;
}

.message-time {
  font-size: 0.8rem;
  color: #6c757d;
}

.user-message {
  background: #007bff;
  color: white;
  padding: 12px 16px;
  border-radius: 18px 18px 4px 18px;
  max-width: 80%;
  word-wrap: break-word;
}

.ai-message {
  max-width: 100%;
}

.loading-message {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #6c757d;
  font-style: italic;
}

.ai-response {
  background: #f8f9fa;
  padding: 12px 16px;
  border-radius: 18px 18px 18px 4px;
  margin-bottom: 15px;
  line-height: 1.6;
  color: #2c3e50;
}

.structured-data {
  margin-top: 15px;
}

.data-result,
.analysis-result,
.advisory-result,
.prediction-result {
  margin-top: 10px;
}

.data-summary {
  padding: 15px;
  background: #e3f2fd;
  border-radius: 8px;
  margin-bottom: 15px;
}

.data-table {
  margin-top: 10px;
}

.more-data {
  text-align: center;
  padding: 10px;
  color: #6c757d;
  font-size: 0.9rem;
}

.quality-assessment {
  margin-bottom: 20px;
}

.grade-display {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.grade-label {
  font-weight: 600;
}

.grade-value {
  font-weight: 700;
  font-size: 1.2rem;
  padding: 4px 12px;
  border-radius: 20px;
  color: white;
}

.grade-excellent { background: #28a745; }
.grade-good { background: #17a2b8; }
.grade-medium { background: #ffc107; color: #212529; }
.grade-pass { background: #fd7e14; }
.grade-poor { background: #dc3545; }

.trends-section,
.anomalies-section {
  margin-bottom: 20px;
}

.trends-section h4,
.anomalies-section h4 {
  margin-bottom: 10px;
  color: #2c3e50;
}

.trend-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.trend-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.trend-indicator {
  font-weight: 600;
  min-width: 60px;
}

.trend-direction {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  color: white;
}

.trend-direction.上升 { background: #28a745; }
.trend-direction.下降 { background: #dc3545; }
.trend-direction.稳定 { background: #6c757d; }

.trend-rate {
  color: #6c757d;
  font-size: 0.9rem;
}

.anomaly-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.anomaly-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.anomaly-desc {
  color: #495057;
  font-size: 0.9rem;
}

.recommendations {
  margin-bottom: 20px;
}

.recommendation-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.recommendation-item {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #007bff;
}

.rec-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.rec-title {
  font-weight: 600;
  color: #2c3e50;
}

.rec-description {
  margin: 8px 0;
  color: #495057;
}

.rec-steps {
  margin-top: 10px;
}

.rec-steps h5 {
  margin-bottom: 8px;
  color: #2c3e50;
}

.rec-steps ul {
  margin: 0;
  padding-left: 20px;
}

.rec-steps li {
  margin-bottom: 5px;
  color: #495057;
}

.risk-assessment {
  padding: 15px;
  background: #fff3cd;
  border-radius: 8px;
  border: 1px solid #ffeaa7;
}

.risk-level {
  display: flex;
  align-items: center;
  gap: 10px;
}

.predictions {
  margin-bottom: 20px;
}

.prediction-item {
  margin-bottom: 15px;
}

.prediction-item h5 {
  margin-bottom: 10px;
  color: #2c3e50;
}

.prediction-chart {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
}

.prediction-values {
  display: flex;
  gap: 20px;
  justify-content: space-around;
}

.value-point {
  text-align: center;
}

.time-label {
  display: block;
  font-size: 0.8rem;
  color: #6c757d;
  margin-bottom: 5px;
}

.predicted-value {
  display: block;
  font-weight: 600;
  color: #2c3e50;
}

.prediction-risk {
  margin-top: 15px;
}

.confidence-indicator {
  margin-top: 15px;
  padding: 10px;
  background: #e9ecef;
  border-radius: 8px;
}

.confidence-label {
  font-weight: 600;
  margin-right: 10px;
}

.chat-input {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.input-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.input-tips {
  color: #6c757d;
  font-size: 0.8rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    padding: 15px 20px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .chat-container {
    margin: 10px;
    gap: 10px;
  }
  
  .chat-messages {
    padding: 20px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .prediction-values {
    flex-direction: column;
    gap: 10px;
  }
}

/* AI配置相关样式 */
.ai-status {
  margin: 20px 0;
}

.status-alert {
  border-radius: 12px;
}

.status-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.config-test {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
  display: flex;
  align-items: center;
  gap: 15px;
}

.test-result {
  font-weight: 600;
  font-size: 0.9rem;
}

.test-result.success {
  color: #67c23a;
}

.test-result.error {
  color: #f56c6c;
}

.form-help {
  margin-top: 5px;
  color: #909399;
  font-size: 0.8rem;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 配置对话框样式优化 */
:deep(.el-dialog__body) {
  padding: 20px 30px;
}

:deep(.el-form-item__label) {
  font-weight: 600;
  color: #303133;
}

:deep(.el-radio-group) {
  display: flex;
  gap: 20px;
}

:deep(.el-slider) {
  margin-right: 20px;
}

:deep(.el-input-number) {
  width: 150px;
}
</style>
