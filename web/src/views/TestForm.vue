<template>
  <div class="test-form">
    <h2>测试表单保存</h2>
    
    <div class="form-container">
      <div class="form-group">
        <label>监测点ID:</label>
        <input v-model="testData.point_id" placeholder="如：测试点001" />
      </div>
      
      <div class="form-group">
        <label>日期:</label>
        <input v-model="testData.date" type="date" />
      </div>
      
      <div class="form-group">
        <label>时间:</label>
        <input v-model="testData.time" type="time" />
      </div>
      
      <div class="form-group">
        <label>余氯(mg/L):</label>
        <input v-model="testData.chlorine" type="number" step="0.1" placeholder="2.5" />
      </div>
      
      <div class="form-group">
        <label>电导率(µS/cm):</label>
        <input v-model="testData.conductivity" type="number" step="0.1" placeholder="450.0" />
      </div>
      
      <div class="form-group">
        <label>pH值:</label>
        <input v-model="testData.ph" type="number" step="0.1" placeholder="7.2" />
      </div>
      
      <div class="form-group">
        <label>氧化还原电位(mV):</label>
        <input v-model="testData.orp" type="number" step="0.1" placeholder="650.0" />
      </div>
      
      <div class="form-group">
        <label>浊度(NTU):</label>
        <input v-model="testData.turbidity" type="number" step="0.1" placeholder="1.8" />
      </div>
      
      <div class="form-actions">
        <button @click="testSave" class="btn-primary">测试保存</button>
        <button @click="clearForm" class="btn-default">清空表单</button>
        <button @click="fillTestData" class="btn-info">填充测试数据</button>
      </div>
    </div>
    
    <div class="result-section">
      <h3>测试结果</h3>
      <div class="result-display">
        <pre>{{ JSON.stringify(testData, null, 2) }}</pre>
      </div>
    </div>
    
    <div class="log-section">
      <h3>操作日志</h3>
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
import { ref } from 'vue'
import { waterQualityApi } from '@/api/waterQuality'

const testData = ref({
  point_id: '',
  date: '',
  time: '',
  chlorine: '',
  conductivity: '',
  ph: '',
  orp: '',
  turbidity: ''
})

const logs = ref([])

const addLog = (message, type = 'info') => {
  logs.value.unshift({
    time: new Date().toLocaleTimeString(),
    message,
    type
  })
  if (logs.value.length > 20) {
    logs.value = logs.value.slice(0, 20)
  }
}

const clearForm = () => {
  testData.value = {
    point_id: '',
    date: '',
    time: '',
    chlorine: '',
    conductivity: '',
    ph: '',
    orp: '',
    turbidity: ''
  }
  addLog('表单已清空', 'info')
}

const fillTestData = () => {
  testData.value = {
    point_id: '测试点001',
    date: '2024-03-11',
    time: '12:00',
    chlorine: '2.5',
    conductivity: '450.0',
    ph: '7.2',
    orp: '650.0',
    turbidity: '1.8'
  }
  addLog('已填充测试数据', 'info')
}

const testSave = async () => {
  try {
    addLog('开始测试保存...', 'info')
    
    // 数据验证
    if (!testData.value.point_id || !testData.value.date || !testData.value.time) {
      addLog('错误：请填写监测点ID、日期和时间', 'error')
      return
    }
    
    // 准备保存数据
    const dataToSave = {
      point_id: testData.value.point_id.trim(),
      date: testData.value.date,
      time: testData.value.time,
      chlorine: parseFloat(testData.value.chlorine) || 0.0,
      conductivity: parseFloat(testData.value.conductivity) || 0.0,
      ph: parseFloat(testData.value.ph) || 7.0,
      orp: parseFloat(testData.value.orp) || 0.0,
      turbidity: parseFloat(testData.value.turbidity) || 0.0
    }
    
    addLog(`准备保存数据: ${JSON.stringify(dataToSave)}`, 'info')
    
    // 调用API
    const response = await waterQualityApi.createRecord(dataToSave)
    addLog(`保存成功！响应: ${JSON.stringify(response)}`, 'success')
    
    // 清空表单
    clearForm()
    
  } catch (error) {
    addLog(`保存失败: ${error.message}`, 'error')
    
    if (error.response && error.response.data) {
      addLog(`详细错误: ${JSON.stringify(error.response.data)}`, 'error')
    }
  }
}
</script>

<style scoped>
.test-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.form-container {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.btn-primary, .btn-default, .btn-info {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: white;
}

.btn-primary { background: #1890ff; }
.btn-default { background: #f0f0f0; color: #333; }
.btn-info { background: #17bfdd; }

.result-section, .log-section {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.result-display pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
}

.log-display {
  max-height: 300px;
  overflow-y: auto;
}

.log-item {
  display: flex;
  gap: 15px;
  padding: 5px 0;
  border-bottom: 1px solid #f0f0f0;
}

.log-time {
  font-family: monospace;
  color: #666;
  min-width: 80px;
}

.log-message {
  flex: 1;
}

.log-item.success .log-message { color: #52c41a; }
.log-item.error .log-message { color: #ff4d4f; }
.log-item.info .log-message { color: #1890ff; }

/* 深色主题 */
.dark .test-form .form-container,
.dark .test-form .result-section,
.dark .test-form .log-section {
  background: #1f1f1f;
  color: #fff;
}

.dark .test-form .form-group input {
  background: #2a2a2a;
  border-color: #4c4d4f;
  color: #fff;
}

.dark .test-form .result-display pre {
  background: #2a2a2a;
}
</style>
