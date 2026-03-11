<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.totalRecords }}</div>
          <div class="stat-label">总记录数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">💧</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.avgPh }}</div>
          <div class="stat-label">平均pH值</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🌊</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.avgTurbidity }}</div>
          <div class="stat-label">平均浊度</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⚠️</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.alertCount }}</div>
          <div class="stat-label">报警数量</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-container">
      <div class="chart-card">
        <h3>水质趋势图</h3>
        <div class="chart-placeholder">
          <div class="chart-info">
            <p>📈 7天水质变化趋势</p>
            <p>显示pH值、余氯、浊度等指标变化</p>
          </div>
        </div>
      </div>
      <div class="chart-card">
        <h3>报警分布</h3>
        <div class="chart-placeholder">
          <div class="chart-info">
            <p>🥧 各类型报警占比</p>
            <p>pH异常、余氯超标、浊度偏高等</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 最近报警 -->
    <div class="alerts-section">
      <h3>最近报警</h3>
      <div class="alert-list">
        <div v-for="alert in recentAlerts" :key="alert.id" class="alert-item" :class="alert.level">
          <div class="alert-info">
            <span class="alert-point">{{ alert.point }}</span>
            <span class="alert-time">{{ alert.time }}</span>
            <span class="alert-message">{{ alert.message }}</span>
          </div>
          <div class="alert-level">{{ alert.level === 'high' ? '严重' : '警告' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const stats = ref({
  totalRecords: 156,
  avgPh: 7.2,
  avgTurbidity: 1.8,
  alertCount: 3
})

const recentAlerts = ref([
  {
    id: 1,
    point: '监测点001',
    time: '2024-03-11 08:00',
    message: 'pH值偏高 (8.5)',
    level: 'warning'
  },
  {
    id: 2,
    point: '监测点002',
    time: '2024-03-11 07:30',
    message: '余氯超标 (4.5 mg/L)',
    level: 'high'
  },
  {
    id: 3,
    point: '监测点003',
    time: '2024-03-11 07:00',
    message: '浊度偏高 (6.2 NTU)',
    level: 'warning'
  }
])

onMounted(() => {
  // 模拟数据加载
  console.log('仪表盘加载完成')
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
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
