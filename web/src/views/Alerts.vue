<template>
  <div class="alerts-container">
    <!-- 统计卡片行 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stats-card" shadow="hover">
          <div class="stats-content">
            <div class="stats-icon danger">
              <el-icon size="32"><Warning /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value">{{ alertStats.total || 0 }}</div>
              <div class="stats-label">总报警数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card" shadow="hover">
          <div class="stats-content">
            <div class="stats-icon warning">
              <el-icon size="32"><Bell /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value">{{ alertStats.warning || 0 }}</div>
              <div class="stats-label">警告级别</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card" shadow="hover">
          <div class="stats-content">
            <div class="stats-icon danger">
              <el-icon size="32"><CircleCloseFilled /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value">{{ alertStats.critical || 0 }}</div>
              <div class="stats-label">严重级别</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card" shadow="hover">
          <div class="stats-content">
            <div class="stats-icon info">
              <el-icon size="32"><TrendCharts /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value">{{ alertStats.today || 0 }}</div>
              <div class="stats-label">今日新增</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表和列表行 -->
    <el-row :gutter="20" class="content-row">
      <!-- 左侧图表 -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>报警类型分布</span>
              <el-radio-group v-model="chartType" size="small">
                <el-radio-button label="pie">饼图</el-radio-button>
                <el-radio-button label="bar">柱状图</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <pie-chart 
            v-if="chartType === 'pie'"
            :data="alertTypeData" 
            height="300px" 
            title="报警类型分布"
          />
          <bar-chart 
            v-else
            :data="alertTypeData" 
            height="300px" 
            title="报警类型分布"
          />
        </el-card>
        
        <el-card class="trend-card" shadow="never">
          <template #header>
            <span>报警趋势（最近7天）</span>
          </template>
          <line-chart 
            :data="alertTrendData" 
            height="250px" 
            title="报警趋势"
          />
        </el-card>
      </el-col>
      
      <!-- 右侧列表 -->
      <el-col :span="12">
        <el-card class="list-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span><el-icon><List /></el-icon> 报警列表</span>
              <div class="list-actions">
                <el-select v-model="levelFilter" placeholder="筛选级别" size="small" style="width: 120px">
                  <el-option label="全部" value="" />
                  <el-option label="警告" value="警告" />
                  <el-option label="严重" value="严重" />
                </el-select>
                <el-button :icon="Refresh" size="small" @click="loadAlerts">
                  刷新
                </el-button>
              </div>
            </div>
          </template>
          
          <div class="alert-list">
            <div 
              v-for="alert in filteredAlerts" 
              :key="alert.record_id"
              class="alert-item"
              :class="alert.alert_level === '严重' ? 'danger' : 'warning'"
              @click="viewAlertDetail(alert)"
            >
              <div class="alert-header">
                <div class="alert-point">
                  <el-icon><Location /></el-icon>
                  {{ alert.point_id }}
                </div>
                <el-tag 
                  :type="alert.alert_level === '严重' ? 'danger' : 'warning'"
                  size="small"
                >
                  {{ alert.alert_level }}
                </el-tag>
              </div>
              
              <div class="alert-time">
                <el-icon><Clock /></el-icon>
                {{ alert.date }} {{ alert.time }}
              </div>
              
              <div class="alert-items">
                <el-tag 
                  v-for="item in alert.alert_items" 
                  :key="item"
                  type="danger"
                  size="small"
                  class="alert-tag"
                >
                  {{ item }}
                </el-tag>
              </div>
              
              <div class="alert-values">
                <div class="value-item">
                  <span class="label">pH:</span>
                  <span :class="getWaterQualityClass('ph', alert.ph)">
                    {{ formatWaterQualityValue(alert.ph) }}
                  </span>
                </div>
                <div class="value-item">
                  <span class="label">余氯:</span>
                  <span :class="getWaterQualityClass('chlorine', alert.chlorine)">
                    {{ formatWaterQualityValue(alert.chlorine) }}
                  </span>
                </div>
                <div class="value-item">
                  <span class="label">浊度:</span>
                  <span :class="getWaterQualityClass('turbidity', alert.turbidity)">
                    {{ formatWaterQualityValue(alert.turbidity) }}
                  </span>
                </div>
              </div>
            </div>
            
            <div v-if="filteredAlerts.length === 0" class="no-alerts">
              <el-empty description="暂无报警信息" :image-size="80" />
            </div>
          </div>
          
          <!-- 分页 -->
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50]"
              :total="total"
              layout="total, sizes, prev, pager, next"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              small
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 报警详情对话框 -->
    <el-dialog v-model="detailVisible" title="报警详情" width="700px">
      <div v-if="currentAlert" class="alert-detail">
        <el-alert
          :title="`${currentAlert.point_id} - ${currentAlert.alert_level}级别报警`"
          :type="currentAlert.alert_level === '严重' ? 'error' : 'warning'"
          :closable="false"
          show-icon
          class="detail-alert"
        >
          <template #default>
            <div>{{ currentAlert.date }} {{ currentAlert.time }}</div>
            <div>报警项目：{{ currentAlert.alert_items.join('、') }}</div>
          </template>
        </el-alert>
        
        <el-descriptions :column="2" border class="detail-descriptions">
          <el-descriptions-item label="监测点">{{ currentAlert.point_id }}</el-descriptions-item>
          <el-descriptions-item label="报警级别">
            <el-tag :type="currentAlert.alert_level === '严重' ? 'danger' : 'warning'">
              {{ currentAlert.alert_level }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="日期">{{ currentAlert.date }}</el-descriptions-item>
          <el-descriptions-item label="时间">{{ currentAlert.time }}</el-descriptions-item>
          <el-descriptions-item label="余氯(mg/L)">
            <span :class="getWaterQualityClass('chlorine', currentAlert.chlorine)">
              {{ formatWaterQualityValue(currentAlert.chlorine) }}
            </span>
            <el-tag 
              v-if="isOutOfRange('chlorine', currentAlert.chlorine)"
              type="danger"
              size="small"
              class="threshold-tag"
            >
              超标
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="电导率(µS/cm)">
            <span :class="getWaterQualityClass('conductivity', currentAlert.conductivity)">
              {{ formatWaterQualityValue(currentAlert.conductivity) }}
            </span>
            <el-tag 
              v-if="isOutOfRange('conductivity', currentAlert.conductivity)"
              type="danger"
              size="small"
              class="threshold-tag"
            >
              超标
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="pH值">
            <span :class="getWaterQualityClass('ph', currentAlert.ph)">
              {{ formatWaterQualityValue(currentAlert.ph) }}
            </span>
            <el-tag 
              v-if="isOutOfRange('ph', currentAlert.ph)"
              type="danger"
              size="small"
              class="threshold-tag"
            >
              超标
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="氧化还原电位(mV)">
            <span :class="getWaterQualityClass('orp', currentAlert.orp)">
              {{ formatWaterQualityValue(currentAlert.orp) }}
            </span>
            <el-tag 
              v-if="isOutOfRange('orp', currentAlert.orp)"
              type="danger"
              size="small"
              class="threshold-tag"
            >
              超标
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="浊度(NTU)">
            <span :class="getWaterQualityClass('turbidity', currentAlert.turbidity)">
              {{ formatWaterQualityValue(currentAlert.turbidity) }}
            </span>
            <el-tag 
              v-if="isOutOfRange('turbidity', currentAlert.turbidity)"
              type="danger"
              size="small"
              class="threshold-tag"
            >
              超标
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间" span="2">
            {{ formatDateTime(currentAlert.create_time) }}
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 阈值说明 -->
        <el-collapse class="threshold-collapse">
          <el-collapse-item title="查看阈值标准" name="thresholds">
            <el-table :data="thresholdTableData" size="small">
              <el-table-column prop="indicator" label="指标" width="120" />
              <el-table-column prop="unit" label="单位" width="100" />
              <el-table-column prop="range" label="正常范围" />
              <el-table-column label="状态">
                <template #default="{ row }">
                  <el-tag type="success">正常</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-collapse-item>
        </el-collapse>
      </div>
      
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="editRecord">编辑记录</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Warning,
  Bell,
  CircleCloseFilled,
  TrendCharts,
  List,
  Refresh,
  Location,
  Clock
} from '@element-plus/icons-vue'
import { getAlerts, getStatistics } from '@/api/records'
import {
  formatDateTime,
  formatWaterQualityValue,
  getWaterQualityStatusColor
} from '@/utils/format'
import PieChart from '@/components/charts/PieChart.vue'
import LineChart from '@/components/charts/LineChart.vue'
import BarChart from '@/components/charts/BarChart.vue'

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
const alerts = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const levelFilter = ref('')
const chartType = ref('pie')
const detailVisible = ref(false)
const currentAlert = ref(null)

// 计算属性
const alertStats = computed(() => {
  const stats = {
    total: alerts.value.length,
    warning: alerts.value.filter(a => a.alert_level === '警告').length,
    critical: alerts.value.filter(a => a.alert_level === '严重').length,
    today: alerts.value.filter(a => {
      const alertDate = new Date(a.date)
      const today = new Date()
      return alertDate.toDateString() === today.toDateString()
    }).length
  }
  return stats
})

const filteredAlerts = computed(() => {
  if (!levelFilter.value) {
    return alerts.value
  }
  return alerts.value.filter(alert => alert.alert_level === levelFilter.value)
})

const alertTypeData = computed(() => {
  const typeCount = {}
  alerts.value.forEach(alert => {
    alert.alert_items.forEach(item => {
      const key = item.replace(/偏高|偏低/g, '')
      typeCount[key] = (typeCount[key] || 0) + 1
    })
  })
  
  return Object.entries(typeCount).map(([name, value]) => ({ name, value }))
})

const alertTrendData = computed(() => {
  // 生成最近7天的趋势数据
  const trendData = []
  const today = new Date()
  
  for (let i = 6; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(today.getDate() - i)
    const dateStr = date.toISOString().split('T')[0]
    
    const count = alerts.value.filter(alert => alert.date === dateStr).length
    trendData.push({
      date: dateStr,
      count: count
    })
  }
  
  return trendData
})

const thresholdTableData = computed(() => [
  {
    indicator: '余氯',
    unit: 'mg/L',
    range: '0.5 - 4.0'
  },
  {
    indicator: '电导率',
    unit: 'µS/cm',
    range: '≤ 1000'
  },
  {
    indicator: 'pH值',
    unit: '',
    range: '6.5 - 8.5'
  },
  {
    indicator: '氧化还原电位',
    unit: 'mV',
    range: '≥ 400'
  },
  {
    indicator: '浊度',
    unit: 'NTU',
    range: '≤ 5.0'
  }
])

// 方法
const loadAlerts = async () => {
  try {
    loading.value = true
    const params = {
      limit: 1000, // 获取更多数据用于统计
      page: 1,
      page_size: 1000
    }
    const data = await getAlerts(params)
    alerts.value = data.results || data
    total.value = data.count || data.length
  } catch (error) {
    ElMessage.error('加载报警数据失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadAlerts()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadAlerts()
}

const viewAlertDetail = (alert) => {
  currentAlert.value = alert
  detailVisible.value = true
}

const editRecord = () => {
  if (currentAlert.value) {
    router.push({
      path: '/records',
      query: { id: currentAlert.value.record_id }
    })
    detailVisible.value = false
  }
}

const getWaterQualityClass = (field, value) => {
  return getWaterQualityStatusColor(field, value, thresholds)
}

const isOutOfRange = (field, value) => {
  const threshold = thresholds[field]
  if (!threshold) return false
  
  if (threshold.min !== undefined && value < threshold.min) return true
  if (threshold.max !== undefined && value > threshold.max) return true
  
  return false
}

// 生命周期
onMounted(() => {
  loadAlerts()
})
</script>

<style lang="scss" scoped>
.alerts-container {
  .stats-row {
    margin-bottom: $spacing-lg;
    
    .stats-card {
      .stats-content {
        @include flex-center;
        gap: $spacing-md;
        
        .stats-icon {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          @include flex-center;
          
          &.danger {
            background-color: rgba(var(--el-color-danger-rgb), 0.1);
            color: var(--el-color-danger);
          }
          
          &.warning {
            background-color: rgba(var(--el-color-warning-rgb), 0.1);
            color: var(--el-color-warning);
          }
          
          &.info {
            background-color: rgba(var(--el-color-info-rgb), 0.1);
            color: var(--el-color-info);
          }
        }
        
        .stats-info {
          .stats-value {
            font-size: $font-size-extra-large;
            font-weight: 600;
            color: var(--el-text-color-primary);
            margin-bottom: $spacing-xs;
          }
          
          .stats-label {
            font-size: $font-size-sm;
            color: var(--el-text-color-secondary);
          }
        }
      }
    }
  }
  
  .content-row {
    .chart-card,
    .trend-card,
    .list-card {
      margin-bottom: $spacing-lg;
      
      .card-header {
        @include flex-between;
        font-weight: 600;
      }
    }
    
    .trend-card {
      margin-top: $spacing-lg;
    }
    
    .list-card {
      .list-actions {
        display: flex;
        gap: $spacing-sm;
      }
      
      .alert-list {
        max-height: 600px;
        overflow-y: auto;
        
        .alert-item {
          padding: $spacing-md;
          border-radius: var(--el-border-radius-base);
          margin-bottom: $spacing-sm;
          border-left: 3px solid transparent;
          cursor: pointer;
          transition: all 0.3s ease;
          
          &.danger {
            background-color: rgba(var(--el-color-danger-rgb), 0.05);
            border-left-color: var(--el-color-danger);
          }
          
          &.warning {
            background-color: rgba(var(--el-color-warning-rgb), 0.05);
            border-left-color: var(--el-color-warning);
          }
          
          &:hover {
            transform: translateX(2px);
            box-shadow: var(--el-box-shadow-light);
          }
          
          .alert-header {
            @include flex-between;
            margin-bottom: $spacing-xs;
            
            .alert-point {
              font-weight: 600;
              color: var(--el-text-color-primary);
              @include flex-center-vertical;
              gap: $spacing-xs;
            }
          }
          
          .alert-time {
            font-size: $font-size-extra-small;
            color: var(--el-text-color-secondary);
            @include flex-center-vertical;
            gap: $spacing-xs;
            margin-bottom: $spacing-xs;
          }
          
          .alert-items {
            display: flex;
            flex-wrap: wrap;
            gap: $spacing-xs;
            margin-bottom: $spacing-xs;
            
            .alert-tag {
              font-size: $font-size-extra-small;
            }
          }
          
          .alert-values {
            display: flex;
            gap: $spacing-md;
            
            .value-item {
              font-size: $font-size-extra-small;
              
              .label {
                color: var(--el-text-color-secondary);
                margin-right: $spacing-xs;
              }
            }
          }
        }
        
        .no-alerts {
          display: flex;
          justify-content: center;
          align-items: center;
          height: 200px;
        }
      }
      
      .pagination-container {
        @include flex-center;
        padding: $spacing-lg 0 0;
      }
    }
  }
  
  .alert-detail {
    .detail-alert {
      margin-bottom: $spacing-lg;
    }
    
    .detail-descriptions {
      margin-bottom: $spacing-lg;
      
      .threshold-tag {
        margin-left: $spacing-sm;
      }
    }
    
    .threshold-collapse {
      .el-collapse-item__header {
        font-weight: 600;
      }
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
  .stats-row {
    .el-col {
      margin-bottom: $spacing-md;
    }
  }
  
  .content-row {
    .el-col {
      margin-bottom: $spacing-md;
    }
  }
  
  .alert-values {
    flex-direction: column;
    gap: $spacing-xs !important;
  }
}
</style>
