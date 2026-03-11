<template>
  <div class="dashboard-container">
    <!-- 顶部KPI卡片行 -->
    <el-row :gutter="20" class="kpi-row">
      <el-col :span="6" v-for="item in kpiList" :key="item.label">
        <el-card :body-style="{ padding: '20px' }" shadow="hover" class="kpi-card">
          <div class="kpi-content">
            <div class="kpi-icon" :style="{ background: item.color + '20' }">
              <el-icon :color="item.color" :size="24">
                <component :is="item.icon" />
              </el-icon>
            </div>
            <div class="kpi-info">
              <div class="kpi-label">{{ item.label }}</div>
              <div class="kpi-value">
                <count-to :start-val="0" :end-val="item.value" :duration="2000" />
              </div>
              <div class="kpi-trend" :class="item.trend > 0 ? 'up' : 'down'">
                <el-icon size="12">
                  <component :is="item.trend > 0 ? 'TrendCharts' : 'Bottom'" />
                </el-icon>
                {{ Math.abs(item.trend) }}% 较昨日
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 中间图表行 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>水质指标趋势（最近7天）</span>
              <el-radio-group v-model="trendType" size="small">
                <el-radio-button label="all">全部</el-radio-button>
                <el-radio-button label="ph">PH值</el-radio-button>
                <el-radio-button label="turbidity">浊度</el-radio-button>
                <el-radio-button label="chlorine">余氯</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <line-chart :data="filteredTrendData" height="350px" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span>当前水质指标</span>
          </template>
          <gauge-chart :data="currentRecord" height="350px" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 底部报警和统计行 -->
    <el-row :gutter="20" class="bottom-row">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><Warning /></el-icon> 报警统计</span>
              <el-button type="primary" link @click="$router.push('/alerts')">
                查看更多
              </el-button>
            </div>
          </template>
          <pie-chart 
            :data="alertStatsData" 
            height="280px" 
            title="报警类型分布"
            :show-legend="true"
          />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="alert-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><Bell /></el-icon> 实时报警（最新5条）</span>
              <el-button type="primary" link @click="$router.push('/alerts')">
                查看全部
              </el-button>
            </div>
          </template>
          <div class="alert-list">
            <div 
              v-for="alert in recentAlerts" 
              :key="alert.record_id"
              class="alert-item"
              :class="alert.alert_level === '严重' ? 'danger' : 'warning'"
            >
              <div class="alert-info">
                <div class="alert-header">
                  <span class="alert-point">{{ alert.point_id }}</span>
                  <el-tag 
                    :type="alert.alert_level === '严重' ? 'danger' : 'warning'"
                    size="small"
                  >
                    {{ alert.alert_level }}
                  </el-tag>
                </div>
                <div class="alert-time">
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
              </div>
            </div>
            <div v-if="recentAlerts.length === 0" class="no-alerts">
              <el-empty description="暂无报警信息" :image-size="80" />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { CountUp } from 'vue-countup'
import { getDashboardData } from '@/api/records'
import { formatWaterQualityValue } from '@/utils/format'
import LineChart from '@/components/charts/LineChart.vue'
import PieChart from '@/components/charts/PieChart.vue'
import GaugeChart from '@/components/charts/GaugeChart.vue'
import {
  DataBoard,
  List,
  Warning,
  Bell,
  TrendCharts,
  Bottom,
  Water,
  Monitor,
  DataAnalysis
} from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const dashboardData = ref({})
const trendType = ref('all')

// 计算属性
const kpiList = computed(() => {
  const stats = dashboardData.value.stats || {}
  return [
    {
      label: '总记录数',
      value: stats.total_records || 0,
      trend: 5.2,
      color: '#409EFF',
      icon: 'DataBoard'
    },
    {
      label: '平均pH值',
      value: (stats.avg_values?.ph || 0).toFixed(1),
      trend: -1.3,
      color: '#67C23A',
      icon: 'Monitor'
    },
    {
      label: '平均浊度',
      value: (stats.avg_values?.turbidity || 0).toFixed(1),
      trend: 2.8,
      color: '#E6A23C',
      icon: 'Water'
    },
    {
      label: '报警数量',
      value: stats.alert_count || 0,
      trend: -8.5,
      color: '#F56C6C',
      icon: 'Warning'
    }
  ]
})

const currentRecord = computed(() => {
  return dashboardData.value.current_record || {}
})

const trendData = computed(() => {
  return dashboardData.value.trend_data || []
})

const filteredTrendData = computed(() => {
  if (trendType.value === 'all') {
    return trendData.value
  }
  return trendData.value.map(item => ({
    ...item,
    ph: trendType.value === 'ph' ? item.ph : null,
    turbidity: trendType.value === 'turbidity' ? item.turbidity : null,
    chlorine: trendType.value === 'chlorine' ? item.chlorine : null
  }))
})

const recentAlerts = computed(() => {
  return dashboardData.value.recent_alerts || []
})

const alertStatsData = computed(() => {
  const alerts = recentAlerts.value
  const stats = {}
  
  alerts.forEach(alert => {
    alert.alert_items.forEach(item => {
      const key = item.replace(/偏高|偏低/g, '')
      stats[key] = (stats[key] || 0) + 1
    })
  })
  
  return Object.entries(stats).map(([name, value]) => ({ name, value }))
})

// 方法
const loadDashboardData = async () => {
  try {
    loading.value = true
    const data = await getDashboardData()
    dashboardData.value = data
  } catch (error) {
    console.error('加载仪表盘数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  loadDashboardData()
})
</script>

<style lang="scss" scoped>
.dashboard-container {
  padding: 0;
}

.kpi-row {
  margin-bottom: $spacing-lg;
}

.kpi-card {
  .kpi-content {
    display: flex;
    align-items: center;
    gap: $spacing-md;
    
    .kpi-icon {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .kpi-info {
      flex: 1;
      
      .kpi-label {
        font-size: $font-size-sm;
        color: var(--el-text-color-secondary);
        margin-bottom: $spacing-xs;
      }
      
      .kpi-value {
        font-size: $font-size-extra-large;
        font-weight: 600;
        color: var(--el-text-color-primary);
        margin-bottom: $spacing-xs;
      }
      
      .kpi-trend {
        display: flex;
        align-items: center;
        gap: $spacing-xs;
        font-size: $font-size-extra-small;
        
        &.up {
          color: var(--el-color-success);
        }
        
        &.down {
          color: var(--el-color-danger);
        }
      }
    }
  }
}

.chart-row {
  margin-bottom: $spacing-lg;
}

.chart-card {
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 600;
  }
}

.bottom-row {
  .alert-card {
    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-weight: 600;
    }
    
    .alert-list {
      max-height: 280px;
      overflow-y: auto;
      
      .alert-item {
        padding: $spacing-md;
        border-radius: var(--el-border-radius-base);
        margin-bottom: $spacing-sm;
        border-left: 3px solid transparent;
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
        }
        
        .alert-info {
          .alert-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: $spacing-xs;
            
            .alert-point {
              font-weight: 600;
              color: var(--el-text-color-primary);
            }
          }
          
          .alert-time {
            font-size: $font-size-extra-small;
            color: var(--el-text-color-secondary);
            margin-bottom: $spacing-xs;
          }
          
          .alert-items {
            display: flex;
            flex-wrap: wrap;
            gap: $spacing-xs;
            
            .alert-tag {
              font-size: $font-size-extra-small;
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
  }
}

// 响应式设计
@include respond-to(md) {
  .kpi-row {
    .el-col {
      margin-bottom: $spacing-md;
    }
  }
}

@include respond-to(sm) {
  .chart-row {
    .el-col {
      margin-bottom: $spacing-md;
    }
  }
  
  .bottom-row {
    .el-col {
      margin-bottom: $spacing-md;
    }
  }
}
</style>
