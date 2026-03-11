<template>
  <div class="query-container">
    <!-- 查询条件卡片 -->
    <el-card class="query-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span><el-icon><Search /></el-icon> 高级查询</span>
          <el-button @click="resetQuery" :icon="Refresh">重置</el-button>
        </div>
      </template>
      
      <!-- 动态查询条件组 -->
      <div class="query-groups">
        <div v-for="(group, index) in queryGroups" :key="index" class="query-item">
          <el-select v-model="group.field" placeholder="选择字段" style="width: 150px">
            <el-option label="监测点" value="point_id" />
            <el-option label="日期" value="date" />
            <el-option label="PH值" value="ph" />
            <el-option label="余氯" value="chlorine" />
            <el-option label="电导率" value="conductivity" />
            <el-option label="氧化还原电位" value="orp" />
            <el-option label="浊度" value="turbidity" />
          </el-select>
          
          <el-select v-model="group.operator" placeholder="操作符" style="width: 120px">
            <el-option label="等于" value="eq" />
            <el-option label="不等于" value="ne" />
            <el-option label="大于" value="gt" />
            <el-option label="大于等于" value="gte" />
            <el-option label="小于" value="lt" />
            <el-option label="小于等于" value="lte" />
            <el-option label="包含" value="contains" />
            <el-option label="介于" value="between" />
          </el-select>
          
          <!-- 动态输入框，根据字段类型变化 -->
          <template v-if="!isBetweenOperator(group.operator)">
            <el-input 
              v-if="isTextField(group.field)"
              v-model="group.value" 
              placeholder="输入值" 
              style="width: 200px" 
            />
            <el-input-number
              v-else
              v-model="group.value" 
              placeholder="输入数值" 
              style="width: 200px"
              :precision="2"
            />
          </template>
          
          <div v-else class="between-inputs">
            <el-input-number
              v-model="group.min" 
              placeholder="最小值" 
              style="width: 100px"
              :precision="2"
            />
            <span class="separator">-</span>
            <el-input-number
              v-model="group.max" 
              placeholder="最大值" 
              style="width: 100px"
              :precision="2"
            />
          </div>
          
          <el-button 
            type="danger" 
            :icon="Delete" 
            circle 
            size="small"
            @click="removeGroup(index)"
          />
        </div>
      </div>
      
      <div class="query-actions">
        <el-button @click="addGroup" :icon="Plus">添加条件</el-button>
        <el-button type="primary" @click="handleQuery" :icon="Search" :loading="loading">
          查询
        </el-button>
        <el-button @click="resetQuery">重置</el-button>
      </div>
    </el-card>

    <!-- 查询结果 -->
    <el-card v-if="showResult" class="result-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>查询结果（共 {{ total }} 条）</span>
          <div class="result-actions">
            <el-button :icon="Download" size="small" @click="exportResults">
              导出
            </el-button>
            <el-button :icon="Refresh" size="small" @click="loadResults">
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 结果表格 -->
      <el-table
        v-loading="loading"
        :data="queryResults"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column prop="record_id" label="ID" width="80" />
        
        <el-table-column prop="point_id" label="监测点" width="120">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.point_id }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="time" label="时间" width="80" />
        
        <el-table-column prop="chlorine" label="余氯(mg/L)" width="110">
          <template #default="{ row }">
            <span :class="getWaterQualityClass('chlorine', row.chlorine)">
              {{ formatWaterQualityValue(row.chlorine) }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="conductivity" label="电导率(µS/cm)" width="130">
          <template #default="{ row }">
            <span :class="getWaterQualityClass('conductivity', row.conductivity)">
              {{ formatWaterQualityValue(row.conductivity) }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="ph" label="pH值" width="80">
          <template #default="{ row }">
            <span :class="getWaterQualityClass('ph', row.ph)">
              {{ formatWaterQualityValue(row.ph) }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="orp" label="氧化还原电位(mV)" width="140">
          <template #default="{ row }">
            <span :class="getWaterQualityClass('orp', row.orp)">
              {{ formatWaterQualityValue(row.orp) }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="turbidity" label="浊度(NTU)" width="100">
          <template #default="{ row }">
            <span :class="getWaterQualityClass('turbidity', row.turbidity)">
              {{ formatWaterQualityValue(row.turbidity) }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag 
              :type="getRecordStatusType(row)"
              size="small"
            >
              {{ getRecordStatus(row) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetail(row)">
              详情
            </el-button>
            <el-button type="success" link size="small" @click="editRecord(row)">
              编辑
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

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="记录详情" width="600px">
      <div v-if="currentRecord" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="记录ID">{{ currentRecord.record_id }}</el-descriptions-item>
          <el-descriptions-item label="监测点">{{ currentRecord.point_id }}</el-descriptions-item>
          <el-descriptions-item label="日期">{{ currentRecord.date }}</el-descriptions-item>
          <el-descriptions-item label="时间">{{ currentRecord.time }}</el-descriptions-item>
          <el-descriptions-item label="余氯(mg/L)">
            <span :class="getWaterQualityClass('chlorine', currentRecord.chlorine)">
              {{ formatWaterQualityValue(currentRecord.chlorine) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="电导率(µS/cm)">
            <span :class="getWaterQualityClass('conductivity', currentRecord.conductivity)">
              {{ formatWaterQualityValue(currentRecord.conductivity) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="pH值">
            <span :class="getWaterQualityClass('ph', currentRecord.ph)">
              {{ formatWaterQualityValue(currentRecord.ph) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="氧化还原电位(mV)">
            <span :class="getWaterQualityClass('orp', currentRecord.orp)">
              {{ formatWaterQualityValue(currentRecord.orp) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="浊度(NTU)">
            <span :class="getWaterQualityClass('turbidity', currentRecord.turbidity)">
              {{ formatWaterQualityValue(currentRecord.turbidity) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(currentRecord.create_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="水质状态">
            <el-tag :type="getRecordStatusType(currentRecord)">
              {{ getRecordStatus(currentRecord) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Search,
  Plus,
  Delete,
  Refresh,
  Download
} from '@element-plus/icons-vue'
import { queryRecords } from '@/api/records'
import {
  formatDateTime,
  formatWaterQualityValue,
  getWaterQualityStatusColor
} from '@/utils/format'

const router = useRouter()

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
const showResult = ref(false)
const queryResults = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

// 查询条件组
const queryGroups = ref([
  {
    field: '',
    operator: 'eq',
    value: null,
    min: null,
    max: null
  }
])

// 详情对话框
const detailVisible = ref(false)
const currentRecord = ref(null)

// 方法
const isTextField = (field) => {
  return field === 'point_id' || field === 'date'
}

const isBetweenOperator = (operator) => {
  return operator === 'between'
}

const addGroup = () => {
  queryGroups.value.push({
    field: '',
    operator: 'eq',
    value: null,
    min: null,
    max: null
  })
}

const removeGroup = (index) => {
  if (queryGroups.value.length > 1) {
    queryGroups.value.splice(index, 1)
  } else {
    ElMessage.warning('至少保留一个查询条件')
  }
}

const resetQuery = () => {
  queryGroups.value = [
    {
      field: '',
      operator: 'eq',
      value: null,
      min: null,
      max: null
    }
  ]
  showResult.value = false
  queryResults.value = []
  total.value = 0
  currentPage.value = 1
}

const buildQueryParams = () => {
  const params = {}
  
  queryGroups.value.forEach(group => {
    if (!group.field) return
    
    const field = group.field
    const operator = group.operator
    
    switch (operator) {
      case 'eq':
        params[field] = group.value
        break
      case 'ne':
        params[`${field}_ne`] = group.value
        break
      case 'gt':
        params[`${field}_min`] = group.value
        break
      case 'gte':
        params[`${field}_gte`] = group.value
        break
      case 'lt':
        params[`${field}_max`] = group.value
        break
      case 'lte':
        params[`${field}_lte`] = group.value
        break
      case 'contains':
        params[`${field}_contains`] = group.value
        break
      case 'between':
        params[`${field}_min`] = group.min
        params[`${field}_max`] = group.max
        break
    }
  })
  
  return params
}

const handleQuery = async () => {
  try {
    // 验证查询条件
    const validGroups = queryGroups.value.filter(group => group.field && group.operator)
    if (validGroups.length === 0) {
      ElMessage.warning('请至少设置一个有效的查询条件')
      return
    }
    
    // 验证between操作符的值
    for (const group of validGroups) {
      if (group.operator === 'between') {
        if (group.min === null || group.max === null) {
          ElMessage.warning('介于操作需要设置最小值和最大值')
          return
        }
        if (group.min > group.max) {
          ElMessage.warning('最小值不能大于最大值')
          return
        }
      } else if (group.value === null || group.value === '') {
        ElMessage.warning('请填写查询值')
        return
      }
    }
    
    loading.value = true
    const params = buildQueryParams()
    params.page = currentPage.value
    params.page_size = pageSize.value
    
    const data = await queryRecords(params)
    queryResults.value = data.results || data
    total.value = data.count || data.length
    showResult.value = true
    
    if (queryResults.value.length === 0) {
      ElMessage.info('未找到符合条件的数据')
    }
  } catch (error) {
    ElMessage.error('查询失败')
  } finally {
    loading.value = false
  }
}

const loadResults = async () => {
  if (!showResult.value) return
  
  try {
    loading.value = true
    const params = buildQueryParams()
    params.page = currentPage.value
    params.page_size = pageSize.value
    
    const data = await queryRecords(params)
    queryResults.value = data.results || data
    total.value = data.count || data.length
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadResults()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadResults()
}

const exportResults = () => {
  if (queryResults.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }
  
  const data = {
    query_conditions: queryGroups.value.filter(group => group.field),
    results: queryResults.value,
    total: total.value,
    export_time: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `query_results_${new Date().toISOString().split('T')[0]}.json`
  a.click()
  window.URL.revokeObjectURL(url)
  ElMessage.success('导出成功')
}

const viewDetail = (row) => {
  currentRecord.value = row
  detailVisible.value = true
}

const editRecord = (row) => {
  router.push({
    path: '/records',
    query: { id: row.record_id }
  })
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
</script>

<style lang="scss" scoped>
.query-container {
  .query-card {
    margin-bottom: $spacing-lg;
    
    .card-header {
      @include flex-between;
      font-weight: 600;
    }
    
    .query-groups {
      margin-bottom: $spacing-lg;
      
      .query-item {
        display: flex;
        align-items: center;
        gap: $spacing-sm;
        margin-bottom: $spacing-md;
        padding: $spacing-md;
        background-color: var(--el-fill-color-extra-light);
        border-radius: var(--el-border-radius-base);
        
        .between-inputs {
          display: flex;
          align-items: center;
          gap: $spacing-xs;
          
          .separator {
            color: var(--el-text-color-secondary);
            font-weight: 600;
          }
        }
      }
    }
    
    .query-actions {
      display: flex;
      gap: $spacing-sm;
    }
  }
  
  .result-card {
    .card-header {
      @include flex-between;
      font-weight: 600;
      
      .result-actions {
        display: flex;
        gap: $spacing-sm;
      }
    }
    
    .pagination-container {
      @include flex-center;
      padding: $spacing-lg 0;
    }
  }
  
  .detail-content {
    .el-descriptions {
      margin-bottom: 0;
    }
  }
}

// 水质状态颜色
.water-quality-normal {
  color: var(--el-color-success);
}

.water-quality-warning {
  color: var(--el-color-warning);
}

.water-quality-danger {
  color: var(--el-color-danger);
}

// 响应式设计
@include respond-to(md) {
  .query-item {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-sm !important;
    
    > * {
      width: 100%;
    }
  }
  
  .query-actions {
    justify-content: center;
  }
}
</style>
