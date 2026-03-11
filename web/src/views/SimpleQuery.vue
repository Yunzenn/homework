<template>
  <div class="query-page">
    <h2>高级查询</h2>
    
    <!-- 查询条件 -->
    <div class="query-form">
      <div class="form-section">
        <h3>基本条件</h3>
        <div class="form-row">
          <div class="form-group">
            <label>监测点</label>
            <input type="text" v-model="queryConditions.point_id" placeholder="如：监测点001" />
          </div>
          <div class="form-group">
            <label>日期范围</label>
            <div class="date-range">
              <input type="date" v-model="queryConditions.date_start" />
              <span>至</span>
              <input type="date" v-model="queryConditions.date_end" />
            </div>
          </div>
        </div>
      </div>
      
      <div class="form-section">
        <h3>指标阈值</h3>
        <div class="form-row">
          <div class="form-group">
            <label>余氯 (mg/L)</label>
            <div class="range-input">
              <input type="number" step="0.1" v-model="queryConditions.chlorine_min" placeholder="最小值" />
              <span>-</span>
              <input type="number" step="0.1" v-model="queryConditions.chlorine_max" placeholder="最大值" />
            </div>
          </div>
          <div class="form-group">
            <label>电导率 (µS/cm)</label>
            <div class="range-input">
              <input type="number" step="0.1" v-model="queryConditions.conductivity_min" placeholder="最小值" />
              <span>-</span>
              <input type="number" step="0.1" v-model="queryConditions.conductivity_max" placeholder="最大值" />
            </div>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>pH值</label>
            <div class="range-input">
              <input type="number" step="0.1" v-model="queryConditions.ph_min" placeholder="最小值" />
              <span>-</span>
              <input type="number" step="0.1" v-model="queryConditions.ph_max" placeholder="最大值" />
            </div>
          </div>
          <div class="form-group">
            <label>氧化还原电位 (mV)</label>
            <div class="range-input">
              <input type="number" step="0.1" v-model="queryConditions.orp_min" placeholder="最小值" />
              <span>-</span>
              <input type="number" step="0.1" v-model="queryConditions.orp_max" placeholder="最大值" />
            </div>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>浊度 (NTU)</label>
            <div class="range-input">
              <input type="number" step="0.1" v-model="queryConditions.turbidity_min" placeholder="最小值" />
              <span>-</span>
              <input type="number" step="0.1" v-model="queryConditions.turbidity_max" placeholder="最大值" />
            </div>
          </div>
          <div class="form-group">
            <label>超标状态</label>
            <select v-model="queryConditions.alert_status">
              <option value="">全部</option>
              <option value="normal">正常</option>
              <option value="warning">警告</option>
              <option value="danger">超标</option>
            </select>
          </div>
        </div>
      </div>
      
      <div class="form-actions">
        <button class="btn-primary" @click="executeQuery">🔍 查询</button>
        <button class="btn-default" @click="resetQuery">🔄 重置</button>
        <button class="btn-success" @click="exportQueryResults">📥 导出结果</button>
      </div>
    </div>
    
    <!-- 查询结果 -->
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
              <th>日期</th>
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
            <tr v-for="record in queryResults" :key="record.record_id || record.id" :class="{ 'warning': record.status === 'warning', 'danger': record.status === 'danger' }">
              <td>{{ record.record_id || record.id }}</td>
              <td>{{ record.point_id }}</td>
              <td>{{ record.date }}</td>
              <td>{{ record.time }}</td>
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
                <button class="btn-sm" @click="viewRecord(record)">👁️</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 无结果提示 -->
    <div class="no-results" v-else-if="hasQueried">
      <p>😔 没有找到符合条件的记录</p>
      <button class="btn-default" @click="resetQuery">重新查询</button>
    </div>
    
    <!-- 记录详情对话框 -->
    <div v-if="showRecordDetail" class="modal-overlay" @click="showRecordDetail = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>记录详情</h3>
          <button class="close-btn" @click="showRecordDetail = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="detail-grid">
            <div class="detail-item">
              <label>记录ID:</label>
              <span>{{ selectedRecord.record_id || selectedRecord.id }}</span>
            </div>
            <div class="detail-item">
              <label>监测点:</label>
              <span>{{ selectedRecord.point_id }}</span>
            </div>
            <div class="detail-item">
              <label>日期:</label>
              <span>{{ selectedRecord.date }}</span>
            </div>
            <div class="detail-item">
              <label>时间:</label>
              <span>{{ selectedRecord.time }}</span>
            </div>
            <div class="detail-item">
              <label>余氯:</label>
              <span>{{ selectedRecord.chlorine }} mg/L</span>
            </div>
            <div class="detail-item">
              <label>电导率:</label>
              <span>{{ selectedRecord.conductivity }} µS/cm</span>
            </div>
            <div class="detail-item">
              <label>pH值:</label>
              <span>{{ selectedRecord.ph }}</span>
            </div>
            <div class="detail-item">
              <label>ORP:</label>
              <span>{{ selectedRecord.orp }} mV</span>
            </div>
            <div class="detail-item">
              <label>浊度:</label>
              <span>{{ selectedRecord.turbidity }} NTU</span>
            </div>
            <div class="detail-item">
              <label>状态:</label>
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
import { ref, computed, onMounted } from 'vue'
import { waterQualityApi } from '@/api/waterQuality'

const queryResults = ref([])
const hasQueried = ref(false)
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
  turbidity_max: '',
  alert_status: ''
})

// 报警阈值配置
const alertThresholds = {
  chlorine: { min: 0.5, max: 4.0 },
  conductivity: { max: 1000 },
  ph: { min: 6.5, max: 8.5 },
  orp: { min: 400 },
  turbidity: { max: 5.0 }
}

// 计算统计信息
const stats = computed(() => {
  const normal = queryResults.value.filter(r => r.status === 'normal').length
  const warning = queryResults.value.filter(r => r.status === 'warning').length
  const danger = queryResults.value.filter(r => r.status === 'danger').length
  return { normal, warning, danger }
})

// 检查记录状态
const checkRecordStatus = (record) => {
  const alerts = []
  
  // 检查各项指标
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

// 执行查询
const executeQuery = async () => {
  try {
    console.log('执行查询，条件:', queryConditions.value)
    
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
    
    // 先获取所有数据，然后在前端进行过滤
    const response = await waterQualityApi.getRecords()
    let allRecords = response.results || response
    
    // 应用过滤条件
    let filteredRecords = allRecords.filter(record => {
      // 监测点过滤
      if (queryParams.point_id && !record.point_id.includes(queryParams.point_id)) {
        return false
      }
      
      // 日期范围过滤
      if (queryParams.date_start && record.date < queryParams.date_start) {
        return false
      }
      if (queryParams.date_end && record.date > queryParams.date_end) {
        return false
      }
      
      // 指标阈值过滤
      if (queryParams.chlorine_min && record.chlorine < queryParams.chlorine_min) {
        return false
      }
      if (queryParams.chlorine_max && record.chlorine > queryParams.chlorine_max) {
        return false
      }
      if (queryParams.conductivity_min && record.conductivity < queryParams.conductivity_min) {
        return false
      }
      if (queryParams.conductivity_max && record.conductivity > queryParams.conductivity_max) {
        return false
      }
      if (queryParams.ph_min && record.ph < queryParams.ph_min) {
        return false
      }
      if (queryParams.ph_max && record.ph > queryParams.ph_max) {
        return false
      }
      if (queryParams.orp_min && record.orp < queryParams.orp_min) {
        return false
      }
      if (queryParams.orp_max && record.orp > queryParams.orp_max) {
        return false
      }
      if (queryParams.turbidity_min && record.turbidity < queryParams.turbidity_min) {
        return false
      }
      if (queryParams.turbidity_max && record.turbidity > queryParams.turbidity_max) {
        return false
      }
      
      return true
    })
    
    // 添加状态检查
    filteredRecords = filteredRecords.map(record => ({
      ...record,
      status: checkRecordStatus(record)
    }))
    
    // 状态过滤
    if (queryConditions.value.alert_status) {
      filteredRecords = filteredRecords.filter(record => record.status === queryConditions.value.alert_status)
    }
    
    queryResults.value = filteredRecords
    hasQueried.value = true
    
    console.log(`查询完成，找到 ${queryResults.value.length} 条记录`)
    
  } catch (error) {
    console.error('查询失败:', error)
    alert('查询失败，请重试')
  }
}

// 重置查询
const resetQuery = () => {
  queryConditions.value = {
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
    turbidity_max: '',
    alert_status: ''
  }
  queryResults.value = []
  hasQueried.value = false
}

// 查看记录详情
const viewRecord = (record) => {
  selectedRecord.value = record
  showRecordDetail.value = true
}

// 导出查询结果
const exportQueryResults = () => {
  if (queryResults.value.length === 0) {
    alert('没有可导出的数据')
    return
  }
  
  const csv = [
    'ID,监测点,日期,时间,余氯,电导率,pH值,ORP,浊度,状态',
    ...queryResults.value.map(record => 
      `${record.record_id || record.id},${record.point_id},${record.date},${record.time},${record.chlorine},${record.conductivity},${record.ph},${record.orp},${record.turbidity},${record.status === 'normal' ? '正常' : record.status === 'warning' ? '警告' : '超标'}`
    )
  ].join('\n')
  
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `query_results_${new Date().toISOString().split('T')[0]}.csv`
  link.click()
  
  alert(`已导出 ${queryResults.value.length} 条记录`)
}

onMounted(() => {
  console.log('查询页面加载完成')
})
</script>

<style scoped>
.query-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.query-form {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.form-section {
  margin-bottom: 25px;
}

.form-section h3 {
  margin: 0 0 15px 0;
  color: #333;
  border-bottom: 2px solid #409EFF;
  padding-bottom: 5px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 5px;
  font-weight: 600;
  color: #333;
}

.form-group input,
.form-group select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 10px;
}

.date-range input {
  flex: 1;
}

.range-input {
  display: flex;
  align-items: center;
  gap: 10px;
}

.range-input input {
  flex: 1;
}

.range-input span {
  color: #666;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid #e6e6e6;
}

.btn-primary, .btn-default, .btn-success {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: white;
}

.btn-primary { background: #409EFF; }
.btn-default { background: #909399; }
.btn-success { background: #67C23A; }

.results-section {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.results-header h3 {
  margin: 0;
  color: #333;
}

.results-stats {
  display: flex;
  gap: 15px;
}

.stat-item {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.stat-item.normal { background: #f0f9ff; color: #409EFF; }
.stat-item.warning { background: #fdf6ec; color: #E6A23C; }
.stat-item.danger { background: #fef0f0; color: #F56C6C; }

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table th,
.data-table td {
  padding: 12px 8px;
  text-align: center;
  border: 1px solid #e6e6e6;
}

.data-table th {
  background: #f5f7fa;
  font-weight: 600;
  color: #333;
}

.data-table tbody tr:hover {
  background: #f5f7fa;
}

.data-table tbody tr.warning {
  background: #fdf6ec;
}

.data-table tbody tr.danger {
  background: #fef0f0;
}

.status-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.normal {
  background: #f0f9ff;
  color: #409EFF;
}

.status-badge.warning {
  background: #fdf6ec;
  color: #E6A23C;
}

.status-badge.danger {
  background: #fef0f0;
  color: #F56C6C;
}

.btn-sm {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background: #409EFF;
  color: white;
  font-size: 12px;
}

.no-results {
  text-align: center;
  padding: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.no-results p {
  margin: 0 0 20px 0;
  color: #666;
  font-size: 16px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  padding: 20px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e6e6e6;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.detail-item {
  display: flex;
  align-items: center;
}

.detail-item label {
  font-weight: 600;
  color: #333;
  min-width: 80px;
  margin-right: 10px;
}

.detail-item span {
  color: #666;
}

/* 深色主题 */
.dark .query-page .query-form,
.dark .query-page .results-section,
.dark .query-page .no-results,
.dark .query-page .modal {
  background: #1f1f1f;
  color: #fff;
}

.dark .query-page .form-group input,
.dark .query-page .form-group select {
  background: #2a2a2a;
  border-color: #4c4d4f;
  color: #fff;
}

.dark .query-page .data-table th {
  background: #2a2a2a;
  color: #fff;
}

.dark .query-page .data-table tbody tr:hover {
  background: #2a2a2a;
}
</style>
