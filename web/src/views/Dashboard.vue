<template>
  <div class="dashboard-container">
    <!-- 顶部欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-left">
        <h2 class="greeting">{{ greeting }}，{{ user?.username || '管理员' }}</h2>
        <div class="weather-info">
          <span class="weather">🌤 北京 20°C</span>
          <span class="suggestion">适合进行水质监测</span>
        </div>
      </div>
      <div class="welcome-right">
        <el-button type="primary" :icon="Plus" @click="showQuickAdd = true">快速录入</el-button>
        <el-button :icon="Refresh" @click="refreshData">刷新数据</el-button>
        <el-badge :value="unreadCount" class="notification-badge">
          <el-button :icon="Bell" @click="showNotifications">通知</el-button>
        </el-badge>
        <el-dropdown @command="handleUserMenu" class="user-dropdown">
          <el-button :icon="User" circle />
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon> 个人资料
              </el-dropdown-item>
              <el-dropdown-item command="settings">
                <el-icon><Setting /></el-icon> 系统设置
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <el-icon><SwitchButton /></el-icon> 退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- KPI指标卡片 -->
    <div class="kpi-cards">
      <div class="kpi-card online">
        <div class="kpi-icon">📍</div>
        <div class="kpi-content">
          <div class="kpi-title">总监测点</div>
          <div class="kpi-value">{{ kpiData.totalPoints || 48 }}</div>
          <div class="kpi-subtitle">在线 {{ kpiData.onlinePoints || 46 }} / 离线 {{ kpiData.offlinePoints || 2 }}</div>
        </div>
      </div>
      
      <div class="kpi-card today">
        <div class="kpi-icon">📊</div>
        <div class="kpi-content">
          <div class="kpi-title">今日数据</div>
          <div class="kpi-value">{{ kpiData.todayRecords || 156 }}</div>
          <div class="kpi-subtitle">已录入记录</div>
        </div>
      </div>
      
      <div class="kpi-card alerts">
        <div class="kpi-icon">⚠️</div>
        <div class="kpi-content">
          <div class="kpi-title">超标报警</div>
          <div class="kpi-value">{{ kpiData.alertCount || 7 }}</div>
          <div class="kpi-subtitle">未处理报警</div>
        </div>
      </div>
      
      <div class="kpi-card device">
        <div class="kpi-icon">💻</div>
        <div class="kpi-content">
          <div class="kpi-title">设备在线率</div>
          <div class="kpi-value">{{ kpiData.onlineRate || 98 }}%</div>
          <div class="kpi-subtitle">{{ kpiData.offlineDevices || 2 }} 台离线</div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧：水质健康指数 + 趋势图 -->
      <div class="left-section">
        <!-- 水质健康指数 -->
        <div class="health-index-card">
          <h3>水质健康指数</h3>
          <div class="health-content">
            <div class="circular-progress">
              <div class="progress-circle">
                <div class="progress-value">{{ healthIndex.score || 86 }}</div>
                <div class="progress-label">分</div>
              </div>
            </div>
            <div class="health-info">
              <div class="health-grade" :class="healthIndex.grade?.toLowerCase() || 'excellent'">
                {{ healthIndex.grade || '优' }}
              </div>
              <div class="health-trend">
                <span :class="healthIndex.trend > 0 ? 'up' : 'down'">
                  {{ healthIndex.trend > 0 ? '↑' : '↓' }} {{ Math.abs(healthIndex.trend || 2) }}%
                </span>
                <span>较昨日</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 主要指标趋势图 -->
        <div class="trend-card">
          <div class="card-header">
            <h3>主要指标趋势</h3>
            <el-radio-group v-model="selectedIndicator" size="small">
              <el-radio-button label="ph">pH值</el-radio-button>
              <el-radio-button label="turbidity">浊度</el-radio-button>
              <el-radio-button label="chlorine">余氯</el-radio-button>
            </el-radio-group>
          </div>
          <div class="chart-container">
            <div class="chart-placeholder">
              📈 {{ selectedIndicator === 'ph' ? 'pH值' : selectedIndicator === 'turbidity' ? '浊度' : '余氯' }}走势图
              <div class="chart-note">最近7天数据趋势</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：监测点分布 + 最新报警 -->
      <div class="right-section">
        <!-- 监测点分布 -->
        <div class="map-card">
          <h3>监测点分布</h3>
          <div class="map-placeholder">
            <div class="map-points">
              <div class="map-point normal" title="正常">●</div>
              <div class="map-point warning" title="警告">●</div>
              <div class="map-point danger" title="超标">●</div>
              <div class="map-point normal" title="正常">●</div>
            </div>
            <div class="map-legend">
              <span class="legend-item">● 正常</span>
              <span class="legend-item warning">● 警告</span>
              <span class="legend-item danger">● 超标</span>
            </div>
          </div>
        </div>

        <!-- 最新报警列表 -->
        <div class="alerts-card">
          <div class="card-header">
            <h3>最新报警</h3>
            <el-link type="primary" @click="$router.push('/alerts')">查看更多 ></el-link>
          </div>
          <div class="alerts-list">
            <div v-for="alert in latestAlerts" :key="alert.id" class="alert-item" :class="alert.level">
              <div class="alert-point">{{ alert.point }}</div>
              <div class="alert-info">
                <span class="alert-indicator">{{ alert.indicator }}</span>
                <span class="alert-value">{{ alert.value }}</span>
              </div>
              <div class="alert-time">{{ alert.time }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 今日数据统计 -->
    <div class="stats-section">
      <div class="stats-card">
        <h3>今日数据统计</h3>
        <div class="stats-content">
          <div class="stat-item">
            <div class="stat-label">今日新增</div>
            <div class="stat-value">{{ todayStats.newRecords || 156 }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">今日超标</div>
            <div class="stat-value warning">{{ todayStats.exceedingRecords || 23 }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">最差监测点</div>
            <div class="stat-value">{{ todayStats.worstPoint || 'P-042' }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 快捷操作悬浮按钮 -->
    <div class="floating-actions">
      <el-button type="primary" circle :icon="Plus" @click="showQuickAdd = true" class="fab" />
    </div>

    <!-- 快速录入对话框 -->
    <el-dialog v-model="showQuickAdd" title="快速录入数据" width="500px">
      <el-form :model="quickForm" label-width="100px">
        <el-form-item label="监测点">
          <el-select v-model="quickForm.pointId" placeholder="选择监测点">
            <el-option label="P-001" value="P-001" />
            <el-option label="P-002" value="P-002" />
          </el-select>
        </el-form-item>
        <el-form-item label="pH值">
          <el-input-number v-model="quickForm.ph" :min="0" :max="14" :precision="2" />
        </el-form-item>
        <el-form-item label="浊度">
          <el-input-number v-model="quickForm.turbidity" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="余氯">
          <el-input-number v-model="quickForm.chlorine" :min="0" :precision="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showQuickAdd = false">取消</el-button>
        <el-button type="primary" @click="submitQuickAdd">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Bell, User, Setting, SwitchButton } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const router = useRouter()
const user = computed(() => authStore.user)

// 响应式数据
const selectedIndicator = ref('ph')
const showQuickAdd = ref(false)
const unreadCount = ref(3)

// KPI数据
const kpiData = ref({
  totalPoints: 48,
  onlinePoints: 46,
  offlinePoints: 2,
  todayRecords: 156,
  alertCount: 7,
  onlineRate: 98,
  offlineDevices: 2
})

// 水质健康指数
const healthIndex = ref({
  score: 86,
  grade: '优',
  trend: 2
})

// 最新报警
const latestAlerts = ref([
  { id: 1, point: 'P-042', indicator: 'pH', value: '9.2', level: 'danger', time: '14:32' },
  { id: 2, point: 'P-038', indicator: '余氯', value: '4.8', level: 'warning', time: '14:28' },
  { id: 3, point: 'P-021', indicator: '浊度', value: '7.3', level: 'warning', time: '14:15' },
  { id: 4, point: 'P-015', indicator: 'ORP', value: '356', level: 'danger', time: '14:02' },
  { id: 5, point: 'P-033', indicator: '电导率', value: '1102', level: 'info', time: '13:58' }
])

// 今日统计
const todayStats = ref({
  newRecords: 156,
  exceedingRecords: 23,
  worstPoint: 'P-042'
})

// 快速录入表单
const quickForm = ref({
  pointId: '',
  ph: null,
  turbidity: null,
  chlorine: null
})

// 计算属性
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '早上好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

// 方法
const refreshData = () => {
  ElMessage.success('数据已刷新')
  // 这里可以调用API刷新数据
}

const showNotifications = () => {
  ElMessage.info('暂无新通知')
}

const submitQuickAdd = () => {
  ElMessage.success('数据录入成功')
  showQuickAdd.value = false
  // 重置表单
  quickForm.value = {
    pointId: '',
    ph: null,
    turbidity: null,
    chlorine: null
  }
}

// 用户菜单处理
const handleUserMenu = async (command) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人资料功能开发中...')
      break
    case 'settings':
      ElMessage.info('系统设置功能开发中...')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm(
          '确定要退出登录吗？',
          '退出确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        await authStore.logout()
        ElMessage.success('已退出登录')
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('退出失败')
        }
      }
      break
  }
}

// 生命周期
onMounted(() => {
  // 页面加载时获取数据
  console.log('Dashboard mounted')
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

/* 欢迎区域 */
.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.welcome-left .greeting {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
}

.weather-info {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #7f8c8d;
}

.welcome-right {
  display: flex;
  gap: 12px;
}

.notification-badge {
  margin-left: 8px;
}

.user-dropdown {
  margin-left: 8px;
}

/* KPI卡片 */
.kpi-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.2s;
}

.kpi-card:hover {
  transform: translateY(-2px);
}

.kpi-card.online {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.kpi-card.today {
  background: linear-gradient(135deg, #48c774 0%, #3ec46d 100%);
  color: white;
}

.kpi-card.alerts {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  color: white;
}

.kpi-card.device {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.kpi-icon {
  font-size: 32px;
  margin-right: 16px;
}

.kpi-content {
  flex: 1;
}

.kpi-title {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 4px;
}

.kpi-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 4px;
}

.kpi-subtitle {
  font-size: 12px;
  opacity: 0.8;
}

/* 主要内容区域 */
.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.left-section,
.right-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 卡片通用样式 */
.health-index-card,
.trend-card,
.map-card,
.alerts-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

/* 水质健康指数 */
.health-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.circular-progress {
  position: relative;
  width: 120px;
  height: 120px;
}

.progress-circle {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: conic-gradient(#4facfe 0deg, #4facfe 309.6deg, #e9ecef 309.6deg);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.progress-value {
  font-size: 32px;
  font-weight: bold;
  color: #2c3e50;
}

.progress-label {
  font-size: 12px;
  color: #7f8c8d;
}

.health-grade {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 8px;
}

.health-grade.excellent { color: #48c774; }
.health-grade.good { color: #3298dc; }
.health-grade.fair { color: #ffdd57; }
.health-grade.poor { color: #ff9f43; }
.health-grade.bad { color: #ff6b6b; }

.health-trend {
  font-size: 14px;
  color: #7f8c8d;
}

.health-trend .up { color: #48c774; }
.health-trend .down { color: #ff6b6b; }

/* 趋势图 */
.chart-container {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  text-align: center;
  color: #7f8c8d;
}

.chart-note {
  font-size: 12px;
  margin-top: 8px;
}

/* 监测点分布 */
.map-placeholder {
  height: 180px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 8px;
}

.map-points {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
}

.map-point {
  font-size: 24px;
  cursor: pointer;
}

.map-point.normal { color: #48c774; }
.map-point.warning { color: #ff9f43; }
.map-point.danger { color: #ff6b6b; }

.map-legend {
  display: flex;
  gap: 16px;
  font-size: 12px;
}

.legend-item.warning { color: #ff9f43; }
.legend-item.danger { color: #ff6b6b; }

/* 报警列表 */
.alerts-list {
  max-height: 300px;
  overflow-y: auto;
}

.alert-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.alert-item:last-child {
  border-bottom: none;
}

.alert-point {
  width: 60px;
  font-weight: 500;
  color: #2c3e50;
}

.alert-info {
  flex: 1;
  display: flex;
  gap: 8px;
}

.alert-indicator {
  color: #7f8c8d;
}

.alert-value {
  font-weight: 500;
}

.alert-time {
  width: 50px;
  text-align: right;
  font-size: 12px;
  color: #7f8c8d;
}

.alert-item.danger .alert-value { color: #ff6b6b; }
.alert-item.warning .alert-value { color: #ff9f43; }
.alert-item.info .alert-value { color: #3298dc; }

/* 统计区域 */
.stats-section {
  margin-bottom: 24px;
}

.stats-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.stats-card h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.stats-content {
  display: flex;
  gap: 40px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
}

.stat-value.warning {
  color: #ff9f43;
}

/* 悬浮按钮 */
.floating-actions {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1000;
}

.fab {
  width: 56px;
  height: 56px;
  font-size: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .welcome-section {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .kpi-cards {
    grid-template-columns: 1fr;
  }
  
  .stats-content {
    flex-direction: column;
    gap: 16px;
  }
}
</style>
