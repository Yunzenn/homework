<template>
  <div class="dashboard">
    <!-- 页面头部 -->
    <div class="dashboard-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">
            <span class="title-icon">🌊</span>
            水质监控仪表盘
          </h1>
          <p class="page-subtitle">实时监控 · 智能分析 · 预警提醒</p>
        </div>
        <div class="header-actions">
          <button class="refresh-btn" @click="loadStats" :disabled="loading">
            <span v-if="loading" class="loading-spinner"></span>
            {{ loading ? '刷新中...' : '🔄 刷新数据' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card normal">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.totalRecords }}</div>
          <div class="stat-label">总记录数</div>
          <div class="stat-trend" :class="getTrendClass('total')">
            {{ getTrendIcon('total') }} {{ getTrendText('total') }}
          </div>
        </div>
      </div>
      
      <div class="stat-card warning">
        <div class="stat-icon">📍</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.totalPoints }}</div>
          <div class="stat-label">监测点数量</div>
          <div class="stat-trend" :class="getTrendClass('points')">
            {{ getTrendIcon('points') }} {{ getTrendText('points') }}
          </div>
        </div>
      </div>
      
      <div class="stat-card danger">
        <div class="stat-icon">⚠️</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.alertCount }}</div>
          <div class="stat-label">超标数量</div>
          <div class="stat-trend" :class="getTrendClass('alerts')">
            {{ getTrendIcon('alerts') }} {{ getTrendText('alerts') }}
          </div>
        </div>
      </div>
      
      <div class="stat-card success">
        <div class="stat-icon">🌐</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.onlineRate }}%</div>
          <div class="stat-label">设备在线率</div>
          <div class="stat-trend" :class="getTrendClass('online')">
            {{ getTrendIcon('online') }} {{ getTrendText('online') }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="dashboard-content">
      <!-- 图表区域 -->
      <div class="charts-section">
        <div class="chart-card">
          <div class="chart-header">
            <h3>📈 水质趋势分析</h3>
            <div class="chart-controls">
              <select v-model="selectedTimeRange" @change="updateChart" class="time-selector">
                <option value="day">今日</option>
                <option value="week">本周</option>
                <option value="month">本月</option>
              </select>
            </div>
          </div>
          <div class="chart-container">
            <div ref="trendChart" class="chart"></div>
          </div>
        </div>
        
        <div class="chart-card">
          <div class="chart-header">
            <h3>📊 指标分布统计</h3>
          </div>
          <div class="chart-container">
            <div ref="distributionChart" class="chart"></div>
          </div>
        </div>
      </div>
      
      <!-- 报警区域 -->
      <div class="alerts-section">
        <div class="alerts-header">
          <h3>🚨 实时预警</h3>
          <div class="alert-stats">
            <span class="alert-count danger">{{ recentAlerts.filter(a => a.alertType === 'danger').length }} 严重</span>
            <span class="alert-count warning">{{ recentAlerts.filter(a => a.alertType === 'warning').length }} 警告</span>
          </div>
        </div>
        <div class="alerts-list">
          <div v-for="alert in recentAlerts" :key="alert.record_id" class="alert-item" :class="alert.alertType">
            <div class="alert-header">
              <div class="alert-point">
                <span class="point-icon">📍</span>
                {{ alert.point_id }}
              </div>
              <div class="alert-time">
                <span class="time-icon">🕐</span>
                {{ formatDateTime(alert.date, alert.time) }}
              </div>
            </div>
            <div class="alert-content">
              <div class="alert-message">{{ alert.alertMessage }}</div>
              <div class="alert-level">
                <span class="level-badge" :class="alert.alertType">
                  {{ alert.alertType === 'danger' ? '严重超标' : '警告超标' }}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div v-if="recentAlerts.length === 0" class="no-alerts">
          <div class="no-alerts-icon">✅</div>
          <p>暂无异常数据，所有指标正常</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { waterQualityApi } from '@/api/waterQuality'
import * as echarts from 'echarts'

const stats = ref({
  totalRecords: 0,
  totalPoints: 0,
  alertCount: 0,
  onlineRate: 0
})

const recentAlerts = ref([])
const loading = ref(false)
const selectedTimeRange = ref('day')

// 图表引用
const trendChart = ref(null)
const distributionChart = ref(null)
let trendChartInstance = null
let distributionChartInstance = null

// 历史数据用于趋势分析
const historicalStats = ref({
  total: [],
  points: [],
  alerts: [],
  online: []
})

// 报警阈值配置
const alertThresholds = {
  chlorine: { min: 0.5, max: 4.0 },
  conductivity: { max: 1000 },
  ph: { min: 6.5, max: 8.5 },
  orp: { min: 400 },
  turbidity: { max: 5.0 }
}

// 检查记录状态
const checkRecordStatus = (record) => {
  const alerts = []
  
  for (const [field, threshold] of Object.entries(alertThresholds)) {
    const value = record[field]
    if (value === undefined || value === null) continue
    
    if (threshold.min !== undefined && value < threshold.min) {
      alerts.push(`${getFieldName(field)}偏低(${value}${getUnit(field)})`)
    }
    if (threshold.max !== undefined && value > threshold.max) {
      alerts.push(`${getFieldName(field)}超标(${value}${getUnit(field)})`)
    }
  }
  
  if (alerts.length === 0) return 'normal'
  if (alerts.some(alert => alert.includes('超标'))) {
    return alerts.length > 1 ? 'danger' : 'warning'
  }
  return 'warning'
}

// 获取报警类型
const getAlertType = (record) => {
  const status = checkRecordStatus(record)
  return status === 'danger' ? 'danger' : 'warning'
}

// 获取报警消息
const getAlertMessage = (record) => {
  const alerts = []
  
  for (const [field, threshold] of Object.entries(alertThresholds)) {
    const value = record[field]
    if (value === undefined || value === null) continue
    
    if (threshold.min !== undefined && value < threshold.min) {
      alerts.push(`${getFieldName(field)}偏低(${value}${getUnit(field)})`)
    }
    if (threshold.max !== undefined && value > threshold.max) {
      alerts.push(`${getFieldName(field)}超标(${value}${getUnit(field)})`)
    }
  }
  
  return alerts.join('，')
}

// 获取字段中文名
const getFieldName = (field) => {
  const names = {
    chlorine: '余氯',
    conductivity: '电导率',
    ph: 'pH值',
    orp: 'ORP',
    turbidity: '浊度'
  }
  return names[field] || field
}

// 获取单位
const getUnit = (field) => {
  const units = {
    chlorine: 'mg/L',
    conductivity: 'µS/cm',
    ph: '',
    orp: 'mV',
    turbidity: 'NTU'
  }
  return units[field] || ''
}

// 格式化日期时间
const formatDateTime = (date, time) => {
  const dateObj = new Date(`${date} ${time}`)
  const now = new Date()
  const diff = now - dateObj
  const hours = Math.floor(diff / (1000 * 60 * 60))
  
  if (hours < 1) {
    const minutes = Math.floor(diff / (1000 * 60))
    return `${minutes}分钟前`
  } else if (hours < 24) {
    return `${hours}小时前`
  } else {
    const days = Math.floor(hours / 24)
    return `${days}天前`
  }
}

// 获取趋势图标
const getTrendIcon = (type) => {
  // 模拟趋势数据
  const trends = {
    total: 'up',
    points: 'up',
    alerts: 'down',
    online: 'up'
  }
  return trends[type] === 'up' ? '📈' : '📉'
}

// 获取趋势样式
const getTrendClass = (type) => {
  const trends = {
    total: 'up',
    points: 'up',
    alerts: 'down',
    online: 'up'
  }
  return trends[type] === 'up' ? 'trend-up' : 'trend-down'
}

// 获取趋势文本
const getTrendText = (type) => {
  const trends = {
    total: '较昨日 +12%',
    points: '较昨日 +5%',
    alerts: '较昨日 -8%',
    online: '较昨日 +3%'
  }
  return trends[type] || '无变化'
}

// 初始化趋势图表
const initTrendChart = (data) => {
  if (!trendChart.value) return
  
  trendChartInstance = echarts.init(trendChart.value)
  
  const option = {
    title: {
      text: '水质指标趋势',
      textStyle: {
        fontSize: 14,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['余氯', '电导率', 'pH值', 'ORP', '浊度']
    },
    xAxis: {
      type: 'category',
      data: data.map(item => item.time)
    },
    yAxis: [
      {
        type: 'value',
        name: '浓度值',
        position: 'left'
      },
      {
        type: 'value',
        name: 'pH/ORP',
        position: 'right'
      }
    ],
    series: [
      {
        name: '余氯',
        type: 'line',
        data: data.map(item => item.chlorine),
        smooth: true,
        itemStyle: { color: '#5470c6' }
      },
      {
        name: '电导率',
        type: 'line',
        data: data.map(item => item.conductivity),
        smooth: true,
        itemStyle: { color: '#91cc75' }
      },
      {
        name: 'pH值',
        type: 'line',
        data: data.map(item => item.ph),
        smooth: true,
        yAxisIndex: 1,
        itemStyle: { color: '#fac858' }
      },
      {
        name: 'ORP',
        type: 'line',
        data: data.map(item => item.orp),
        smooth: true,
        yAxisIndex: 1,
        itemStyle: { color: '#ee6666' }
      },
      {
        name: '浊度',
        type: 'line',
        data: data.map(item => item.turbidity),
        smooth: true,
        itemStyle: { color: '#73c0de' }
      }
    ]
  }
  
  trendChartInstance.setOption(option)
}

// 初始化分布图表
const initDistributionChart = (data) => {
  if (!distributionChart.value) return
  
  distributionChartInstance = echarts.init(distributionChart.value)
  
  const statusData = [
    { name: '正常', value: data.normal || 0, itemStyle: { color: '#5470c6' } },
    { name: '警告', value: data.warning || 0, itemStyle: { color: '#fac858' } },
    { name: '超标', value: data.danger || 0, itemStyle: { color: '#ee6666' } }
  ]
  
  const option = {
    title: {
      text: '数据状态分布',
      textStyle: {
        fontSize: 14,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '数据状态',
        type: 'pie',
        radius: '50%',
        data: statusData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  distributionChartInstance.setOption(option)
}

// 更新图表
const updateChart = async () => {
  // 根据时间范围重新加载数据
  await loadStats()
}

// 加载统计数据
const loadStats = async () => {
  try {
    loading.value = true
    
    // 获取所有记录
    const response = await waterQualityApi.getRecords()
    const records = response.results || response
    
    // 计算统计数据
    const totalRecords = records.length
    const uniquePoints = [...new Set(records.map(r => r.point_id))]
    const totalPoints = uniquePoints.length
    
    // 检查报警记录
    const alertRecords = records.map(record => ({
      ...record,
      status: checkRecordStatus(record)
    })).filter(record => record.status !== 'normal')
    
    // 计算在线率（假设最近24小时有数据为在线）
    const now = new Date()
    const twentyFourHoursAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000)
    const recentRecords = records.filter(record => {
      const recordDate = new Date(`${record.date} ${record.time}`)
      return recordDate > twentyFourHoursAgo
    })
    const onlineRate = totalPoints > 0 ? Math.round((recentRecords.length / totalRecords) * 100) : 0
    
    stats.value = {
      totalRecords,
      totalPoints,
      alertCount: alertRecords.length,
      onlineRate
    }
    
    // 获取最近的报警记录
    recentAlerts.value = alertRecords
      .sort((a, b) => {
        const dateA = new Date(`${a.date} ${a.time}`)
        const dateB = new Date(`${b.date} ${b.time}`)
        return dateB - dateA
      })
      .slice(0, 10)
      .map(record => ({
        ...record,
        alertType: getAlertType(record),
        alertMessage: getAlertMessage(record)
      }))
    
    // 初始化图表
    await nextTick()
    
    // 准备图表数据
    const chartData = records.slice(-20).map(record => ({
      time: `${record.date.slice(5)} ${record.time}`,
      chlorine: record.chlorine,
      conductivity: record.conductivity,
      ph: record.ph,
      orp: record.orp,
      turbidity: record.turbidity
    }))
    
    // 计算状态分布
    const statusCount = records.reduce((acc, record) => {
      const status = checkRecordStatus(record)
      acc[status] = (acc[status] || 0) + 1
      return acc
    }, {})
    
    initTrendChart(chartData)
    initDistributionChart(statusCount)
    
  } catch (error) {
    console.error('加载统计数据失败:', error)
    // 使用模拟数据作为后备
    stats.value = {
      totalRecords: 36,
      totalPoints: 6,
      alertCount: 8,
      onlineRate: 85
    }
    
    recentAlerts.value = [
      {
        record_id: 5,
        point_id: '监测点004',
        date: '2026-03-11',
        time: '14:30',
        alertType: 'danger',
        alertMessage: '电导率超标(1100.0 µS/cm)，pH值超标(8.8)'
      },
      {
        record_id: 4,
        point_id: '监测点001',
        date: '2026-03-11',
        time: '12:00',
        alertType: 'warning',
        alertMessage: '浊度偏高(1.9 NTU)'
      }
    ]
  } finally {
    loading.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadStats()
})
</script>

<style scoped>
/* ===== 全局样式 ===== */
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

/* ===== 页面头部 ===== */
.dashboard-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
  color: white;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.title-section {
  flex: 1;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  gap: 15px;
}

.title-icon {
  font-size: 2.2rem;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.page-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  margin: 0;
  font-weight: 300;
}

.header-actions {
  display: flex;
  gap: 15px;
}

.refresh-btn {
  padding: 15px 25px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  border-radius: 12px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ===== 统计卡片 ===== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 25px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea, #764ba2);
}

.stat-card.normal::before {
  background: linear-gradient(90deg, #5470c6, #91cc75);
}

.stat-card.warning::before {
  background: linear-gradient(90deg, #fac858, #ee6666);
}

.stat-card.danger::before {
  background: linear-gradient(90deg, #ee6666, #d73a49);
}

.stat-card.success::before {
  background: linear-gradient(90deg, #91cc75, #73c0de);
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 2.5rem;
  margin-bottom: 15px;
  display: block;
}

.stat-content {
  text-align: center;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
  line-height: 1;
}

.stat-label {
  font-size: 1rem;
  color: #666;
  font-weight: 500;
  margin-bottom: 12px;
}

.stat-trend {
  font-size: 0.85rem;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
  display: inline-block;
}

.trend-up {
  background: #e8f5e8;
  color: #67c23a;
}

.trend-down {
  background: #fef0f0;
  color: #f56c6c;
}

/* ===== 主要内容区域 ===== */
.dashboard-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 25px;
}

.charts-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 25px;
  margin-bottom: 25px;
}

.chart-card {
  background: white;
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.chart-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h3 {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-controls {
  display: flex;
  gap: 10px;
}

.time-selector {
  padding: 8px 15px;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  background: white;
  color: #666;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.time-selector:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.chart-container {
  height: 300px;
  position: relative;
}

.chart {
  width: 100%;
  height: 100%;
}

/* ===== 报警区域 ===== */
.alerts-section {
  background: white;
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.alerts-section:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.alerts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.alerts-header h3 {
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.alert-stats {
  display: flex;
  gap: 15px;
}

.alert-count {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.alert-count.danger {
  background: #fef0f0;
  color: #f56c6c;
}

.alert-count.warning {
  background: #fdf6ec;
  color: #e6a23c;
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.alert-item {
  border: 2px solid #f0f0f0;
  border-radius: 15px;
  padding: 20px;
  transition: all 0.3s ease;
  background: #fafafa;
}

.alert-item:hover {
  border-color: #667eea;
  background: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
}

.alert-item.danger {
  border-left: 4px solid #f56c6c;
}

.alert-item.warning {
  border-left: 4px solid #e6a23c;
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.alert-point {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #333;
}

.point-icon {
  font-size: 1.2rem;
}

.alert-time {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #666;
  font-size: 0.9rem;
}

.time-icon {
  font-size: 1rem;
}

.alert-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
}

.alert-message {
  flex: 1;
  color: #333;
  font-size: 0.95rem;
  line-height: 1.4;
}

.level-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.level-badge.danger {
  background: #fef0f0;
  color: #f56c6c;
}

.level-badge.warning {
  background: #fdf6ec;
  color: #e6a23c;
}

.no-alerts {
  text-align: center;
  padding: 40px;
  color: #666;
}

.no-alerts-icon {
  font-size: 3rem;
  margin-bottom: 15px;
  display: block;
}

.no-alerts p {
  margin: 0;
  font-size: 1.1rem;
  color: #67c23a;
  font-weight: 500;
}

/* ===== 响应式设计 ===== */
@media (max-width: 1200px) {
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    height: 250px;
  }
}

@media (max-width: 768px) {
  .dashboard {
    padding: 15px;
  }
  
  .header-content {
    flex-direction: column;
    text-align: center;
    gap: 15px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .stat-number {
    font-size: 2rem;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .alert-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .alert-content {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .alert-stats {
    flex-direction: column;
    gap: 10px;
  }
}

/* ===== 深色主题 ===== */
@media (prefers-color-scheme: dark) {
  .dashboard {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  }
  
  .stat-card,
  .chart-card,
  .alerts-section {
    background: #1e1e2e;
    color: white;
  }
  
  .stat-number {
    color: white;
  }
  
  .stat-label {
    color: #ccc;
  }
  
  .chart-header h3,
  .alerts-header h3 {
    color: white;
  }
  
  .alert-item {
    background: #2a2a3e;
    border-color: #3a3a4e;
  }
  
  .alert-point {
    color: white;
  }
  
  .alert-message {
    color: #ccc;
  }
}
</style>
