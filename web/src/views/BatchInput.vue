<template>
  <div class="batch-input-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">
            <span class="title-icon">📊</span>
            {{ isEditMode ? '编辑记录' : '批量数据录入' }}
          </h1>
          <p class="page-subtitle">{{ isEditMode ? '修改数据信息 · 智能验证' : '高效批量导入 · 智能验证 · 实时预览' }}</p>
        </div>
        <div class="header-stats">
          <div class="stat-card">
            <div class="stat-number">{{ tableData.length }}</div>
            <div class="stat-label">待录入</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ validCount }}</div>
            <div class="stat-label">已验证</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入方式选择 - 只在非编辑模式显示 -->
    <div v-if="!isEditMode" class="input-method-tabs">
      <div class="method-tabs">
        <div 
          class="tab-item" 
          :class="{ active: inputMethod === 'manual' }" 
          @click="inputMethod = 'manual'"
        >
          <div class="tab-icon">📝</div>
          <div class="tab-content">
            <h3>手动输入</h3>
            <p>单条记录精确录入</p>
          </div>
        </div>
        <div 
          class="tab-item" 
          :class="{ active: inputMethod === 'table' }" 
          @click="inputMethod = 'table'"
        >
          <div class="tab-icon">📊</div>
          <div class="tab-content">
            <h3>表格输入</h3>
            <p>Excel式批量录入</p>
          </div>
        </div>
        <div 
          class="tab-item" 
          :class="{ active: inputMethod === 'import' }" 
          @click="inputMethod = 'import'"
        >
          <div class="tab-icon">📁</div>
          <div class="tab-content">
            <h3>文件导入</h3>
            <p>CSV/Excel文件导入</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 手动输入模式 -->
    <div v-if="inputMethod === 'manual'" class="manual-input-section">
      <div class="input-card">
        <div class="card-header">
          <h3>📝 单条记录录入</h3>
          <div class="validation-status" :class="getValidationStatus()">
            {{ getValidationText() }}
          </div>
        </div>
        
        <div class="card-content">
          <div class="form-grid">
            <div class="form-group" v-for="(field, key) in formFields" :key="key">
              <label class="form-label">
                <span class="label-icon">{{ field.icon }}</span>
                {{ field.label }}
              </label>
              <div class="input-wrapper">
                <input 
                  :type="field.type" 
                  v-model="singleRecord[key]" 
                  :placeholder="field.placeholder"
                  :step="field.step"
                  class="form-input"
                  @input="validateField(key)"
                />
                <div class="input-status" :class="getFieldStatus(key)"></div>
              </div>
            </div>
          </div>
          
          <div class="form-actions">
            <button class="action-btn primary" @click="addSingleRecord" :disabled="!isFormValid">
              <span class="btn-icon">➕</span>
              添加到列表
            </button>
            <button class="action-btn secondary" @click="clearSingleRecord">
              <span class="btn-icon">🔄</span>
              清空表单
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 表格输入模式 -->
    <div v-if="inputMethod === 'table'" class="table-input-section">
      <div class="table-card">
        <div class="card-header">
          <h3>📊 Excel式批量输入</h3>
          <div class="table-tools">
            <button class="tool-btn" @click="addTableRow">
              <span class="tool-icon">➕</span>
              添加行
            </button>
            <button class="tool-btn" @click="fillSampleData">
              <span class="tool-icon">📋</span>
              示例数据
            </button>
            <button class="tool-btn" @click="autoFillSequence">
              <span class="tool-icon">🔢</span>
              自动序列
            </button>
            <button class="tool-btn danger" @click="clearTable">
              <span class="tool-icon">🗑️</span>
              清空表格
            </button>
          </div>
        </div>
        
        <div class="card-content">
          <!-- 快捷工具栏 -->
          <div class="quick-toolbar">
            <div class="toolbar-group">
              <label class="toolbar-label">快速填充监测点:</label>
              <input type="text" v-model="quickFill.point_id" placeholder="输入监测点ID" class="toolbar-input" />
              <button class="toolbar-btn" @click="quickFillColumn('point_id')">填充列</button>
            </div>
            <div class="toolbar-group">
              <label class="toolbar-label">快速填充日期:</label>
              <input type="date" v-model="quickFill.date" class="toolbar-input" />
              <button class="toolbar-btn" @click="quickFillColumn('date')">填充列</button>
            </div>
            <div class="toolbar-group">
              <label class="toolbar-label">时间序列:</label>
              <div class="time-sequence">
                <input type="time" v-model="quickFill.start_time" placeholder="开始时间" class="toolbar-input" />
                <span class="sequence-separator">间隔</span>
                <input type="number" v-model="quickFill.interval" placeholder="分钟" min="5" max="1440" class="toolbar-input small" />
                <button class="toolbar-btn" @click="quickFillTimeSequence()">生成序列</button>
              </div>
            </div>
          </div>
          
          <!-- 数据表格 -->
          <div class="table-container">
            <div class="table-wrapper">
              <table class="batch-input-table">
                <thead>
                  <tr>
                    <th v-for="(field, key) in tableFields" :key="key" class="header-cell">
                      <div class="header-content">
                        <span>{{ field.label }}</span>
                        <button class="sort-btn" @click="sortTable(key)" title="排序">
                          {{ sortOrder.key === key && sortOrder.order === 'asc' ? '↑' : '↓' }}
                        </button>
                      </div>
                    </th>
                    <th class="header-cell actions">
                      <div class="header-content">操作</div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in tableData" :key="index" class="data-row" :class="getRowClass(row)">
                    <td v-for="(field, key) in tableFields" :key="key" class="data-cell">
                      <input 
                        :type="field.type" 
                        v-model="row[key]" 
                        :step="field.step"
                        class="cell-input"
                        @input="validateRow(index)"
                      />
                    </td>
                    <td class="data-cell actions">
                      <div class="row-actions">
                        <button class="action-icon-btn delete" @click="deleteRow(index)" title="删除">
                          🗑️
                        </button>
                        <button class="action-icon-btn duplicate" @click="duplicateRow(index)" title="复制">
                          📋
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 文件导入模式 -->
    <div v-if="inputMethod === 'import'" class="import-section">
      <div class="import-card">
        <div class="card-header">
          <h3>📁 文件批量导入</h3>
        </div>
        
        <div class="card-content">
          <div class="upload-area" :class="{ 'drag-over': isDragOver }" @drop="handleDrop" @dragover="isDragOver = true" @dragleave="isDragOver = false">
            <div class="upload-icon">📁</div>
            <div class="upload-text">
              <h4>拖拽文件到此处</h4>
              <p>或者点击选择文件</p>
              <input type="file" @change="handleFileSelect" accept=".csv,.xlsx,.xls" class="file-input" />
            </div>
          </div>
          
          <div class="import-options">
            <div class="option-group">
              <label class="option-label">
                <input type="checkbox" v-model="importOptions.hasHeader" />
                文件包含标题行
              </label>
            </div>
            <div class="option-group">
              <label class="option-label">
                <input type="checkbox" v-model="importOptions.skipDuplicates" />
                跳过重复数据
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 操作区域 -->
    <div class="actions-section">
      <div class="actions-container">
        <!-- 数据验证 - 编辑模式下也显示 -->
        <div class="action-group">
          <h4>数据验证</h4>
          <div class="validation-summary">
            <div class="validation-item">
              <span class="validation-count">{{ validCount }}</span>
              <span class="validation-label">有效数据</span>
            </div>
            <div class="validation-item">
              <span class="validation-count">{{ invalidCount }}</span>
              <span class="validation-label">无效数据</span>
            </div>
            <div class="validation-item">
              <span class="validation-count">{{ duplicateCount }}</span>
              <span class="validation-label">重复数据</span>
            </div>
          </div>
        </div>
        
        <!-- 批量操作 - 只在非编辑模式显示 -->
        <div v-if="!isEditMode" class="action-group">
          <h4>批量操作</h4>
          <div class="batch-actions">
            <button class="batch-btn primary" @click="validateAllData" :disabled="tableData.length === 0">
              <span class="btn-icon">✅</span>
              验证数据
            </button>
            <button class="batch-btn success" @click="submitBatchData" :disabled="validCount === 0">
              <span class="btn-icon">📤</span>
              提交数据
            </button>
            <button class="batch-btn secondary" @click="exportTableData">
              <span class="btn-icon">📥</span>
              导出模板
            </button>
            <button class="batch-btn danger" @click="clearAllData">
              <span class="btn-icon">🗑️</span>
              清空数据
            </button>
          </div>
        </div>
        
        <!-- 编辑操作 - 只在编辑模式显示 -->
        <div v-if="isEditMode" class="action-group">
          <h4>编辑操作</h4>
          <div class="batch-actions">
            <button class="batch-btn success" @click="updateRecord" :disabled="!isFormValid">
              <span class="btn-icon">💾</span>
              保存修改
            </button>
            <button class="batch-btn secondary" @click="router.push('/records')">
              <span class="btn-icon">↩️</span>
              返回列表
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { waterQualityApi } from '@/api/waterQuality'

const route = useRoute()
const router = useRouter()

// 检查是否为编辑模式
const isEditMode = computed(() => !!route.params.id)
const editRecordId = computed(() => route.params.id)

// 输入方式
const inputMethod = ref('table')

// 表单字段配置
const formFields = ref({
  point_id: { label: '监测点ID', type: 'text', icon: '📍', placeholder: '如：监测点001' },
  date: { label: '日期', type: 'date', icon: '📅', placeholder: '选择日期' },
  time: { label: '时间', type: 'time', icon: '🕐', placeholder: '选择时间' },
  chlorine: { label: '余氯(mg/L)', type: 'number', icon: '🧪', step: '0.1', placeholder: '0.0' },
  conductivity: { label: '电导率(µS/cm)', type: 'number', icon: '⚡', step: '0.1', placeholder: '0.0' },
  ph: { label: 'pH值', type: 'number', icon: '💧', step: '0.1', placeholder: '0.0' },
  orp: { label: 'ORP(mV)', type: 'number', icon: '🔋', step: '0.1', placeholder: '0.0' },
  turbidity: { label: '浊度(NTU)', type: 'number', icon: '🌊', step: '0.1', placeholder: '0.0' }
})

const tableFields = ref({
  point_id: { label: '监测点', type: 'text', step: '' },
  date: { label: '日期', type: 'date', step: '' },
  time: { label: '时间', type: 'time', step: '' },
  chlorine: { label: '余氯', type: 'number', step: '0.1' },
  conductivity: { label: '电导率', type: 'number', step: '0.1' },
  ph: { label: 'pH值', type: 'number', step: '0.1' },
  orp: { label: 'ORP', type: 'number', step: '0.1' },
  turbidity: { label: '浊度', type: 'number', step: '0.1' }
})

// 数据状态
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

const tableData = ref([])
const quickFill = ref({
  point_id: '',
  date: '',
  start_time: '08:00',
  interval: 30
})

const importOptions = ref({
  hasHeader: true,
  skipDuplicates: true
})

const isDragOver = ref(false)
const sortOrder = ref({ key: '', order: 'asc' })

// 计算属性
const validCount = computed(() => {
  return tableData.value.filter(row => validateRowData(row)).length
})

const invalidCount = computed(() => {
  return tableData.value.filter(row => !validateRowData(row)).length
})

const duplicateCount = computed(() => {
  const pointIds = tableData.value.map(row => row.point_id)
  const duplicates = pointIds.filter((id, index) => pointIds.indexOf(id) !== index)
  return duplicates.length
})

const isFormValid = computed(() => {
  return Object.values(singleRecord.value).every(value => value !== '' && value !== null)
})

// 验证方法
const validateRowData = (row) => {
  return row.point_id && row.date && row.time && 
         row.chlorine !== null && row.chlorine !== '' && !isNaN(row.chlorine) &&
         row.conductivity !== null && row.conductivity !== '' && !isNaN(row.conductivity) &&
         row.ph !== null && row.ph !== '' && !isNaN(row.ph) &&
         row.orp !== null && row.orp !== '' && !isNaN(row.orp) &&
         row.turbidity !== null && row.turbidity !== '' && !isNaN(row.turbidity)
}

const validateField = (key) => {
  return singleRecord.value[key] !== ''
}

const getValidationStatus = () => {
  const allValid = Object.values(singleRecord.value).every(value => value !== '' && value !== null)
  return allValid ? 'valid' : 'invalid'
}

const getValidationText = () => {
  const allValid = Object.values(singleRecord.value).every(value => value !== '' && value !== null)
  return allValid ? '✅ 表单完整' : '⚠️ 请填写完整信息'
}

const getFieldStatus = (key) => {
  return singleRecord.value[key] !== '' ? 'valid' : 'invalid'
}

const getRowClass = (row) => {
  return validateRowData(row) ? 'valid' : 'invalid'
}

// 操作方法
const addSingleRecord = () => {
  if (isFormValid.value) {
    // 转换数据类型
    const record = {
      point_id: singleRecord.value.point_id,
      date: singleRecord.value.date,
      time: singleRecord.value.time,
      chlorine: parseFloat(singleRecord.value.chlorine),
      conductivity: parseFloat(singleRecord.value.conductivity),
      ph: parseFloat(singleRecord.value.ph),
      orp: parseFloat(singleRecord.value.orp),
      turbidity: parseFloat(singleRecord.value.turbidity)
    }
    
    tableData.value.push(record)
    clearSingleRecord()
  }
}

const clearSingleRecord = () => {
  Object.keys(singleRecord.value).forEach(key => {
    singleRecord.value[key] = ''
  })
}

const addTableRow = () => {
  const newRow = {
    point_id: '',
    date: new Date().toISOString().split('T')[0],
    time: new Date().toTimeString().slice(0, 5),
    chlorine: 0,
    conductivity: 0,
    ph: 0,
    orp: 0,
    turbidity: 0
  }
  tableData.value.push(newRow)
}

const deleteRow = (index) => {
  tableData.value.splice(index, 1)
}

const duplicateRow = (index) => {
  const originalRow = tableData.value[index]
  const duplicatedRow = { ...originalRow }
  tableData.value.splice(index + 1, 0, duplicatedRow)
}

const clearTable = () => {
  tableData.value = []
}

const fillSampleData = () => {
  const sampleData = [
    { point_id: '监测点001', date: '2026-03-11', time: '08:00', chlorine: 1.2, conductivity: 850, ph: 7.2, orp: 450, turbidity: 1.5 },
    { point_id: '监测点002', date: '2026-03-11', time: '09:00', chlorine: 2.1, conductivity: 920, ph: 7.5, orp: 480, turbidity: 2.0 },
    { point_id: '监测点003', date: '2026-03-11', time: '10:00', chlorine: 0.8, conductivity: 780, ph: 6.8, orp: 420, turbidity: 1.2 }
  ]
  tableData.value = sampleData
}

const autoFillSequence = () => {
  const baseData = {
    point_id: '监测点001',
    date: new Date().toISOString().split('T')[0],
    chlorine: 1.0,
    conductivity: 800,
    ph: 7.0,
    orp: 400,
    turbidity: 1.0
  }
  
  const sequence = []
  for (let i = 0; i < 10; i++) {
    const time = new Date()
    time.setHours(8 + i * 2)
    time.setMinutes(0)
    
    sequence.push({
      ...baseData,
      point_id: `监测点00${(i % 3) + 1}`,
      time: time.toTimeString().slice(0, 5)
    })
  }
  
  tableData.value = sequence
}

const quickFillColumn = (column) => {
  const value = quickFill.value[column]
  if (value) {
    tableData.value.forEach(row => {
      row[column] = value
    })
  }
}

const quickFillTimeSequence = () => {
  const startTime = quickFill.value.start_time
  const interval = quickFill.value.interval || 30
  
  tableData.value.forEach((row, index) => {
    const [hours, minutes] = startTime.split(':').map(Number)
    const totalMinutes = hours * 60 + minutes + (index * interval)
    const newHours = Math.floor(totalMinutes / 60) % 24
    const newMinutes = totalMinutes % 60
    row.time = `${String(newHours).padStart(2, '0')}:${String(newMinutes).padStart(2, '0')}`
  })
}

const sortTable = (key) => {
  if (sortOrder.value.key === key) {
    sortOrder.value.order = sortOrder.value.order === 'asc' ? 'desc' : 'asc'
  } else {
    sortOrder.value.key = key
    sortOrder.value.order = 'asc'
  }
  
  tableData.value.sort((a, b) => {
    const aVal = a[key]
    const bVal = b[key]
    
    if (sortOrder.value.order === 'asc') {
      return aVal > bVal ? 1 : -1
    } else {
      return aVal < bVal ? 1 : -1
    }
  })
}

const validateAllData = () => {
  tableData.value.forEach(row => {
    row.isValid = validateRowData(row)
  })
}

const updateRecord = async () => {
  try {
    // 转换数据类型
    const convertedRecord = {
      point_id: singleRecord.value.point_id,
      date: singleRecord.value.date,
      time: singleRecord.value.time,
      chlorine: parseFloat(singleRecord.value.chlorine),
      conductivity: parseFloat(singleRecord.value.conductivity),
      ph: parseFloat(singleRecord.value.ph),
      orp: parseFloat(singleRecord.value.orp),
      turbidity: parseFloat(singleRecord.value.turbidity)
    }
    
    await waterQualityApi.updateRecord(editRecordId.value, convertedRecord)
    alert('记录更新成功！')
    router.push('/records')
  } catch (error) {
    console.error('记录更新失败:', error)
    const errorMsg = error.response?.data?.detail || error.message || '未知错误'
    alert('更新失败: ' + errorMsg)
  }
}

const submitBatchData = async () => {
  try {
    const validData = tableData.value.filter(row => validateRowData(row))
    
    if (validData.length === 0) {
      alert('没有有效数据可以提交！')
      return
    }
    
    let successCount = 0
    let errorCount = 0
    const errorDetails = []
    
    for (const [index, record] of validData.entries()) {
      try {
        // 转换数据类型
        const convertedRecord = {
          point_id: record.point_id,
          date: record.date,
          time: record.time,
          chlorine: parseFloat(record.chlorine),
          conductivity: parseFloat(record.conductivity),
          ph: parseFloat(record.ph),
          orp: parseFloat(record.orp),
          turbidity: parseFloat(record.turbidity)
        }
        
        await waterQualityApi.createRecord(convertedRecord)
        successCount++
      } catch (error) {
        errorCount++
        const errorMsg = error.response?.data?.detail || error.message || '未知错误'
        errorDetails.push(`第${index + 1}条: ${errorMsg}`)
        console.error(`记录提交失败:`, record, error)
      }
    }
    
    if (successCount > 0) {
      // 移除成功提交的数据
      tableData.value = tableData.value.filter(row => !validData.includes(row))
      
      let message = `成功提交 ${successCount} 条记录！`
      if (errorCount > 0) {
        message += `\n失败 ${errorCount} 条记录。`
        if (errorDetails.length <= 3) {
          message += `\n错误详情:\n${errorDetails.join('\n')}`
        } else {
          message += `\n部分错误:\n${errorDetails.slice(0, 3).join('\n')}...`
        }
      }
      alert(message)
    } else {
      alert(`提交失败！\n${errorDetails.join('\n')}`)
    }
  } catch (error) {
    console.error('批量提交失败:', error)
    alert('提交过程中发生异常，请检查网络连接或联系管理员')
  }
}

const exportTableData = () => {
  const csvContent = [
    '监测点,日期,时间,余氯,电导率,pH值,ORP,浊度',
    ...tableData.value.map(row => 
      `${row.point_id},${row.date},${row.time},${row.chlorine},${row.conductivity},${row.ph},${row.orp},${row.turbidity}`
    )
  ].join('\n')
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = '水质数据模板.csv'
  link.click()
}

const clearAllData = () => {
  if (confirm('确定要清空所有数据吗？')) {
    tableData.value = []
    quickFill.value = { point_id: '', date: '', start_time: '08:00', interval: 30 }
  }
}

// 文件导入相关
const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    processFile(file)
  }
}

const handleDrop = (event) => {
  event.preventDefault()
  isDragOver.value = false
  
  const file = event.dataTransfer.files[0]
  if (file) {
    processFile(file)
  }
}

const processFile = async (file) => {
  console.log('处理文件:', file.name)
  alert('文件导入功能开发中...')
}

const validateRow = (index) => {
  // 实时验证行数据
  tableData.value[index].isValid = validateRowData(tableData.value[index])
}

const loadEditRecord = async () => {
  if (isEditMode.value && editRecordId.value) {
    try {
      const response = await waterQualityApi.getRecord(editRecordId.value)
      const record = response
      
      // 填充到表单
      singleRecord.value = {
        point_id: record.point_id,
        date: record.date,
        time: record.time,
        chlorine: record.chlorine.toString(),
        conductivity: record.conductivity.toString(),
        ph: record.ph.toString(),
        orp: record.orp.toString(),
        turbidity: record.turbidity.toString()
      }
      
      // 切换到手动输入模式
      inputMethod.value = 'manual'
      
    } catch (error) {
      console.error('加载记录失败:', error)
      alert('加载记录失败，请返回重试')
      router.push('/records')
    }
  }
}

onMounted(() => {
  // 初始化
  loadEditRecord()
})
</script>

<style scoped>
/* ===== 全局样式 ===== */
.batch-input-page {
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

/* ===== 方法选择器 ===== */
.method-selector {
  margin-bottom: 30px;
}

.method-tabs {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.tab-item {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 20px;
  border: 2px solid transparent;
}

.tab-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.tab-item.active {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
}

.tab-icon {
  font-size: 2.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  width: 70px;
  height: 70px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab-content h3 {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #333;
}

.tab-content p {
  font-size: 0.9rem;
  color: #666;
  margin: 0;
  line-height: 1.4;
}

/* ===== 输入卡片 ===== */
.input-card, .table-card, .import-card {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  margin-bottom: 30px;
}

.input-card:hover, .table-card:hover, .import-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.card-header h3 {
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0;
  color: #333;
  display: flex;
  align-items: center;
  gap: 10px;
}

.validation-status {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.validation-status.valid {
  background: #e8f5e8;
  color: #67c23a;
}

.validation-status.invalid {
  background: #fef0f0;
  color: #f56c6c;
}

/* ===== 表单样式 ===== */
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 25px;
  margin-bottom: 30px;
}

.form-group {
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

.input-status {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.input-status.valid {
  background: #67c23a;
}

.input-status.invalid {
  background: #f56c6c;
}

/* ===== 表格工具 ===== */
.table-tools {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.tool-btn {
  padding: 10px 20px;
  border: 2px solid #e1e8ed;
  border-radius: 10px;
  background: white;
  color: #666;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tool-btn:hover {
  border-color: #667eea;
  color: #667eea;
  background: #f0f4ff;
  transform: translateY(-2px);
}

.tool-btn.danger {
  border-color: #f56c6c;
  color: #f56c6c;
}

.tool-btn.danger:hover {
  background: #fef0f0;
  border-color: #f56c6c;
}

.tool-icon {
  font-size: 1.1rem;
}

/* ===== 快捷工具栏 ===== */
.quick-toolbar {
  background: #f8fafc;
  border-radius: 15px;
  padding: 20px;
  margin-bottom: 25px;
  border: 1px solid #e1e8ed;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.toolbar-label {
  font-weight: 500;
  color: #333;
  min-width: 120px;
}

.toolbar-input {
  flex: 1;
  padding: 10px 15px;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  font-size: 0.9rem;
  background: white;
}

.toolbar-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.toolbar-input.small {
  max-width: 100px;
}

.toolbar-btn {
  padding: 8px 16px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.85rem;
  font-weight: 500;
}

.toolbar-btn:hover {
  background: #5a67d8;
  transform: translateY(-2px);
}

.sequence-separator {
  color: #666;
  margin: 0 10px;
}

/* ===== 表格样式 ===== */
.table-container {
  overflow-x: auto;
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.table-wrapper {
  background: white;
  border-radius: 15px;
  overflow: hidden;
}

.batch-input-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.header-cell {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 15px;
  text-align: left;
  font-weight: 600;
  position: relative;
}

.header-cell.actions {
  background: #f8fafc;
  color: #333;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sort-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.8rem;
}

.sort-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.data-row {
  transition: all 0.3s ease;
}

.data-row:hover {
  background: #f8fafc;
}

.data-row.valid {
  background: #f0f9ff;
}

.data-row.invalid {
  background: #fef0f0;
}

.data-cell {
  padding: 12px 15px;
  border-bottom: 1px solid #f0f0f0;
}

.data-cell.actions {
  background: #f8fafc;
  text-align: center;
  width: 120px;
}

.cell-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e1e8ed;
  border-radius: 6px;
  font-size: 0.9rem;
  background: transparent;
  transition: all 0.3s ease;
}

.cell-input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.row-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.action-icon-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-icon-btn.delete {
  background: #fef0f0;
  color: #f56c6c;
}

.action-icon-btn.delete:hover {
  background: #f56c6c;
  color: white;
  transform: scale(1.1);
}

.action-icon-btn.duplicate {
  background: #e8f5e8;
  color: #67c23a;
}

.action-icon-btn.duplicate:hover {
  background: #67c23a;
  color: white;
  transform: scale(1.1);
}

/* ===== 文件导入 ===== */
.import-section {
  margin-bottom: 30px;
}

.upload-area {
  border: 3px dashed #d1d5db;
  border-radius: 20px;
  padding: 60px 40px;
  text-align: center;
  background: #f8fafc;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.upload-area:hover, .upload-area.drag-over {
  border-color: #667eea;
  background: #f0f4ff;
  transform: scale(1.02);
}

.upload-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  display: block;
}

.upload-text h4 {
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0 0 10px 0;
  color: #333;
}

.upload-text p {
  font-size: 1rem;
  color: #666;
  margin: 0 0 20px 0;
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.import-options {
  margin-top: 25px;
  display: flex;
  gap: 30px;
}

.option-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.option-label {
  font-weight: 500;
  color: #333;
  cursor: pointer;
}

/* ===== 操作区域 ===== */
.actions-section {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.actions-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.action-group h4 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 15px 0;
  color: #333;
}

.validation-summary {
  display: flex;
  gap: 20px;
}

.validation-item {
  text-align: center;
  padding: 15px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e1e8ed;
}

.validation-count {
  font-size: 1.5rem;
  font-weight: 700;
  color: #667eea;
  display: block;
  margin-bottom: 5px;
}

.validation-label {
  font-size: 0.9rem;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.batch-actions {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.batch-btn {
  padding: 15px 25px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 140px;
  justify-content: center;
}

.batch-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.batch-btn.primary:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.batch-btn.success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.batch-btn.success:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
}

.batch-btn.secondary {
  background: #f8fafc;
  color: #666;
  border: 2px solid #e1e8ed;
}

.batch-btn.secondary:hover:not(:disabled) {
  border-color: #667eea;
  color: #667eea;
  background: #f0f4ff;
  transform: translateY(-3px);
}

.batch-btn.danger {
  background: #fef0f0;
  color: #f56c6c;
  border: 2px solid #f56c6c;
}

.batch-btn.danger:hover:not(:disabled) {
  background: #f56c6c;
  color: white;
  transform: translateY(-3px);
}

.batch-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.btn-icon {
  font-size: 1.1rem;
}

/* ===== 表单操作 ===== */
.form-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 20px;
}

.action-btn {
  padding: 15px 25px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
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
  transform: translateY(-3px);
}

/* ===== 响应式设计 ===== */
@media (max-width: 768px) {
  .batch-input-page {
    padding: 15px;
  }
  
  .header-content {
    flex-direction: column;
    text-align: center;
    gap: 15px;
  }
  
  .method-tabs {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .table-tools {
    flex-direction: column;
    gap: 10px;
  }
  
  .quick-toolbar {
    padding: 15px;
  }
  
  .toolbar-group {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .toolbar-label {
    min-width: auto;
  }
  
  .actions-container {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .validation-summary {
    flex-direction: column;
    gap: 15px;
  }
  
  .batch-actions {
    flex-direction: column;
  }
  
  .batch-btn {
    width: 100%;
    min-width: auto;
  }
}

/* ===== 深色主题 ===== */
@media (prefers-color-scheme: dark) {
  .batch-input-page {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  }
  
  .input-card, .table-card, .import-card, .actions-section {
    background: #1e1e2e;
    color: white;
  }
  
  .form-label, .card-header h3, .toolbar-label {
    color: white;
  }
  
  .batch-input-table {
    color: white;
  }
  
  .header-cell {
    background: linear-gradient(135deg, #4c1d95 0%, #5a189a 100%);
  }
  
  .data-cell {
    border-color: #3a3a4e;
  }
  
  .data-row:hover {
    background: #2a2a3e;
  }
  
  .validation-item {
    background: #2a2a3e;
    border-color: #3a3a4e;
  }
}
</style>
