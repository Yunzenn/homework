<template>
  <div class="query-page">
    <!-- 页面标题区域 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">
            <span class="title-icon">🔍</span>
            高级查询
          </h1>
          <p class="page-subtitle">智能水质数据检索与分析</p>
        </div>
        <div class="header-stats">
          <div class="stat-card">
            <div class="stat-number">{{ stats.normal }}</div>
            <div class="stat-label">正常</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ stats.warning }}</div>
            <div class="stat-label">警告</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ stats.danger }}</div>
            <div class="stat-label">超标</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 查询表单区域 -->
    <div class="query-container">
      <div class="query-card">
        <div class="card-header">
          <div class="header-icon">📍</div>
          <h2 class="card-title">基本查询条件</h2>
        </div>
        
        <div class="card-content">
          <div class="form-grid">
            <div class="form-item">
              <label class="form-label">
                <span class="label-icon">🏷️</span>
                监测点
              </label>
              <div class="input-wrapper">
                <input 
                  type="text" 
                  v-model="queryConditions.point_id" 
                  placeholder="输入监测点编号，如：监测点001" 
                  class="form-input"
                />
              </div>
            </div>
            
            <div class="form-item">
              <label class="form-label">
                <span class="label-icon">📅</span>
                日期范围
              </label>
              <div class="date-range-wrapper">
                <div class="input-group">
                  <input 
                    type="date" 
                    v-model="queryConditions.date_start" 
                    class="form-input"
                  />
                  <span class="date-separator">至</span>
                  <input 
                    type="date" 
                    v-model="queryConditions.date_end" 
                    class="form-input"
                  />
                </div>
                <div class="quick-actions">
                  <button 
                    v-for="range in dateRanges" 
                    :key="range.value"
                    class="quick-btn"
                    @click="setDateRange(range.value)"
                  >
                    {{ range.label }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="query-card">
        <div class="card-header">
          <div class="header-icon">⚗️</div>
          <h2 class="card-title">指标阈值查询</h2>
        </div>
        
        <div class="card-content">
          <div class="indicators-grid">
            <div 
              v-for="indicator in indicators" 
              :key="indicator.key"
              class="indicator-item"
            >
              <div class="indicator-header">
                <div class="indicator-icon">{{ indicator.icon }}</div>
                <div class="indicator-info">
                  <h3 class="indicator-name">{{ indicator.name }}</h3>
                  <p class="indicator-unit">{{ indicator.unit }}</p>
                </div>
                <div class="indicator-status" :class="getRangeStatus(indicator.key)">
                  {{ getRangeStatusText(indicator.key) }}
                </div>
              </div>
              
              <div class="range-input-group">
                <div class="input-group">
                  <input 
                    type="number" 
                    :step="indicator.step"
                    v-model="queryConditions[`${indicator.key}_min`]" 
                    placeholder="最小值"
                    class="range-input"
                  />
                  <span class="range-separator">—</span>
                  <input 
                    type="number" 
                    :step="indicator.step"
                    v-model="queryConditions[`${indicator.key}_max`]" 
                    placeholder="最大值"
                    class="range-input"
                  />
                </div>
                <div class="range-info">
                  <span class="normal-range">{{ indicator.normalRange }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 快速模板 -->
      <div class="query-card">
        <div class="card-header">
          <div class="header-icon">⚡</div>
          <h2 class="card-title">快速查询模板</h2>
        </div>
        
        <div class="card-content">
          <div class="templates-grid">
            <div 
              v-for="template in queryTemplates" 
              :key="template.key"
              class="template-item"
              @click="applyTemplate(template.key)"
            >
              <div class="template-icon">{{ template.icon }}</div>
              <div class="template-content">
                <h4 class="template-title">{{ template.title }}</h4>
                <p class="template-desc">{{ template.desc }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按钮区域 -->
    <div class="actions-section">
      <div class="actions-container">
        <button 
          class="action-btn primary" 
          @click="executeQuery" 
          :disabled="loading"
        >
          <span v-if="loading" class="loading-spinner"></span>
          {{ loading ? '查询中...' : '开始查询' }}
        </button>
        <button class="action-btn secondary" @click="resetQuery">
          重置条件
        </button>
        <button 
          class="action-btn success" 
          @click="exportQueryResults" 
          :disabled="queryResults.length === 0"
        >
          导出数据
        </button>
      </div>
    </div>

    <div class="results-section" v-if="queryResults.length > 0">
      <div class="results-header">
        <h3>查询结果 ({{ queryResults.length }} 条)</h3>
        <div class="results-stats">
          <span class="stat-item normal">正常: {{ stats.normal }}</span>
          <span class="stat-item warning">警告: {{ stats.warning }}</span>
          <span class="stat-item danger">超标: {{ stats.danger }}</span>
        </div>
      </div>
      
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>监测点</th>
              <th>时间</th>
              <th>余氯</th>
              <th>电导率</th>
              <th>pH值</th>
              <th>ORP</th>
              <th>浊度</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in queryResults" :key="record.id" :class="record.status">
              <td>{{ record.id }}</td>
              <td>{{ record.point_id }}</td>
              <td>{{ record.date }} {{ record.time }}</td>
              <td>{{ record.chlorine }}</td>
              <td>{{ record.conductivity }}</td>
              <td>{{ record.ph }}</td>
              <td>{{ record.orp }}</td>
              <td>{{ record.turbidity }}</td>
              <td>
                <span class="status-badge" :class="record.status">
                  {{ record.status === 'normal' ? '正常' : record.status === 'warning' ? '警告' : '超标' }}
                </span>
              </td>
              <td>
                <button class="btn-sm" @click="viewRecord(record)">查看详情</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <div class="no-results" v-else-if="hasQueried && !loading">
      <p>😔 没有找到符合条件的记录</p>
      <button class="btn-default" @click="resetQuery">清空条件</button>
    </div>

    <div v-if="showRecordDetail" class="modal-overlay" @click="showRecordDetail = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>数据详情记录</h3>
          <button class="close-btn" @click="showRecordDetail = false">✕</button>
        </div>
        <div class="modal-body">
            <div class="detail-grid">
                <div class="detail-item"><label>监测点:</label><span>{{ selectedRecord.point_id }}</span></div>
                <div class="detail-item"><label>采样时间:</label><span>{{ selectedRecord.date }} {{ selectedRecord.time }}</span></div>
                <div class="detail-item"><label>余氯:</label><span>{{ selectedRecord.chlorine }} mg/L</span></div>
                <div class="detail-item"><label>电导率:</label><span>{{ selectedRecord.conductivity }} µS/cm</span></div>
                <div class="detail-item"><label>pH值:</label><span>{{ selectedRecord.ph }}</span></div>
                <div class="detail-item"><label>ORP:</label><span>{{ selectedRecord.orp }} mV</span></div>
                <div class="detail-item"><label>浊度:</label><span>{{ selectedRecord.turbidity }} NTU</span></div>
                <div class="detail-item">
                    <label>判定状态:</label>
                    <span class="status-badge" :class="selectedRecord.status">
                        {{ selectedRecord.status === 'normal' ? '正常' : selectedRecord.status === 'warning' ? '警告' : '超标' }}
                    </span>
                </div>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { waterQualityApi } from '@/api/waterQuality'

const queryResults = ref([])
const hasQueried = ref(false)
const loading = ref(false)
const showRecordDetail = ref(false)
const selectedRecord = ref({})

const queryConditions = ref({
  point_id: '',
  date_start: '',
  date_end: '',
  chlorine_min: '',
  chlorine_max: '',
  conductivity_min: '',
  conductivity_max: '',
  ph_min: '',
  ph_max: '',
  orp_min: '',
  orp_max: '',
  turbidity_min: '',
  turbidity_max: ''
})

// 日期范围选项
const dateRanges = ref([
  { label: '今天', value: 'today' },
  { label: '昨天', value: 'yesterday' },
  { label: '本周', value: 'week' },
  { label: '本月', value: 'month' }
])

// 水质指标配置
const indicators = ref([
  {
    key: 'chlorine',
    name: '余氯',
    unit: 'mg/L',
    icon: '🧪',
    step: '0.1',
    normalRange: '正常范围: 0.5-4.0'
  },
  {
    key: 'conductivity',
    name: '电导率',
    unit: 'µS/cm',
    icon: '⚡',
    step: '0.1',
    normalRange: '正常范围: ≤1000'
  },
  {
    key: 'ph',
    name: 'pH值',
    unit: '',
    icon: '💧',
    step: '0.1',
    normalRange: '正常范围: 6.5-8.5'
  },
  {
    key: 'orp',
    name: 'ORP',
    unit: 'mV',
    icon: '🔋',
    step: '0.1',
    normalRange: '正常范围: ≥400'
  },
  {
    key: 'turbidity',
    name: '浊度',
    unit: 'NTU',
    icon: '🌊',
    step: '0.1',
    normalRange: '正常范围: ≤5.0'
  }
])

// 查询模板
const queryTemplates = ref([
  {
    key: 'normal',
    title: '正常数据',
    desc: '查询所有正常范围内的数据',
    icon: '✅'
  },
  {
    key: 'warning',
    title: '异常警告',
    desc: '查询处于临界值的数据',
    icon: '⚠️'
  },
  {
    key: 'danger',
    title: '严重超标',
    desc: '查询所有严重超标记录',
    icon: '🚨'
  }
])

const alertThresholds = {
  chlorine: { min: 0.5, max: 4.0 },
  conductivity: { max: 1000 },
  ph: { min: 6.5, max: 8.5 },
  orp: { min: 400 },
  turbidity: { max: 5.0 }
}

const stats = computed(() => {
  const res = { normal: 0, warning: 0, danger: 0 }
  queryResults.value.forEach(r => res[r.status]++)
  return res
})

// 优化后的状态检查逻辑
const checkRecordStatus = (record) => {
  let severity = 0 // 0:正常, 1:警告, 2:严重
  
  for (const [field, threshold] of Object.entries(alertThresholds)) {
    const val = parseFloat(record[field])
    if (isNaN(val)) continue

    // 严重超标逻辑：超出范围 20% 以上定义为 danger
    if (threshold.min !== undefined) {
      if (val < threshold.min * 0.8) severity = Math.max(severity, 2)
      else if (val < threshold.min) severity = Math.max(severity, 1)
    }
    if (threshold.max !== undefined) {
      if (val > threshold.max * 1.2) severity = Math.max(severity, 2)
      else if (val > threshold.max) severity = Math.max(severity, 1)
    }
  }
  
  return severity === 2 ? 'danger' : (severity === 1 ? 'warning' : 'normal')
}

const executeQuery = async () => {
  loading.value = true
  try {
    // 构建查询参数
    const queryParams = {}
    
    // 添加基本条件
    if (queryConditions.value.point_id) {
      queryParams.point_id = queryConditions.value.point_id
    }
    if (queryConditions.value.date_start) {
      queryParams.date_start = queryConditions.value.date_start
    }
    if (queryConditions.value.date_end) {
      queryParams.date_end = queryConditions.value.date_end
    }
    
    // 添加指标阈值
    if (queryConditions.value.chlorine_min) {
      queryParams.chlorine_min = parseFloat(queryConditions.value.chlorine_min)
    }
    if (queryConditions.value.chlorine_max) {
      queryParams.chlorine_max = parseFloat(queryConditions.value.chlorine_max)
    }
    if (queryConditions.value.conductivity_min) {
      queryParams.conductivity_min = parseFloat(queryConditions.value.conductivity_min)
    }
    if (queryConditions.value.conductivity_max) {
      queryParams.conductivity_max = parseFloat(queryConditions.value.conductivity_max)
    }
    if (queryConditions.value.ph_min) {
      queryParams.ph_min = parseFloat(queryConditions.value.ph_min)
    }
    if (queryConditions.value.ph_max) {
      queryParams.ph_max = parseFloat(queryConditions.value.ph_max)
    }
    if (queryConditions.value.orp_min) {
      queryParams.orp_min = parseFloat(queryConditions.value.orp_min)
    }
    if (queryConditions.value.orp_max) {
      queryParams.orp_max = parseFloat(queryConditions.value.orp_max)
    }
    if (queryConditions.value.turbidity_min) {
      queryParams.turbidity_min = parseFloat(queryConditions.value.turbidity_min)
    }
    if (queryConditions.value.turbidity_max) {
      queryParams.turbidity_max = parseFloat(queryConditions.value.turbidity_max)
    }
    
    // 调用真实API
    const response = await waterQualityApi.getRecords(queryParams)
    let allRecords = response.results || response
    
    // 添加状态检查
    const filteredRecords = allRecords.map(record => ({
      ...record,
      status: checkRecordStatus(record)
    }))
    
    queryResults.value = filteredRecords
    hasQueried.value = true
  } catch (e) {
    alert('查询失败')
  } finally {
    loading.value = false
  }
}

const resetQuery = () => {
  Object.keys(queryConditions.value).forEach(k => queryConditions.value[k] = '')
  queryResults.value = []
  hasQueried.value = false
}

const getRangeStatus = (field) => {
  const min = queryConditions.value[`${field}_min`]
  const max = queryConditions.value[`${field}_max`]
  if (min === '' && max === '') return ''
  
  const t = alertThresholds[field]
  if ((t.min && min < t.min) || (t.max && max > t.max)) return 'warning'
  return 'normal'
}

const getRangeStatusText = (field) => {
  const status = getRangeStatus(field)
  return status === 'normal' ? '符合标准' : '范围超标'
}

const setDateRange = (range) => {
  const now = new Date()
  const format = (d) => d.toISOString().split('T')[0]
  queryConditions.value.date_end = format(now)
  
  if (range === 'today') queryConditions.value.date_start = format(now)
  if (range === 'yesterday') {
    const d = new Date(); d.setDate(d.getDate() - 1)
    queryConditions.value.date_start = format(d)
    queryConditions.value.date_end = format(d)
  }
  if (range === 'week') {
    const d = new Date(); d.setDate(d.getDate() - 7)
    queryConditions.value.date_start = format(d)
  }
  if (range === 'month') {
    const d = new Date(); d.setMonth(d.getMonth() - 1)
    queryConditions.value.date_start = format(d)
  }
}

const applyTemplate = (type) => {
  resetQuery()
  if (type === 'normal') {
    queryConditions.value.chlorine_min = 0.5
    queryConditions.value.chlorine_max = 4.0
    queryConditions.value.ph_min = 6.5
    queryConditions.value.ph_max = 8.5
  } else if (type === 'danger') {
    queryConditions.value.turbidity_min = 5.1
    queryConditions.value.ph_max = 6.0
  }
}

const viewRecord = (r) => {
  selectedRecord.value = r
  showRecordDetail.value = true
}

const exportQueryResults = () => {
    // 简单 CSV 导出逻辑
    const headers = "ID,点位,日期,余氯,电导率,pH,状态\n";
    const rows = queryResults.value.map(r => `${r.id},${r.point_id},${r.date},${r.chlorine},${r.conductivity},${r.ph},${r.status}`).join("\n");
    const blob = new Blob(["\ufeff" + headers + rows], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "水质导出.csv");
    link.click();
}
</script>

<style scoped>
/* ===== 全局样式 ===== */
.query-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

/* ===== 页面头部 ===== */
.page-header {
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
  gap: 30px;
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

.header-stats {
  display: flex;
  gap: 20px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  padding: 20px;
  text-align: center;
  min-width: 100px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.25);
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* ===== 查询容器 ===== */
.query-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 25px;
  margin-bottom: 30px;
}

.query-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.query-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 25px 30px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-icon {
  font-size: 1.8rem;
  background: rgba(255, 255, 255, 0.2);
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0;
}

.card-content {
  padding: 30px;
}

/* ===== 表单样式 ===== */
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-label {
  font-weight: 600;
  color: #333;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.label-icon {
  font-size: 1.2rem;
}

.input-wrapper {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 15px 20px;
  border: 2px solid #e1e8ed;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: #f8fafc;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* ===== 日期范围 ===== */
.date-range-wrapper {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.input-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.date-separator {
  color: #666;
  font-weight: 500;
  padding: 0 10px;
}

.quick-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.quick-btn {
  padding: 8px 16px;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  background: white;
  color: #666;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 500;
}

.quick-btn:hover {
  border-color: #667eea;
  color: #667eea;
  background: #f0f4ff;
  transform: translateY(-2px);
}

/* ===== 指标网格 ===== */
.indicators-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 25px;
}

.indicator-item {
  border: 2px solid #e1e8ed;
  border-radius: 15px;
  padding: 25px;
  transition: all 0.3s ease;
  background: #f8fafc;
}

.indicator-item:hover {
  border-color: #667eea;
  background: white;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
}

.indicator-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.indicator-icon {
  font-size: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  width: 60px;
  height: 60px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.indicator-info {
  flex: 1;
}

.indicator-name {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0 0 5px 0;
  color: #333;
}

.indicator-unit {
  color: #666;
  margin: 0;
  font-size: 0.9rem;
}

.indicator-status {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.indicator-status.normal {
  background: #d4edda;
  color: #155724;
}

.indicator-status.warning {
  background: #fff3cd;
  color: #856404;
}

.indicator-status.danger {
  background: #f8d7da;
  color: #721c24;
}

.range-input-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.range-input {
  flex: 1;
  padding: 12px 15px;
  border: 2px solid #e1e8ed;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.range-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.range-separator {
  color: #666;
  font-weight: 500;
  padding: 0 10px;
  display: flex;
  align-items: center;
}

.range-info {
  font-size: 0.85rem;
  color: #666;
  padding: 8px 12px;
  background: #f0f4ff;
  border-radius: 8px;
  border-left: 3px solid #667eea;
}

/* ===== 模板网格 ===== */
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.template-item {
  border: 2px solid #e1e8ed;
  border-radius: 15px;
  padding: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f8fafc;
  display: flex;
  align-items: center;
  gap: 20px;
}

.template-item:hover {
  border-color: #667eea;
  background: white;
  transform: translateY(-5px);
  box-shadow: 0 12px 30px rgba(102, 126, 234, 0.2);
}

.template-icon {
  font-size: 2.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  width: 70px;
  height: 70px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.template-content {
  flex: 1;
}

.template-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #333;
}

.template-desc {
  color: #666;
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.4;
}

/* ===== 操作按钮 ===== */
.actions-section {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.actions-container {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-btn {
  padding: 15px 30px;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 150px;
  justify-content: center;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.action-btn.primary:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.action-btn.secondary {
  background: #f8fafc;
  color: #666;
  border: 2px solid #e1e8ed;
}

.action-btn.secondary:hover {
  border-color: #667eea;
  color: #667eea;
  background: #f0f4ff;
}

.action-btn.success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.action-btn.success:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
}

.action-btn:disabled {
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

/* ===== 响应式设计 ===== */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    text-align: center;
  }
  
  .header-stats {
    justify-content: center;
  }
  
  .form-grid,
  .indicators-grid,
  .templates-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-container {
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .input-group {
    flex-direction: column;
    gap: 10px;
  }
  
  .quick-actions {
    justify-content: center;
  }
}

/* ===== 深色主题 ===== */
@media (prefers-color-scheme: dark) {
  .query-page {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  }
  
  .query-card,
  .actions-section {
    background: #1e1e2e;
    color: white;
  }
  
  .form-input {
    background: #2a2a3e;
    border-color: #3a3a4e;
    color: white;
  }
  
  .form-input:focus {
    background: #2a2a3e;
  }
  
  .indicator-item,
  .template-item {
    background: #2a2a3e;
    border-color: #3a3a4e;
  }
  
  .indicator-item:hover,
  .template-item:hover {
    background: #1e1e2e;
  }
}
</style>