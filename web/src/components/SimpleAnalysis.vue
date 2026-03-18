<template>
  <div class="simple-analysis">
    <el-card class="analysis-card">
      <template #header>
        <div class="card-header">
          <h3>🧠 智能分析功能</h3>
          <el-tag type="success">已集成</el-tag>
        </div>
      </template>
      
      <div class="analysis-content">
        <el-row :gutter="20">
          <!-- 污染溯源 -->
          <el-col :span="8">
            <div class="feature-card">
              <div class="feature-icon">🔍</div>
              <h4>污染溯源分析</h4>
              <ul>
                <li>上下游关联分析</li>
                <li>扩散模型模拟</li>
                <li>贡献度分析</li>
                <li>反向追溯</li>
              </ul>
              <el-button type="primary" size="small" @click="testTraceAnalysis">
                测试溯源分析
              </el-button>
            </div>
          </el-col>
          
          <!-- 水质预测 -->
          <el-col :span="8">
            <div class="feature-card">
              <div class="feature-icon">📈</div>
              <h4>水质预测分析</h4>
              <ul>
                <li>多因素预测</li>
                <li>极端事件预警</li>
                <li>影响范围预测</li>
                <li>修复效果模拟</li>
              </ul>
              <el-button type="success" size="small" @click="testPredictionAnalysis">
                测试预测分析
              </el-button>
            </div>
          </el-col>
          
          <!-- 综合分析 -->
          <el-col :span="8">
            <div class="feature-card">
              <div class="feature-icon">🎯</div>
              <h4>综合决策支持</h4>
              <ul>
                <li>风险评估</li>
                <li>治理建议</li>
                <li>成本效益分析</li>
                <li>报告生成</li>
              </ul>
              <el-button type="warning" size="small" @click="testComprehensiveAnalysis">
                测试综合分析
              </el-button>
            </div>
          </el-col>
        </el-row>
        
        <!-- 测试结果区域 -->
        <div v-if="testResult" class="test-result">
          <el-divider>测试结果</el-divider>
          <el-alert
            :title="testResult.title"
            :type="testResult.type"
            :description="testResult.description"
            show-icon
            :closable="false"
          />
        </div>
        
        <!-- API状态检查 -->
        <div class="api-status">
          <el-divider>API状态检查</el-divider>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-button @click="checkBackendStatus" :loading="checkingBackend">
                检查后端API状态
              </el-button>
            </el-col>
            <el-col :span="12">
              <div v-if="apiStatus">
                <el-tag :type="apiStatus.type">
                  {{ apiStatus.message }}
                </el-tag>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

// 响应式数据
const testResult = ref(null)
const checkingBackend = ref(false)
const apiStatus = ref(null)

// 方法
const testTraceAnalysis = async () => {
  try {
    ElMessage.info('正在测试污染溯源分析...')
    
    const response = await fetch('/api/ai/analysis/pollution-trace/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        target_location: 'P-042',
        analysis_type: 'full',
        time_range: '7d',
        ai_config: {
          modelType: 'local',
          localUrl: 'http://localhost:11434/v1',
          localModel: 'qwen2.5-coder:7b'
        }
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      testResult.value = {
        title: '污染溯源分析测试成功',
        type: 'success',
        description: `分析完成，置信度: ${result.data?.confidence_score ? (result.data.confidence_score * 100).toFixed(1) : '未知'}%`
      }
    } else {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
  } catch (error) {
    console.error('污染溯源分析测试失败:', error)
    testResult.value = {
      title: '污染溯源分析测试失败',
      type: 'error',
      description: `错误信息: ${error.message}`
    }
  }
}

const testPredictionAnalysis = async () => {
  try {
    ElMessage.info('正在测试水质预测分析...')
    
    const response = await fetch('/api/ai/analysis/water-quality-prediction/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        target_location: 'P-042',
        prediction_hours: 48,
        include_weather: true,
        include_extreme_events: true,
        ai_config: {
          modelType: 'local',
          localUrl: 'http://localhost:11434/v1',
          localModel: 'qwen2.5-coder:7b'
        }
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      const extremeEvents = result.data?.extreme_events || []
      testResult.value = {
        title: '水质预测分析测试成功',
        type: 'success',
        description: `预测完成，检测到${extremeEvents.length}个极端事件，模型可靠性: ${result.data?.model_performance?.model_reliability || '未知'}`
      }
    } else {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
  } catch (error) {
    console.error('水质预测分析测试失败:', error)
    testResult.value = {
      title: '水质预测分析测试失败',
      type: 'error',
      description: `错误信息: ${error.message}`
    }
  }
}

const testComprehensiveAnalysis = async () => {
  try {
    ElMessage.info('正在测试综合分析...')
    
    const response = await fetch('/api/ai/analysis/comprehensive/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        target_location: 'P-042',
        include_trace: true,
        include_prediction: true,
        prediction_hours: 48,
        ai_config: {
          modelType: 'local',
          localUrl: 'http://localhost:11434/v1',
          localModel: 'qwen2.5-coder:7b'
        }
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      const riskLevel = result.data?.comprehensive_report?.executive_summary?.overall_risk_level || 'unknown'
      testResult.value = {
        title: '综合分析测试成功',
        type: 'success',
        description: `综合分析完成，风险等级: ${riskLevel}，包含${Object.keys(result.data?.analysis_results || {}).length}个分析组件`
      }
    } else {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
  } catch (error) {
    console.error('综合分析测试失败:', error)
    testResult.value = {
      title: '综合分析测试失败',
      type: 'error',
      description: `错误信息: ${error.message}`
    }
  }
}

const checkBackendStatus = async () => {
  checkingBackend.value = true
  apiStatus.value = null
  
  try {
    // 测试基础API连接
    const response = await fetch('/api/ai/analysis/capabilities/')
    
    if (response.ok) {
      const result = await response.json()
      apiStatus.value = {
        type: 'success',
        message: '后端API连接正常'
      }
      ElMessage.success('后端API状态良好')
    } else {
      throw new Error(`HTTP ${response.status}`)
    }
  } catch (error) {
    console.error('后端API检查失败:', error)
    apiStatus.value = {
      type: 'danger',
      message: '后端API连接失败'
    }
    ElMessage.error('后端API服务未启动或配置错误')
  } finally {
    checkingBackend.value = false
  }
}
</script>

<style scoped>
.simple-analysis {
  margin: 20px 0;
}

.analysis-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.analysis-content {
  padding: 20px 0;
}

.feature-card {
  text-align: center;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.feature-card h4 {
  margin: 10px 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
}

.feature-card ul {
  list-style: none;
  padding: 0;
  margin: 15px 0;
  text-align: left;
}

.feature-card li {
  padding: 5px 0;
  color: #7f8c8d;
  font-size: 14px;
  border-bottom: 1px solid #ecf0f1;
}

.feature-card li:last-child {
  border-bottom: none;
}

.feature-card li:before {
  content: "✓";
  color: #27ae60;
  font-weight: bold;
  margin-right: 8px;
}

.test-result {
  margin-top: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.api-status {
  margin-top: 20px;
  padding: 20px;
  background: #fff3cd;
  border-radius: 8px;
  border: 1px solid #ffeaa7;
}
</style>
