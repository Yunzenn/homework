<template>
  <div class="enhanced-analysis">
    <!-- 分析类型选择 -->
    <div class="analysis-header">
      <el-card class="analysis-selector">
        <div class="selector-content">
          <h3>智能数据分析</h3>
          <el-radio-group v-model="analysisType" @change="onAnalysisTypeChange">
            <el-radio-button label="trace">污染溯源</el-radio-button>
            <el-radio-button label="prediction">水质预测</el-radio-button>
            <el-radio-button label="comprehensive">综合分析</el-radio-button>
          </el-radio-group>
        </div>
      </el-card>
    </div>

    <!-- 参数配置面板 -->
    <div class="analysis-params">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>分析参数配置</span>
            <el-button type="primary" @click="runAnalysis" :loading="analyzing">
              {{ analyzing ? '分析中...' : '开始分析' }}
            </el-button>
          </div>
        </template>

        <el-form :model="analysisParams" label-width="120px">
          <!-- 基础参数 -->
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="目标监测点">
                <el-select v-model="analysisParams.targetLocation" placeholder="选择监测点">
                  <el-option
                    v-for="point in monitoringPoints"
                    :key="point"
                    :label="point"
                    :value="point"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="AI模型">
                <el-select v-model="analysisParams.aiModel" placeholder="选择AI模型">
                  <el-option label="本地Ollama" value="local" />
                  <el-option label="OpenAI GPT" value="openai" />
                  <el-option label="Claude" value="claude" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <!-- 污染溯源参数 -->
          <div v-if="analysisType === 'trace'">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="分析类型">
                  <el-select v-model="analysisParams.traceType">
                    <el-option label="完整分析" value="full" />
                    <el-option label="仅关联分析" value="correlation_only" />
                    <el-option label="仅贡献度分析" value="contribution_only" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="时间范围">
                  <el-select v-model="analysisParams.timeRange">
                    <el-option label="最近7天" value="7d" />
                    <el-option label="最近30天" value="30d" />
                    <el-option label="最近90天" value="90d" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <!-- 水质预测参数 -->
          <div v-if="analysisType === 'prediction'">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="预测时长">
                  <el-select v-model="analysisParams.predictionHours">
                    <el-option label="24小时" :value="24" />
                    <el-option label="48小时" :value="48" />
                    <el-option label="72小时" :value="72" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="包含气象数据">
                  <el-switch v-model="analysisParams.includeWeather" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="极端事件预警">
                  <el-switch v-model="analysisParams.includeExtremeEvents" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <!-- 综合分析参数 -->
          <div v-if="analysisType === 'comprehensive'">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="包含溯源">
                  <el-switch v-model="analysisParams.includeTrace" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="包含预测">
                  <el-switch v-model="analysisParams.includePrediction" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="预测时长">
                  <el-select v-model="analysisParams.predictionHours">
                    <el-option label="24小时" :value="24" />
                    <el-option label="48小时" :value="48" />
                    <el-option label="72小时" :value="72" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </div>
        </el-form>
      </el-card>
    </div>

    <!-- 分析结果展示 -->
    <div class="analysis-results" v-if="analysisResults">
      <!-- 污染溯源结果 -->
      <div v-if="analysisType === 'trace' && analysisResults.data">
        <el-card class="result-card">
          <template #header>
            <span>污染溯源分析结果</span>
            <el-tag :type="getConfidenceType(analysisResults.data.confidence_score)">
              置信度: {{ (analysisResults.data.confidence_score * 100).toFixed(1) }}%
            </el-tag>
          </template>

          <el-row :gutter="20">
            <!-- 上下游关联 -->
            <el-col :span="12">
              <h4>上下游关联分析</h4>
              <el-table :data="analysisResults.data.upstream_correlations" size="small">
                <el-table-column prop="upstream_point" label="上游监测点" />
                <el-table-column prop="correlation" label="相关系数">
                  <template #default="{ row }">
                    <el-progress 
                      :percentage="Math.abs(row.correlation) * 100" 
                      :color="row.correlation > 0 ? '#67c23a' : '#f56c6c'"
                      :show-text="false"
                      style="width: 60px"
                    />
                    <span style="margin-left: 10px">{{ row.correlation.toFixed(3) }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="time_delay_minutes" label="延迟(分钟)" />
              </el-table>
            </el-col>

            <!-- 贡献度分析 -->
            <el-col :span="12">
              <h4>污染源贡献度</h4>
              <div v-for="source in analysisResults.data.contribution_analysis.contributions" :key="source.name" class="contribution-item">
                <div class="source-info">
                  <span class="source-name">{{ source.name }}</span>
                  <el-tag size="small">{{ source.type }}</el-tag>
                </div>
                <el-progress 
                  :percentage="source.contribution_percentage" 
                  :color="getContributionColor(source.contribution_percentage)"
                />
                <span class="contribution-value">{{ source.contribution_percentage.toFixed(1) }}%</span>
              </div>
            </el-col>
          </el-row>

          <!-- 反向追溯结果 -->
          <el-row v-if="analysisResults.data.reverse_trace.potential_sources" style="margin-top: 20px">
            <el-col :span="24">
              <h4>反向追溯结果</h4>
              <el-table :data="analysisResults.data.reverse_trace.potential_sources" size="small">
                <el-table-column prop="source_name" label="污染源" />
                <el-table-column prop="source_type" label="类型" />
                <el-table-column prop="location" label="位置" />
                <el-table-column prop="contribution_percentage" label="贡献度">
                  <template #default="{ row }">
                    {{ row.contribution_percentage.toFixed(1) }}%
                  </template>
                </el-table-column>
                <el-table-column prop="confidence" label="置信度">
                  <template #default="{ row }">
                    <el-tag :type="getConfidenceType(row.confidence)">
                      {{ (row.confidence * 100).toFixed(1) }}%
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </el-col>
          </el-row>
        </el-card>
      </div>

      <!-- 水质预测结果 -->
      <div v-if="analysisType === 'prediction' && analysisResults.data">
        <el-card class="result-card">
          <template #header>
            <span>水质预测分析结果</span>
            <el-tag :type="getReliabilityType(analysisResults.data.model_performance?.model_reliability)">
              模型可靠性: {{ analysisResults.data.model_performance?.model_reliability || '未知' }}
            </el-tag>
          </template>

          <!-- 预测图表 -->
          <el-row :gutter="20">
            <el-col :span="16">
              <h4>多指标预测趋势</h4>
              <div ref="predictionChart" style="width: 100%; height: 400px"></div>
            </el-col>
            <el-col :span="8">
              <h4>极端事件预警</h4>
              <div v-if="analysisResults.data.extreme_events.length > 0">
                <el-timeline>
                  <el-timeline-item
                    v-for="event in analysisResults.data.extreme_events"
                    :key="event.timestamp"
                    :timestamp="event.timestamp"
                    :type="getSeverityType(event.severity)"
                  >
                    <el-card size="small">
                      <div class="event-content">
                        <strong>{{ event.metric }}</strong>
                        <el-tag :type="getSeverityType(event.severity)" size="small">
                          {{ event.severity }}
                        </el-tag>
                        <p>预测值: {{ event.predicted_value?.toFixed(2) }}</p>
                        <p>持续时间: {{ event.duration_hours }}小时</p>
                      </div>
                    </el-card>
                  </el-timeline-item>
                </el-timeline>
              </div>
              <div v-else>
                <el-empty description="暂无极端事件预警" />
              </div>
            </el-col>
          </el-row>

          <!-- 修复效果预测 -->
          <el-row v-if="analysisResults.data.remediation_effects" style="margin-top: 20px">
            <el-col :span="24">
              <h4>治理措施效果预测</h4>
              <el-table :data="analysisResults.data.remediation_effects" size="small">
                <el-table-column prop="measure_name" label="治理措施" />
                <el-table-column prop="measure_type" label="类型" />
                <el-table-column prop="recommendation_score" label="推荐分数">
                  <template #default="{ row }">
                    <el-progress 
                      :percentage="row.recommendation_score" 
                      :color="getScoreColor(row.recommendation_score)"
                      style="width: 80px"
                    />
                  </template>
                </el-table-column>
                <el-table-column prop="suitability" label="适用性">
                  <template #default="{ row }">
                    <el-tag :type="getSuitabilityType(row.suitability)">
                      {{ getSuitabilityText(row.suitability) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="cost_analysis.implementation_cost" label="实施成本">
                  <template #default="{ row }">
                    ¥{{ row.cost_analysis?.implementation_cost?.toLocaleString() }}
                  </template>
                </el-table-column>
              </el-table>
            </el-col>
          </el-row>
        </el-card>
      </div>

      <!-- 综合分析结果 -->
      <div v-if="analysisType === 'comprehensive' && analysisResults.data?.comprehensive_report">
        <el-card class="result-card">
          <template #header>
            <span>综合分析报告</span>
            <el-tag :type="getRiskType(analysisResults.data.comprehensive_report.executive_summary.overall_risk_level)">
              风险等级: {{ getRiskText(analysisResults.data.comprehensive_report.executive_summary.overall_risk_level) }}
            </el-tag>
          </template>

          <!-- 执行摘要 -->
          <el-row :gutter="20">
            <el-col :span="24">
              <h4>执行摘要</h4>
              <div class="executive-summary">
                <div class="summary-item">
                  <strong>监测点:</strong> {{ analysisResults.data.comprehensive_report.executive_summary.location }}
                </div>
                <div class="summary-item">
                  <strong>分析时间:</strong> {{ formatDateTime(analysisResults.data.comprehensive_report.executive_summary.analysis_time) }}
                </div>
                <div class="summary-item">
                  <strong>关键发现:</strong>
                  <ul>
                    <li v-for="finding in analysisResults.data.comprehensive_report.executive_summary.key_findings" :key="finding">
                      {{ finding }}
                    </li>
                  </ul>
                </div>
                <div class="summary-item">
                  <strong>建议措施:</strong>
                  <ul>
                    <li v-for="recommendation in analysisResults.data.comprehensive_report.executive_summary.recommendations" :key="recommendation">
                      {{ recommendation }}
                    </li>
                  </ul>
                </div>
              </div>
            </el-col>
          </el-row>

          <!-- 详细分析结果 -->
          <el-row :gutter="20" style="margin-top: 20px">
            <el-col :span="12">
              <h4>污染溯源摘要</h4>
              <div v-if="analysisResults.data.comprehensive_report.pollution_trace_summary">
                <p><strong>置信度:</strong> {{ (analysisResults.data.comprehensive_report.pollution_trace_summary.confidence_score * 100).toFixed(1) }}%</p>
                <p><strong>上游关联:</strong> {{ analysisResults.data.comprehensive_report.pollution_trace_summary.upstream_correlations }}个</p>
                <p><strong>主要污染源:</strong></p>
                <ul>
                  <li v-for="source in analysisResults.data.comprehensive_report.pollution_trace_summary.dominant_sources" :key="source.name">
                    {{ source.name }} ({{ source.contribution.toFixed(1) }}%)
                  </li>
                </ul>
              </div>
            </el-col>
            <el-col :span="12">
              <h4>预测摘要</h4>
              <div v-if="analysisResults.data.comprehensive_report.prediction_summary">
                <p><strong>预测时长:</strong> {{ analysisResults.data.comprehensive_report.prediction_summary.prediction_hours }}小时</p>
                <p><strong>极端事件:</strong> {{ analysisResults.data.comprehensive_report.prediction_summary.extreme_events_count }}个</p>
                <p><strong>严重事件:</strong> {{ analysisResults.data.comprehensive_report.prediction_summary.critical_events_count }}个</p>
                <p><strong>模型可靠性:</strong> {{ analysisResults.data.comprehensive_report.prediction_summary.model_reliability }}</p>
              </div>
            </el-col>
          </el-row>

          <!-- 行动计划 -->
          <el-row v-if="analysisResults.data.comprehensive_report.action_plan" style="margin-top: 20px">
            <el-col :span="24">
              <h4>推荐行动计划</h4>
              <el-timeline>
                <el-timeline-item
                  v-for="action in analysisResults.data.comprehensive_report.action_plan"
                  :key="action.measure"
                  :timestamp="`优先级: ${action.priority}`"
                  :type="action.priority === 'high' ? 'danger' : 'primary'"
                >
                  <el-card>
                    <div class="action-content">
                      <h5>{{ action.measure }}</h5>
                      <p><strong>适用性:</strong> {{ getSuitabilityText(action.suitability) }}</p>
                      <p><strong>实施成本:</strong> ¥{{ action.implementation_cost?.toLocaleString() }}</p>
                      <p><strong>预期改善:</strong></p>
                      <ul>
                        <li v-for="(value, key) in action.expected_improvement" :key="key">
                          {{ key }}: {{ value.direction === 'increase' ? '提升' : '降低' }} {{ value.improvement_percentage.toFixed(1) }}%
                        </li>
                      </ul>
                    </div>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </el-col>
          </el-row>
        </el-card>
      </div>
    </div>

    <!-- 分析进度提示 -->
    <div v-if="analyzing" class="analysis-progress">
      <el-card>
        <div class="progress-content">
          <el-progress :percentage="progressPercentage" :status="progressStatus" />
          <p>{{ progressMessage }}</p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { aiApi } from '@/api/ai'

// 响应式数据
const analysisType = ref('trace')
const analyzing = ref(false)
const progressPercentage = ref(0)
const progressStatus = ref('')
const progressMessage = ref('')
const analysisResults = ref(null)
const predictionChart = ref(null)

// 分析参数
const analysisParams = reactive({
  targetLocation: 'P-042',
  aiModel: 'local',
  // 污染溯源参数
  traceType: 'full',
  timeRange: '7d',
  // 水质预测参数
  predictionHours: 48,
  includeWeather: true,
  includeExtremeEvents: true,
  // 综合分析参数
  includeTrace: true,
  includePrediction: true
})

// 监测点列表
const monitoringPoints = ref([
  'P-042', 'P-038', 'P-040', 'P-035', 'P-045', 'P-048'
])

// 生命周期
onMounted(() => {
  // 初始化
})

// 方法
const onAnalysisTypeChange = (type) => {
  // 重置分析结果
  analysisResults.value = null
  
  // 根据类型调整默认参数
  if (type === 'comprehensive') {
    analysisParams.includeTrace = true
    analysisParams.includePrediction = true
  }
}

const runAnalysis = async () => {
  analyzing.value = true
  progressPercentage.value = 0
  progressStatus.value = ''
  progressMessage.value = '准备分析...'
  
  try {
    // 获取AI配置
    const aiConfig = aiApi.getAIConfig()
    
    // 构建请求参数
    const requestData = {
      target_location: analysisParams.targetLocation,
      ai_config: aiConfig
    }
    
    // 根据分析类型添加特定参数
    if (analysisType.value === 'trace') {
      Object.assign(requestData, {
        analysis_type: analysisParams.traceType,
        time_range: analysisParams.timeRange
      })
      progressMessage.value = '执行污染溯源分析...'
    } else if (analysisType.value === 'prediction') {
      Object.assign(requestData, {
        prediction_hours: analysisParams.predictionHours,
        include_weather: analysisParams.includeWeather,
        include_extreme_events: analysisParams.includeExtremeEvents
      })
      progressMessage.value = '执行水质预测分析...'
    } else if (analysisType.value === 'comprehensive') {
      Object.assign(requestData, {
        include_trace: analysisParams.includeTrace,
        include_prediction: analysisParams.includePrediction,
        prediction_hours: analysisParams.predictionHours
      })
      progressMessage.value = '执行综合分析...'
    }
    
    progressPercentage.value = 30
    
    // 发送API请求
    let response
    if (analysisType.value === 'trace') {
      response = await fetch('/api/ai/analysis/pollution-trace/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      })
    } else if (analysisType.value === 'prediction') {
      response = await fetch('/api/ai/analysis/water-quality-prediction/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      })
    } else if (analysisType.value === 'comprehensive') {
      response = await fetch('/api/ai/analysis/comprehensive/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      })
    }
    
    progressPercentage.value = 70
    progressMessage.value = '处理分析结果...'
    
    if (!response.ok) {
      throw new Error(`分析失败: ${response.status}`)
    }
    
    const result = await response.json()
    
    if (result.success) {
      analysisResults.value = result
      progressPercentage.value = 100
      progressStatus.value = 'success'
      progressMessage.value = '分析完成！'
      
      // 如果是预测分析，绘制图表
      if (analysisType.value === 'prediction' && result.data?.predictions) {
        await nextTick()
        drawPredictionChart(result.data.predictions)
      }
      
      ElMessage.success('分析完成！')
    } else {
      throw new Error(result.error || '分析失败')
    }
    
  } catch (error) {
    console.error('分析失败:', error)
    progressStatus.value = 'exception'
    progressMessage.value = `分析失败: ${error.message}`
    ElMessage.error(`分析失败: ${error.message}`)
  } finally {
    setTimeout(() => {
      analyzing.value = false
    }, 2000)
  }
}

const drawPredictionChart = (predictions) => {
  if (!predictionChart.value) return
  
  const chart = echarts.init(predictionChart.value)
  
  // 按指标分组数据
  const metrics = {}
  predictions.forEach(pred => {
    if (!metrics[pred.metric]) {
      metrics[pred.metric] = []
    }
    metrics[pred.metric].push({
      time: pred.timestamp,
      value: pred.predicted_value,
      hour: pred.hour_ahead
    })
  })
  
  // 准备图表数据
  const series = []
  const colors = {
    ph_value: '#5470c6',
    dissolved_oxygen: '#91cc75',
    turbidity: '#fac858',
    conductivity: '#ee6666',
    ammonia_nitrogen: '#73c0de'
  }
  
  Object.keys(metrics).forEach(metric => {
    const data = metrics[metric].sort((a, b) => a.hour - b.hour)
    
    series.push({
      name: getMetricName(metric),
      type: 'line',
      data: data.map(item => [item.hour, item.value]),
      smooth: true,
      lineStyle: {
        color: colors[metric] || '#666'
      }
    })
  })
  
  const option = {
    title: {
      text: '水质指标预测趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        let result = `时间: ${params[0].value[0]}小时后<br/>`
        params.forEach(param => {
          result += `${param.seriesName}: ${param.value[1]?.toFixed(2)}<br/>`
        })
        return result
      }
    },
    legend: {
      data: Object.keys(metrics).map(metric => getMetricName(metric)),
      bottom: 0
    },
    xAxis: {
      type: 'value',
      name: '预测时间(小时)',
      min: 0,
      max: analysisParams.predictionHours
    },
    yAxis: {
      type: 'value',
      name: '指标值'
    },
    series: series
  }
  
  chart.setOption(option)
  
  // 响应式调整
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

// 辅助方法
const getMetricName = (metric) => {
  const names = {
    ph_value: 'pH值',
    dissolved_oxygen: '溶解氧',
    turbidity: '浊度',
    conductivity: '电导率',
    ammonia_nitrogen: '氨氮'
  }
  return names[metric] || metric
}

const getConfidenceType = (score) => {
  if (score > 0.8) return 'success'
  if (score > 0.6) return 'warning'
  return 'danger'
}

const getReliabilityType = (reliability) => {
  if (reliability === 'high') return 'success'
  if (reliability === 'medium') return 'warning'
  return 'danger'
}

const getSeverityType = (severity) => {
  const types = {
    red: 'danger',
    orange: 'warning',
    yellow: 'primary',
    blue: 'info'
  }
  return types[severity] || 'info'
}

const getContributionColor = (percentage) => {
  if (percentage > 50) return '#f56c6c'
  if (percentage > 30) return '#e6a23c'
  if (percentage > 15) return '#409eff'
  return '#67c23a'
}

const getScoreColor = (score) => {
  if (score > 80) return '#67c23a'
  if (score > 60) return '#e6a23c'
  return '#f56c6c'
}

const getSuitabilityType = (suitability) => {
  const types = {
    highly_suitable: 'success',
    suitable: 'primary',
    moderately_suitable: 'warning',
    not_suitable: 'danger'
  }
  return types[suitability] || 'info'
}

const getSuitabilityText = (suitability) => {
  const texts = {
    highly_suitable: '高度适用',
    suitable: '适用',
    moderately_suitable: '中等适用',
    not_suitable: '不适用'
  }
  return texts[suitability] || suitability
}

const getRiskType = (risk) => {
  const types = {
    high: 'danger',
    medium: 'warning',
    low: 'success'
  }
  return types[risk] || 'info'
}

const getRiskText = (risk) => {
  const texts = {
    high: '高风险',
    medium: '中风险',
    low: '低风险'
  }
  return texts[risk] || risk
}

const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return ''
  return new Date(dateTimeStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.enhanced-analysis {
  padding: 20px;
}

.analysis-header {
  margin-bottom: 20px;
}

.selector-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selector-content h3 {
  margin: 0;
  color: #303133;
}

.analysis-params {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.analysis-results {
  margin-top: 20px;
}

.result-card {
  margin-bottom: 20px;
}

.contribution-item {
  margin-bottom: 15px;
  padding: 10px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.source-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.source-name {
  font-weight: bold;
}

.contribution-value {
  margin-left: 10px;
  font-size: 12px;
  color: #909399;
}

.event-content {
  font-size: 12px;
}

.action-content h5 {
  margin: 0 0 10px 0;
  color: #303133;
}

.action-content p {
  margin: 5px 0;
  font-size: 12px;
  color: #606266;
}

.executive-summary {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}

.summary-item {
  margin-bottom: 10px;
}

.summary-item ul {
  margin: 5px 0;
  padding-left: 20px;
}

.summary-item li {
  margin-bottom: 5px;
  color: #606266;
}

.analysis-progress {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1000;
  min-width: 300px;
}

.progress-content {
  text-align: center;
}

.progress-content p {
  margin-top: 10px;
  color: #606266;
}
</style>
