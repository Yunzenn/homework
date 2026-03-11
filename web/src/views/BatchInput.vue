<template>
  <div class="batch-input-page">
    <h2>批量数据录入</h2>
    
    <!-- 输入方式选择 -->
    <div class="input-method-tabs">
      <button 
        class="tab-btn" 
        :class="{ active: inputMethod === 'manual' }" 
        @click="inputMethod = 'manual'"
      >
        📝 手动输入
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: inputMethod === 'table' }" 
        @click="inputMethod = 'table'"
      >
        📊 表格输入
      </button>
    </div>
    
    <!-- 手动输入模式 -->
    <div v-if="inputMethod === 'manual'" class="manual-input-section">
      <div class="input-form">
        <h3>添加单条记录</h3>
        <div class="form-grid">
          <div class="form-group">
            <label>监测点ID</label>
            <input type="text" v-model="singleRecord.point_id" placeholder="如：监测点001" />
          </div>
          <div class="form-group">
            <label>日期</label>
            <input type="date" v-model="singleRecord.date" />
          </div>
          <div class="form-group">
            <label>时间</label>
            <input type="time" v-model="singleRecord.time" />
          </div>
          <div class="form-group">
            <label>余氯(mg/L)</label>
            <input type="number" step="0.1" v-model="singleRecord.chlorine" placeholder="0.0" />
          </div>
          <div class="form-group">
            <label>电导率(µS/cm)</label>
            <input type="number" step="0.1" v-model="singleRecord.conductivity" placeholder="0.0" />
          </div>
          <div class="form-group">
            <label>pH值</label>
            <input type="number" step="0.1" v-model="singleRecord.ph" placeholder="0.0" />
          </div>
          <div class="form-group">
            <label>氧化还原电位(mV)</label>
            <input type="number" step="0.1" v-model="singleRecord.orp" placeholder="0.0" />
          </div>
          <div class="form-group">
            <label>浊度(NTU)</label>
            <input type="number" step="0.1" v-model="singleRecord.turbidity" placeholder="0.0" />
          </div>
        </div>
        <div class="form-actions">
          <button class="btn-primary" @click="addSingleRecord">➕ 添加到列表</button>
          <button class="btn-default" @click="clearSingleRecord">🔄 清空表单</button>
        </div>
      </div>
    </div>
    
    <!-- 表格输入模式 -->
    <div v-if="inputMethod === 'table'" class="table-input-section">
      <div class="table-controls">
        <h3>📊 Excel式批量输入</h3>
        <div class="control-buttons">
          <button class="btn-success" @click="addTableRow">➕ 添加行</button>
          <button class="btn-default" @click="clearTable">🔄 清空表格</button>
          <button class="btn-info" @click="fillSampleData">📋 填充示例</button>
          <button class="btn-warning" @click="autoFillSequence">🔢 自动填充序列</button>
        </div>
      </div>
      
      <!-- 快捷工具栏 -->
      <div class="toolbar">
        <div class="toolbar-group">
          <label>快速填充监测点:</label>
          <input type="text" v-model="quickFill.point_id" placeholder="输入监测点ID" />
          <button class="btn-sm" @click="quickFillColumn('point_id')">填充列</button>
        </div>
        <div class="toolbar-group">
          <label>快速填充日期:</label>
          <input type="date" v-model="quickFill.date" />
          <button class="btn-sm" @click="quickFillColumn('date')">填充列</button>
        </div>
        <div class="toolbar-group">
          <label>快速填充时间:</label>
          <div class="time-sequence">
            <input type="time" v-model="quickFill.start_time" placeholder="开始时间" />
            <span>间隔</span>
            <input type="number" v-model="quickFill.interval" placeholder="分钟" min="5" max="1440" />
            <button class="btn-sm" @click="quickFillTimeSequence()">填充时间序列</button>
          </div>
        </div>
      </div>
      
      <div class="table-container">
        <table class="batch-input-table excel-style">
          <thead>
            <tr>
              <th class="header-cell">
                <div class="header-content">
                  <span>监测点</span>
                  <button class="header-btn" @click="sortTable('point_id')" title="排序">⇅</button>
                </div>
              </th>
              <th class="header-cell">
                <div class="header-content">
                  <span>日期</span>
                  <button class="header-btn" @click="sortTable('date')" title="排序">⇅</button>
                </div>
              </th>
              <th class="header-cell">
                <div class="header-content">
                  <span>时间</span>
                  <button class="header-btn" @click="sortTable('time')" title="排序">⇅</button>
                </div>
              </th>
              <th class="header-cell">
                <div class="header-content">
                  <span>余氯</span>
                  <button class="header-btn" @click="sortTable('chlorine')" title="排序">⇅</button>
                </div>
              </th>
              <th class="header-cell">
                <div class="header-content">
                  <span>电导率</span>
                  <button class="header-btn" @click="sortTable('conductivity')" title="排序">⇅</button>
                </div>
              </th>
              <th class="header-cell">
                <div class="header-content">
                  <span>pH值</span>
                  <button class="header-btn" @click="sortTable('ph')" title="排序">⇅</button>
                </div>
              </th>
              <th class="header-cell">
                <div class="header-content">
                  <span>ORP</span>
                  <button class="header-btn" @click="sortTable('orp')" title="排序">⇅</button>
                </div>
              </th>
              <th class="header-cell">
                <div class="header-content">
                  <span>浊度</span>
                  <button class="header-btn" @click="sortTable('turbidity')" title="排序">⇅</button>
                </div>
              </th>
              <th class="header-cell">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(record, index) in batchRecords" :key="index" :class="{ 'selected': selectedRow === index }" @click="selectRow(index)">
              <td class="editable-cell" @dblclick="editCell(index, 'point_id')">
                <input 
                  type="text" 
                  v-model="record.point_id" 
                  placeholder="监测点ID"
                  @focus="selectRow(index)"
                  @keydown="handleKeydown($event, index)"
                  class="cell-input"
                />
              </td>
              <td class="editable-cell" @dblclick="editCell(index, 'date')">
                <input 
                  type="date" 
                  v-model="record.date" 
                  @focus="selectRow(index)"
                  @keydown="handleKeydown($event, index)"
                  class="cell-input"
                />
              </td>
              <td class="editable-cell" @dblclick="editCell(index, 'time')">
                <input 
                  type="time" 
                  v-model="record.time" 
                  @focus="selectRow(index)"
                  @keydown="handleKeydown($event, index)"
                  class="cell-input"
                />
              </td>
              <td class="editable-cell" @dblclick="editCell(index, 'chlorine')">
                <input 
                  type="number" 
                  step="0.1" 
                  v-model="record.chlorine" 
                  placeholder="0.0"
                  @focus="selectRow(index)"
                  @keydown="handleKeydown($event, index)"
                  class="cell-input number-input"
                />
              </td>
              <td class="editable-cell" @dblclick="editCell(index, 'conductivity')">
                <input 
                  type="number" 
                  step="0.1" 
                  v-model="record.conductivity" 
                  placeholder="0.0"
                  @focus="selectRow(index)"
                  @keydown="handleKeydown($event, index)"
                  class="cell-input number-input"
                />
              </td>
              <td class="editable-cell" @dblclick="editCell(index, 'ph')">
                <input 
                  type="number" 
                  step="0.1" 
                  v-model="record.ph" 
                  placeholder="0.0"
                  @focus="selectRow(index)"
                  @keydown="handleKeydown($event, index)"
                  class="cell-input number-input"
                />
              </td>
              <td class="editable-cell" @dblclick="editCell(index, 'orp')">
                <input 
                  type="number" 
                  step="0.1" 
                  v-model="record.orp" 
                  placeholder="0.0"
                  @focus="selectRow(index)"
                  @keydown="handleKeydown($event, index)"
                  class="cell-input number-input"
                />
              </td>
              <td class="editable-cell" @dblclick="editCell(index, 'turbidity')">
                <input 
                  type="number" 
                  step="0.1" 
                  v-model="record.turbidity" 
                  placeholder="0.0"
                  @focus="selectRow(index)"
                  @keydown="handleKeydown($event, index)"
                  class="cell-input number-input"
                />
              </td>
              <td class="action-cell">
                <button class="btn-danger btn-sm" @click="removeTableRow(index)" title="删除行">🗑️</button>
                <button class="btn-info btn-sm" @click="duplicateRow(index)" title="复制行">📋</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 状态栏 -->
      <div class="status-bar">
        <div class="status-info">
          <span>总行数: {{ batchRecords.length }}</span>
          <span>选中行: {{ selectedRow + 1 }}</span>
          <span>完成度: {{ completionPercentage }}%</span>
        </div>
        <div class="status-actions">
          <button class="btn-sm" @click="exportToExcel">📥 导出Excel</button>
          <button class="btn-sm" @click="importFromExcel">📥 导入Excel</button>
        </div>
      </div>
    </div>
    
    <!-- 数据预览 -->
    <div class="preview-section" v-if="batchRecords.length > 0">
      <div class="preview-header">
        <h3>数据预览 ({{ batchRecords.length }} 条)</h3>
        <div class="preview-stats">
          <span class="stat-item">总记录: {{ batchRecords.length }}</span>
          <span class="stat-item warning">待验证: {{ unvalidatedCount }}</span>
        </div>
      </div>
      
      <div class="preview-table">
        <table class="data-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>监测点</th>
              <th>日期</th>
              <th>时间</th>
              <th>余氯</th>
              <th>电导率</th>
              <th>pH值</th>
              <th>ORP</th>
              <th>浊度</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(record, index) in batchRecords" :key="index" :class="{ 'warning': !isRecordValid(record) }">
              <td>{{ index + 1 }}</td>
              <td>{{ record.point_id || '-' }}</td>
              <td>{{ record.date || '-' }}</td>
              <td>{{ record.time || '-' }}</td>
              <td>{{ record.chlorine || '-' }}</td>
              <td>{{ record.conductivity || '-' }}</td>
              <td>{{ record.ph || '-' }}</td>
              <td>{{ record.orp || '-' }}</td>
              <td>{{ record.turbidity || '-' }}</td>
              <td>
                <span class="status-badge" :class="getRecordStatus(record)">
                  {{ getRecordStatusText(record) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 操作按钮 -->
    <div class="action-section">
      <div class="action-buttons">
        <button class="btn-success" @click="validateAllRecords" :disabled="batchRecords.length === 0">
          ✅ 验证数据
        </button>
        <button class="btn-primary" @click="saveAllRecords" :disabled="batchRecords.length === 0 || !allRecordsValid">
          💾 保存所有数据
        </button>
        <button class="btn-default" @click="clearAllRecords">
          🗑️ 清空所有数据
        </button>
      </div>
      
      <div class="progress-info" v-if="saving">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${saveProgress}%` }"></div>
        </div>
        <span>保存进度: {{ savedCount }} / {{ batchRecords.length }}</span>
      </div>
    </div>
    
    <!-- 结果对话框 -->
    <div v-if="showResultDialog" class="modal-overlay" @click="showResultDialog = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>保存结果</h3>
          <button class="close-btn" @click="showResultDialog = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="result-summary">
            <div class="result-item success">
              <span class="result-icon">✅</span>
              <span>成功保存: {{ saveResult.success }} 条</span>
            </div>
            <div class="result-item error" v-if="saveResult.failed > 0">
              <span class="result-icon">❌</span>
              <span>保存失败: {{ saveResult.failed }} 条</span>
            </div>
          </div>
          
          <div class="error-details" v-if="saveResult.errors.length > 0">
            <h4>错误详情:</h4>
            <div class="error-list">
              <div v-for="(error, index) in saveResult.errors" :key="index" class="error-item">
                第 {{ error.index + 1 }} 条: {{ error.message }}
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-primary" @click="showResultDialog = false">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { waterQualityApi } from '@/api/waterQuality'

const inputMethod = ref('manual')
const batchRecords = ref([])
const saving = ref(false)
const saveProgress = ref(0)
const savedCount = ref(0)
const showResultDialog = ref(false)
const saveResult = ref({
  success: 0,
  failed: 0,
  errors: []
})

// 单条记录表单
const singleRecord = ref({
  point_id: '',
  date: '',
  time: '',
  chlorine: '',
  conductivity: '',
  ph: '',
  orp: '',
  turbidity: ''
})

// 报警阈值配置
const alertThresholds = {
  chlorine: { min: 0.5, max: 4.0 },
  conductivity: { max: 1000 },
  ph: { min: 6.5, max: 8.5 },
  orp: { min: 400 },
  turbidity: { max: 5.0 }
}

// 计算属性
const unvalidatedCount = computed(() => {
  return batchRecords.value.filter(record => !isRecordValid(record)).length
})

const allRecordsValid = computed(() => {
  return batchRecords.value.length > 0 && batchRecords.value.every(record => isRecordValid(record))
})

// 添加单条记录
const addSingleRecord = () => {
  if (!isRecordValid(singleRecord.value)) {
    alert('请填写完整的记录信息')
    return
  }
  
  batchRecords.value.push({ ...singleRecord.value })
  clearSingleRecord()
  alert('记录已添加到列表')
}

// 清空单条记录表单
const clearSingleRecord = () => {
  singleRecord.value = {
    point_id: '',
    date: '',
    time: '',
    chlorine: '',
    conductivity: '',
    ph: '',
    orp: '',
    turbidity: ''
  }
}

// 快速填充数据
const quickFill = ref({
  point_id: '',
  date: '',
  start_time: '08:00',
  interval: 30
})

const selectedRow = ref(-1)

// Excel式操作方法
const selectRow = (index) => {
  selectedRow.value = index
}

const editCell = (index, field) => {
  selectedRow.value = index
  // 聚焦到对应单元格
  setTimeout(() => {
    const input = document.querySelector(`tr:nth-child(${index + 1}) td:nth-child(${getFieldColumn(field)}) input`)
    if (input) {
      input.focus()
      input.select()
    }
  }, 0)
}

const getFieldColumn = (field) => {
  const fieldMap = {
    'point_id': 1,
    'date': 2,
    'time': 3,
    'chlorine': 4,
    'conductivity': 5,
    'ph': 6,
    'orp': 7,
    'turbidity': 8
  }
  return fieldMap[field] || 1
}

// 键盘操作
const handleKeydown = (event, index) => {
  if (event.key === 'ArrowUp' && index > 0) {
    event.preventDefault()
    selectRow(index - 1)
  } else if (event.key === 'ArrowDown' && index < batchRecords.value.length - 1) {
    event.preventDefault()
    selectRow(index + 1)
  } else if (event.key === 'Enter') {
    event.preventDefault()
    if (index < batchRecords.value.length - 1) {
      selectRow(index + 1)
    }
  }
}

// 排序功能
const sortTable = (field) => {
  batchRecords.value.sort((a, b) => {
    const aVal = a[field] || ''
    const bVal = b[field] || ''
    
    // 数字排序
    if (['chlorine', 'conductivity', 'ph', 'orp', 'turbidity'].includes(field)) {
      return parseFloat(aVal) - parseFloat(bVal)
    }
    
    // 字符串排序
    return aVal.localeCompare(bVal)
  })
}

// 快速填充列
const quickFillColumn = (field) => {
  const value = quickFill.value[field]
  if (!value) {
    alert(`请先输入要填充的${field === 'point_id' ? '监测点' : '日期'}值`)
    return
  }
  
  batchRecords.value.forEach(record => {
    record[field] = value
  })
  
  alert(`已填充${field === 'point_id' ? '监测点' : '日期'}列`)
}

// 快速填充时间序列
const quickFillTimeSequence = () => {
  if (!quickFill.value.start_time || !quickFill.value.interval) {
    alert('请输入开始时间和间隔')
    return
  }
  
  const startTime = quickFill.value.start_time
  const interval = parseInt(quickFill.value.interval)
  
  batchRecords.value.forEach((record, index) => {
    const [hours, minutes] = startTime.split(':').map(Number)
    const totalMinutes = hours * 60 + minutes + (index * interval)
    const newHours = Math.floor(totalMinutes / 60) % 24
    const newMinutes = totalMinutes % 60
    record.time = `${String(newHours).padStart(2, '0')}:${String(newMinutes).padStart(2, '0')}`
  })
  
  alert(`已填充时间序列，间隔${interval}分钟`)
}

// 自动填充序列
const autoFillSequence = () => {
  const baseData = {
    point_id: '监测点001',
    date: '2024-03-11',
    time: '08:00',
    chlorine: 2.5,
    conductivity: 450.0,
    ph: 7.2,
    orp: 650.0,
    turbidity: 1.8
  }
  
  const sequence = []
  for (let i = 0; i < 10; i++) {
    const record = { ...baseData }
    
    // 递增时间
    const [hours, minutes] = baseData.time.split(':').map(Number)
    const totalMinutes = hours * 60 + minutes + (i * 30)
    const newHours = Math.floor(totalMinutes / 60) % 24
    const newMinutes = totalMinutes % 60
    record.time = `${String(newHours).padStart(2, '0')}:${String(newMinutes).padStart(2, '0')}`
    
    // 递增监测点
    record.point_id = `监测点${String(i + 1).padStart(3, '0')}`
    
    // 微调数值
    record.chlorine = (2.5 + i * 0.1).toFixed(1)
    record.conductivity = (450 + i * 5).toFixed(1)
    record.ph = (7.2 + i * 0.05).toFixed(1)
    
    sequence.push(record)
  }
  
  batchRecords.value = sequence
  alert('已自动填充10条序列数据')
}

// 复制行
const duplicateRow = (index) => {
  const original = batchRecords.value[index]
  const duplicate = { ...original }
  
  // 生成新的监测点ID
  if (duplicate.point_id) {
    const match = duplicate.point_id.match(/(\d+)$/)
    if (match) {
      const num = parseInt(match[1]) + 1
      duplicate.point_id = duplicate.point_id.replace(/\d+$/, String(num).padStart(3, '0'))
    }
  }
  
  batchRecords.value.splice(index + 1, 0, duplicate)
  alert('已复制行')
}

// 计算完成度
const completionPercentage = computed(() => {
  if (batchRecords.value.length === 0) return 0
  
  const completed = batchRecords.value.filter(record => isRecordValid(record)).length
  return Math.round((completed / batchRecords.value.length) * 100)
})

// 导出Excel格式
const exportToExcel = () => {
  if (batchRecords.value.length === 0) {
    alert('没有数据可导出')
    return
  }
  
  const csv = [
    '监测点,日期,时间,余氯,电导率,pH值,ORP,浊度',
    ...batchRecords.value.map(record => 
      `${record.point_id || ''},${record.date || ''},${record.time || ''},${record.chlorine || ''},${record.conductivity || ''},${record.ph || ''},${record.orp || ''},${record.turbidity || ''}`
    )
  ].join('\n')
  
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `水质数据_${new Date().toISOString().split('T')[0]}.csv`
  link.click()
  
  alert(`已导出 ${batchRecords.value.length} 条记录`)
}

// 从Excel导入
const importFromExcel = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.csv,.xlsx,.xls'
  input.onchange = (event) => {
    const file = event.target.files[0]
    if (!file) return
    
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const text = e.target.result
        const lines = text.split('\n').filter(line => line.trim())
        
        if (lines.length < 2) {
          alert('文件格式错误')
          return
        }
        
        const headers = lines[0].split(',').map(h => h.trim())
        const data = []
        
        for (let i = 1; i < lines.length; i++) {
          const values = lines[i].split(',').map(v => v.trim())
          if (values.length >= 8) {
            data.push({
              point_id: values[0] || '',
              date: values[1] || '',
              time: values[2] || '',
              chlorine: values[3] || '',
              conductivity: values[4] || '',
              ph: values[5] || '',
              orp: values[6] || '',
              turbidity: values[7] || ''
            })
          }
        }
        
        batchRecords.value = data
        alert(`成功导入 ${data.length} 条记录`)
        
      } catch (error) {
        alert('文件解析失败: ' + error.message)
      }
    }
    
    reader.readAsText(file)
  }
  
  input.click()
}
const addTableRow = () => {
  batchRecords.value.push({
    point_id: '',
    date: '',
    time: '',
    chlorine: '',
    conductivity: '',
    ph: '',
    orp: '',
    turbidity: ''
  })
}

// 删除表格行
const removeTableRow = (index) => {
  batchRecords.value.splice(index, 1)
}

// 清空表格
const clearTable = () => {
  if (confirm('确定要清空所有数据吗？')) {
    batchRecords.value = []
  }
}

// 填充示例数据
const fillSampleData = () => {
  const sampleData = [
    {
      point_id: '监测点001',
      date: '2024-03-11',
      time: '08:00',
      chlorine: '2.5',
      conductivity: '450.0',
      ph: '7.2',
      orp: '650.0',
      turbidity: '1.8'
    },
    {
      point_id: '监测点002',
      date: '2024-03-11',
      time: '09:00',
      chlorine: '3.0',
      conductivity: '520.0',
      ph: '7.8',
      orp: '680.0',
      turbidity: '2.1'
    },
    {
      point_id: '监测点003',
      date: '2024-03-11',
      time: '10:00',
      chlorine: '2.8',
      conductivity: '480.0',
      ph: '7.5',
      orp: '660.0',
      turbidity: '2.0'
    }
  ]
  
  batchRecords.value = [...sampleData]
  alert('已填充3条示例数据')
}

// 验证记录
const isRecordValid = (record) => {
  return record.point_id && 
         record.date && 
         record.time && 
         record.chlorine !== '' && 
         record.conductivity !== '' && 
         record.ph !== '' && 
         record.orp !== '' && 
         record.turbidity !== ''
}

// 获取记录状态
const getRecordStatus = (record) => {
  if (!isRecordValid(record)) return 'invalid'
  
  const chlorine = parseFloat(record.chlorine)
  const conductivity = parseFloat(record.conductivity)
  const ph = parseFloat(record.ph)
  const orp = parseFloat(record.orp)
  const turbidity = parseFloat(record.turbidity)
  
  const alerts = []
  
  if (chlorine < alertThresholds.chlorine.min || chlorine > alertThresholds.chlorine.max) {
    alerts.push('chlorine')
  }
  if (conductivity > alertThresholds.conductivity.max) {
    alerts.push('conductivity')
  }
  if (ph < alertThresholds.ph.min || ph > alertThresholds.ph.max) {
    alerts.push('ph')
  }
  if (orp < alertThresholds.orp.min) {
    alerts.push('orp')
  }
  if (turbidity > alertThresholds.turbidity.max) {
    alerts.push('turbidity')
  }
  
  if (alerts.length === 0) return 'normal'
  return alerts.length > 1 ? 'danger' : 'warning'
}

// 获取状态文本
const getRecordStatusText = (record) => {
  const status = getRecordStatus(record)
  switch (status) {
    case 'normal': return '正常'
    case 'warning': return '警告'
    case 'danger': return '超标'
    case 'invalid': return '待验证'
    default: return '未知'
  }
}

// 验证所有记录
const validateAllRecords = () => {
  const invalidRecords = batchRecords.value.filter(record => !isRecordValid(record))
  
  if (invalidRecords.length > 0) {
    alert(`发现 ${invalidRecords.length} 条待验证记录，请完善后再保存`)
    return
  }
  
  alert('所有记录验证通过！')
}

// 保存所有记录
const saveAllRecords = async () => {
  if (!allRecordsValid.value) {
    alert('请先验证所有记录')
    return
  }
  
  if (!confirm(`确定要保存 ${batchRecords.value.length} 条记录吗？`)) {
    return
  }
  
  saving.value = true
  saveProgress.value = 0
  savedCount.value = 0
  saveResult.value = {
    success: 0,
    failed: 0,
    errors: []
  }
  
  for (let i = 0; i < batchRecords.value.length; i++) {
    const record = batchRecords.value[i]
    
    try {
      // 转换数据类型
      const dataToSave = {
        point_id: record.point_id.trim(),
        date: record.date,
        time: record.time,
        chlorine: parseFloat(record.chlorine),
        conductivity: parseFloat(record.conductivity),
        ph: parseFloat(record.ph),
        orp: parseFloat(record.orp),
        turbidity: parseFloat(record.turbidity)
      }
      
      await waterQualityApi.createRecord(dataToSave)
      saveResult.value.success++
      savedCount.value++
      
    } catch (error) {
      saveResult.value.failed++
      saveResult.value.errors.push({
        index: i,
        message: error.message || '保存失败'
      })
    }
    
    // 更新进度
    saveProgress.value = Math.round(((i + 1) / batchRecords.value.length) * 100)
    
    // 模拟延迟，避免请求过快
    await new Promise(resolve => setTimeout(resolve, 100))
  }
  
  saving.value = false
  showResultDialog.value = true
}

// 清空所有记录
const clearAllRecords = () => {
  if (confirm('确定要清空所有记录吗？')) {
    batchRecords.value = []
    saveResult.value = {
      success: 0,
      failed: 0,
      errors: []
    }
  }
}

onMounted(() => {
  console.log('批量输入页面加载完成')
})
</script>

<style scoped>
.batch-input-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.input-method-tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 2px solid #e6e6e6;
}

.tab-btn {
  padding: 10px 20px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 16px;
  color: #666;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.tab-btn.active {
  color: #409EFF;
  border-bottom-color: #409EFF;
}

.tab-btn:hover {
  color: #409EFF;
}

.manual-input-section,
.table-input-section {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.input-form h3,
.table-controls h3 {
  margin: 0 0 20px 0;
  color: #333;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
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

.form-group input {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.form-actions,
.control-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn-primary, .btn-default, .btn-success, .btn-info, .btn-danger {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: white;
  font-size: 14px;
}

.btn-primary { background: #409EFF; }
.btn-default { background: #909399; }
.btn-success { background: #67C23A; }
.btn-info { background: #17bfdd; }
.btn-danger { background: #F56C6C; }

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.table-container {
  overflow-x: auto;
  margin-top: 20px;
}

.batch-input-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.batch-input-table th,
.batch-input-table td {
  padding: 8px;
  border: 1px solid #e6e6e6;
  text-align: center;
}

.batch-input-table th {
  background: #f5f7fa;
  font-weight: 600;
  color: #333;
}

.batch-input-table input {
  width: 100%;
  padding: 4px 8px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 12px;
}

.preview-section {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.preview-header h3 {
  margin: 0;
  color: #333;
}

.preview-stats {
  display: flex;
  gap: 15px;
}

.stat-item {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.stat-item.warning {
  background: #fdf6ec;
  color: #E6A23C;
}

.preview-table {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table th,
.data-table td {
  padding: 8px;
  border: 1px solid #e6e6e6;
  text-align: center;
}

.data-table th {
  background: #f5f7fa;
  font-weight: 600;
  color: #333;
}

.data-table tbody tr.warning {
  background: #fdf6ec;
}

.status-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.normal { background: #f0f9ff; color: #409EFF; }
.status-badge.warning { background: #fdf6ec; color: #E6A23C; }
.status-badge.danger { background: #fef0f0; color: #F56C6C; }
.status-badge.invalid { background: #f4f4f5; color: #909399; }

.action-section {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e6e6e6;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #409EFF;
  transition: width 0.3s ease;
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
  max-width: 500px;
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

.result-summary {
  margin-bottom: 20px;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  font-size: 16px;
}

.result-item.success { color: #67C23A; }
.result-item.error { color: #F56C6C; }

.error-details h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.error-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 10px;
}

.error-item {
  padding: 5px 0;
  border-bottom: 1px solid #f0f0f0;
  color: #F56C6C;
  font-size: 14px;
}

.error-item:last-child {
  border-bottom: none;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding-top: 10px;
  border-top: 1px solid #e6e6e6;
}

/* Excel式表格样式 */
.excel-style {
  border-collapse: collapse;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 13px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.excel-style th,
.excel-style td {
  border: 1px solid #d4d4d4;
  padding: 6px 8px;
  text-align: left;
  vertical-align: middle;
  min-width: 80px;
}

.excel-style th {
  background: linear-gradient(to bottom, #f8f8f8 0%, #e8e8e8 100%);
  font-weight: 600;
  color: #333;
  text-align: center;
  position: relative;
  user-select: none;
}

.excel-style tbody tr:hover {
  background: #f0f8ff;
}

.excel-style tbody tr.selected {
  background: #e3f2fd;
  box-shadow: 0 0 0 2px #409EFF inset;
}

.header-cell {
  position: relative;
  padding: 0;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px;
  font-weight: 600;
}

.header-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 2px;
  font-size: 12px;
  color: #666;
  opacity: 0.7;
  transition: all 0.2s;
}

.header-btn:hover {
  background: #e0e0e0;
  opacity: 1;
}

.editable-cell {
  padding: 0;
  cursor: text;
  position: relative;
}

.editable-cell:hover {
  background: #f8f8f8;
}

.cell-input {
  width: 100%;
  height: 32px;
  border: none;
  padding: 6px 8px;
  font-size: 13px;
  font-family: inherit;
  background: transparent;
  outline: none;
  transition: background 0.2s;
}

.cell-input:focus {
  background: #fff;
  box-shadow: 0 0 0 2px #409EFF inset;
  z-index: 10;
  position: relative;
}

.number-input {
  text-align: right;
}

.action-cell {
  text-align: center;
  white-space: nowrap;
  width: 80px;
}

/* 工具栏样式 */
.toolbar {
  background: #f8f9fa;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-group label {
  font-size: 12px;
  color: #666;
  white-space: nowrap;
  font-weight: 500;
}

.toolbar-group input {
  padding: 4px 8px;
  border: 1px solid #d9d9d9;
  border-radius: 3px;
  font-size: 12px;
}

.time-sequence {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-sequence span {
  font-size: 12px;
  color: #666;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 11px;
  border-radius: 3px;
  border: 1px solid #d9d9d9;
  background: #fff;
  color: #333;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-sm:hover {
  background: #f5f5f5;
  border-color: #409EFF;
  color: #409EFF;
}

/* 状态栏样式 */
.status-bar {
  background: #f8f9fa;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 10px 15px;
  margin-top: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-info {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #666;
}

.status-info span {
  padding: 2px 6px;
  background: #fff;
  border-radius: 3px;
  border: 1px solid #e6e6e6;
}

.status-actions {
  display: flex;
  gap: 8px;
}

.btn-warning {
  background: #E6A23C;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.btn-warning:hover {
  background: #cf9236;
}

/* 深色主题适配 */
.dark .excel-style th,
.dark .excel-style td {
  border-color: #4c4d4f;
}

.dark .excel-style th {
  background: linear-gradient(to bottom, #2a2a2a 0%, #1f1f1f 100%);
  color: #fff;
}

.dark .excel-style tbody tr:hover {
  background: #2a2a2a;
}

.dark .excel-style tbody tr.selected {
  background: #1e3a8a;
}

.dark .toolbar {
  background: #2a2a2a;
  border-color: #4c4d4f;
}

.dark .status-bar {
  background: #2a2a2a;
  border-color: #4c4d4f;
}

.dark .cell-input:focus {
  background: #2a2a2a;
}

.dark .btn-sm {
  background: #2a2a2a;
  color: #fff;
  border-color: #4c4d4f;
}

.dark .btn-sm:hover {
  background: #409EFF;
  border-color: #409EFF;
}
</style>
