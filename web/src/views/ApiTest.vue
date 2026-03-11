<template>
  <div class="api-test">
    <h2>API连通性测试</h2>
    
    <div class="test-section">
      <h3>测试结果</h3>
      <div class="test-results">
        <div class="test-item" :class="{ success: testResults.getRecords, error: testResults.getRecords === false }">
          <span>获取记录列表：</span>
          <span>{{ testResults.getRecords ? '✅ 成功' : testResults.getRecords === false ? '❌ 失败' : '⏳ 测试中...' }}</span>
        </div>
        <div class="test-item" :class="{ success: testResults.createRecord, error: testResults.createRecord === false }">
          <span>创建记录：</span>
          <span>{{ testResults.createRecord ? '✅ 成功' : testResults.createRecord === false ? '❌ 失败' : '⏳ 测试中...' }}</span>
        </div>
        <div class="test-item" :class="{ success: testResults.updateRecord, error: testResults.updateRecord === false }">
          <span>更新记录：</span>
          <span>{{ testResults.updateRecord ? '✅ 成功' : testResults.updateRecord === false ? '❌ 失败' : '⏳ 测试中...' }}</span>
        </div>
        <div class="test-item" :class="{ success: testResults.deleteRecord, error: testResults.deleteRecord === false }">
          <span>删除记录：</span>
          <span>{{ testResults.deleteRecord ? '✅ 成功' : testResults.deleteRecord === false ? '❌ 失败' : '⏳ 测试中...' }}</span>
        </div>
      </div>
    </div>

    <div class="test-section">
      <h3>API响应数据</h3>
      <div class="data-display">
        <h4>记录列表 ({{ records.length }} 条)</h4>
        <div class="records-grid">
          <div v-for="record in records.slice(0, 5)" :key="record.record_id" class="record-card">
            <div class="record-header">
              <strong>{{ record.point_id }}</strong>
              <span>{{ record.date }} {{ record.time }}</span>
            </div>
            <div class="record-data">
              <div>pH: {{ record.ph }}</div>
              <div>余氯: {{ record.chlorine }}</div>
              <div>浊度: {{ record.turbidity }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="test-section">
      <h3>手动测试</h3>
      <div class="manual-test">
        <button @click="testGetRecords" class="btn-primary">测试获取记录</button>
        <button @click="testCreateRecord" class="btn-success">测试创建记录</button>
        <button @click="testUpdateRecord" class="btn-warning">测试更新记录</button>
        <button @click="testDeleteRecord" class="btn-danger">测试删除记录</button>
      </div>
    </div>

    <div class="test-section">
      <h3>日志输出</h3>
      <div class="log-display">
        <div v-for="(log, index) in logs" :key="index" class="log-item" :class="log.type">
          <span class="log-time">{{ log.time }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { waterQualityApi } from '@/api/waterQuality'

const records = ref([])
const testResults = ref({
  getRecords: null,
  createRecord: null,
  updateRecord: null,
  deleteRecord: null
})
const logs = ref([])
const testRecordId = ref(null)

const addLog = (message, type = 'info') => {
  logs.value.unshift({
    time: new Date().toLocaleTimeString(),
    message,
    type
  })
  if (logs.value.length > 50) {
    logs.value = logs.value.slice(0, 50)
  }
}

const testGetRecords = async () => {
  try {
    addLog('开始测试获取记录列表...', 'info')
    const response = await waterQualityApi.getRecords()
    records.value = response.results || response
    testResults.value.getRecords = true
    addLog(`成功获取 ${records.value.length} 条记录`, 'success')
  } catch (error) {
    testResults.value.getRecords = false
    addLog(`获取记录失败: ${error.message}`, 'error')
  }
}

const testCreateRecord = async () => {
  try {
    addLog('开始测试创建记录...', 'info')
    const newRecord = {
      point_id: '测试点999',
      date: '2024-03-11',
      time: '12:00',
      chlorine: 2.5,
      conductivity: 450.0,
      ph: 7.2,
      orp: 650.0,
      turbidity: 1.8
    }
    const response = await waterQualityApi.createRecord(newRecord)
    testRecordId.value = response.record_id || response.id
    testResults.value.createRecord = true
    addLog(`成功创建记录，ID: ${testRecordId.value}`, 'success')
    
    // 重新获取记录列表
    await testGetRecords()
  } catch (error) {
    testResults.value.createRecord = false
    addLog(`创建记录失败: ${error.message}`, 'error')
  }
}

const testUpdateRecord = async () => {
  if (!testRecordId.value && records.value.length > 0) {
    testRecordId.value = records.value[0].record_id
  }
  
  if (!testRecordId.value) {
    addLog('没有可更新的记录ID', 'error')
    return
  }
  
  try {
    addLog(`开始测试更新记录 ID: ${testRecordId.value}...`, 'info')
    const updatedData = {
      point_id: '测试点999-更新',
      date: '2024-03-11',
      time: '12:30',
      chlorine: 3.0,
      conductivity: 460.0,
      ph: 7.5,
      orp: 660.0,
      turbidity: 2.0
    }
    await waterQualityApi.updateRecord(testRecordId.value, updatedData)
    testResults.value.updateRecord = true
    addLog(`成功更新记录 ID: ${testRecordId.value}`, 'success')
    
    // 重新获取记录列表
    await testGetRecords()
  } catch (error) {
    testResults.value.updateRecord = false
    addLog(`更新记录失败: ${error.message}`, 'error')
  }
}

const testDeleteRecord = async () => {
  if (!testRecordId.value && records.value.length > 0) {
    testRecordId.value = records.value[0].record_id
  }
  
  if (!testRecordId.value) {
    addLog('没有可删除的记录ID', 'error')
    return
  }
  
  try {
    addLog(`开始测试删除记录 ID: ${testRecordId.value}...`, 'info')
    await waterQualityApi.deleteRecord(testRecordId.value)
    testResults.value.deleteRecord = true
    addLog(`成功删除记录 ID: ${testRecordId.value}`, 'success')
    testRecordId.value = null
    
    // 重新获取记录列表
    await testGetRecords()
  } catch (error) {
    testResults.value.deleteRecord = false
    addLog(`删除记录失败: ${error.message}`, 'error')
  }
}

const runAllTests = async () => {
  addLog('开始运行所有API测试...', 'info')
  
  await testGetRecords()
  await new Promise(resolve => setTimeout(resolve, 500))
  
  await testCreateRecord()
  await new Promise(resolve => setTimeout(resolve, 500))
  
  await testUpdateRecord()
  await new Promise(resolve => setTimeout(resolve, 500))
  
  await testDeleteRecord()
  
  addLog('所有API测试完成', 'info')
}

onMounted(() => {
  runAllTests()
})
</script>

<style scoped>
.api-test {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.test-section {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.test-section h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.test-results {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.test-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-radius: 4px;
  background: #f5f5f5;
}

.test-item.success {
  background: #f6ffed;
  color: #52c41a;
}

.test-item.error {
  background: #fff2f0;
  color: #ff4d4f;
}

.data-display h4 {
  margin: 0 0 15px 0;
  color: #333;
}

.records-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
}

.record-card {
  border: 1px solid #e6e6e6;
  border-radius: 6px;
  padding: 15px;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-weight: 600;
}

.record-data {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.manual-test {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn-primary, .btn-success, .btn-warning, .btn-danger {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: white;
}

.btn-primary { background: #1890ff; }
.btn-success { background: #52c41a; }
.btn-warning { background: #faad14; }
.btn-danger { background: #ff4d4f; }

.log-display {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 10px;
  background: #fafafa;
}

.log-item {
  display: flex;
  gap: 15px;
  padding: 5px 0;
  border-bottom: 1px solid #f0f0f0;
}

.log-item:last-child {
  border-bottom: none;
}

.log-time {
  font-family: monospace;
  color: #666;
  min-width: 80px;
}

.log-message {
  flex: 1;
}

.log-item.success .log-message {
  color: #52c41a;
}

.log-item.error .log-message {
  color: #ff4d4f;
}

.log-item.info .log-message {
  color: #1890ff;
}

/* 深色主题 */
.dark .api-test .test-section {
  background: #1f1f1f;
  color: #fff;
}

.dark .api-test .test-item {
  background: #2a2a2a;
}

.dark .api-test .record-card {
  border-color: #4c4d4f;
}

.dark .api-test .log-display {
  background: #2a2a2a;
  border-color: #4c4d4f;
}
</style>
