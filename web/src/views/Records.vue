<template>
  <div class="records-container">
    <!-- 操作栏 -->
    <el-card class="operation-card" shadow="never">
      <div class="operation-bar">
        <div class="operation-left">
          <el-button type="primary" :icon="Plus" @click="handleAdd">
            新增记录
          </el-button>
          <el-button type="success" :icon="Upload" @click="handleBatchUpload">
            批量上传
          </el-button>
          <el-button 
            type="danger" 
            :icon="Delete" 
            :disabled="!selectedRecords.length"
            @click="handleBatchDelete"
          >
            批量删除
          </el-button>
          <el-button :icon="Download" @click="handleExport">
            导出数据
          </el-button>
          <el-button :icon="Refresh" @click="loadRecords">
            刷新
          </el-button>
        </div>
        
        <div class="operation-right">
          <el-input
            v-model="searchText"
            placeholder="搜索监测点"
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
            style="width: 200px"
          />
        </div>
      </div>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="filteredRecords"
        @selection-change="handleSelectionChange"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="record_id" label="ID" width="80" sortable />
        
        <el-table-column prop="point_id" label="监测点" width="120">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.point_id }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="date" label="日期" width="120" sortable />
        <el-table-column prop="time" label="时间" width="80" sortable />
        
        <el-table-column prop="chlorine" label="余氯(mg/L)" width="110" sortable>
          <template #default="{ row }">
            <span :class="getWaterQualityClass('chlorine', row.chlorine)">
              {{ formatWaterQualityValue(row.chlorine) }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="conductivity" label="电导率(µS/cm)" width="130" sortable>
          <template #default="{ row }">
            <span :class="getWaterQualityClass('conductivity', row.conductivity)">
              {{ formatWaterQualityValue(row.conductivity) }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="ph" label="pH值" width="80" sortable>
          <template #default="{ row }">
            <span :class="getWaterQualityClass('ph', row.ph)">
              {{ formatWaterQualityValue(row.ph) }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="orp" label="氧化还原电位(mV)" width="140" sortable>
          <template #default="{ row }">
            <span :class="getWaterQualityClass('orp', row.orp)">
              {{ formatWaterQualityValue(row.orp) }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="turbidity" label="浊度(NTU)" width="100" sortable>
          <template #default="{ row }">
            <span :class="getWaterQualityClass('turbidity', row.turbidity)">
              {{ formatWaterQualityValue(row.turbidity) }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="create_time" label="创建时间" width="160" sortable>
          <template #default="{ row }">
            {{ formatDateTime(row.create_time) }}
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="80" fixed="right">
          <template #default="{ row }">
            <el-tag 
              :type="getRecordStatusType(row)"
              size="small"
            >
              {{ getRecordStatus(row) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="监测点" prop="point_id">
              <el-input v-model="formData.point_id" placeholder="请输入监测点ID" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="日期" prop="date">
              <el-date-picker
                v-model="formData.date"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="时间" prop="time">
              <el-time-picker
                v-model="formData.time"
                placeholder="选择时间"
                format="HH:mm"
                value-format="HH:mm"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="余氯(mg/L)" prop="chlorine">
              <el-input-number
                v-model="formData.chlorine"
                :min="0"
                :precision="2"
                placeholder="0.00"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="电导率(µS/cm)" prop="conductivity">
              <el-input-number
                v-model="formData.conductivity"
                :min="0"
                :precision="1"
                placeholder="0.0"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="pH值" prop="ph">
              <el-input-number
                v-model="formData.ph"
                :min="0"
                :max="14"
                :precision="2"
                placeholder="0.00"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="氧化还原电位(mV)" prop="orp">
              <el-input-number
                v-model="formData.orp"
                :precision="1"
                placeholder="0.0"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="浊度(NTU)" prop="turbidity">
              <el-input-number
                v-model="formData.turbidity"
                :min="0"
                :precision="2"
                placeholder="0.00"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 批量上传对话框 -->
    <el-dialog
      v-model="batchUploadVisible"
      title="批量上传数据"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="batch-upload-content">
        <el-alert
          title="支持CSV和Excel文件格式"
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
        >
          <template #default>
            <p>请按照以下格式准备数据：</p>
            <p>监测点ID,日期,时间,余氯(mg/L),电导率(µS/cm),pH值,氧化还原电位(mV),浊度(NTU)</p>
            <p>示例：监测点001,2024-03-11,08:00,2.5,450.0,7.2,650.0,1.8</p>
          </template>
        </el-alert>

        <el-upload
          ref="uploadRef"
          class="upload-demo"
          drag
          :auto-upload="false"
          :on-change="handleFileChange"
          :limit="1"
          accept=".csv,.xlsx,.xls"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              只能上传 csv/xlsx/xls 文件，且不超过 10MB
            </div>
          </template>
        </el-upload>

        <div v-if="previewData.length > 0" class="preview-section">
          <h4>数据预览（前5条）</h4>
          <el-table :data="previewData.slice(0, 5)" border size="small">
            <el-table-column prop="point_id" label="监测点" width="100" />
            <el-table-column prop="date" label="日期" width="100" />
            <el-table-column prop="time" label="时间" width="80" />
            <el-table-column prop="chlorine" label="余氯" width="80" />
            <el-table-column prop="conductivity" label="电导率" width="90" />
            <el-table-column prop="ph" label="pH值" width="70" />
            <el-table-column prop="orp" label="氧化还原电位" width="110" />
            <el-table-column prop="turbidity" label="浊度" width="70" />
          </el-table>
          <p style="margin-top: 10px; color: #666;">
            共解析到 {{ previewData.length }} 条数据
          </p>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="batchUploadVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleBatchUploadSubmit" 
          :loading="uploading"
          :disabled="previewData.length === 0"
        >
          确认上传 ({{ previewData.length }}条)
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Delete,
  Download,
  Refresh,
  Search,
  Edit,
  View,
  Upload,
  UploadFilled
} from '@element-plus/icons-vue'
import {
  getRecordsList,
  createRecord,
  updateRecord,
  deleteRecord,
  batchDeleteRecords,
  exportRecords
} from '@/api/records'
import {
  formatDateTime,
  formatWaterQualityValue,
  getWaterQualityStatusColor
} from '@/utils/format'

// 水质阈值
const thresholds = {
  chlorine: { min: 0.5, max: 4.0 },
  conductivity: { max: 1000 },
  ph: { min: 6.5, max: 8.5 },
  orp: { min: 400 },
  turbidity: { max: 5.0 }
}

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const uploading = ref(false)
const records = ref([])
const selectedRecords = ref([])
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 对话框相关
const dialogVisible = ref(false)
const batchUploadVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const formRef = ref()
const uploadRef = ref()

// 批量上传相关
const previewData = ref([])

// 表单数据
const formData = reactive({
  record_id: null,
  point_id: '',
  date: '',
  time: '',
  chlorine: null,
  conductivity: null,
  ph: null,
  orp: null,
  turbidity: null
})

// 表单验证规则
const formRules = {
  point_id: [
    { required: true, message: '请输入监测点ID', trigger: 'blur' }
  ],
  date: [
    { required: true, message: '请选择日期', trigger: 'change' }
  ],
  time: [
    { required: true, message: '请选择时间', trigger: 'change' }
  ],
  chlorine: [
    { required: true, message: '请输入余氯值', trigger: 'blur' },
    { type: 'number', min: 0, message: '余氯值不能为负数', trigger: 'blur' }
  ],
  conductivity: [
    { required: true, message: '请输入电导率', trigger: 'blur' },
    { type: 'number', min: 0, message: '电导率不能为负数', trigger: 'blur' }
  ],
  ph: [
    { required: true, message: '请输入pH值', trigger: 'blur' },
    { type: 'number', min: 0, max: 14, message: 'pH值必须在0-14之间', trigger: 'blur' }
  ],
  orp: [
    { required: true, message: '请输入氧化还原电位', trigger: 'blur' }
  ],
  turbidity: [
    { required: true, message: '请输入浊度', trigger: 'blur' },
    { type: 'number', min: 0, message: '浊度不能为负数', trigger: 'blur' }
  ]
}

// 计算属性
const filteredRecords = computed(() => {
  if (!searchText.value) {
    return records.value
  }
  return records.value.filter(record => 
    record.point_id.toLowerCase().includes(searchText.value.toLowerCase())
  )
})

// 方法
const loadRecords = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    const data = await getRecordsList(params)
    records.value = data.results || data
    total.value = data.count || data.length
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadRecords()
}

const handleSelectionChange = (selection) => {
  selectedRecords.value = selection
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadRecords()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadRecords()
}

const resetForm = () => {
  Object.assign(formData, {
    record_id: null,
    point_id: '',
    date: '',
    time: '',
    chlorine: null,
    conductivity: null,
    ph: null,
    orp: null,
    turbidity: null
  })
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增记录'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑记录'
  Object.assign(formData, row)
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    const data = { ...formData }
    delete data.record_id
    
    if (isEdit.value) {
      await updateRecord(formData.record_id, data)
      ElMessage.success('更新成功')
    } else {
      await createRecord(data)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadRecords()
  } catch (error) {
    if (error.errors) {
      // 表单验证错误
      return
    }
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除记录 ${row.point_id} (${row.date} ${row.time}) 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteRecord(row.record_id)
    ElMessage.success('删除成功')
    loadRecords()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleBatchDelete = async () => {
  if (!selectedRecords.value.length) {
    ElMessage.warning('请选择要删除的记录')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRecords.value.length} 条记录吗？`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const recordIds = selectedRecords.value.map(record => record.record_id)
    await batchDeleteRecords({ record_ids: recordIds })
    ElMessage.success('批量删除成功')
    loadRecords()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const handleExport = async () => {
  try {
    const data = await exportRecords()
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `water_quality_records_${new Date().toISOString().split('T')[0]}.json`
    a.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 批量上传相关方法
const handleBatchUpload = () => {
  batchUploadVisible.value = true
  previewData.value = []
}

const handleFileChange = (file) => {
  const reader = new FileReader()
  
  reader.onload = (e) => {
    try {
      const text = e.target.result
      const lines = text.split('\n').filter(line => line.trim())
      
      if (lines.length < 2) {
        ElMessage.error('文件内容为空或格式不正确')
        return
      }
      
      // 解析CSV数据
      const parsedData = []
      const headers = lines[0].split(',').map(h => h.trim())
      
      for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',').map(v => v.trim())
        if (values.length >= 8) {
          const record = {
            point_id: values[0],
            date: values[1],
            time: values[2],
            chlorine: parseFloat(values[3]) || 0,
            conductivity: parseFloat(values[4]) || 0,
            ph: parseFloat(values[5]) || 0,
            orp: parseFloat(values[6]) || 0,
            turbidity: parseFloat(values[7]) || 0
          }
          
          // 验证数据
          if (record.point_id && record.date && record.time) {
            parsedData.push(record)
          }
        }
      }
      
      previewData.value = parsedData
      ElMessage.success(`成功解析 ${parsedData.length} 条数据`)
    } catch (error) {
      ElMessage.error('文件解析失败，请检查格式')
    }
  }
  
  reader.readAsText(file.raw)
}

const handleBatchUploadSubmit = async () => {
  if (previewData.value.length === 0) {
    ElMessage.warning('没有可上传的数据')
    return
  }
  
  try {
    uploading.value = true
    
    // 分批上传，每批20条
    const batchSize = 20
    const batches = []
    
    for (let i = 0; i < previewData.value.length; i += batchSize) {
      batches.push(previewData.value.slice(i, i + batchSize))
    }
    
    let successCount = 0
    let errorCount = 0
    
    for (const batch of batches) {
      try {
        // 模拟批量创建API调用
        await Promise.all(batch.map(record => createRecord(record)))
        successCount += batch.length
      } catch (error) {
        errorCount += batch.length
      }
    }
    
    if (errorCount === 0) {
      ElMessage.success(`成功上传 ${successCount} 条数据`)
    } else {
      ElMessage.warning(`上传完成：成功 ${successCount} 条，失败 ${errorCount} 条`)
    }
    
    batchUploadVisible.value = false
    previewData.value = []
    loadRecords()
  } catch (error) {
    ElMessage.error('批量上传失败')
  } finally {
    uploading.value = false
  }
}

const getWaterQualityClass = (field, value) => {
  return getWaterQualityStatusColor(field, value, thresholds)
}

const getRecordStatus = (record) => {
  const fields = ['chlorine', 'conductivity', 'ph', 'orp', 'turbidity']
  for (const field of fields) {
    const status = getWaterQualityStatusColor(field, record[field], thresholds)
    if (status === 'danger') return '超标'
    if (status === 'warning') return '警告'
  }
  return '正常'
}

const getRecordStatusType = (record) => {
  const status = getRecordStatus(record)
  const typeMap = {
    '正常': 'success',
    '警告': 'warning',
    '超标': 'danger'
  }
  return typeMap[status] || 'info'
}

// 生命周期
onMounted(() => {
  loadRecords()
})
</script>

<style scoped>
.records-container {
  .operation-card {
    margin-bottom: 20px;
    
    .operation-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .operation-left {
        display: flex;
        gap: 10px;
      }
      
      .operation-right {
        display: flex;
        gap: 10px;
      }
    }
  }
  
  .table-card {
    .pagination-container {
      display: flex;
      justify-content: center;
      padding: 20px 0;
    }
  }
  
  .batch-upload-content {
    .preview-section {
      margin-top: 20px;
      
      h4 {
        margin-bottom: 10px;
        color: #333;
      }
    }
  }
}

// 水质状态颜色
.water-quality-normal {
  color: #67c23a;
}

.water-quality-warning {
  color: #e6a23c;
}

.water-quality-danger {
  color: #f56c6c;
}
</style>
