<template>
  <div class="alerts-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon><Warning /></el-icon>
          报警监控中心
        </h1>
        <div class="header-stats">
          <el-tag type="danger" size="large">
            当前未处理: {{ alertStats.unhandled || 0 }}
          </el-tag>
        </div>
      </div>
      <div class="header-actions">
        <el-button-group>
          <el-button @click="refreshData" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
          <el-button @click="toggleSound" :type="soundEnabled ? 'primary' : 'default'">
            <el-icon><VideoPlay /></el-icon>
            {{ soundEnabled ? '声音开' : '声音关' }}
          </el-button>
          <el-button @click="showRulesDialog = true" type="success">
            <el-icon><Setting /></el-icon>
            规则配置
          </el-button>
          <el-button @click="showStatsDialog = true" type="info">
            <el-icon><TrendCharts /></el-icon>
            统计分析
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 报警级别筛选 -->
    <div class="filter-section">
      <el-radio-group v-model="filterLevel" @change="filterAlerts" size="large">
        <el-radio-button label="all">
          <el-icon><List /></el-icon>
          全部 {{ alertStats.total || 0 }}
        </el-radio-button>
        <el-radio-button label="danger">
          <el-icon><CircleCloseFilled /></el-icon>
          严重 {{ alertStats.critical || 0 }}
        </el-radio-button>
        <el-radio-button label="warning">
          <el-icon><Warning /></el-icon>
          警告 {{ alertStats.warning || 0 }}
        </el-radio-button>
        <el-radio-button label="info">
          <el-icon><InfoFilled /></el-icon>
          提示 {{ alertStats.info || 0 }}
        </el-radio-button>
      </el-radio-group>
    </div>

    <!-- 实时报警列表 -->
    <div class="alerts-table">
      <el-table 
        :data="filteredAlerts" 
        v-loading="loading"
        @selection-change="handleSelectionChange"
        row-key="id"
        :row-class-name="getRowClassName"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="time" label="时间" width="150" sortable>
          <template #default="{ row }">
            <div class="time-cell">
              <el-icon><Clock /></el-icon>
              {{ formatTime(row.time) }}
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="point_id" label="监测点" width="120">
          <template #default="{ row }">
            <el-tag type="primary">{{ row.point_id }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="metric" label="指标" width="100">
          <template #default="{ row }">
            <span class="metric-name">{{ getMetricName(row.metric) }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="value" label="数值" width="100">
          <template #default="{ row }">
            <span class="metric-value" :class="getLevelClass(row.level)">
              {{ row.value }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="threshold" label="阈值" width="100">
          <template #default="{ row }">
            <span class="threshold-value">{{ row.threshold }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)" size="small">
              {{ getLevelName(row.level) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusName(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button-group size="small">
              <el-button 
                v-if="row.status === 'unhandled'"
                @click="acknowledgeAlert(row)"
                type="primary"
              >
                确认
              </el-button>
              <el-button 
                v-if="row.status === 'unhandled'"
                @click="ignoreAlert(row)"
                type="warning"
              >
                忽略
              </el-button>
              <el-button 
                v-if="row.status === 'acknowledged'"
                @click="resolveAlert(row)"
                type="success"
              >
                处理完成
              </el-button>
              <el-button @click="showAlertDetail(row)" type="info">
                详情
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="alertStats.total || 0"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>

      <!-- 批量操作 -->
      <div class="batch-actions" v-if="selectedAlerts.length > 0">
        <el-card>
          <div class="batch-content">
            <span>已选择 {{ selectedAlerts.length }} 条报警</span>
            <el-button-group>
              <el-button @click="batchAcknowledge" type="primary">
                批量确认
              </el-button>
              <el-button @click="batchIgnore" type="warning">
                批量忽略
              </el-button>
              <el-button @click="clearSelection">
                清除选择
              </el-button>
            </el-button-group>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 报警详情弹窗 -->
    <el-dialog
      v-model="showDetailDialog"
      title="报警详情"
      width="800px"
      :before-close="handleDetailClose"
    >
      <div v-if="selectedAlert" class="alert-detail">
        <div class="detail-header">
          <div class="detail-info">
            <div class="info-item">
              <el-icon><Location /></el-icon>
              <span>监测点: {{ selectedAlert.point_id }} ({{ getPointName(selectedAlert.point_id) }})</span>
            </div>
            <div class="info-item">
              <el-icon><Clock /></el-icon>
              <span>时间: {{ formatDateTime(selectedAlert.time) }}</span>
            </div>
            <div class="info-item">
              <el-icon><Warning /></el-icon>
              <span>级别: 
                <el-tag :type="getLevelType(selectedAlert.level)">
                  {{ getLevelName(selectedAlert.level) }}
                </el-tag>
              </span>
            </div>
          </div>
        </div>

        <div class="detail-metrics">
          <h4>超标指标分析</h4>
          <div class="metric-analysis">
            <div class="metric-main">
              <span class="metric-label">{{ getMetricName(selectedAlert.metric) }}</span>
              <span class="metric-current" :class="getLevelClass(selectedAlert.level)">
                {{ selectedAlert.value }}
              </span>
              <span class="metric-threshold">阈值: {{ selectedAlert.threshold }}</span>
              <span class="metric-excess">超限: {{ calculateExcess(selectedAlert) }}</span>
            </div>
          </div>
        </div>

        <div class="detail-data">
          <h4>完整指标数据</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item 
              v-for="metric in selectedAlert.all_metrics" 
              :key="metric.name"
              :label="getMetricName(metric.name)"
            >
              <span :class="metric.is_abnormal ? 'abnormal' : 'normal'">
                {{ metric.value }} {{ metric.unit }}
                <el-tag v-if="metric.is_abnormal" type="danger" size="small">异常</el-tag>
              </span>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="detail-history">
          <h4>处理记录</h4>
          <el-timeline>
            <el-timeline-item
              v-for="record in selectedAlert.history"
              :key="record.id"
              :timestamp="formatDateTime(record.time)"
              :type="getTimelineType(record.action)"
            >
              {{ getActionText(record.action) }} - {{ record.operator }}
              <div v-if="record.comment" class="action-comment">
                {{ record.comment }}
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>

        <div class="detail-actions">
          <el-button-group>
            <el-button 
              v-if="selectedAlert.status === 'unhandled'"
              @click="acknowledgeAlert(selectedAlert)"
              type="primary"
            >
              确认
            </el-button>
            <el-button 
              v-if="selectedAlert.status === 'unhandled'"
              @click="ignoreAlert(selectedAlert)"
              type="warning"
            >
              忽略
            </el-button>
            <el-button 
              v-if="selectedAlert.status === 'acknowledged'"
              @click="resolveAlert(selectedAlert)"
              type="success"
            >
              处理完成
            </el-button>
            <el-button @click="viewPointDetail(selectedAlert.point_id)">
              查看监测点详情
            </el-button>
          </el-button-group>
        </div>
      </div>
    </el-dialog>

    <!-- 报警规则配置弹窗 -->
    <el-dialog
      v-model="showRulesDialog"
      title="报警规则配置"
      width="900px"
    >
      <div class="rules-config">
        <div class="rules-section">
          <h3>⚙️ 全局规则 (所有监测点)</h3>
          <el-table :data="globalRules" border>
            <el-table-column prop="metric" label="指标" width="100">
              <template #default="{ row }">
                {{ getMetricName(row.metric) }}
              </template>
            </el-table-column>
            <el-table-column prop="info_threshold" label="提示阈值" width="120">
              <template #default="{ row }">
                <el-input v-model="row.info_threshold" size="small" />
              </template>
            </el-table-column>
            <el-table-column prop="warning_threshold" label="警告阈值" width="120">
              <template #default="{ row }">
                <el-input v-model="row.warning_threshold" size="small" />
              </template>
            </el-table-column>
            <el-table-column prop="danger_threshold" label="严重阈值" width="120">
              <template #default="{ row }">
                <el-input v-model="row.danger_threshold" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button @click="editRule(row)" size="small" type="primary">
                  编辑
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="rules-section">
          <h3>⚙️ 特殊规则 (指定监测点)</h3>
          <el-table :data="specialRules" border>
            <el-table-column prop="point_id" label="监测点" width="100" />
            <el-table-column prop="metric" label="指标" width="100">
              <template #default="{ row }">
                {{ getMetricName(row.metric) }}
              </template>
            </el-table-column>
            <el-table-column prop="threshold" label="阈值" width="150" />
            <el-table-column prop="reason" label="原因" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button-group size="small">
                  <el-button @click="editSpecialRule(row)" type="primary">
                    编辑
                  </el-button>
                  <el-button @click="deleteSpecialRule(row)" type="danger">
                    删除
                  </el-button>
                </el-button-group>
              </template>
            </el-table-column>
          </el-table>
          <el-button @click="addSpecialRule" type="primary" style="margin-top: 10px;">
            <el-icon><Plus /></el-icon>
            添加特殊规则
          </el-button>
        </div>

        <div class="rules-section">
          <h3>高级设置</h3>
          <el-form :model="advancedSettings" label-width="200px">
            <el-form-item label="连续超标次数">
              <el-input-number v-model="advancedSettings.consecutive_count" :min="1" :max="10" />
              <span style="margin-left: 10px;">次后才触发报警</span>
            </el-form-item>
            <el-form-item label="沉默周期">
              <el-input-number v-model="advancedSettings.silence_period" :min="5" :max="120" />
              <span style="margin-left: 10px;">分钟内不重复报警</span>
            </el-form-item>
            <el-form-item label="夜间模式">
              <el-switch v-model="advancedSettings.night_mode" />
              <span style="margin-left: 10px;">22:00-8:00 升级通知方式</span>
            </el-form-item>
          </el-form>
        </div>

        <div class="rules-actions">
          <el-button-group>
            <el-button @click="saveRules" type="primary">
              保存
            </el-button>
            <el-button @click="resetRules">
              恢复默认
            </el-button>
            <el-button @click="showRulesDialog = false">
              取消
            </el-button>
          </el-button-group>
        </div>
      </div>
    </el-dialog>

    <!-- 统计分析弹窗 -->
    <el-dialog
      v-model="showStatsDialog"
      title="报警统计分析"
      width="1000px"
    >
      <div class="stats-analysis">
        <div class="stats-filters">
          <el-form inline>
            <el-form-item label="时间范围">
              <el-select v-model="statsFilter.timeRange">
                <el-option label="最近7天" value="7d" />
                <el-option label="最近30天" value="30d" />
                <el-option label="最近90天" value="90d" />
              </el-select>
            </el-form-item>
            <el-form-item label="指标">
              <el-select v-model="statsFilter.metric">
                <el-option label="全部" value="all" />
                <el-option v-for="metric in metrics" :key="metric" :label="getMetricName(metric)" :value="metric" />
              </el-select>
            </el-form-item>
            <el-form-item label="监测点">
              <el-select v-model="statsFilter.pointId">
                <el-option label="全部" value="all" />
                <el-option v-for="point in monitoringPoints" :key="point.id" :label="point.name" :value="point.id" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button @click="loadStatsData" type="primary">查询</el-button>
            </el-form-item>
          </el-form>
        </div>

        <div class="stats-content">
          <el-row :gutter="20">
            <el-col :span="16">
              <el-card title="报警趋势图">
                <div ref="trendChart" class="chart-container"></div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card title="指标分布">
                <div ref="distributionChart" class="chart-container"></div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="12">
              <el-card title="监测点排名">
                <div ref="rankingChart" class="chart-container"></div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card title="处理时效统计">
                <div class="processing-stats">
                  <div class="stat-item">
                    <span class="stat-label">平均处理时间:</span>
                    <span class="stat-value">{{ processingStats.avgTime }}分钟</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">48小时内处理率:</span>
                    <span class="stat-value">{{ processingStats.processingRate }}%</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">升级报警数量:</span>
                    <span class="stat-value">{{ processingStats.escalatedCount }}次</span>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Warning,
  Bell,
  CircleCloseFilled,
  TrendCharts,
  Refresh,
  VideoPlay,
  Setting,
  List,
  InfoFilled,
  Clock,
  Location,
  Plus
} from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/format'
import * as echarts from 'echarts'

// 响应式数据
const loading = ref(false)
const soundEnabled = ref(true)
const filterLevel = ref('all')
const currentPage = ref(1)
const pageSize = ref(20)
const selectedAlerts = ref([])
const showDetailDialog = ref(false)
const showRulesDialog = ref(false)
const showStatsDialog = ref(false)
const selectedAlert = ref(null)

// 图表引用
const trendChart = ref(null)
const distributionChart = ref(null)
const rankingChart = ref(null)

// 报警统计数据
const alertStats = reactive({
  total: 0,
  unhandled: 0,
  critical: 0,
  warning: 0,
  info: 0
})

// 报警列表数据
const alerts = ref([])

// 全局规则配置
const globalRules = ref([
  { metric: 'chlorine', info_threshold: '4.0-4.2', warning_threshold: '4.2-4.5', danger_threshold: '>4.5' },
  { metric: 'ph', info_threshold: '8.5-8.8', warning_threshold: '8.8-9.0', danger_threshold: '>9.0' },
  { metric: 'conductivity', info_threshold: '1000-1200', warning_threshold: '1200-1500', danger_threshold: '>1500' }
])

// 特殊规则配置
const specialRules = ref([
  { point_id: 'P-042', metric: 'ph', threshold: '8.8', reason: '上游监测点敏感' },
  { point_id: 'P-038', metric: 'chlorine', threshold: '4.0', reason: '排污口严格标准' }
])

// 高级设置
const advancedSettings = reactive({
  consecutive_count: 2,
  silence_period: 30,
  night_mode: true
})

// 统计筛选条件
const statsFilter = reactive({
  timeRange: '7d',
  metric: 'all',
  pointId: 'all'
})

// 处理时效统计
const processingStats = reactive({
  avgTime: 12.5,
  processingRate: 95,
  escalatedCount: 3
})

// 监测点数据
const monitoringPoints = ref([
  { id: 'P-001', name: '上游监测站' },
  { id: 'P-002', name: '中游监测站' },
  { id: 'P-003', name: '下游监测站' },
  { id: 'P-004', name: '排污口监测站' }
])

// 指标列表
const metrics = ['chlorine', 'ph', 'conductivity', 'turbidity', 'orp', 'temperature']

// WebSocket连接
let wsConnection = null

// 计算属性
const filteredAlerts = computed(() => {
  if (filterLevel.value === 'all') {
    return alerts.value
  }
  return alerts.value.filter(alert => alert.level === filterLevel.value)
})

// 方法
const loadAlerts = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟数据
    alerts.value = [
      {
        id: 1,
        time: '2026-03-15 14:32:45',
        point_id: 'P-042',
        metric: 'ph',
        value: 9.2,
        threshold: 8.5,
        level: 'danger',
        status: 'unhandled',
        all_metrics: [
          { name: 'chlorine', value: 2.1, unit: 'mg/L', is_abnormal: false },
          { name: 'conductivity', value: 567, unit: 'µS/cm', is_abnormal: false },
          { name: 'ph', value: 9.2, unit: '', is_abnormal: true },
          { name: 'orp', value: 412, unit: 'mV', is_abnormal: false },
          { name: 'turbidity', value: 3.1, unit: 'NTU', is_abnormal: false }
        ],
        history: [
          { id: 1, time: '2026-03-15 14:32:45', action: 'trigger', operator: '系统', comment: '系统触发报警' }
        ]
      },
      {
        id: 2,
        time: '2026-03-15 14:30:22',
        point_id: 'P-038',
        metric: 'chlorine',
        value: 4.8,
        threshold: 4.5,
        level: 'warning',
        status: 'acknowledged',
        all_metrics: [],
        history: []
      },
      {
        id: 3,
        time: '2026-03-15 14:28:15',
        point_id: 'P-021',
        metric: 'turbidity',
        value: 7.3,
        threshold: 5.0,
        level: 'warning',
        status: 'unhandled',
        all_metrics: [],
        history: []
      }
    ]
    
    // 更新统计数据
    updateStats()
  } catch (error) {
    ElMessage.error('加载报警数据失败')
  } finally {
    loading.value = false
  }
}

const updateStats = () => {
  alertStats.total = alerts.value.length
  alertStats.unhandled = alerts.value.filter(a => a.status === 'unhandled').length
  alertStats.critical = alerts.value.filter(a => a.level === 'danger').length
  alertStats.warning = alerts.value.filter(a => a.level === 'warning').length
  alertStats.info = alerts.value.filter(a => a.level === 'info').length
}

const refreshData = () => {
  loadAlerts()
}

const toggleSound = () => {
  soundEnabled.value = !soundEnabled.value
  ElMessage.success(`声音提示已${soundEnabled.value ? '开启' : '关闭'}`)
}

const filterAlerts = () => {
  // 筛选逻辑已在计算属性中处理
}

const handleSelectionChange = (selection) => {
  selectedAlerts.value = selection
}

const getRowClassName = ({ row }) => {
  return `alert-row-${row.level} alert-row-${row.status}`
}

const getLevelClass = (level) => {
  return `level-${level}`
}

const getLevelType = (level) => {
  const typeMap = {
    danger: 'danger',
    warning: 'warning',
    info: 'info'
  }
  return typeMap[level] || 'info'
}

const getLevelName = (level) => {
  const nameMap = {
    danger: '严重',
    warning: '警告',
    info: '提示'
  }
  return nameMap[level] || '未知'
}

const getStatusType = (status) => {
  const typeMap = {
    unhandled: 'danger',
    acknowledged: 'warning',
    resolved: 'success',
    ignored: 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusName = (status) => {
  const nameMap = {
    unhandled: '未处理',
    acknowledged: '已确认',
    resolved: '已处理',
    ignored: '已忽略'
  }
  return nameMap[status] || '未知'
}

const getMetricName = (metric) => {
  const nameMap = {
    chlorine: '余氯',
    ph: 'pH值',
    conductivity: '电导率',
    turbidity: '浊度',
    orp: 'ORP',
    temperature: '温度'
  }
  return nameMap[metric] || metric
}

const getPointName = (pointId) => {
  const point = monitoringPoints.value.find(p => p.id === pointId)
  return point ? point.name : pointId
}

const formatTime = (time) => {
  return new Date(time).toLocaleTimeString()
}

const calculateExcess = (alert) => {
  const excess = Math.abs(alert.value - alert.threshold)
  return excess.toFixed(2)
}

const acknowledgeAlert = async (alert) => {
  try {
    await ElMessageBox.confirm('确认此报警？', '确认操作', {
      type: 'warning'
    })
    
    alert.status = 'acknowledged'
    alert.history.push({
      id: Date.now(),
      time: new Date().toISOString(),
      action: 'acknowledge',
      operator: '当前用户',
      comment: '用户确认报警'
    })
    
    ElMessage.success('报警已确认')
    updateStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const ignoreAlert = async (alert) => {
  try {
    const { value: reason } = await ElMessageBox.prompt('请输入忽略原因', '忽略报警', {
      inputType: 'textarea',
      inputPlaceholder: '请输入忽略原因...'
    })
    
    alert.status = 'ignored'
    alert.history.push({
      id: Date.now(),
      time: new Date().toISOString(),
      action: 'ignore',
      operator: '当前用户',
      comment: reason
    })
    
    ElMessage.success('报警已忽略')
    updateStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const resolveAlert = async (alert) => {
  try {
    const { value: result } = await ElMessageBox.prompt('请记录处理结果', '处理完成', {
      inputType: 'textarea',
      inputPlaceholder: '请描述处理措施和结果...'
    })
    
    alert.status = 'resolved'
    alert.history.push({
      id: Date.now(),
      time: new Date().toISOString(),
      action: 'resolve',
      operator: '当前用户',
      comment: result
    })
    
    ElMessage.success('报警已处理完成')
    updateStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const showAlertDetail = (alert) => {
  selectedAlert.value = alert
  showDetailDialog.value = true
}

const handleDetailClose = () => {
  showDetailDialog.value = false
  selectedAlert.value = null
}

const viewPointDetail = (pointId) => {
  // 跳转到监测点详情页面
  ElMessage.info(`查看监测点 ${pointId} 详情`)
}

const batchAcknowledge = async () => {
  try {
    await ElMessageBox.confirm(`确认选中的 ${selectedAlerts.value.length} 条报警？`, '批量确认', {
      type: 'warning'
    })
    
    selectedAlerts.value.forEach(alert => {
      if (alert.status === 'unhandled') {
        alert.status = 'acknowledged'
        alert.history.push({
          id: Date.now(),
          time: new Date().toISOString(),
          action: 'acknowledge',
          operator: '当前用户',
          comment: '批量确认'
        })
      }
    })
    
    ElMessage.success(`已确认 ${selectedAlerts.value.length} 条报警`)
    clearSelection()
    updateStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量操作失败')
    }
  }
}

const batchIgnore = async () => {
  try {
    const { value: reason } = await ElMessageBox.prompt('请输入批量忽略原因', '批量忽略', {
      inputType: 'textarea',
      inputPlaceholder: '请输入忽略原因...'
    })
    
    selectedAlerts.value.forEach(alert => {
      if (alert.status === 'unhandled') {
        alert.status = 'ignored'
        alert.history.push({
          id: Date.now(),
          time: new Date().toISOString(),
          action: 'ignore',
          operator: '当前用户',
          comment: reason
        })
      }
    })
    
    ElMessage.success(`已忽略 ${selectedAlerts.value.length} 条报警`)
    clearSelection()
    updateStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量操作失败')
    }
  }
}

const clearSelection = () => {
  selectedAlerts.value = []
}

const handleSizeChange = (size) => {
  pageSize.value = size
  loadAlerts()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadAlerts()
}

const saveRules = () => {
  ElMessage.success('规则配置已保存')
  showRulesDialog.value = false
}

const resetRules = () => {
  ElMessage.warning('已恢复默认配置')
}

const editRule = (rule) => {
  ElMessage.info(`编辑规则: ${rule.metric}`)
}

const addSpecialRule = () => {
  ElMessage.info('添加特殊规则')
}

const editSpecialRule = (rule) => {
  ElMessage.info(`编辑特殊规则: ${rule.point_id}`)
}

const deleteSpecialRule = (rule) => {
  ElMessage.warning(`删除特殊规则: ${rule.point_id}`)
}

const loadStatsData = () => {
  ElMessage.success('统计数据已更新')
  initCharts()
}

const getTimelineType = (action) => {
  const typeMap = {
    trigger: 'danger',
    acknowledge: 'warning',
    resolve: 'success',
    ignore: 'info'
  }
  return typeMap[action] || 'primary'
}

const getActionText = (action) => {
  const textMap = {
    trigger: '触发报警',
    acknowledge: '确认报警',
    resolve: '处理完成',
    ignore: '忽略报警'
  }
  return textMap[action] || action
}

const initCharts = () => {
  nextTick(() => {
    // 趋势图
    if (trendChart.value) {
      const chart = echarts.init(trendChart.value)
      chart.setOption({
        title: { text: '报警数量趋势' },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: ['3/9', '3/10', '3/11', '3/12', '3/13', '3/14', '3/15'] },
        yAxis: { type: 'value' },
        series: [{
          data: [12, 15, 8, 20, 18, 25, 23],
          type: 'line',
          smooth: true,
          areaStyle: {}
        }]
      })
    }
    
    // 分布图
    if (distributionChart.value) {
      const chart = echarts.init(distributionChart.value)
      chart.setOption({
        title: { text: '指标分布' },
        tooltip: { trigger: 'item' },
        series: [{
          type: 'pie',
          radius: '50%',
          data: [
            { value: 45, name: 'pH值' },
            { value: 30, name: '余氯' },
            { value: 15, name: '浊度' },
            { value: 10, name: '其他' }
          ]
        }]
      })
    }
    
    // 排名图
    if (rankingChart.value) {
      const chart = echarts.init(rankingChart.value)
      chart.setOption({
        title: { text: '监测点报警排名' },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'value' },
        yAxis: { 
          type: 'category',
          data: ['P-042', 'P-038', 'P-021', 'P-015', 'P-009']
        },
        series: [{
          data: [12, 8, 6, 5, 4],
          type: 'bar'
        }]
      })
    }
  })
}

const initWebSocket = () => {
  try {
    wsConnection = new WebSocket('ws://localhost:8000/ws/alerts/')
    
    wsConnection.onmessage = (event) => {
      const alert = JSON.parse(event.data)
      
      // 添加新报警到列表顶部
      alerts.value.unshift(alert)
      
      // 播放提示音
      if (soundEnabled.value) {
        playAlertSound()
      }
      
      // 显示通知
      ElMessage.warning(`新报警: ${getPointName(alert.point_id)} - ${getMetricName(alert.metric)}`)
      
      // 更新统计
      updateStats()
    }
    
    wsConnection.onclose = () => {
      // 断线重连
      setTimeout(initWebSocket, 5000)
    }
    
    wsConnection.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  } catch (error) {
    console.error('Failed to connect WebSocket:', error)
  }
}

const playAlertSound = () => {
  // 播放提示音
  const audio = new Audio('/alert-sound.mp3')
  audio.play().catch(error => {
    console.log('Failed to play alert sound:', error)
  })
}

// 生命周期
onMounted(() => {
  loadAlerts()
  initWebSocket()
})

onUnmounted(() => {
  if (wsConnection) {
    wsConnection.close()
  }
})
</script>

<style lang="scss" scoped>
.alerts-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  @include flex-between;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: $shadow-sm;
  
  .header-left {
    .page-title {
      @include flex-center-vertical;
      font-size: 24px;
      font-weight: 600;
      color: #2c3e50;
      margin: 0 0 10px 0;
      
      .el-icon {
        margin-right: 10px;
        color: #f56c6c;
      }
    }
    
    .header-stats {
      .el-tag {
        font-size: 14px;
      }
    }
  }
}

.filter-section {
  margin-bottom: 20px;
  padding: 15px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: $shadow-sm;
  
  .el-radio-group {
    .el-radio-button {
      margin-right: 10px;
      
      .el-icon {
        margin-right: 5px;
      }
    }
  }
}

.alerts-table {
  background: white;
  border-radius: 8px;
  box-shadow: $shadow-sm;
  padding: 20px;
  
  .time-cell {
    @include flex-center-vertical;
    font-size: 12px;
    color: #666;
    
    .el-icon {
      margin-right: 5px;
    }
  }
  
  .metric-name {
    font-weight: 500;
  }
  
  .metric-value {
    font-weight: 600;
    
    &.level-danger {
      color: #f56c6c;
    }
    
    &.level-warning {
      color: #e6a23c;
    }
    
    &.level-info {
      color: #909399;
    }
  }
  
  .threshold-value {
    color: #666;
    font-size: 12px;
  }
}

.pagination-container {
  @include flex-center;
  margin-top: 20px;
}

.batch-actions {
  margin-top: 20px;
  
  .batch-content {
    @include flex-between;
    align-items: center;
    
    .el-button-group {
      margin-left: 20px;
    }
  }
}

.alert-detail {
  .detail-header {
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #eee;
    
    .detail-info {
      .info-item {
        @include flex-center-vertical;
        margin-bottom: 10px;
        
        .el-icon {
          margin-right: 8px;
          color: #409eff;
        }
      }
    }
  }
  
  .detail-metrics {
    margin-bottom: 20px;
    
    .metric-analysis {
      .metric-main {
        @include flex-center;
        gap: 15px;
        padding: 15px;
        background: #fef5e7;
        border-radius: 6px;
        border-left: 4px solid #e6a23c;
        
        .metric-label {
          font-weight: 500;
        }
        
        .metric-current {
          font-size: 18px;
          font-weight: 600;
          color: #e6a23c;
        }
        
        .metric-threshold {
          color: #666;
        }
        
        .metric-excess {
          color: #e6a23c;
          font-weight: 500;
        }
      }
    }
  }
  
  .detail-data {
    margin-bottom: 20px;
    
    .normal {
      color: #67c23a;
    }
    
    .abnormal {
      color: #f56c6c;
      font-weight: 500;
    }
  }
  
  .detail-history {
    margin-bottom: 20px;
  }
  
  .detail-actions {
    text-align: center;
  }
}

.rules-config {
  .rules-section {
    margin-bottom: 30px;
    
    h3 {
      margin-bottom: 15px;
      color: #2c3e50;
    }
  }
  
  .rules-actions {
    text-align: center;
    margin-top: 30px;
  }
}

.stats-analysis {
  .stats-filters {
    margin-bottom: 20px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 6px;
  }
  
  .stats-content {
    .chart-container {
      height: 300px;
    }
    
    .processing-stats {
      padding: 20px;
      
      .stat-item {
        @include flex-between;
        margin-bottom: 15px;
        padding: 10px;
        background: #f8f9fa;
        border-radius: 4px;
        
        .stat-label {
          color: #666;
        }
        
        .stat-value {
          font-weight: 600;
          color: #409eff;
        }
      }
    }
  }
}

// 行样式
:deep(.alert-row-danger) {
  background-color: #fef0f0;
}

:deep(.alert-row-warning) {
  background-color: #fdf6ec;
}

:deep(.alert-row-info) {
  background-color: #f4f4f5;
}

:deep(.alert-row-unhandled) {
  border-left: 3px solid #f56c6c;
}

:deep(.alert-row-acknowledged) {
  border-left: 3px solid #e6a23c;
}

:deep(.alert-row-resolved) {
  border-left: 3px solid #67c23a;
}

:deep(.alert-row-ignored) {
  border-left: 3px solid #909399;
}
</style>
