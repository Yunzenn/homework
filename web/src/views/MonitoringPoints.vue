<template>
  <div class="monitoring-points-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">
            <span class="title-icon">📍</span>
            监测点管理
          </h1>
          <p class="page-subtitle">监测点信息管理 · 地理位置分布 · 状态监控</p>
        </div>
        <div class="header-stats">
          <div class="stat-card">
            <div class="stat-number">{{ totalPoints }}</div>
            <div class="stat-label">总监测点</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ activePoints }}</div>
            <div class="stat-label">启用状态</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          新增监测点
        </el-button>
        <el-button @click="loadMonitoringPoints">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-input
          v-model="searchText"
          placeholder="搜索监测点名称或编号"
          class="search-input"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <!-- 监测点列表 -->
    <div class="points-grid" v-loading="loading">
      <div 
        v-for="point in filteredPoints" 
        :key="point.id" 
        class="point-card"
        :class="{ 'inactive': !point.is_active }"
      >
        <div class="card-header">
          <div class="point-info">
            <h3 class="point-id">{{ point.point_id }}</h3>
            <h4 class="point-name">{{ point.name }}</h4>
          </div>
          <div class="point-status">
            <el-tag :type="point.is_active ? 'success' : 'danger'" size="small">
              {{ point.is_active ? '启用' : '禁用' }}
            </el-tag>
          </div>
        </div>
        
        <div class="card-content">
          <div class="location-info">
            <div class="location-item">
              <span class="label">📍 经纬度:</span>
              <span class="value">{{ point.latitude }}, {{ point.longitude }}</span>
            </div>
            <div class="location-item" v-if="point.location_description">
              <span class="label">📝 位置描述:</span>
              <span class="value">{{ point.location_description }}</span>
            </div>
          </div>
          
          <div class="time-info">
            <div class="time-item">
              <span class="label">创建时间:</span>
              <span class="value">{{ formatDate(point.created_at) }}</span>
            </div>
            <div class="time-item">
              <span class="label">更新时间:</span>
              <span class="value">{{ formatDate(point.updated_at) }}</span>
            </div>
          </div>
        </div>
        
        <div class="card-actions">
          <el-button type="text" size="small" @click="editPoint(point)">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button 
            type="text" 
            size="small" 
            :class="point.is_active ? 'danger' : 'success'"
            @click="togglePointStatus(point)"
          >
            <el-icon><Switch /></el-icon>
            {{ point.is_active ? '禁用' : '启用' }}
          </el-button>
          <el-button type="text" size="small" class="danger" @click="deletePoint(point)">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog 
      v-model="showAddDialog" 
      :title="editingPoint ? '编辑监测点' : '新增监测点'"
      width="600px"
      @close="resetForm"
    >
      <el-form 
        ref="formRef" 
        :model="formData" 
        :rules="formRules" 
        label-width="100px"
      >
        <el-form-item label="监测点编号" prop="point_id">
          <el-input v-model="formData.point_id" placeholder="如：HZ001" />
        </el-form-item>
        <el-form-item label="监测点名称" prop="name">
          <el-input v-model="formData.name" placeholder="如：西湖断桥监测站" />
        </el-form-item>
        <el-form-item label="纬度" prop="latitude">
          <el-input-number 
            v-model="formData.latitude" 
            :precision="7" 
            :min="-90" 
            :max="90"
            placeholder="30.2544000"
          />
        </el-form-item>
        <el-form-item label="经度" prop="longitude">
          <el-input-number 
            v-model="formData.longitude" 
            :precision="7" 
            :min="-180" 
            :max="180"
            placeholder="120.1463000"
          />
        </el-form-item>
        <el-form-item label="位置描述" prop="location_description">
          <el-input 
            v-model="formData.location_description" 
            type="textarea" 
            :rows="3"
            placeholder="详细描述监测点位置"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="formData.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="savePoint" :loading="saving">
          {{ editingPoint ? '更新' : '保存' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { monitoringPointApi } from '@/api/waterQuality'

// 响应式数据
const points = ref([])
const loading = ref(false)
const searchText = ref('')
const showAddDialog = ref(false)
const editingPoint = ref(null)
const saving = ref(false)
const formRef = ref()

// 表单数据
const formData = ref({
  point_id: '',
  name: '',
  latitude: 0,
  longitude: 0,
  location_description: '',
  is_active: true
})

// 表单验证规则
const formRules = {
  point_id: [
    { required: true, message: '请输入监测点编号', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入监测点名称', trigger: 'blur' }
  ],
  latitude: [
    { required: true, message: '请输入纬度', trigger: 'blur' },
    { type: 'number', min: -90, max: 90, message: '纬度必须在-90到90之间', trigger: 'blur' }
  ],
  longitude: [
    { required: true, message: '请输入经度', trigger: 'blur' },
    { type: 'number', min: -180, max: 180, message: '经度必须在-180到180之间', trigger: 'blur' }
  ]
}

// 计算属性
const totalPoints = computed(() => points.value.length)
const activePoints = computed(() => points.value.filter(p => p.is_active).length)

const filteredPoints = computed(() => {
  if (!searchText.value) {
    return points.value
  }
  const search = searchText.value.toLowerCase()
  return points.value.filter(point => 
    point.point_id.toLowerCase().includes(search) ||
    point.name.toLowerCase().includes(search) ||
    point.location_description?.toLowerCase().includes(search)
  )
})

// 方法
const loadMonitoringPoints = async () => {
  loading.value = true
  try {
    const response = await monitoringPointApi.getMonitoringPoints()
    points.value = response.data || []
  } catch (error) {
    console.error('加载监测点失败:', error)
    ElMessage.error('加载监测点失败')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  formData.value = {
    point_id: '',
    name: '',
    latitude: 0,
    longitude: 0,
    location_description: '',
    is_active: true
  }
  editingPoint.value = null
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

const editPoint = (point) => {
  editingPoint.value = point
  formData.value = { ...point }
  showAddDialog.value = true
}

const savePoint = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    saving.value = true
    
    if (editingPoint.value) {
      await monitoringPointApi.updateMonitoringPoint(editingPoint.value.id, formData.value)
      ElMessage.success('监测点更新成功')
    } else {
      await monitoringPointApi.createMonitoringPoint(formData.value)
      ElMessage.success('监测点创建成功')
    }
    
    showAddDialog.value = false
    resetForm()
    loadMonitoringPoints()
  } catch (error) {
    console.error('保存监测点失败:', error)
    ElMessage.error('保存监测点失败')
  } finally {
    saving.value = false
  }
}

const togglePointStatus = async (point) => {
  try {
    const action = point.is_active ? '禁用' : '启用'
    await ElMessageBox.confirm(`确定要${action}监测点"${point.name}"吗？`, '确认操作', {
      type: 'warning'
    })
    
    const updatedPoint = { ...point, is_active: !point.is_active }
    await monitoringPointApi.updateMonitoringPoint(point.id, updatedPoint)
    ElMessage.success(`监测点${action}成功`)
    loadMonitoringPoints()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('切换状态失败:', error)
      ElMessage.error('操作失败')
    }
  }
}

const deletePoint = async (point) => {
  try {
    await ElMessageBox.confirm(`确定要删除监测点"${point.name}"吗？此操作不可恢复。`, '确认删除', {
      type: 'warning',
      confirmButtonText: '删除',
      confirmButtonClass: 'el-button--danger'
    })
    
    await monitoringPointApi.deleteMonitoringPoint(point.id)
    ElMessage.success('监测点删除成功')
    loadMonitoringPoints()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除监测点失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleSearch = () => {
  // 搜索逻辑已在计算属性中处理
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadMonitoringPoints()
})
</script>

<style scoped>
.monitoring-points-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 15px;
  margin-bottom: 30px;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section h1 {
  font-size: 2.5rem;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  gap: 15px;
}

.title-icon {
  font-size: 2.5rem;
}

.page-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  margin: 0;
}

.header-stats {
  display: flex;
  gap: 20px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  backdrop-filter: blur(10px);
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.8;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.toolbar-left {
  display: flex;
  gap: 15px;
}

.search-input {
  width: 300px;
}

.points-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 25px;
}

.point-card {
  background: white;
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.point-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
  border-color: #667eea;
}

.point-card.inactive {
  opacity: 0.6;
  border-color: #f56c6c;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.point-id {
  font-size: 1.2rem;
  font-weight: bold;
  color: #667eea;
  margin: 0 0 5px 0;
}

.point-name {
  font-size: 1rem;
  color: #606266;
  margin: 0;
}

.location-info, .time-info {
  margin-bottom: 20px;
}

.location-item, .time-item {
  display: flex;
  margin-bottom: 8px;
  align-items: flex-start;
}

.label {
  font-weight: 500;
  color: #909399;
  min-width: 100px;
  margin-right: 10px;
}

.value {
  color: #606266;
  flex: 1;
}

.card-actions {
  display: flex;
  gap: 10px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.card-actions .el-button {
  padding: 8px 16px;
}

.card-actions .danger {
  color: #f56c6c;
}

.card-actions .danger:hover {
  background-color: #fef0f0;
}
</style>
