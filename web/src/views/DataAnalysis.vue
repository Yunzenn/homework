<template>
  <div class="data-analysis-page" v-loading="loading">
    <!-- 页面头部 -->
    <div class="analysis-header">
      <div class="header-left">
        <h2 class="page-title">
          <el-icon><DataLine /></el-icon>
          数据分析中心
        </h2>
        <p class="page-subtitle">专业水质监控 · 智能分析 · 决策支持</p>
      </div>
      <div class="header-right">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          :shortcuts="dateShortcuts"
          @change="onDateRangeChange"
          class="date-picker"
        />
        <el-button 
          type="primary" 
          :icon="Refresh" 
          @click="refreshData"
          :loading="loading"
          class="refresh-btn"
        >
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- KPI 概览卡片 -->
    <div class="overview-section">
      <div class="overview-cards">
        <div 
          v-for="(card, index) in kpiCards" 
          :key="card.key"
          class="overview-card"
          :class="`card-${index + 1}`"
          @mouseenter="card.hovered = true"
          @mouseleave="card.hovered = false"
        >
          <div class="card-icon-container">
            <el-icon :class="getIconClass(card.icon)" :size="32">
              <component :is="card.icon" />
            </el-icon>
          </div>
          <div class="card-content">
            <div class="card-title">{{ card.title }}</div>
            <div class="card-value">{{ formatNumber(card.value) }}</div>
            <div class="card-change" :class="getChangeClass(card.change)">
              <span class="change-text">{{ formatChange(card.change) }}</span>
              <el-icon class="change-icon" :size="12">
                <ArrowUp v-if="card.change > 0" />
                <ArrowDown v-else-if="card.change < 0" />
                <Minus v-else />
              </el-icon>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 智能分析区域 -->
    <div class="intelligent-analysis-section">
      <div class="analysis-header">
        <h3 class="section-title">
          <el-icon><MagicStick /></el-icon>
          智能分析中心
        </h3>
        <p class="section-subtitle">污染溯源 · 水质预测 · 决策支持</p>
      </div>
      
      <SimpleAnalysis />
    </div>

    <!-- 图表分析区域 -->
    <div class="charts-section">
      <div class="chart-row">
        <!-- 数据趋势图 -->
        <div class="chart-container trend-chart">
          <div class="chart-header">
            <h3 class="chart-title">
              <el-icon><TrendCharts /></el-icon>
              数据趋势分析
            </h3>
            <div class="chart-controls">
              <el-select
                v-model="trendMetrics"
                multiple
                collapse-tags
                collapse-tags-tooltip
                placeholder="选择指标"
                @change="updateTrendChart"
                class="metric-select"
              >
                <el-option
                  v-for="metric in metricOptions"
                  :key="metric.value"
                  :label="metric.label"
                  :value="metric.value"
                >
                  <el-icon class="option-icon">
                    <component :is="metric.icon" />
                  </el-icon>
                  {{ metric.label }}
                </el-option>
              </el-select>
              <el-select
                v-model="trendPeriod"
                @change="updateTrendChart"
                class="period-select"
              >
                <el-option label="按天" value="day" />
                <el-option label="按周" value="week" />
                <el-option label="按月" value="month" />
              </el-select>
            </div>
          </div>
          <div class="chart-content" ref="trendChartRef"></div>
        </div>

        <!-- 指标分布图 -->
        <div class="chart-container distribution-chart">
          <div class="chart-header">
            <h3 class="chart-title">
              <el-icon><PieChart /></el-icon>
              {{ distributionTitle }}
            </h3>
            <div class="chart-controls">
              <el-button-group>
                <el-button 
                  :type="distributionType === 'alerts' ? 'primary' : 'default'"
                  @click="switchDistributionType('alerts')"
                >
                  超标统计
                </el-button>
                <el-button 
                  :type="distributionType === 'radar' ? 'primary' : 'default'"
                  @click="switchDistributionType('radar')"
                >
                  雷达分析
                </el-button>
              </el-button-group>
            </div>
          </div>
          <div class="chart-content" ref="distributionChartRef"></div>
        </div>
      </div>

      <div class="chart-row">
        <!-- 相关性热力图 -->
        <div class="chart-container correlation-chart">
          <div class="chart-header">
            <h3 class="chart-title">
              <el-icon><Histogram /></el-icon>
              指标相关性分析
            </h3>
          </div>
          <div class="chart-content" ref="correlationChartRef"></div>
        </div>

        <!-- 监测点对比 -->
        <div class="chart-container comparison-chart">
          <div class="chart-header">
            <h3 class="chart-title">
              <el-icon><Histogram /></el-icon>
              监测点对比分析
            </h3>
            <div class="chart-controls">
              <el-select
                v-model="comparisonMetric"
                @change="updateComparisonChart"
                class="comparison-select"
              >
                <el-option label="平均值" value="avg" />
                <el-option label="最大值" value="max" />
                <el-option label="最小值" value="min" />
                <el-option label="超标率" value="alert_rate" />
              </el-select>
            </div>
          </div>
          <div class="chart-content" ref="comparisonChartRef"></div>
        </div>
      </div>
    </div>

    <!-- 详细数据表格 -->
    <div class="data-table-section">
      <div class="table-header">
        <h3 class="table-title">
          <el-icon><Grid /></el-icon>
          监测点详细分析
        </h3>
        <div class="table-controls">
          <el-input
            v-model="tableSearch"
            placeholder="搜索监测点..."
            :prefix-icon="Search"
            clearable
            class="search-input"
          />
          <el-select
            v-model="tableSort"
            @change="updateTableData"
            class="sort-select"
          >
            <el-option label="按日期" value="date" />
            <el-option label="按监测点" value="point_id" />
            <el-option label="按超标数" value="alert_count" />
          </el-select>
          <el-button 
            type="success" 
            :icon="Download" 
            @click="exportAnalysisData"
          >
            导出报告
          </el-button>
        </div>
      </div>
      
      <div class="table-container">
        <el-table
          :data="filteredTableData"
          style="width: 100%"
          :default-sort="{ prop: tableSort, order: 'descending' }"
          @sort-change="handleSortChange"
          class="analysis-table"
        >
          <el-table-column prop="point_id" label="监测点" width="120" />
          <el-table-column prop="record_count" label="记录数" width="100" />
          <el-table-column prop="alert_count" label="超标数" width="100" />
          <el-table-column prop="alert_rate" label="超标率" width="100">
            <template #default="scope">
              <el-tag :type="getAlertTagType(scope.row.alert_rate)" size="small">
                {{ scope.row.alert_rate }}%
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="avg_chlorine" label="平均余氯" width="120">
            <template #default="scope">
              {{ scope.row.avg_chlorine?.toFixed(2) }} mg/L
            </template>
          </el-table-column>
          <el-table-column prop="avg_conductivity" label="平均电导率" width="130">
            <template #default="scope">
              {{ scope.row.avg_conductivity?.toFixed(2) }} µS/cm
            </template>
          </el-table-column>
          <el-table-column prop="avg_ph" label="平均pH值" width="110">
            <template #default="scope">
              {{ scope.row.avg_ph?.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="avg_orp" label="平均ORP" width="110">
            <template #default="scope">
              {{ scope.row.avg_orp?.toFixed(2) }} mV
            </template>
          </el-table-column>
          <el-table-column prop="avg_turbidity" label="平均浊度" width="120">
            <template #default="scope">
              {{ scope.row.avg_turbidity?.toFixed(2) }} NTU
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="scope">
              <el-button 
                type="primary" 
                size="small" 
                :icon="View" 
                @click="viewPointDetail(scope.row)"
              >
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="showDetailModal"
      :title="`${selectedPoint?.point_id} - 详细分析`"
      width="800px"
      class="detail-dialog"
    >
      <div class="detail-content">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="detail-section">
              <h4 class="section-title">
                <el-icon><DataLine /></el-icon>
                基础统计
              </h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>记录总数：</label>
                  <span class="detail-value">{{ selectedPointAnalysis?.record_count || 0 }}</span>
                </div>
                <div class="detail-item">
                  <label>超标数量：</label>
                  <span class="detail-value alert">{{ selectedPointAnalysis?.alert_count || 0 }}</span>
                </div>
                <div class="detail-item">
                  <label>超标率：</label>
                  <span class="detail-value">{{ selectedPointAnalysis?.alert_rate || 0 }}%</span>
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="detail-section">
              <h4 class="section-title">
                <el-icon><TrendCharts /></el-icon>
                指标平均值
              </h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>余氯：</label>
                  <span class="detail-value">{{ selectedPointAnalysis?.avg_chlorine?.toFixed(2) }} mg/L</span>
                </div>
                <div class="detail-item">
                  <label>电导率：</label>
                  <span class="detail-value">{{ selectedPointAnalysis?.avg_conductivity?.toFixed(2) }} µS/cm</span>
                </div>
                <div class="detail-item">
                  <label>pH值：</label>
                  <span class="detail-value">{{ selectedPointAnalysis?.avg_ph?.toFixed(2) }}</span>
                </div>
                <div class="detail-item">
                  <label>ORP：</label>
                  <span class="detail-value">{{ selectedPointAnalysis?.avg_orp?.toFixed(2) }} mV</span>
                </div>
                <div class="detail-item">
                  <label>浊度：</label>
                  <span class="detail-value">{{ selectedPointAnalysis?.avg_turbidity?.toFixed(2) }} NTU</span>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="24">
            <div class="detail-section">
              <h4 class="section-title">
                <el-icon><Histogram /></el-icon>
                指标范围分析
              </h4>
              <div class="range-grid">
                <div class="range-item">
                  <div class="range-label">余氯范围</div>
                  <div class="range-value">
                    <span class="min">{{ selectedPointAnalysis?.min_chlorine?.toFixed(2) }}</span>
                    <span class="separator">~</span>
                    <span class="max">{{ selectedPointAnalysis?.max_chlorine?.toFixed(2) }}</span>
                    <span class="unit">mg/L</span>
                  </div>
                </div>
                <div class="range-item">
                  <div class="range-label">电导率范围</div>
                  <div class="range-value">
                    <span class="min">{{ selectedPointAnalysis?.min_conductivity?.toFixed(2) }}</span>
                    <span class="separator">~</span>
                    <span class="max">{{ selectedPointAnalysis?.max_conductivity?.toFixed(2) }}</span>
                    <span class="unit">µS/cm</span>
                  </div>
                </div>
                <div class="range-item">
                  <div class="range-label">pH值范围</div>
                  <div class="range-value">
                    <span class="min">{{ selectedPointAnalysis?.min_ph?.toFixed(2) }}</span>
                    <span class="separator">~</span>
                    <span class="max">{{ selectedPointAnalysis?.max_ph?.toFixed(2) }}</span>
                  </div>
                </div>
                <div class="range-item">
                  <div class="range-label">ORP范围</div>
                  <div class="range-value">
                    <span class="min">{{ selectedPointAnalysis?.min_orp?.toFixed(2) }}</span>
                    <span class="separator">~</span>
                    <span class="max">{{ selectedPointAnalysis?.max_orp?.toFixed(2) }}</span>
                    <span class="unit">mV</span>
                  </div>
                </div>
                <div class="range-item">
                  <div class="range-label">浊度范围</div>
                  <div class="range-value">
                    <span class="min">{{ selectedPointAnalysis?.min_turbidity?.toFixed(2) }}</span>
                    <span class="separator">~</span>
                    <span class="max">{{ selectedPointAnalysis?.max_turbidity?.toFixed(2) }}</span>
                    <span class="unit">NTU</span>
                  </div>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useWaterQualityStore } from '@/stores/waterQuality'
import * as echarts from 'echarts'
import SimpleAnalysis from '@/components/SimpleAnalysis.vue'
import {
  DataLine,
  Location,
  Warning,
  CircleCheck,
  TrendCharts,
  PieChart,
  Histogram,
  Grid,
  Refresh,
  Search,
  Download,
  View,
  ArrowUp,
  ArrowDown,
  Minus,
  MagicStick
} from '@element-plus/icons-vue'

// Store
const waterQualityStore = useWaterQualityStore()

// 响应式数据
const loading = ref(false)
const dateRange = ref([])
const trendMetrics = ref(['chlorine', 'ph'])
const trendPeriod = ref('day')
const distributionType = ref('alerts')
const comparisonMetric = ref('avg')
const tableSearch = ref('')
const tableSort = ref('alert_count')
const showDetailModal = ref(false)
const selectedPoint = ref(null)

// 图表引用
const trendChartRef = ref()
const distributionChartRef = ref()
const correlationChartRef = ref()
const comparisonChartRef = ref()

// 图表实例
let trendChart = null
let distributionChart = null
let correlationChart = null
let comparisonChart = null

// 配置数据
const metricOptions = [
  { label: '余氯', value: 'chlorine', icon: 'TestTube' },
  { label: '电导率', value: 'conductivity', icon: 'Lightning' },
  { label: 'pH值', value: 'ph', icon: 'MostlyCloudy' },
  { label: 'ORP', value: 'orp', icon: 'Cpu' },
  { label: '浊度', value: 'turbidity', icon: 'IceCream' }
]

const dateShortcuts = [
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    }
  },
  {
    text: '最近一月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    }
  }
]

// 预警阈值
const alertThresholds = {
  chlorine: { min: 0.5, max: 4.0 },
  conductivity: { max: 1000 },
  ph: { min: 6.5, max: 8.5 },
  orp: { min: 400 },
  turbidity: { max: 5.0 }
}

// 计算属性
const kpiCards = computed(() => [
  {
    key: 'records',
    title: '总记录数',
    icon: 'DataLine',
    value: waterQualityStore.overview.totalRecords,
    change: waterQualityStore.overview.recordsChange,
    hovered: false
  },
  {
    key: 'points',
    title: '监测点数量',
    icon: 'Location',
    value: waterQualityStore.overview.totalPoints,
    change: waterQualityStore.overview.pointsChange,
    hovered: false
  },
  {
    key: 'alerts',
    title: '超标数量',
    icon: 'Warning',
    value: waterQualityStore.overview.alertCount,
    change: waterQualityStore.overview.alertsChange,
    hovered: false
  },
  {
    key: 'completeness',
    title: '数据完整率',
    icon: 'CircleCheck',
    value: waterQualityStore.overview.completenessRate,
    change: waterQualityStore.overview.completenessChange,
    hovered: false
  }
])

const distributionTitle = computed(() => 
  distributionType.value === 'alerts' ? '各监测点超标频次统计' : '全指标雷达图分析'
)

const filteredTableData = computed(() => {
  let data = [...waterQualityStore.pointAnalysis]
  
  if (tableSearch.value) {
    data = data.filter(point => 
      point.point_id.toLowerCase().includes(tableSearch.value.toLowerCase())
    )
  }
  
  return data.sort((a, b) => {
    switch (tableSort.value) {
      case 'alert_count':
        return b.alert_count - a.alert_count
      case 'point_id':
        return a.point_id.localeCompare(b.point_id)
      default:
        return 0
    }
  })
})

const selectedPointAnalysis = computed(() => {
  if (!selectedPoint.value) return null
  return waterQualityStore.pointAnalysis.find(p => p.point_id === selectedPoint.value.point_id)
})

// 方法
const fetchData = async () => {
  try {
    loading.value = true
    
    // 模拟加载延迟
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 从store获取数据
    await waterQualityStore.fetchAnalysisData(dateRange.value)
    
    // 更新图表
    await nextTick()
    initCharts()
    updateAllCharts()
    
  } catch (error) {
    console.error('加载分析数据失败:', error)
    ElMessage.error('加载数据失败，请重试')
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  fetchData()
}

const onDateRangeChange = (dates) => {
  if (dates && dates.length === 2) {
    fetchData()
  }
}

const updateTrendChart = () => {
  if (!trendChart) return
  
  const option = getTrendChartOption()
  trendChart.setOption(option)
}

const updateDistributionChart = () => {
  if (!distributionChart) return
  
  const option = distributionType.value === 'alerts' 
    ? getAlertsChartOption()
    : getRadarChartOption()
  
  distributionChart.setOption(option)
}

const updateComparisonChart = () => {
  if (!comparisonChart) return
  
  const option = getComparisonChartOption()
  comparisonChart.setOption(option)
}

const updateCorrelationChart = () => {
  if (!correlationChart) return
  
  const option = getCorrelationChartOption()
  correlationChart.setOption(option)
}

const updateAllCharts = () => {
  updateTrendChart()
  updateDistributionChart()
  updateComparisonChart()
  updateCorrelationChart()
}

const switchDistributionType = (type) => {
  distributionType.value = type
  nextTick(() => {
    updateDistributionChart()
  })
}

const viewPointDetail = (point) => {
  selectedPoint.value = point
  showDetailModal.value = true
}

const handleSortChange = ({ prop, order }) => {
  tableSort.value = prop
}

const exportAnalysisData = () => {
  const csv = [
    '监测点,记录数,超标数,超标率,平均余氯,平均电导率,平均pH值,平均ORP,平均浊度',
    ...waterQualityStore.pointAnalysis.map(point => [
      point.point_id,
      point.record_count,
      point.alert_count,
      `${point.alert_rate}%`,
      point.avg_chlorine?.toFixed(2),
      point.avg_conductivity?.toFixed(2),
      point.avg_ph?.toFixed(2),
      point.avg_orp?.toFixed(2),
      point.avg_turbidity?.toFixed(2)
    ])
  ].join('\n')
  
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `数据分析报告_${new Date().toISOString().split('T')[0]}.csv`
  link.click()
  
  ElMessage.success('分析报告已导出')
}

// 工具方法
const formatNumber = (num) => {
  if (typeof num === 'number') {
    return num.toLocaleString()
  }
  return num
}

const formatChange = (change) => {
  if (change > 0) return `+${Math.abs(change)}%`
  if (change < 0) return `-${Math.abs(change)}%`
  return '0%'
}

const getChangeClass = (change) => {
  if (change > 0) return 'positive'
  if (change < 0) return 'negative'
  return 'neutral'
}

const getIconClass = (icon) => {
  const iconMap = {
    'DataLine': 'icon-blue',
    'Location': 'icon-green',
    'Warning': 'icon-red',
    'CircleCheck': 'icon-purple'
  }
  return iconMap[icon] || 'icon-default'
}

const getAlertTagType = (rate) => {
  if (rate > 20) return 'danger'
  if (rate > 10) return 'warning'
  return 'success'
}

// ECharts配置
const getTrendChartOption = () => {
  const data = waterQualityStore.analysisData
  const timeData = {}
  
  // 按时间分组数据
  data.forEach(record => {
    const timeKey = getTimeKey(record)
    if (!timeData[timeKey]) timeData[timeKey] = {}
    
    trendMetrics.value.forEach(metric => {
      if (!timeData[timeKey][metric]) timeData[timeKey][metric] = []
      timeData[timeKey][metric].push(record[metric] || 0)
    })
  })
  
  const categories = Object.keys(timeData).sort()
  const series = trendMetrics.value.map(metric => ({
    name: metricOptions.find(m => m.value === metric)?.label || metric,
    type: 'line',
    data: categories.map(time => {
      const values = timeData[time][metric] || []
      return values.reduce((sum, val) => sum + val, 0) / values.length
    }),
    smooth: true,
    areaStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: getMetricColor(metric, 0.3) },
        { offset: 1, color: getMetricColor(metric, 0.1) }
      ])
    },
    lineStyle: {
      width: 3,
      color: getMetricColor(metric)
    }
  }))
  
  // 添加预警线
  const markLines = []
  trendMetrics.value.forEach(metric => {
    const threshold = alertThresholds[metric]
    if (threshold) {
      if (threshold.min !== undefined) {
        markLines.push({
          yAxis: threshold.min,
          name: `${metric}下限`,
          lineStyle: { color: '#ff6b6b', type: 'dashed' }
        })
      }
      if (threshold.max !== undefined) {
        markLines.push({
          yAxis: threshold.max,
          name: `${metric}上限`,
          lineStyle: { color: '#ff6b6b', type: 'dashed' }
        })
      }
    }
  })
  
  return {
    title: { text: '多指标趋势分析', left: 'center' },
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    legend: { data: series.map(s => s.name), bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: categories },
    yAxis: { type: 'value' },
    series,
    markLine: { data: markLines, silent: false }
  }
}

const getAlertsChartOption = () => {
  const data = waterQualityStore.pointAnalysis
    .sort((a, b) => b.alert_count - a.alert_count)
    .slice(0, 10)
  
  return {
    title: { text: '监测点超标频次', left: 'center' },
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value' },
    yAxis: { 
      type: 'category',
      data: data.map(item => item.point_id)
    },
    series: [{
      name: '超标次数',
      type: 'bar',
      data: data.map(item => item.alert_count),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#ff6b6b' },
          { offset: 1, color: '#ff8787' }
        ])
      },
      emphasis: {
        itemStyle: { color: '#ff4757' }
      }
    }]
  }
}

const getRadarChartOption = () => {
  const data = waterQualityStore.analysisData
  const metrics = ['chlorine', 'conductivity', 'ph', 'orp', 'turbidity']
  
  const avgData = metrics.map(metric => {
    const values = data.map(record => record[metric] || 0)
    const avg = values.reduce((sum, val) => sum + val, 0) / values.length
    
    // 归一化到0-100范围
    const threshold = alertThresholds[metric]
    let normalized = 50 // 默认中间值
    
    if (threshold) {
      if (threshold.min !== undefined && threshold.max !== undefined) {
        normalized = ((avg - threshold.min) / (threshold.max - threshold.min)) * 100
      } else if (threshold.max !== undefined) {
        normalized = (avg / threshold.max) * 100
      }
    }
    
    return Math.max(0, Math.min(100, normalized))
  })
  
  return {
    title: { text: '水质健康度雷达图', left: 'center' },
    tooltip: {},
    legend: { 
      data: ['当前水质'],
      bottom: 0
    },
    radar: {
      indicator: metrics.map(metric => ({
        name: metricOptions.find(m => m.value === metric)?.label || metric,
        max: 100
      }))
    },
    series: [{
      name: '水质健康度',
      type: 'radar',
      data: [avgData],
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
          { offset: 1, color: 'rgba(102, 126, 234, 0.1)' }
        ])
      },
      lineStyle: { color: '#667eea' },
      itemStyle: { color: '#667eea' }
    }]
  }
}

const getComparisonChartOption = () => {
  const data = waterQualityStore.pointAnalysis
  
  return {
    title: { text: '监测点对比分析', left: 'center' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['对比数据'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { 
      type: 'category',
      data: data.map(item => item.point_id)
    },
    yAxis: { type: 'value' },
    series: [{
      name: '对比数据',
      type: 'bar',
      data: data.map(item => {
        switch (comparisonMetric.value) {
          case 'max':
            return Math.max(
              item.max_chlorine || 0,
              item.max_conductivity || 0,
              item.max_ph || 0,
              item.max_orp || 0,
              item.max_turbidity || 0
            )
          case 'min':
            return Math.min(
              item.min_chlorine || 0,
              item.min_conductivity || 0,
              item.min_ph || 0,
              item.min_orp || 0,
              item.min_turbidity || 0
            )
          case 'alert_rate':
            return item.alert_rate || 0
          default:
            return Math.max(
              item.avg_chlorine || 0,
              item.avg_conductivity || 0,
              item.avg_ph || 0,
              item.avg_orp || 0,
              item.avg_turbidity || 0
            )
        }
      }),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#667eea' },
          { offset: 1, color: '#764ba2' }
        ])
      }
    }]
  }
}

const getCorrelationChartOption = () => {
  const metrics = ['chlorine', 'conductivity', 'ph', 'orp', 'turbidity']
  const data = waterQualityStore.analysisData
  
  const correlationData = []
  for (let i = 0; i < metrics.length; i++) {
    for (let j = 0; j < metrics.length; j++) {
      const values1 = data.map(r => r[metrics[i]] || 0)
      const values2 = data.map(r => r[metrics[j]] || 0)
      
      const correlation = calculateCorrelation(values1, values2)
      correlationData.push([i, j, correlation])
    }
  }
  
  return {
    title: { text: '指标相关性热力图', left: 'center' },
    tooltip: {
      position: 'top',
      formatter: function (params) {
        return `${metrics[params.data[0]]} vs ${metrics[params.data[1]]}: ${params.data[2].toFixed(3)}`
      }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: metrics,
      axisLabel: { 
        formatter: value => metricOptions.find(m => m.value === value)?.label || value
      }
    },
    yAxis: {
      type: 'category',
      data: metrics,
      axisLabel: { 
        formatter: value => metricOptions.find(m => m.value === value)?.label || value
      }
    },
    visualMap: {
      min: -1,
      max: 1,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '5%',
      inRange: {
        color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8']
      }
    },
    series: [{
      name: '相关性',
      type: 'heatmap',
      data: correlationData,
      label: { show: false },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }
}

// 辅助方法
const getTimeKey = (record) => {
  const date = new Date(record.date + ' ' + record.time)
  switch (trendPeriod.value) {
    case 'day':
      return date.toLocaleDateString()
    case 'week':
      const weekStart = new Date(date)
      weekStart.setDate(date.getDate() - date.getDay())
      return `第${Math.ceil((date - weekStart) / (7 * 24 * 60 * 60 * 1000))}周`
    case 'month':
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
    default:
      return date.toLocaleDateString()
  }
}

const getMetricColor = (metric, alpha = 1) => {
  const colors = {
    chlorine: `rgba(64, 158, 255, ${alpha})`,
    conductivity: `rgba(103, 194, 58, ${alpha})`,
    ph: `rgba(118, 75, 162, ${alpha})`,
    orp: `rgba(255, 107, 107, ${alpha})`,
    turbidity: `rgba(52, 211, 153, ${alpha})`
  }
  return colors[metric] || `rgba(102, 126, 234, ${alpha})`
}

const calculateCorrelation = (values1, values2) => {
  if (values1.length !== values2.length) return 0
  
  const mean1 = values1.reduce((a, b) => a + b, 0) / values1.length
  const mean2 = values2.reduce((a, b) => a + b, 0) / values2.length
  
  let numerator = 0
  let denom1 = 0
  let denom2 = 0
  
  for (let i = 0; i < values1.length; i++) {
    const diff1 = values1[i] - mean1
    const diff2 = values2[i] - mean2
    numerator += diff1 * diff2
    denom1 += diff1 * diff1
    denom2 += diff2 * diff2
  }
  
  const denominator = Math.sqrt(denom1 * denom2)
  return denominator === 0 ? 0 : numerator / denominator
}

const initCharts = () => {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
  }
  
  if (distributionChartRef.value) {
    distributionChart = echarts.init(distributionChartRef.value)
  }
  
  if (correlationChartRef.value) {
    correlationChart = echarts.init(correlationChartRef.value)
  }
  
  if (comparisonChartRef.value) {
    comparisonChart = echarts.init(comparisonChartRef.value)
  }
}

onMounted(() => {
  // 设置默认时间范围为最近一周
  const end = new Date()
  const start = new Date()
  start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
  dateRange.value = [start, end]
  
  fetchData()
})
</script>

<style scoped>
.data-analysis-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
}

/* ===== 页面头部 ===== */
.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 24px 30px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
  opacity: 0.8;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.date-picker {
  width: 280px;
}

.refresh-btn {
  padding: 10px 20px;
}

/* ===== KPI 卡片 ===== */
.overview-section {
  margin-bottom: 30px;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.overview-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 20px;
  position: relative;
  overflow: hidden;
}

.overview-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.overview-card:hover::before {
  opacity: 1;
}

.card-icon-container {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.icon-blue { color: #3b82f6; }
.icon-green { color: #10b981; }
.icon-red { color: #ef4444; }
.icon-purple { color: #8b5cf6; }

.card-content {
  flex: 1;
}

.card-title {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 8px;
  font-weight: 500;
}

.card-value {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
  line-height: 1;
}

.card-change {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  width: fit-content;
}

.card-change.positive {
  background: #10b98133;
  color: #10b981;
}

.card-change.negative {
  background: #ef444433;
  color: #ef4444;
}

.card-change.neutral {
  background: #6b728033;
  color: #6b7280;
}

.change-text {
  font-weight: 600;
}

.change-icon {
  margin-left: 4px;
}

/* ===== 智能分析区域 ===== */
.intelligent-analysis-section {
  margin: 32px 0;
  padding: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
}

.intelligent-analysis-section .analysis-header {
  text-align: center;
  margin-bottom: 24px;
}

.intelligent-analysis-section .section-title {
  font-size: 20px;
  font-weight: 700;
  color: white;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.intelligent-analysis-section .section-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  font-weight: 400;
}

/* ===== 图表区域 ===== */
.charts-section {
  margin-bottom: 30px;
}

.chart-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.chart-container {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.chart-container:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.metric-select {
  width: 200px;
}

.period-select,
.comparison-select {
  width: 120px;
}

.chart-content {
  height: 400px;
  width: 100%;
}

/* ===== 数据表格 ===== */
.data-table-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.table-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.table-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input {
  width: 200px;
}

.sort-select {
  width: 120px;
}

.analysis-table {
  font-size: 14px;
}

/* ===== 详情对话框 ===== */
.detail-dialog .el-dialog__body {
  padding: 0;
}

.detail-content {
  padding: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-item label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

.detail-value {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.detail-value.alert {
  color: #ef4444;
}

.range-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.range-item {
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.range-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  margin-bottom: 8px;
}

.range-value {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
}

.range-value .min,
.range-value .max {
  font-family: 'Monaco', 'Menlo', monospace;
  background: #1f2937;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
}

.range-value .separator {
  color: #64748b;
  font-weight: 400;
}

.range-value .unit {
  font-size: 12px;
  color: #64748b;
  font-weight: 400;
}

/* ===== 响应式设计 ===== */
@media (max-width: 1440px) {
  .chart-row {
    grid-template-columns: 1fr;
  }
  
  .overview-cards {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }
}

@media (max-width: 768px) {
  .data-analysis-page {
    padding: 16px;
  }
  
  .analysis-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-right {
    flex-direction: column;
    width: 100%;
  }
  
  .date-picker {
    width: 100%;
  }
  
  .overview-cards {
    grid-template-columns: 1fr;
  }
  
  .overview-card {
    padding: 20px;
  }
  
  .card-value {
    font-size: 28px;
  }
  
  .chart-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .metric-select,
  .period-select,
  .comparison-select {
    width: 100%;
  }
  
  .table-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input,
  .sort-select {
    width: 100%;
  }
}

/* ===== Element Plus 样式覆盖 ===== */
.option-icon {
  margin-right: 8px;
}

:deep(.el-loading-mask) {
  background-color: rgba(255, 255, 255, 0.8);
}

:deep(.el-loading-spinner) {
  margin-top: -40px;
}
</style>
