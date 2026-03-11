<template>
  <div class="data-analysis-page">
    <div class="analysis-header">
      <h2>📊 数据分析</h2>
      <div class="time-filter">
        <label>时间范围：</label>
        <select v-model="timeRange" @change="onTimeRangeChange">
          <option value="today">今天</option>
          <option value="week">本周</option>
          <option value="month">本月</option>
          <option value="year">今年</option>
          <option value="custom">自定义</option>
        </select>
        <div v-if="timeRange === 'custom'" class="custom-range">
          <input type="date" v-model="customStartDate" />
          <span>至</span>
          <input type="date" v-model="customEndDate" />
          <button @click="applyCustomRange">应用</button>
        </div>
      </div>
      <div class="refresh-btn">
        <button @click="refreshData" :disabled="loading">
          🔄 {{ loading ? '加载中...' : '刷新数据' }}
        </button>
      </div>
    </div>

    <!-- 概览卡片 -->
    <div class="overview-cards">
      <div class="overview-card">
        <div class="card-icon">📈</div>
        <div class="card-content">
          <div class="card-title">总记录数</div>
          <div class="card-value">{{ overview.totalRecords }}</div>
          <div class="card-change" :class="getChangeClass(overview.recordsChange)">
            {{ formatChange(overview.recordsChange) }}
          </div>
        </div>
      </div>
      
      <div class="overview-card">
        <div class="card-icon">📍</div>
        <div class="card-content">
          <div class="card-title">监测点数量</div>
          <div class="card-value">{{ overview.totalPoints }}</div>
          <div class="card-change" :class="getChangeClass(overview.pointsChange)">
            {{ formatChange(overview.pointsChange) }}
          </div>
        </div>
      </div>
      
      <div class="overview-card">
        <div class="card-icon">⚠️</div>
        <div class="card-content">
          <div class="card-title">超标数量</div>
          <div class="card-value">{{ overview.alertCount }}</div>
          <div class="card-change" :class="getChangeClass(overview.alertsChange)">
            {{ formatChange(overview.alertsChange) }}
          </div>
        </div>
      </div>
      
      <div class="overview-card">
        <div class="card-icon">📊</div>
        <div class="card-content">
          <div class="card-title">数据完整率</div>
          <div class="card-value">{{ overview.completenessRate }}%</div>
          <div class="card-change" :class="getChangeClass(overview.completenessChange)">
            {{ formatChange(overview.completenessChange) }}
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <div class="chart-row">
        <!-- 趋势图 -->
        <div class="chart-container">
          <h3>📈 数据趋势</h3>
          <div class="chart-controls">
            <select v-model="trendMetric" @change="updateTrendChart">
              <option value="chlorine">余氯</option>
              <option value="conductivity">电导率</option>
              <option value="ph">pH值</option>
              <option value="orp">ORP</option>
              <option value="turbidity">浊度</option>
            </select>
            <select v-model="trendPeriod" @change="updateTrendChart">
              <option value="day">按天</option>
              <option value="week">按周</option>
              <option value="month">按月</option>
            </select>
          </div>
          <div class="chart-placeholder" ref="trendChart">
            <canvas id="trendCanvas" width="400" height="200"></canvas>
          </div>
        </div>

        <!-- 分布图 -->
        <div class="chart-container">
          <h3>📊 指标分布</h3>
          <div class="chart-controls">
            <select v-model="distributionMetric" @change="updateDistributionChart">
              <option value="point_id">监测点分布</option>
              <option value="chlorine">余氯分布</option>
              <option value="conductivity">电导率分布</option>
              <option value="ph">pH值分布</option>
              <option value="orp">ORP分布</option>
              <option value="turbidity">浊度分布</option>
            </select>
          </div>
          <div class="chart-placeholder" ref="distributionChart">
            <canvas id="distributionCanvas" width="400" height="200"></canvas>
          </div>
        </div>
      </div>

      <div class="chart-row">
        <!-- 相关性热力图 -->
        <div class="chart-container">
          <h3>🔥 指标相关性</h3>
          <div class="chart-placeholder" ref="correlationChart">
            <canvas id="correlationCanvas" width="400" height="300"></canvas>
          </div>
        </div>

        <!-- 监测点对比 -->
        <div class="chart-container">
          <h3>📊 监测点对比</h3>
          <div class="chart-controls">
            <select v-model="comparisonMetric" @change="updateComparisonChart">
              <option value="avg">平均值</option>
              <option value="max">最大值</option>
              <option value="min">最小值</option>
              <option value="alert_rate">超标率</option>
            </select>
          </div>
          <div class="chart-placeholder" ref="comparisonChart">
            <canvas id="comparisonCanvas" width="400" height="300"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- 详细数据表格 -->
    <div class="data-table-section">
      <div class="table-header">
        <h3>📋 详细数据</h3>
        <div class="table-controls">
          <input type="text" v-model="tableSearch" placeholder="搜索监测点..." />
          <select v-model="tableSort">
            <option value="date">按日期</option>
            <option value="point_id">按监测点</option>
            <option value="alert_count">按超标数</option>
          </select>
          <button @click="exportAnalysisData">📥 导出分析报告</button>
        </div>
      </div>
      
      <div class="table-container">
        <table class="analysis-table">
          <thead>
            <tr>
              <th>监测点</th>
              <th>记录数</th>
              <th>超标数</th>
              <th>超标率</th>
              <th>平均余氯</th>
              <th>平均电导率</th>
              <th>平均pH值</th>
              <th>平均ORP</th>
              <th>平均浊度</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="point in pointAnalysis" :key="point.point_id">
              <td>{{ point.point_id }}</td>
              <td>{{ point.record_count }}</td>
              <td>{{ point.alert_count }}</td>
              <td>{{ point.alert_rate }}%</td>
              <td>{{ point.avg_chlorine?.toFixed(2) }}</td>
              <td>{{ point.avg_conductivity?.toFixed(2) }}</td>
              <td>{{ point.avg_ph?.toFixed(2) }}</td>
              <td>{{ point.avg_orp?.toFixed(2) }}</td>
              <td>{{ point.avg_turbidity?.toFixed(2) }}</td>
              <td>
                <button class="btn-sm" @click="viewPointDetail(point)">👁️</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 详情对话框 -->
    <div v-if="showDetailModal" class="modal-overlay" @click="showDetailModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedPoint?.point_id }} - 详细分析</h3>
          <button class="close-btn" @click="showDetailModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="detail-grid">
            <div class="detail-section">
              <h4>📊 基础统计</h4>
              <div class="detail-item">
                <label>记录总数：</label>
                <span>{{ selectedPointAnalysis?.record_count || 0 }}</span>
              </div>
              <div class="detail-item">
                <label>超标数量：</label>
                <span>{{ selectedPointAnalysis?.alert_count || 0 }}</span>
              </div>
              <div class="detail-item">
                <label>超标率：</label>
                <span>{{ selectedPointAnalysis?.alert_rate || 0 }}%</span>
              </div>
            </div>
            
            <div class="detail-section">
              <h4>📈 指标平均值</h4>
              <div class="detail-item">
                <label>余氯：</label>
                <span>{{ selectedPointAnalysis?.avg_chlorine?.toFixed(2) }} mg/L</span>
              </div>
              <div class="detail-item">
                <label>电导率：</label>
                <span>{{ selectedPointAnalysis?.avg_conductivity?.toFixed(2) }} µS/cm</span>
              </div>
              <div class="detail-item">
                <label>pH值：</label>
                <span>{{ selectedPointAnalysis?.avg_ph?.toFixed(2) }}</span>
              </div>
              <div class="detail-item">
                <label>ORP：</label>
                <span>{{ selectedPointAnalysis?.avg_orp?.toFixed(2) }} mV</span>
              </div>
              <div class="detail-item">
                <label>浊度：</label>
                <span>{{ selectedPointAnalysis?.avg_turbidity?.toFixed(2) }} NTU</span>
              </div>
            </div>
            
            <div class="detail-section">
              <h4>📊 指标范围</h4>
              <div class="detail-item">
                <label>余氯范围：</label>
                <span>{{ selectedPointAnalysis?.min_chlorine?.toFixed(2) }} - {{ selectedPointAnalysis?.max_chlorine?.toFixed(2) }} mg/L</span>
              </div>
              <div class="detail-item">
                <label>电导率范围：</label>
                <span>{{ selectedPointAnalysis?.min_conductivity?.toFixed(2) }} - {{ selectedPointAnalysis?.max_conductivity?.toFixed(2) }} µS/cm</span>
              </div>
              <div class="detail-item">
                <label>pH值范围：</label>
                <span>{{ selectedPointAnalysis?.min_ph?.toFixed(2) }} - {{ selectedPointAnalysis?.max_ph?.toFixed(2) }}</span>
              </div>
              <div class="detail-item">
                <label>ORP范围：</label>
                <span>{{ selectedPointAnalysis?.min_orp?.toFixed(2) }} - {{ selectedPointAnalysis?.max_orp?.toFixed(2) }} mV</span>
              </div>
              <div class="detail-item">
                <label>浊度范围：</label>
                <span>{{ selectedPointAnalysis?.min_turbidity?.toFixed(2) }} - {{ selectedPointAnalysis?.max_turbidity?.toFixed(2) }} NTU</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { waterQualityApi } from '@/api/waterQuality'

// 响应式数据
const loading = ref(false);
const timeRange = ref('week');
const customStartDate = ref('');
const customEndDate = ref('');
const trendMetric = ref('chlorine');
const trendPeriod = ref('day');
const distributionMetric = ref('point_id');
const comparisonMetric = ref('avg');
const tableSearch = ref('');
const tableSort = ref('date');

// 数据状态
const overview = ref({
  totalRecords: 0,
  totalPoints: 0,
  alertCount: 0,
  recordsChange: 0,
  pointsChange: 0,
  alertsChange: 0,
  completenessRate: 0,
  completenessChange: 0
})

const analysisData = ref([]);
const pointAnalysis = ref([]);
const showDetailModal = ref(false);
const selectedPoint = ref(null);
const selectedPointAnalysis = ref(null);

// 图表实例
let trendChartInstance = null;
let distributionChartInstance = null;
let correlationChartInstance = null;
let comparisonChartInstance = null;

// 时间范围处理
const onTimeRangeChange = () => {
  if (timeRange.value !== 'custom') {
    loadAnalysisData();
  }
};

const applyCustomRange = () => {
  if (customStartDate.value && customEndDate.value) {
    loadAnalysisData();
  }
};

// 加载分析数据
const loadAnalysisData = async () => {
  try {
    loading.value = true;
    
    // 获取时间范围内的数据
    const dateRange = getDateRange();
    const response = await waterQualityApi.getRecords({
      date_after: dateRange.start,
      date_before: dateRange.end
    });
    
    const records = response.results || response;
    analysisData.value = records;
    
    // 计算概览数据
    await calculateOverview(records);
    
    // 计算监测点分析
    calculatePointAnalysis(records);
    
    // 更新图表
    await nextTick();
    updateAllCharts();
    
  } catch (error) {
    console.error('加载分析数据失败:', error);
    alert('加载数据失败，请重试');
  } finally {
    loading.value = false;
  }
};

// 获取日期范围
const getDateRange = () => {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  
  switch (timeRange.value) {
    case 'today':
      return { start: formatDate(today), end: formatDate(today) };
    case 'week':
      const weekAgo = new Date(today);
      weekAgo.setDate(weekAgo.getDate() - 7);
      return { start: formatDate(weekAgo), end: formatDate(today) };
    case 'month':
      const monthAgo = new Date(today);
      monthAgo.setMonth(monthAgo.getMonth() - 1);
      return { start: formatDate(monthAgo), end: formatDate(today) };
    case 'year':
      const yearAgo = new Date(today);
      yearAgo.setFullYear(yearAgo.getFullYear() - 1);
      return { start: formatDate(yearAgo), end: formatDate(today) };
    case 'custom':
      return { start: customStartDate.value, end: customEndDate.value };
    default:
      return { start: formatDate(weekAgo), end: formatDate(today) };
  }
};

const formatDate = (date) => {
  return date.toISOString().split('T')[0];
};

// 计算概览数据
const calculateOverview = async (records) => {
  const totalRecords = records.length;
  const totalPoints = [...new Set(records.map(r => r.point_id))].length;
  const alertRecords = records.filter(r => {
    return r.chlorine < 0.5 || r.chlorine > 4.0 ||
           r.conductivity > 1000 ||
           r.ph < 6.5 || r.ph > 8.5 ||
           r.orp < 400 ||
           r.turbidity > 5.0;
  });
  
  const alertCount = alertRecords.length;
  const completenessRate = totalRecords > 0 ? Math.round((totalRecords - alertRecords.length) / totalRecords * 100) : 100;
  
  // 模拟历史数据对比（实际应用中应该从数据库获取历史数据）
  const previousData = await getPreviousPeriodData()
  
  overview.value = {
    totalRecords,
    totalPoints,
    alertCount,
    recordsChange: totalRecords - previousData.records,
    pointsChange: totalPoints - previousData.points,
    alertsChange: alertCount - previousData.alerts,
    completenessRate,
    completenessChange: completenessRate - previousData.completeness
  };
};

// 获取历史数据（模拟）
const getPreviousPeriodData = async () => {
  // 这里应该从数据库获取上一个周期的数据
  // 为了演示，返回模拟数据
  return {
    records: Math.floor(Math.random() * 10) + 5,
    points: Math.floor(Math.random() * 3) + 2,
    alerts: Math.floor(Math.random() * 3) + 1,
    completeness: Math.floor(Math.random() * 10) + 80
  };
};

// 计算监测点分析
const calculatePointAnalysis = (records) => {
  const pointGroups = {};
  
  records.forEach(record => {
    if (!pointGroups[record.point_id]) {
      pointGroups[record.point_id] = {
        point_id: record.point_id,
        records: [],
        chlorine: [],
        conductivity: [],
        ph: [],
        orp: [],
        turbidity: []
      };
    }
    
    const group = pointGroups[record.point_id];
    group.records.push(record);
    group.chlorine.push(record.chlorine);
    group.conductivity.push(record.conductivity);
    group.ph.push(record.ph);
    group.orp.push(record.orp);
    group.turbidity.push(record.turbidity);
  });
  
  // 计算每个监测点的统计数据
  const analysis = Object.values(pointGroups).map(group => {
    const alertRecords = group.records.filter(r => {
      return r.chlorine < 0.5 || r.chlorine > 4.0 ||
             r.conductivity > 1000 ||
             r.ph < 6.5 || r.ph > 8.5 ||
             r.orp < 400 ||
             r.turbidity > 5.0;
    });
    
    return {
      point_id: group.point_id,
      record_count: group.records.length,
      alert_count: alertRecords.length,
      alert_rate: group.records.length > 0 ? Math.round((alertRecords.length / group.records.length) * 100) : 0,
      avg_chlorine: group.chlorine.reduce((a, b) => a + b, 0) / group.chlorine.length,
      avg_conductivity: group.conductivity.reduce((a, b) => a + b, 0) / group.conductivity.length,
      avg_ph: group.ph.reduce((a, b) => a + b, 0) / group.ph.length,
      avg_orp: group.orp.reduce((a, b) => a + b, 0) / group.orp.length,
      avg_turbidity: group.turbidity.reduce((a, b) => a + b, 0) / group.turbidity.length,
      min_chlorine: Math.min(...group.chlorine),
      max_chlorine: Math.max(...group.chlorine),
      min_conductivity: Math.min(...group.conductivity),
      max_conductivity: Math.max(...group.conductivity),
      min_ph: Math.min(...group.ph),
      max_ph: Math.max(...group.ph),
      min_orp: Math.min(...group.orp),
      max_orp: Math.max(...group.orp),
      min_turbidity: Math.min(...group.turbidity),
      max_turbidity: Math.max(...group.turbidity)
    };
  });
  
  // 应用搜索和排序
  let filteredAnalysis = analysis;
  if (tableSearch.value) {
    filteredAnalysis = analysis.filter(point => 
      point.point_id.toLowerCase().includes(tableSearch.value.toLowerCase())
    );
  }
  
  filteredAnalysis.sort((a, b) => {
    switch (tableSort.value) {
      case 'date':
        return 0; // 需要日期信息时排序
      case 'point_id':
        return a.point_id.localeCompare(b.point_id);
      case 'alert_count':
        return b.alert_count - a.alert_count;
      default:
        return 0;
    }
  });
  
  pointAnalysis.value = filteredAnalysis;
};

// 格式化变化
const formatChange = (change) => {
  if (change > 0) return `+${change}`;
  if (change < 0) return `${change}`;
  return '0';
};

const getChangeClass = (change) => {
  if (change > 0) return 'positive';
  if (change < 0) return 'negative';
  return 'neutral';
};

// 查看详情
const viewPointDetail = (point) => {
  selectedPoint.value = point;
  selectedPointAnalysis.value = pointAnalysis.value.find(p => p.point_id === point.point_id);
  showDetailModal.value = true;
};

// 刷新数据
const refreshData = () => {
  loadAnalysisData();
};

// 导出分析报告
const exportAnalysisData = () => {
  const csv = [
    '监测点,记录数,超标数,超标率,平均余氯,平均电导率,平均pH值,平均ORP,平均浊度',
    ...pointAnalysis.value.map(point => [
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
  ].join('\n');
  
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `数据分析报告_${new Date().toISOString().split('T')[0]}.csv`;
  link.click();
  
  alert('分析报告已导出');
};

// 图表更新函数
const updateTrendChart = () => {
  // 简单的Canvas图表实现
  const canvas = document.getElementById('trendCanvas');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  const data = getTrendData();
  
  // 清空画布
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  // 绘制简单的折线图
  drawLineChart(ctx, data, canvas.width, canvas.height);
};

const updateDistributionChart = () => {
  const canvas = document.getElementById('distributionCanvas');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  const data = getDistributionData();
  
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawBarChart(ctx, data, canvas.width, canvas.height);
};

const updateCorrelationChart = () => {
  const canvas = document.getElementById('correlationCanvas');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  const data = getCorrelationData();
  
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawHeatmap(ctx, data, canvas.width, canvas.height);
};

const updateComparisonChart = () => {
  const canvas = document.getElementById('comparisonCanvas');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  const data = getComparisonData();
  
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawBarChart(ctx, data, canvas.width, canvas.height);
};

const updateAllCharts = () => {
  updateTrendChart();
  updateDistributionChart();
  updateCorrelationChart();
  updateComparisonChart();
};

// 数据获取函数
const getTrendData = () => {
  const grouped = {};
  analysisData.value.forEach(record => {
    const key = getTrendGroupKey(record);
    if (!grouped[key]) grouped[key] = [];
    grouped[key].push(record);
  });
  
  return Object.entries(grouped).map(([key, records]) => ({
    label: key,
    value: records.reduce((sum, r) => sum + (r[trendMetric.value] || 0), 0) / records.length
  }));
};

const getDistributionData = () => {
  const grouped = {};
  analysisData.value.forEach(record => {
    const key = record[distributionMetric.value] || 'unknown';
    if (!grouped[key]) grouped[key] = 0;
    grouped[key]++;
  });
  
  return Object.entries(grouped).map(([key, count]) => ({ label: key, value: count }));
};

const getCorrelationData = () => {
  // 简化的相关性数据
  const metrics = ['chlorine', 'conductivity', 'ph', 'orp', 'turbidity'];
  const data = [];
  
  for (let i = 0; i < metrics.length; i++) {
    for (let j = 0; j < metrics.length; j++) {
      const correlation = calculateCorrelation(metrics[i], metrics[j]);
      data.push({ x: i, y: j, value: correlation });
    }
  }
  
  return data;
};

const getComparisonData = () => {
  return pointAnalysis.value.map(point => {
    const value = point[`avg_${comparisonMetric.value}`] || 0;
    return { label: point.point_id, value };
  });
};

const getTrendGroupKey = (record) => {
  const date = new Date(record.date + ' ' + record.time);
  switch (trendPeriod.value) {
    case 'day':
      return date.toLocaleDateString();
    case 'week':
      const weekStart = new Date(date);
      weekStart.setDate(date.getDate() - date.getDay());
      return `第${Math.ceil((date - weekStart) / (7 * 24 * 60 * 60 * 1000))}周`;
    case 'month':
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    default:
      return date.toLocaleDateString();
  }
};

const calculateCorrelation = (metric1, metric2) => {
  const values1 = analysisData.value.map(r => r[metric1] || 0);
  const values2 = analysisData.value.map(r => r[metric2] || 0);
  
  if (values1.length !== values2.length) return 0;
  
  // 简化的相关系数计算
  const mean1 = values1.reduce((a, b) => a + b, 0) / values1.length;
  const mean2 = values2.reduce((a, b) => a + b, 0) / values2.length;
  
  let numerator = 0;
  let denom1 = 0;
  let denom2 = 0;
  
  for (let i = 0; i < values1.length; i++) {
    const diff1 = values1[i] - mean1;
    const diff2 = values2[i] - mean2;
    numerator += diff1 * diff2;
    denom1 += diff1 * diff1;
    denom2 += diff2 * diff2;
  }
  
  const denominator = Math.sqrt(denom1 * denom2);
  return denominator === 0 ? 0 : numerator / denominator;
};

// 简单的图表绘制函数
const drawLineChart = (ctx, data, width, height) => {
  if (data.length === 0) return;
  
  const padding = 40;
  const chartWidth = width - padding * 2;
  const chartHeight = height - padding * 2;
  
  const maxValue = Math.max(...data.map(d => d.value));
  const minValue = Math.min(...data.map(d => d.value));
  const valueRange = maxValue - minValue || 1;
  
  // 绘制坐标轴
  ctx.strokeStyle = '#666';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padding, padding);
  ctx.lineTo(padding, height - padding);
  ctx.lineTo(width - padding, height - padding);
  ctx.stroke();
  
  ctx.beginPath();
  ctx.moveTo(padding, height - padding);
  ctx.lineTo(width - padding, height - padding);
  ctx.stroke();
  
  // 绘制数据线
  ctx.strokeStyle = '#409EFF';
  ctx.lineWidth = 2;
  ctx.beginPath();
  
  data.forEach((point, index) => {
    const x = padding + (index / (data.length - 1)) * chartWidth;
    const y = height - padding - ((point.value - minValue) / valueRange) * chartHeight;
    
    if (index === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  });
  
  ctx.stroke();
  
  // 绘制数据点
  ctx.fillStyle = '#409EFF';
  data.forEach((point, index) => {
    const x = padding + (index / (data.length - 1)) * chartWidth;
    const y = height - padding - ((point.value - minValue) / valueRange) * chartHeight;
    
    ctx.beginPath();
    ctx.arc(x, y, 3, 0, 2 * Math.PI);
    ctx.fill();
  });
};

const drawBarChart = (ctx, data, width, height) => {
  if (data.length === 0) return;
  
  const padding = 40;
  const chartWidth = width - padding * 2;
  const chartHeight = height - padding * 2;
  
  const maxValue = Math.max(...data.map(d => d.value));
  const barWidth = chartWidth / data.length * 0.8;
  const barSpacing = chartWidth / data.length * 0.2;
  
  data.forEach((item, index) => {
    const x = padding + index * (barWidth + barSpacing) + barSpacing / 2;
    const barHeight = (item.value / maxValue) * chartHeight;
    const y = height - padding - barHeight;
    
    // 绘制柱子
    ctx.fillStyle = '#409EFF';
    ctx.fillRect(x, y, barWidth, barHeight);
    
    // 绘制标签
    ctx.fillStyle = '#333';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(item.label, x + barWidth / 2, height - padding + 15);
    ctx.fillText(item.value.toFixed(1), x + barWidth / 2, y - 5);
  });
};

const drawHeatmap = (ctx, data, width, height) => {
  const cellSize = Math.min(width / 6, height / 6);
  const metrics = ['余氯', '电导率', 'pH', 'ORP', '浊度'];
  
  for (let i = 0; i < 5; i++) {
    for (let j = 0; j < 5; j++) {
      const x = j * cellSize;
      const y = i * cellSize;
      
      const value = data.find(d => d.x === i && d.y === j)?.value || 0;
      
      // 根据相关系数设置颜色
      let color = '#f0f0f0';
      if (value > 0.7) color = '#409EFF';
      else if (value > 0.3) color = '#67C23A';
      else if (value > 0) color = '#E6A23C';
      else if (value < -0.3) color = '#F56C6C';
      else if (value < -0.7) color = '#909399';
      
      ctx.fillStyle = color;
      ctx.fillRect(x, y, cellSize - 1, cellSize - 1);
      
      // 绘制数值
      ctx.fillStyle = value > 0 ? '#fff' : '#333';
      ctx.font = '10px Arial';
      ctx.textAlign = 'center';
      ctx.fillText(value.toFixed(2), x + cellSize / 2, y + cellSize / 2);
    }
  }
  
  // 绘制标签
  ctx.fillStyle = '#333';
  ctx.font = '12px Arial';
  metrics.forEach((metric, i) => {
    ctx.fillText(metric, i * cellSize + cellSize / 2, -20);
  });
};

onMounted(() => {
  loadAnalysisData();
});
</script>

<style scoped>
.data-analysis-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.time-filter {
  display: flex;
  align-items: center;
  gap: 15px;
}

.time-filter select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.custom-range {
  display: flex;
  align-items: center;
  gap: 10px;
}

.custom-range input {
  padding: 6px 10px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.refresh-btn button {
  padding: 8px 16px;
  background: #409EFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.refresh-btn button:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.overview-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
  transition: transform 0.2s;
}

.overview-card:hover {
  transform: translateY(-2px);
}

.card-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.card-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
}

.card-change {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
}

.card-change.positive {
  background: #f0f9ff;
  color: #409EFF;
}

.card-change.negative {
  background: #fef0f0;
  color: #F56C6C;
}

.card-change.neutral {
  background: #f5f5f5;
  color: #909399;
}

.charts-section {
  margin-bottom: 30px;
}

.chart-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.chart-container {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.chart-container h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.chart-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.chart-controls select {
  padding: 6px 10px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 12px;
}

.chart-placeholder {
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 10px;
  text-align: center;
  background: #fafafa;
}

.data-table-section {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.table-header h3 {
  margin: 0;
  color: #333;
}

.table-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.table-controls input,
.table-controls select {
  padding: 6px 10px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 12px;
}

.table-container {
  overflow-x: auto;
}

.analysis-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.analysis-table th,
.analysis-table td {
  padding: 10px;
  text-align: center;
  border: 1px solid #e6e6e6;
}

.analysis-table th {
  background: #f5f7fa;
  font-weight: 600;
  color: #333;
}

.analysis-table tbody tr:hover {
  background: #f5f7fa;
}

.btn-sm {
  padding: 4px 8px;
  background: #409EFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
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
  gap: 20px;
}

.detail-section {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
}

.detail-section h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #e6e6e6;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-item label {
  font-weight: 600;
  color: #666;
}

.detail-item span {
  color: #333;
  font-weight: 500;
}

/* 深色主题 */
.dark .data-analysis-page {
  background: #1f1f1f;
  color: #fff;
}

.dark .analysis-header,
.dark .overview-card,
.dark .chart-container,
.dark .data-table-section {
  background: #2a2a2a;
  color: #fff;
}

.dark .overview-card {
  box-shadow: 0 2px 8px rgba(255,255,255,0.1);
}

.dark .chart-placeholder {
  background: #2a2a2a;
  border-color: #4c4d4f;
}

.dark .analysis-table th {
  background: #2a2a2a;
  color: #fff;
}

.dark .analysis-table tbody tr:hover {
  background: #2a2a2a;
}

.dark .detail-section {
  background: #2a2a2a;
}

.dark .detail-item {
  border-bottom-color: #4c4d4f;
}

.dark .modal {
  background: #2a2a2a;
  color: #fff;
}
</style>
