<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h2>仪表盘概览</h2>
      <button class="refresh-btn" @click="loadStats" :disabled="loading">
        🔄 {{ loading ? '刷新中...' : '刷新数据' }}
      </button>
    </div>
    
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.totalRecords }}</div>
          <div class="stat-label">总记录数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">�</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.totalPoints }}</div>
          <div class="stat-label">监测点数量</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">⚠️</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.alertCount }}</div>
          <div class="stat-label">超标数量</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">🌐</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.onlineRate }}%</div>
          <div class="stat-label">设备在线率</div>
        </div>
      </div>
    </div>
    
    <div class="dashboard-content">
      <div class="charts-section">
        <div class="chart-placeholder">
          <h3>📈 数据趋势图</h3>
          <p>图表功能开发中...</p>
        </div>
        
        <div class="chart-placeholder">
          <h3>📊 指标分布图</h3>
          <p>图表功能开发中...</p>
        </div>
      </div>
      
      <div class="alerts-section">
        <h3>🚨 最近报警</h3>
        <div class="alerts-list">
          <div v-for="alert in recentAlerts" :key="alert.record_id" class="alert-item" :class="alert.alertType">
            <div class="alert-header">
              <span class="alert-point">{{ alert.point_id }}</span>
              <span class="alert-time">{{ alert.date }} {{ alert.time }}</span>
            </div>
            <div class="alert-message">{{ alert.alertMessage }}</div>
            <div class="alert-level">{{ alert.alertType === 'danger' ? '严重' : '警告' }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { waterQualityApi } from '@/api/waterQuality'

const stats = ref({
  totalRecords: 0,
  totalPoints: 0,
  alertCount: 0,
  onlineRate: 0
})

const recentAlerts = ref([])
const loading = ref(false)

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
      alerts.push(`${field}偏低`)
    }
    if (threshold.max !== undefined && value > threshold.max) {
      alerts.push(`${field}偏高`)
    }
  }
  
  if (alerts.length === 0) return 'normal'
  if (alerts.some(alert => alert.includes('偏高'))) {
    return alerts.length > 1 ? 'danger' : 'warning'
  }
  return 'warning'
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
      .slice(0, 5)
      .map(record => ({
        ...record,
        alertType: getAlertType(record),
        alertMessage: getAlertMessage(record)
      }))
    
  } catch (error) {
    console.error('加载统计数据失败:', error)
    // 使用模拟数据
    stats.value = {
      totalRecords: 8,
      totalPoints: 5,
      alertCount: 2,
      onlineRate: 80
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

// 获取报警类型
const getAlertType = (record) => {
  const status = checkRecordStatus(record)
  return status
}

// 获取报警消息
const getAlertMessage = (record) => {
  const alerts = []
  
  if (record.chlorine < alertThresholds.chlorine.min) {
    alerts.push(`余氯偏低(${record.chlorine} mg/L)`)
  } else if (record.chlorine > alertThresholds.chlorine.max) {
    alerts.push(`余氯超标(${record.chlorine} mg/L)`)
  }
  
  if (record.conductivity > alertThresholds.conductivity.max) {
    alerts.push(`电导率超标(${record.conductivity} µS/cm)`)
  }
  
  if (record.ph < alertThresholds.ph.min) {
    alerts.push(`pH值偏低(${record.ph})`)
  } else if (record.ph > alertThresholds.ph.max) {
    alerts.push(`pH值超标(${record.ph})`)
  }
  
  if (record.orp < alertThresholds.orp.min) {
    alerts.push(`ORP偏低(${record.orp} mV)`)
  }
  
  if (record.turbidity > alertThresholds.turbidity.max) {
    alerts.push(`浊度超标(${record.turbidity} NTU)`)
  }
  
  return alerts.join('，')
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.dashboard-header h2 {
  margin: 0;
  color: #333;
}

.refresh-btn {
  padding: 8px 16px;
  background: #409EFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.refresh-btn:hover:not(:disabled) {
  background: #66b1ff;
}

.refresh-btn:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 15px;
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.stat-icon {
  font-size: 32px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f5ff;
  border-radius: 12px;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: 600;
  color: #1890ff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.chart-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.chart-card h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 16px;
}

.chart-placeholder {
  height: 300px;
  background: #fafafa;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed #d9d9d9;
}

.chart-info {
  text-align: center;
  color: #666;
}

.chart-info p {
  margin: 5px 0;
}

.alerts-section {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.alerts-section h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 16px;
}

.alert-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.alert-item {
  padding: 15px;
  border-radius: 6px;
  border-left: 4px solid;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-item.warning {
  background: #fff7e6;
  border-left-color: #faad14;
}

.alert-item.high {
  background: #fff2f0;
  border-left-color: #ff4d4f;
}

.alert-info {
  display: flex;
  gap: 15px;
  align-items: center;
  flex: 1;
}

.alert-point {
  font-weight: 600;
  color: #333;
  min-width: 80px;
}

.alert-time {
  color: #666;
  font-size: 14px;
  min-width: 120px;
}

.alert-message {
  color: #666;
}

.alert-level {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.alert-item.warning .alert-level {
  background: #faad14;
  color: #fff;
}

.alert-item.high .alert-level {
  background: #ff4d4f;
  color: #fff;
}

/* 深色主题 */
.dark .dashboard .stat-card,
.dark .dashboard .chart-card,
.dark .dashboard .alerts-section {
  background: #1f1f1f;
  color: #fff;
}

.dark .dashboard .stat-number {
  color: #1890ff;
}

.dark .dashboard .stat-label,
.dark .dashboard .chart-info p,
.dark .dashboard .alert-info {
  color: #ccc;
}

.dark .dashboard .chart-placeholder {
  background: #2a2a2a;
  border-color: #4c4d4f;
}

.dark .dashboard .alert-item.warning {
  background: #2b2111;
}

.dark .dashboard .alert-item.high {
  background: #2a1215;
}
</style>
