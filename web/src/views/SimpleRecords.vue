<template>
  <div class="records-page">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <button class="btn-primary" @click="showAddDialog = true">
          ➕ 新增记录
        </button>
        <button class="btn-success" @click="showUploadDialog = true">
          📁 批量上传
        </button>
        <button class="btn-danger" :disabled="selectedCount === 0" @click="batchDelete">
          🗑️ 批量删除
        </button>
        <button class="btn-default" @click="exportData">
          📥 导出数据
        </button>
      </div>
      <div class="toolbar-right">
        <input 
          type="text" 
          placeholder="搜索监测点..." 
          v-model="searchText"
          class="search-input"
        />
        <button class="btn-default" @click="loadData">🔄 刷新</button>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>
              <input type="checkbox" @change="toggleAllSelect" :checked="allSelected" />
            </th>
            <th>ID</th>
            <th>监测点</th>
            <th>日期</th>
            <th>时间</th>
            <th>余氯(mg/L)</th>
            <th>电导率(µS/cm)</th>
            <th>pH值</th>
            <th>氧化还原电位(mV)</th>
            <th>浊度(NTU)</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="record in filteredRecords" :key="record.id" :class="{ 'warning': record.status === 'warning', 'danger': record.status === 'danger' }">
            <td>
              <input type="checkbox" :value="record.id" v-model="selectedIds" />
            </td>
            <td>{{ record.id }}</td>
            <td>{{ record.point }}</td>
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
              <button class="btn-sm" @click="editRecord(record)">✏️</button>
              <button class="btn-sm btn-danger" @click="deleteRecord(record.id)">🗑️</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="pagination">
      <span>共 {{ total }} 条记录</span>
      <div class="pagination-controls">
        <button @click="currentPage > 1 && currentPage--" :disabled="currentPage === 1">上一页</button>
        <span>{{ currentPage }} / {{ totalPages }}</span>
        <button @click="currentPage < totalPages && currentPage++" :disabled="currentPage === totalPages">下一页</button>
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <div v-if="showAddDialog" class="modal-overlay" @click="showAddDialog = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ editingRecord ? '编辑记录' : '新增记录' }}</h3>
          <button class="close-btn" @click="showAddDialog = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-group">
              <label>监测点ID</label>
              <input type="text" v-model="formData.point" placeholder="如：监测点001" />
            </div>
            <div class="form-group">
              <label>日期</label>
              <input type="date" v-model="formData.date" />
            </div>
            <div class="form-group">
              <label>时间</label>
              <input type="time" v-model="formData.time" />
            </div>
            <div class="form-group">
              <label>余氯(mg/L)</label>
              <input type="number" step="0.1" v-model="formData.chlorine" placeholder="0.0" />
            </div>
            <div class="form-group">
              <label>电导率(µS/cm)</label>
              <input type="number" step="0.1" v-model="formData.conductivity" placeholder="0.0" />
            </div>
            <div class="form-group">
              <label>pH值</label>
              <input type="number" step="0.1" v-model="formData.ph" placeholder="0.0" />
            </div>
            <div class="form-group">
              <label>氧化还原电位(mV)</label>
              <input type="number" step="0.1" v-model="formData.orp" placeholder="0.0" />
            </div>
            <div class="form-group">
              <label>浊度(NTU)</label>
              <input type="number" step="0.1" v-model="formData.turbidity" placeholder="0.0" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-default" @click="showAddDialog = false">取消</button>
          <button class="btn-primary" @click="saveRecord">保存</button>
        </div>
      </div>
    </div>

    <!-- 批量上传对话框 -->
    <div v-if="showUploadDialog" class="modal-overlay" @click="showUploadDialog = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>批量上传数据</h3>
          <button class="close-btn" @click="showUploadDialog = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="upload-area">
            <div class="upload-placeholder">
              <div class="upload-icon">📁</div>
              <p>将CSV文件拖拽到此处，或点击选择文件</p>
              <p style="font-size: 12px; color: #666;">支持格式：CSV (监测点ID,日期,时间,余氯,电导率,pH值,氧化还原电位,浊度)</p>
            </div>
            <input type="file" accept=".csv" @change="handleFileUpload" style="display: none;" ref="fileInput" />
          </div>
          <div v-if="uploadPreview.length > 0" class="upload-preview">
            <h4>数据预览 (前5条)</h4>
            <table class="preview-table">
              <thead>
                <tr>
                  <th>监测点</th>
                  <th>日期</th>
                  <th>时间</th>
                  <th>余氯</th>
                  <th>pH值</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in uploadPreview.slice(0, 5)" :key="index">
                  <td>{{ item.point }}</td>
                  <td>{{ item.date }}</td>
                  <td>{{ item.time }}</td>
                  <td>{{ item.chlorine }}</td>
                  <td>{{ item.ph }}</td>
                </tr>
              </tbody>
            </table>
            <p>共解析到 {{ uploadPreview.length }} 条数据</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-default" @click="showUploadDialog = false">取消</button>
          <button class="btn-primary" @click="confirmUpload" :disabled="uploadPreview.length === 0">
            确认上传 ({{ uploadPreview.length }}条)
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const records = ref([
  { id: 1, point: '监测点001', date: '2024-03-11', time: '08:00', chlorine: 2.5, conductivity: 450.0, ph: 7.2, orp: 650.0, turbidity: 1.8, status: 'normal' },
  { id: 2, point: '监测点002', date: '2024-03-11', time: '08:00', chlorine: 3.0, conductivity: 520.0, ph: 8.5, orp: 680.0, turbidity: 2.1, status: 'warning' },
  { id: 3, point: '监测点003', date: '2024-03-11', time: '08:00', chlorine: 1.8, conductivity: 380.0, ph: 6.8, orp: 620.0, turbidity: 1.5, status: 'normal' },
  { id: 4, point: '监测点004', date: '2024-03-11', time: '08:00', chlorine: 4.5, conductivity: 410.0, ph: 7.3, orp: 635.0, turbidity: 1.9, status: 'danger' },
  { id: 5, point: '监测点005', date: '2024-03-11', time: '08:00', chlorine: 2.7, conductivity: 480.0, ph: 7.4, orp: 660.0, turbidity: 2.2, status: 'normal' }
])

const searchText = ref('')
const selectedIds = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const showAddDialog = ref(false)
const showUploadDialog = ref(false)
const editingRecord = ref(null)
const uploadPreview = ref([])
const fileInput = ref(null)

const formData = ref({
  point: '',
  date: '',
  time: '',
  chlorine: '',
  conductivity: '',
  ph: '',
  orp: '',
  turbidity: ''
})

const filteredRecords = computed(() => {
  if (!searchText.value) return records.value
  return records.value.filter(record => 
    record.point.toLowerCase().includes(searchText.value.toLowerCase())
  )
})

const total = computed(() => filteredRecords.value.length)
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))
const selectedCount = computed(() => selectedIds.value.length)
const allSelected = computed(() => selectedIds.value.length === filteredRecords.value.length && filteredRecords.value.length > 0)

const toggleAllSelect = () => {
  if (allSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = filteredRecords.value.map(record => record.id)
  }
}

const editRecord = (record) => {
  editingRecord.value = record
  formData.value = { ...record }
  showAddDialog.value = true
}

const deleteRecord = (id) => {
  if (confirm('确定要删除这条记录吗？')) {
    const index = records.value.findIndex(r => r.id === id)
    if (index > -1) {
      records.value.splice(index, 1)
    }
  }
}

const batchDelete = () => {
  if (confirm(`确定要删除选中的 ${selectedCount.value} 条记录吗？`)) {
    records.value = records.value.filter(record => !selectedIds.value.includes(record.id))
    selectedIds.value = []
  }
}

const saveRecord = () => {
  if (editingRecord.value) {
    // 编辑
    const index = records.value.findIndex(r => r.id === editingRecord.value.id)
    if (index > -1) {
      records.value[index] = { ...formData.value, id: editingRecord.value.id }
    }
  } else {
    // 新增
    const newId = Math.max(...records.value.map(r => r.id)) + 1
    records.value.push({ ...formData.value, id: newId, status: 'normal' })
  }
  
  showAddDialog.value = false
  editingRecord.value = null
  formData.value = {
    point: '',
    date: '',
    time: '',
    chlorine: '',
    conductivity: '',
    ph: '',
    orp: '',
    turbidity: ''
  }
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  const reader = new FileReader()
  reader.onload = (e) => {
    const text = e.target.result
    const lines = text.split('\n').filter(line => line.trim())
    
    if (lines.length < 2) {
      alert('文件内容为空或格式不正确')
      return
    }
    
    const parsedData = []
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim())
      if (values.length >= 8) {
        parsedData.push({
          point: values[0],
          date: values[1],
          time: values[2],
          chlorine: values[3],
          conductivity: values[4],
          ph: values[5],
          orp: values[6],
          turbidity: values[7]
        })
      }
    }
    
    uploadPreview.value = parsedData
  }
  reader.readAsText(file)
}

const confirmUpload = () => {
  let nextId = Math.max(...records.value.map(r => r.id)) + 1
  
  uploadPreview.value.forEach(item => {
    records.value.push({
      ...item,
      id: nextId++,
      status: 'normal'
    })
  })
  
  showUploadDialog.value = false
  uploadPreview.value = []
  fileInput.value.value = ''
}

const exportData = () => {
  const data = filteredRecords.value
  const csv = [
    'ID,监测点,日期,时间,余氯,电导率,pH值,氧化还原电位,浊度',
    ...data.map(record => 
      `${record.id},${record.point},${record.date},${record.time},${record.chlorine},${record.conductivity},${record.ph},${record.orp},${record.turbidity}`
    )
  ].join('\n')
  
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `water_quality_${new Date().toISOString().split('T')[0]}.csv`
  link.click()
}

const loadData = () => {
  // 模拟数据加载
  console.log('数据已刷新')
}

onMounted(() => {
  console.log('数据管理页面加载完成')
})
</script>

<style scoped>
.records-page {
  max-width: 1200px;
  margin: 0 auto;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.toolbar-left, .toolbar-right {
  display: flex;
  gap: 10px;
  align-items: center;
}

.btn-primary, .btn-success, .btn-danger, .btn-default {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #1890ff;
  color: white;
}

.btn-primary:hover {
  background: #40a9ff;
}

.btn-success {
  background: #52c41a;
  color: white;
}

.btn-success:hover {
  background: #73d13d;
}

.btn-danger {
  background: #ff4d4f;
  color: white;
}

.btn-danger:hover {
  background: #ff7875;
}

.btn-danger:disabled {
  background: #d9d9d9;
  cursor: not-allowed;
}

.btn-default {
  background: #f0f0f0;
  color: #333;
}

.btn-default:hover {
  background: #d9d9d9;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.table-container {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  overflow: hidden;
  margin-bottom: 20px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th, .data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.data-table th {
  background: #fafafa;
  font-weight: 600;
  color: #333;
}

.data-table tr:hover {
  background: #fafafa;
}

.data-table tr.warning {
  background: #fff7e6;
}

.data-table tr.danger {
  background: #fff2f0;
}

.status-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.normal {
  background: #f6ffed;
  color: #52c41a;
}

.status-badge.warning {
  background: #fff7e6;
  color: #faad14;
}

.status-badge.danger {
  background: #fff2f0;
  color: #ff4d4f;
}

.btn-sm {
  padding: 4px 8px;
  margin: 0 2px;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
  background: #f0f0f0;
}

.btn-sm.btn-danger {
  background: #ff4d4f;
  color: white;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.pagination-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.pagination-controls button {
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
}

.pagination-controls button:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
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
  background: #fff;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.modal-body {
  padding: 20px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
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

.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.upload-area:hover {
  border-color: #1890ff;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.upload-preview {
  margin-top: 20px;
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

.preview-table th, .preview-table td {
  padding: 8px;
  border: 1px solid #f0f0f0;
  text-align: left;
}

.preview-table th {
  background: #fafafa;
  font-weight: 600;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 深色主题 */
.dark .records-page .toolbar,
.dark .records-page .table-container,
.dark .records-page .pagination,
.dark .records-page .modal {
  background: #1f1f1f;
  color: #fff;
}

.dark .records-page .data-table th {
  background: #2a2a2a;
  color: #fff;
}

.dark .records-page .data-table tr:hover {
  background: #2a2a2a;
}

.dark .records-page .search-input,
.dark .records-page .form-group input {
  background: #2a2a2a;
  border-color: #4c4d4f;
  color: #fff;
}

.dark .records-page .upload-area {
  border-color: #4c4d4f;
}

.dark .records-page .upload-area:hover {
  border-color: #1890ff;
}
</style>
