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

            

            <p>请输入您的问题开始对话</p>

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

                  <div v-if="message.data && message.data.data" class="structured-data">

                    <!-- 数据查询结果 -->

                    <div v-if="message.data.type === 'data_query'" class="data-result">

                      <el-collapse v-model="activeCollapse">

                        <el-collapse-item title="📊 查询结果" name="data">

                          <div class="data-summary">

                            <p>{{ message.data.data.message }}</p>

                            <div v-if="message.data.data.count" class="data-count">

                              共找到 {{ message.data.data.count }} 条记录

                            </div>

                          </div>

                          <div v-if="message.data.data.data && message.data.data.data.length" class="data-table">

                            <el-table :data="message.data.data.data.slice(0, 5)" size="small">

                              <el-table-column prop="point_id" label="监测点" width="100" />

                              <el-table-column prop="date" label="日期" width="100" />

                              <el-table-column prop="time" label="时间" width="80" />

                              <el-table-column prop="ph" label="pH值" width="80" />

                              <el-table-column prop="chlorine" label="余氯" width="80" />

                              <el-table-column prop="turbidity" label="浊度" width="80" />

                            </el-table>

                            <div v-if="message.data.data.data.length > 5" class="more-data">

                              还有 {{ message.data.data.data.length - 5 }} 条数据...

                            </div>

                          </div>

                        </el-collapse-item>

                      </el-collapse>

                    </div>



                    <!-- 分析结果 -->

                    <div v-if="message.data.type === 'analysis'" class="analysis-result">

                      <el-collapse v-model="activeCollapse">

                        <el-collapse-item title="📈 分析结果" name="analysis">

                          <div class="analysis-content">

                            <p>{{ message.data.data.message }}</p>

                            <div v-if="message.data.data.statistics" class="stats-grid">

                              <div v-for="(value, key) in message.data.data.statistics.indicators" :key="key" class="stat-item">

                                <div class="stat-label">{{ getIndicatorName(key) }}</div>

                                <div class="stat-value">平均: {{ value.avg }}</div>

                                <div class="stat-range">范围: {{ value.min }} - {{ value.max }}</div>

                              </div>

                            </div>

                          </div>

                        </el-collapse-item>

                      </el-collapse>

                    </div>



                    <!-- 报警结果 -->

                    <div v-if="message.data.type === 'alert_query'" class="alert-result">

                      <el-collapse v-model="activeCollapse">

                        <el-collapse-item title="🚨 报警信息" name="alerts">

                          <div class="alert-summary">

                            <p>{{ message.data.data.message }}</p>

                            <div v-if="message.data.data.count" class="alert-count">

                              发现 {{ message.data.data.count }} 条报警

                            </div>

                          </div>

                          <div v-if="message.data.data.alerts && message.data.data.alerts.length" class="alert-list">

                            <div v-for="alert in message.data.data.alerts.slice(0, 5)" :key="alert.id" class="alert-item">

                              <el-tag type="danger" size="small">{{ alert.point_id }}</el-tag>

                              <span class="alert-time">{{ alert.date }} {{ alert.time }}</span>

                              <div class="alert-items">

                                <el-tag 

                                  v-for="item in alert.alert_items" 

                                  :key="item" 

                                  type="warning" 

                                  size="small"

                                  class="alert-item-tag"

                                >

                                  {{ item }}

                                </el-tag>

                              </div>

                            </div>

                            <div v-if="message.data.data.alerts.length > 5" class="more-alerts">

                              还有 {{ message.data.data.alerts.length - 5 }} 条报警...

                            </div>

                          </div>

                        </el-collapse-item>

                      </el-collapse>

                    </div>



                    <!-- 统计结果 -->

                    <div v-if="message.data.type === 'statistics'" class="statistics-result">

                      <el-collapse v-model="activeCollapse">

                        <el-collapse-item title="📊 统计数据" name="statistics">

                          <div class="stats-content">

                            <p>{{ message.data.data.message }}</p>

                            <div v-if="message.data.data.statistics" class="stats-overview">

                              <div class="overview-item">

                                <span class="overview-label">总记录数:</span>

                                <span class="overview-value">{{ message.data.data.statistics.total_records }}</span>

                              </div>

                              <div class="overview-item">

                                <span class="overview-label">监测点数:</span>

                                <span class="overview-value">{{ message.data.data.statistics.point_count }}</span>

                              </div>

                              <div class="overview-item">

                                <span class="overview-label">报警数量:</span>

                                <span class="overview-value">{{ message.data.data.statistics.alert_count }}</span>

                              </div>

                              <div class="overview-item">

                                <span class="overview-label">报警率:</span>

                                <span class="overview-value">{{ message.data.data.statistics.alert_rate }}%</span>

                              </div>

                            </div>

                          </div>

                        </el-collapse-item>

                      </el-collapse>

                    </div>



                    <!-- 监测点信息 -->

                    <div v-if="message.data.type === 'monitoring_point'" class="points-result">

                      <el-collapse v-model="activeCollapse">

                        <el-collapse-item title="📍 监测点信息" name="points">

                          <div class="points-content">

                            <p>{{ message.data.data.message }}</p>

                            <div v-if="message.data.data.points && message.data.data.points.length" class="points-grid">

                              <div v-for="point in message.data.data.points" :key="point.id" class="point-card">

                                <div class="point-name">{{ point.name }}</div>

                                <div class="point-id">{{ point.point_id }}</div>

                                <div class="point-location">{{ point.location_description }}</div>

                                <el-tag :type="point.is_active ? 'success' : 'info'" size="small">

                                  {{ point.is_active ? '启用' : '停用' }}

                                </el-tag>

                              </div>

                            </div>

                          </div>

                        </el-collapse-item>

                      </el-collapse>

                    </div>



                    <!-- 趋势结果 -->

                    <div v-if="message.data.type === 'trend'" class="trend-result">

                      <el-collapse v-model="activeCollapse">

                        <el-collapse-item title="📈 趋势分析" name="trend">

                          <div class="trend-content">

                            <p>{{ message.data.data.message }}</p>

                            <div v-if="message.data.data.trend_data && message.data.data.trend_data.length" class="trend-chart">

                              <div class="trend-summary">

                                <div class="trend-info">

                                  <span>监测点: {{ message.data.data.point_id }}</span>

                                  <span>指标: {{ getIndicatorName(message.data.data.indicator) }}</span>

                                  <span>时间范围: {{ message.data.data.days }}天</span>

                                </div>

                              </div>

                            </div>

                          </div>

                        </el-collapse-item>

                      </el-collapse>

                    </div>

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

            @keydown.ctrl.enter="handleKeyDown"

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



// 处理键盘事件

const handleKeyDown = (event) => {

  if (event.ctrlKey && event.key === 'Enter') {

    event.preventDefault()

    sendMessage()

  }

}



// 发送消息

const sendMessage = async (event = null) => {

  // 如果是事件对象，忽略它，使用输入框的值

  const text = inputMessage.value.trim()

  if (!text || loading.value) return



  // 添加用户消息

  const userMessage = {

    type: 'user',

    content: text,

    timestamp: new Date()

  }

  messages.value.push(userMessage)



  // 清空输入框

  inputMessage.value = ''



  // 添加加载中的AI消息

  const aiMessage = {

    type: 'ai',

    content: '',

    timestamp: new Date(),

    loading: true,

    data: null

  }

  messages.value.push(aiMessage)

  const messageIndex = messages.value.length - 1



  // 滚动到底部

  await nextTick()

  scrollToBottom()



  try {

    loading.value = true



    let streamCompleted = false



    // 优先走Vercel AI SDK流式接口（在本地开发可能不可用，失败后自动回退）

    try {

      const streamResponse = await aiApi.streamChat({

        message: text,

        context: {

          user_id: 'current_user',

          session_id: 'chat_session'

        }

      }, {

        onChunk: (fullText) => {

          messages.value[messageIndex] = {

            ...messages.value[messageIndex],

            type: 'ai',

            content: fullText,

            timestamp: new Date(),

            loading: false,

            data: null

          }

          scrollToBottom()

        }

      })



      if (streamResponse.success) {

        messages.value[messageIndex] = {

          ...messages.value[messageIndex],

          type: 'ai',

          content: streamResponse.data?.message || '处理完成',

          timestamp: new Date(),

          loading: false,

          data: null

        }

        streamCompleted = true

      }

    } catch (streamError) {

      if (import.meta.env.PROD) {

        console.warn('流式接口不可用，回退到标准接口:', streamError)

      }

    }



    if (!streamCompleted) {

      const response = await aiApi.chat({

        message: text,

        context: {

          user_id: 'current_user',

          session_id: 'chat_session'

        }

      })



      if (response.success) {

        // 处理可能的编码问题

        let messageContent = response.data.data?.message || response.data.message || '处理完成'

        

        // 尝试修复编码问题

        try {

          // 如果是乱码，尝试解码

          if (messageContent && messageContent.includes('æ')) {

            // 可能是UTF-8编码问题，尝试修复

            const textArea = document.createElement('textarea')

            textArea.innerHTML = messageContent

            messageContent = textArea.value

          }

        } catch (e) {

          console.warn('编码修复失败:', e)

        }

        

        messages.value[messageIndex] = {

          type: 'ai',

          content: messageContent,

          timestamp: new Date(),

          loading: false,

          data: response.data

        }

      } else {

        throw new Error(response.error || '处理失败')

      }

    }



  } catch (error) {

    console.error('AI对话错误:', error)

    

    // 更新为错误消息

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

        // 使用后端的Ollama测试接口

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

