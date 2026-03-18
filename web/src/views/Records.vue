<template>
  <div class="data-viewer-container" v-loading="loading">
    <!-- 页面头部 -->
    <div class="viewer-header">
      <div class="header-left">
        <h2 class="page-title">
          <el-icon><Document /></el-icon>
          数据查看
          <span class="subtitle">数据浏览中心 · 完整呈现 · 便捷操作</span>
        </h2>
      </div>
      <div class="header-right">
        <!-- 视图切换 -->
        <el-button-group class="view-switcher">
          <el-button 
            :type="currentView === 'timeline' ? 'primary' : 'default'"
            @click="switchView('timeline')"
          >
            <el-icon><Clock /></el-icon>
            时间轴
          </el-button>
          <el-button 
            :type="currentView === 'calendar' ? 'primary' : 'default'"
            @click="switchView('calendar')"
          >
            <el-icon><Calendar /></el-icon>
            日历
          </el-button>
          <el-button 
            :type="currentView === 'wave' ? 'primary' : 'default'"
            @click="switchView('wave')"
          >
            <el-icon><TrendCharts /></el-icon>
            波形
          </el-button>
          <el-button 
            :type="currentView === 'table' ? 'primary' : 'default'"
            @click="switchView('table')"
          >
            <el-icon><Grid /></el-icon>
            表格
          </el-button>
          <el-button 
            :type="currentView === 'compare' ? 'primary' : 'default'"
            @click="switchView('compare')"
          >
            <el-icon><Histogram /></el-icon>
            对比
          </el-button>
          <el-button 
            :type="currentView === 'quality' ? 'primary' : 'default'"
            @click="switchView('quality')"
          >
            <el-icon><DataLine /></el-icon>
            质量看板
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 快照管理栏 -->
    <div class="snapshot-bar">
      <div class="snapshot-left">
        <el-dropdown @command="loadSnapshot" trigger="click">
          <el-button type="info" plain>
            <el-icon><Camera /></el-icon>
            快照: {{ currentSnapshot?.name || '无' }}
            <el-icon><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item 
                v-for="snapshot in snapshots" 
                :key="snapshot.id"
                :command="snapshot"
              >
                <div class="snapshot-item">
                  <span class="snapshot-name">{{ snapshot.name }}</span>
                  <span class="snapshot-time">{{ formatTime(snapshot.createdAt) }}</span>
                </div>
              </el-dropdown-item>
              <el-dropdown-item divided command="manage">
                <el-icon><Setting /></el-icon>
                管理快照
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        
        <el-button type="success" plain @click="saveSnapshot">
          <el-icon><Plus /></el-icon>
          保存当前快照
        </el-button>
        
        <el-button type="warning" plain @click="shareSnapshot">
          <el-icon><Share /></el-icon>
          分享
        </el-button>
        
        <el-button type="primary" plain @click="showSubscribeDialog = true">
          <el-icon><Bell /></el-icon>
          订阅
        </el-button>
      </div>
      
      <div class="snapshot-right">
        <el-tag v-if="currentSnapshot" type="info" closable @close="clearSnapshot">
          {{ currentSnapshot.name }}
        </el-tag>
      </div>
    </div>

    <!-- 快速筛选栏 -->
    <div class="filter-bar">
      <div class="filter-group">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          :shortcuts="dateShortcuts"
          @change="applyFilters"
          style="width: 280px"
        />
        
        <el-select
          v-model="selectedPoints"
          multiple
          collapse-tags
          collapse-tags-tooltip
          placeholder="监测点"
          style="width: 200px"
          @change="applyFilters"
        >
          <el-option
            v-for="point in monitorPoints"
            :key="point.id"
            :label="point.name"
            :value="point.id"
          />
        </el-select>
        
        <el-select
          v-model="selectedMetrics"
          multiple
          placeholder="指标范围"
          style="width: 150px"
          @change="applyFilters"
        >
          <el-option label="余氯" value="chlorine" />
          <el-option label="pH值" value="ph" />
          <el-option label="电导率" value="conductivity" />
          <el-option label="ORP" value="orp" />
          <el-option label="浊度" value="turbidity" />
        </el-select>
        
        <el-select
          v-model="selectedStatus"
          placeholder="状态"
          style="width: 120px"
          @change="applyFilters"
        >
          <el-option label="全部" value="" />
          <el-option label="正常" value="normal" />
          <el-option label="警告" value="warning" />
          <el-option label="超标" value="danger" />
        </el-select>
        
        <el-select
          v-model="selectedTags"
          multiple
          placeholder="标签"
          style="width: 150px"
          @change="applyFilters"
        >
          <el-option label="可疑数据" value="suspicious" />
          <el-option label="已核实" value="verified" />
          <el-option label="待处理" value="pending" />
        </el-select>
      </div>
      
      <div class="filter-actions">
        <el-button @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon>
          重置
        </el-button>
        <el-button type="primary" @click="applyFilters">
          <el-icon><Search /></el-icon>
          筛选
        </el-button>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 时间轴视图 -->
      <div v-if="currentView === 'timeline'" class="timeline-view">
        <div class="timeline-header">
          <h3>时间轴快速定位</h3>
          <div class="timeline-dates">
            <div 
              v-for="date in timelineDates" 
              :key="date.value"
              class="timeline-date"
              :class="{ active: date.value === selectedDate }"
              @click="selectTimelineDate(date.value)"
            >
              <div class="date-label">{{ date.label }}</div>
              <div class="date-indicator" :class="date.status"></div>
            </div>
            <el-button type="text" @click="loadMoreDates">
              <el-icon><More /></el-icon>
              更多
            </el-button>
          </div>
        </div>
        
        <div class="timeline-content">
          <div class="timeline-records">
            <div 
              v-for="record in timelineRecords" 
              :key="record.id"
              class="timeline-record"
              :class="getRecordClass(record)"
              @click="viewRecordDetail(record)"
            >
              <div class="record-time">{{ formatRecordTime(record.time) }}</div>
              <div class="record-point">{{ record.point_id }}</div>
              <div class="record-metrics">
                <span v-for="metric in getAbnormalMetrics(record)" :key="metric.name" class="metric-tag">
                  {{ metric.name }}: {{ metric.value }}
                </span>
              </div>
              <div class="record-status" :class="record.status">
                {{ getStatusText(record.status) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 日历视图 -->
      <div v-if="currentView === 'calendar'" class="calendar-view">
        <div class="calendar-header">
          <el-button-group>
            <el-button @click="previousMonth">
              <el-icon><ArrowLeft /></el-icon>
            </el-button>
            <el-button>{{ currentYear }}年{{ currentMonth }}月</el-button>
            <el-button @click="nextMonth">
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </el-button-group>
        </div>
        
        <div class="calendar-grid">
          <div class="calendar-weekdays">
            <div v-for="day in ['日', '一', '二', '三', '四', '五', '六']" :key="day" class="weekday">
              {{ day }}
            </div>
          </div>
          <div class="calendar-days">
            <div 
              v-for="day in calendarDays" 
              :key="day.date"
              class="calendar-day"
              :class="{ 
                'other-month': day.otherMonth,
                'selected': day.date === selectedDate,
                'has-data': day.hasData
              }"
              @click="selectCalendarDate(day.date)"
            >
              <div class="day-number">{{ day.day }}</div>
              <div v-if="day.hasData" class="day-indicator" :class="day.status"></div>
            </div>
          </div>
        </div>
        
        <div v-if="selectedDateRecords.length" class="calendar-records">
          <h4>{{ selectedDate }} 的记录</h4>
          <div class="day-records">
            <div 
              v-for="record in selectedDateRecords" 
              :key="record.id"
              class="day-record"
              @click="viewRecordDetail(record)"
            >
              <span class="record-time">{{ record.time }}</span>
              <span class="record-point">{{ record.point_id }}</span>
              <span class="record-status" :class="record.status">{{ getStatusText(record.status) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 波形视图 -->
      <div v-if="currentView === 'wave'" class="wave-view">
        <div class="wave-controls">
          <el-select v-model="waveMetric" @change="updateWaveChart">
            <el-option label="pH值" value="ph" />
            <el-option label="浊度" value="turbidity" />
            <el-option label="余氯" value="chlorine" />
            <el-option label="电导率" value="conductivity" />
            <el-option label="ORP" value="orp" />
          </el-select>
          
          <el-date-picker
            v-model="waveDateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            @change="updateWaveChart"
          />
        </div>
        
        <div class="wave-chart-container" ref="waveChartRef"></div>
        
        <div v-if="selectedWavePoint" class="wave-point-info">
          <el-alert 
            :title="`标记点：${selectedWavePoint.point_id} ${selectedWavePoint.time} ${waveMetric} ${selectedWavePoint.value}`"
            :type="selectedWavePoint.status === 'danger' ? 'error' : selectedWavePoint.status === 'warning' ? 'warning' : 'info'"
            show-icon
            :closable="false"
          />
        </div>
      </div>

      <!-- 表格视图 -->
      <div v-if="currentView === 'table'" class="table-view">
        <div class="table-toolbar">
          <div class="toolbar-left">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              新增记录
            </el-button>
            <el-button type="success" @click="handleBatchUpload">
              <el-icon><Upload /></el-icon>
              批量上传
            </el-button>
            <el-button 
              type="danger" 
              :disabled="!selectedRecords.length"
              @click="handleBatchDelete"
            >
              <el-icon><Delete /></el-icon>
              批量删除
            </el-button>
          </div>
          
          <div class="toolbar-right">
            <el-input
              v-model="tableSearch"
              placeholder="搜索记录"
              :prefix-icon="Search"
              clearable
              @input="handleTableSearch"
              style="width: 200px"
            />
            
            <el-dropdown @command="handleExport">
              <el-button>
                <el-icon><Download /></el-icon>
                导出
                <el-icon><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="csv">CSV格式</el-dropdown-item>
                  <el-dropdown-item command="excel">Excel格式</el-dropdown-item>
                  <el-dropdown-item command="pdf">PDF格式</el-dropdown-item>
                  <el-dropdown-item command="json">JSON格式</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
        
        <div class="table-container">
          <el-table
            v-loading="tableLoading"
            :data="paginatedRecords"
            @selection-change="handleSelectionChange"
            @sort-change="handleSortChange"
            stripe
            border
            style="width: 100%"
          >
            <el-table-column type="selection" width="55" fixed="left" />
            <el-table-column prop="point_id" label="监测点" width="120" fixed="left" sortable />
            <el-table-column prop="date" label="日期" width="120" sortable />
            <el-table-column prop="time" label="时间" width="100" sortable />
            <el-table-column prop="chlorine" label="余氯" width="100" sortable>
              <template #default="scope">
                <span :class="getMetricClass(scope.row.chlorine, 'chlorine')">
                  {{ scope.row.chlorine }} mg/L
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="ph" label="pH值" width="100" sortable>
              <template #default="scope">
                <span :class="getMetricClass(scope.row.ph, 'ph')">
                  {{ scope.row.ph }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="conductivity" label="电导率" width="120" sortable>
              <template #default="scope">
                <span :class="getMetricClass(scope.row.conductivity, 'conductivity')">
                  {{ scope.row.conductivity }} µS/cm
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="orp" label="ORP" width="100" sortable>
              <template #default="scope">
                <span :class="getMetricClass(scope.row.orp, 'orp')">
                  {{ scope.row.orp }} mV
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="turbidity" label="浊度" width="100" sortable>
              <template #default="scope">
                <span :class="getMetricClass(scope.row.turbidity, 'turbidity')">
                  {{ scope.row.turbidity }} NTU
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getStatusTagType(scope.row.status)" size="small">
                  {{ getStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="tags" label="标签" width="150">
              <template #default="scope">
                <el-tag 
                  v-for="tag in scope.row.tags" 
                  :key="tag"
                  :type="getTagType(tag)"
                  size="small"
                  class="record-tag"
                >
                  {{ getTagText(tag) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="scope">
                <el-button type="text" size="small" @click="viewRecordDetail(scope.row)">
                  <el-icon><View /></el-icon>
                  查看
                </el-button>
                <el-button type="text" size="small" @click="editRecord(scope.row)">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button type="text" size="small" @click="addRecordTag(scope.row)">
                  <el-icon><CollectionTag /></el-icon>
                  标注
                </el-button>
                <el-button type="text" size="small" @click="deleteRecord(scope.row)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="table-pagination">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="totalRecords"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
              />
            </div>
        </div>
      </div>

      <!-- 对比视图 -->
      <div v-if="currentView === 'compare'" class="compare-view">
        <div class="compare-selector">
          <h4>选择要对比的记录（最多4条）</h4>
          <div class="compare-cards">
            <div 
              v-for="(record, index) in compareRecords" 
              :key="record.id"
              class="compare-card"
              :class="{ selected: record.selected }"
            >
              <div class="card-header">
                <el-checkbox 
                  v-model="record.selected"
                  :disabled="!record.selected && compareRecords.filter(r => r.selected).length >= 4"
                  @change="updateCompareSelection"
                >
                  {{ record.point_id }}
                </el-checkbox>
                <el-button type="text" size="small" @click="removeCompareRecord(index)">
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
              <div class="card-content">
                <div class="record-info">
                  <span>{{ record.date }} {{ record.time }}</span>
                  <el-tag :type="getStatusTagType(record.status)" size="small">
                    {{ getStatusText(record.status) }}
                  </el-tag>
                </div>
              </div>
            </div>
            
            <el-button type="dashed" @click="showCompareSelector = true">
              <el-icon><Plus /></el-icon>
              添加记录
            </el-button>
          </div>
        </div>
        
        <div v-if="selectedCompareRecords.length >= 2" class="compare-result">
          <div class="compare-actions">
            <el-button type="primary" @click="generateCompareReport">
              <el-icon><Document /></el-icon>
              生成对比报告
            </el-button>
            <el-button @click="exportCompareResult">
              <el-icon><Download /></el-icon>
              导出对比结果
            </el-button>
          </div>
          
          <div class="compare-table">
            <table class="comparison-table">
              <thead>
                <tr>
                  <th>指标</th>
                  <th v-for="record in selectedCompareRecords" :key="record.id">
                    {{ record.point_id }}({{ getStatusText(record.status) }})
                  </th>
                  <th>差值</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="metric in compareMetrics" :key="metric.key">
                  <td>{{ metric.name }}</td>
                  <td v-for="record in selectedCompareRecords" :key="record.id">
                    <span :class="getMetricClass(record[metric.key], metric.key)">
                      {{ record[metric.key] }} {{ metric.unit }}
                    </span>
                  </td>
                  <td>
                    <span :class="getDifferenceClass(calculateDifference(metric.key))">
                      {{ calculateDifference(metric.key) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 质量看板视图 -->
      <div v-if="currentView === 'quality'" class="quality-view">
        <div class="quality-overview">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-card class="quality-card">
                <div class="quality-item">
                  <div class="quality-label">今日数据完整率</div>
                  <div class="quality-value">{{ qualityMetrics.completeness }}%</div>
                  <el-progress :percentage="qualityMetrics.completeness" :color="getProgressColor(qualityMetrics.completeness)" />
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="quality-card">
                <div class="quality-item">
                  <div class="quality-label">缺失记录</div>
                  <div class="quality-value">{{ qualityMetrics.missingCount }}条</div>
                  <el-button type="text" @click="viewMissingRecords">查看</el-button>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="quality-card">
                <div class="quality-item">
                  <div class="quality-label">异常值检测</div>
                  <div class="quality-value">{{ qualityMetrics.anomalyCount }}条</div>
                  <el-button type="text" @click="viewAnomalyRecords">核实</el-button>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="quality-card">
                <div class="quality-item">
                  <div class="quality-label">监测点在线状态</div>
                  <div class="online-status">
                    <span class="status-item online">🟢 在线: {{ qualityMetrics.onlineCount }}</span>
                    <span class="status-item delayed">🟡 延迟: {{ qualityMetrics.delayedCount }}</span>
                    <span class="status-item offline">🔴 离线: {{ qualityMetrics.offlineCount }}</span>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
        
        <div class="quality-charts">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card>
                <div class="chart-header">
                  <h4>数据质量趋势</h4>
                </div>
                <div ref="qualityTrendChartRef" class="chart-container"></div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <div class="chart-header">
                  <h4>异常值分布</h4>
                </div>
                <div ref="anomalyDistributionChartRef" class="chart-container"></div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </div>
    </div>

    <!-- 记录详情弹窗 -->
    <el-dialog v-model="showDetailModal" title="记录详情" width="800px">
      <div v-if="selectedRecord" class="record-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="监测点">{{ selectedRecord.point_id }}</el-descriptions-item>
          <el-descriptions-item label="日期时间">{{ selectedRecord.date }} {{ selectedRecord.time }}</el-descriptions-item>
          <el-descriptions-item label="余氯">{{ selectedRecord.chlorine }} mg/L</el-descriptions-item>
          <el-descriptions-item label="pH值">{{ selectedRecord.ph }}</el-descriptions-item>
          <el-descriptions-item label="电导率">{{ selectedRecord.conductivity }} µS/cm</el-descriptions-item>
          <el-descriptions-item label="ORP">{{ selectedRecord.orp }} mV</el-descriptions-item>
          <el-descriptions-item label="浊度">{{ selectedRecord.turbidity }} NTU</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(selectedRecord.status)">
              {{ getStatusText(selectedRecord.status) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="record-notes">
          <h4>备注</h4>
          <div class="notes-content">
            <div v-for="note in selectedRecord.notes" :key="note.id" class="note-item">
              <div class="note-header">
                <span class="note-author">{{ note.author }}</span>
                <span class="note-time">{{ formatTime(note.createdAt) }}</span>
              </div>
              <div class="note-content">{{ note.content }}</div>
            </div>
            <el-input
              v-model="newNote"
              type="textarea"
              :rows="3"
              placeholder="添加备注..."
              @keyup.ctrl.enter="addNote"
            />
            <el-button type="primary" @click="addNote">添加备注</el-button>
          </div>
        </div>
        
        <div class="record-actions">
          <el-button @click="editRecord(selectedRecord)">编辑</el-button>
          <el-button @click="deleteRecord(selectedRecord)" type="danger">删除</el-button>
          <el-button @click="navigateRecord('prev')" :disabled="!hasPrevRecord">上一条</el-button>
          <el-button @click="navigateRecord('next')" :disabled="!hasNextRecord">下一条</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 订阅对话框 -->
    <el-dialog v-model="showSubscribeDialog" title="订阅设置" width="600px">
      <el-form :model="subscribeForm" label-width="120px">
        <el-form-item label="订阅名称">
          <el-input v-model="subscribeForm.name" placeholder="如：每日超标数据" />
        </el-form-item>
        <el-form-item label="订阅条件">
          <el-select v-model="subscribeForm.condition" placeholder="选择条件">
            <el-option label="每天8点发送昨日超标数据" value="daily_alerts" />
            <el-option label="每周一发送上周数据报告" value="weekly_report" />
            <el-option label="监测点异常时立即通知" value="realtime_alert" />
            <el-option label="自定义条件" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="发送格式">
          <el-radio-group v-model="subscribeForm.format">
            <el-radio label="excel">Excel附件</el-radio>
            <el-radio label="pdf">PDF报告</el-radio>
            <el-radio label="email">邮件正文</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="收件人">
          <el-select v-model="subscribeForm.recipients" multiple placeholder="选择收件人">
            <el-option label="admin@example.com" value="admin@example.com" />
            <el-option label="operator@example.com" value="operator@example.com" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSubscribeDialog = false">取消</el-button>
        <el-button type="primary" @click="saveSubscribe">保存订阅</el-button>
      </template>
    </el-dialog>

    <!-- 标注对话框 -->
    <el-dialog v-model="showTagDialog" title="数据标注" width="500px">
      <el-form :model="tagForm" label-width="80px">
        <el-form-item label="标签类型">
          <el-select v-model="tagForm.type" placeholder="选择标签">
            <el-option label="可疑数据" value="suspicious" />
            <el-option label="已核实" value="verified" />
            <el-option label="待处理" value="pending" />
            <el-option label="异常" value="anomaly" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="tagForm.note" type="textarea" :rows="3" placeholder="添加备注..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTagDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTag">保存标注</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Document, Clock, Calendar, TrendCharts, Grid, Histogram, DataLine,
  Camera, Plus, Share, Bell, Search, RefreshLeft, More, ArrowLeft, ArrowRight,
  Download, Upload, Delete, View, Edit, CollectionTag, Close, Setting,
  ArrowDown
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { useWaterQualityStore } from '@/stores/waterQuality'
import { waterQualityApi } from '@/api/waterQuality'

const router = useRouter()
const waterQualityStore = useWaterQualityStore()

// 响应式数据
const loading = ref(false)
const currentView = ref('table')
const currentSnapshot = ref(null)
const showDetailModal = ref(false)
const showSubscribeDialog = ref(false)
const showTagDialog = ref(false)
const selectedRecord = ref(null)
const newNote = ref('')

// 筛选条件
const dateRange = ref([])
const selectedPoints = ref([])
const selectedMetrics = ref([])
const selectedStatus = ref('')
const selectedTags = ref([])

// 表格相关
const tableSearch = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const selectedRecords = ref([])
const tableSort = ref({ prop: 'date', order: 'descending' })

// 时间轴相关
const timelineDates = ref([])
const selectedDate = ref('')
const timelineRecords = ref([])

// 日历相关
const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)
const calendarDays = ref([])
const selectedDateRecords = computed(() => {
  if (!selectedDate.value) return []
  return waterQualityRecords.value.filter(record => record.date === selectedDate.value)
})

// 波形相关
const waveMetric = ref('ph')
const waveDateRange = ref([])
const selectedWavePoint = ref(null)
const waveChartRef = ref()

// 对比相关
const compareRecords = ref([])
const showCompareSelector = ref(false)

// 质量看板相关
const qualityMetrics = reactive({
  completeness: 98,
  missingCount: 3,
  anomalyCount: 2,
  onlineCount: 45,
  delayedCount: 2,
  offlineCount: 1
})

// 快照相关
const snapshots = ref([
  { id: 1, name: '今日超标数据', createdAt: new Date() },
  { id: 2, name: '3月15日异常记录', createdAt: new Date(Date.now() - 86400000) },
  { id: 3, name: '上周数据报告', createdAt: new Date(Date.now() - 604800000) }
])

// 订阅表单
const subscribeForm = reactive({
  name: '',
  condition: '',
  format: 'excel',
  recipients: []
})

// 标注表单
const tagForm = reactive({
  type: '',
  note: ''
})

// 监测点数据
const monitorPoints = ref([
  { id: 'P-001', name: 'P-001' },
  { id: 'P-042', name: 'P-042' },
  { id: 'P-038', name: 'P-038' },
  { id: 'P-021', name: 'P-021' }
])

// 水质记录数据
const waterQualityRecords = ref([])
const totalRecords = ref(0)

// 计算属性
const filteredRecords = computed(() => {
  let records = [...waterQualityRecords.value]
  
  // 应用筛选条件
  if (dateRange.value && dateRange.value.length === 2) {
    records = records.filter(record => {
      const recordDate = new Date(record.date)
      return recordDate >= dateRange.value[0] && recordDate <= dateRange.value[1]
    })
  }
  
  if (selectedPoints.value.length) {
    records = records.filter(record => selectedPoints.value.includes(record.point_id))
  }
  
  if (selectedStatus.value) {
    records = records.filter(record => record.status === selectedStatus.value)
  }
  
  if (selectedTags.value.length) {
    records = records.filter(record => 
      record.tags && record.tags.some(tag => selectedTags.value.includes(tag))
    )
  }
  
  if (tableSearch.value) {
    const search = tableSearch.value.toLowerCase()
    records = records.filter(record => 
      record.point_id.toLowerCase().includes(search) ||
      record.date.includes(search) ||
      record.time.includes(search)
    )
  }
  
  return records
})

const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRecords.value.slice(start, end)
})

const selectedCompareRecords = computed(() => {
  return compareRecords.value.filter(record => record.selected)
})

const compareMetrics = [
  { key: 'chlorine', name: '余氯', unit: 'mg/L' },
  { key: 'ph', name: 'pH值', unit: '' },
  { key: 'conductivity', name: '电导率', unit: 'µS/cm' },
  { key: 'orp', name: 'ORP', unit: 'mV' },
  { key: 'turbidity', name: '浊度', unit: 'NTU' }
]

const dateShortcuts = [
  {
    text: '今天',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24)
      return [start, end]
    }
  },
  {
    text: '最近7天',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    }
  },
  {
    text: '最近30天',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    }
  }
]

// API调用方法
const loadRecords = async () => {
  try {
    loading.value = true
    
    // 构建查询参数
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: tableSearch.value
    }
    
    // 添加日期范围
    if (dateRange.value && dateRange.value.length === 2) {
      params.date_after = dateRange.value[0].toISOString().split('T')[0]
      params.date_before = dateRange.value[1].toISOString().split('T')[0]
    }
    
    // 添加监测点筛选
    if (selectedPoints.value.length > 0) {
      params.point_id = selectedPoints.value.join(',')
    }
    
    // 添加状态筛选
    if (selectedStatus.value) {
      params.status = selectedStatus.value
    }
    
    // 添加排序
    if (tableSort.value.prop) {
      params.ordering = tableSort.value.order === 'descending' ? `-${tableSort.value.prop}` : tableSort.value.prop
    }
    
    const response = await waterQualityApi.getRecords(params)
    
    // 处理响应数据
    if (response.results) {
      // 分页响应
      waterQualityRecords.value = response.results.map(record => ({
        ...record,
        tags: record.tags || [],
        notes: record.notes || []
      }))
      totalRecords.value = response.count
    } else {
      // 非分页响应
      waterQualityRecords.value = response.map(record => ({
        ...record,
        tags: record.tags || [],
        notes: record.notes || []
      }))
      totalRecords.value = response.length
    }
    
    ElMessage.success('数据加载成功')
    
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

const loadMonitorPoints = async () => {
  try {
    // 从已有数据中提取监测点
    const points = [...new Set(waterQualityRecords.value.map(record => record.point_id))]
    monitorPoints.value = points.map(point => ({ id: point, name: point }))
  } catch (error) {
    console.error('加载监测点失败:', error)
  }
}

const calculateStatus = (record) => {
  // 根据指标值计算状态
  const thresholds = {
    chlorine: { min: 0.5, max: 2.0 },
    ph: { min: 6.5, max: 8.5 },
    conductivity: { min: 200, max: 800 },
    orp: { min: 400, max: 800 },
    turbidity: { min: 0, max: 5.0 }
  }
  
  let status = 'normal'
  
  // 检查各项指标
  if (record.chlorine < thresholds.chlorine.min || record.chlorine > thresholds.chlorine.max) {
    status = 'danger'
  } else if (record.ph < thresholds.ph.min || record.ph > thresholds.ph.max) {
    status = 'danger'
  } else if (record.conductivity < thresholds.conductivity.min || record.conductivity > thresholds.conductivity.max) {
    status = 'danger'
  } else if (record.orp < thresholds.orp.min || record.orp > thresholds.orp.max) {
    status = 'danger'
  } else if (record.turbidity > thresholds.turbidity.max) {
    status = 'danger'
  } else {
    // 检查警告状态
    const warningThresholds = {
      chlorine: { min: 0.8, max: 1.8 },
      ph: { min: 7.0, max: 8.0 },
      conductivity: { min: 300, max: 700 },
      orp: { min: 500, max: 700 },
      turbidity: { min: 0, max: 3.0 }
    }
    
    if (record.chlorine < warningThresholds.chlorine.min || record.chlorine > warningThresholds.chlorine.max ||
        record.ph < warningThresholds.ph.min || record.ph > warningThresholds.ph.max ||
        record.conductivity < warningThresholds.conductivity.min || record.conductivity > warningThresholds.conductivity.max ||
        record.orp < warningThresholds.orp.min || record.orp > warningThresholds.orp.max ||
        record.turbidity > warningThresholds.turbidity.max) {
      status = 'warning'
    }
  }
  
  return status
}

// 方法
const switchView = (view) => {
  currentView.value = view
  if (view === 'wave') {
    nextTick(() => {
      initWaveChart()
    })
  } else if (view === 'quality') {
    nextTick(() => {
      initQualityCharts()
    })
  }
}

const loadSnapshot = (snapshot) => {
  if (snapshot === 'manage') {
    // 管理快照逻辑
    return
  }
  currentSnapshot.value = snapshot
  // 应用快照筛选条件
  ElMessage.success(`已加载快照: ${snapshot.name}`)
}

const saveSnapshot = () => {
  ElMessageBox.prompt('请输入快照名称', '保存快照', {
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(({ value }) => {
    const snapshot = {
      id: Date.now(),
      name: value,
      createdAt: new Date(),
      filters: {
        dateRange: dateRange.value,
        selectedPoints: selectedPoints.value,
        selectedMetrics: selectedMetrics.value,
        selectedStatus: selectedStatus.value,
        selectedTags: selectedTags.value
      }
    }
    snapshots.value.unshift(snapshot)
    ElMessage.success('快照保存成功')
  })
}

const shareSnapshot = () => {
  if (!currentSnapshot.value) {
    ElMessage.warning('请先选择或创建快照')
    return
  }
  // 生成分享链接逻辑
  ElMessage.success('分享链接已生成')
}

const applyFilters = () => {
  currentPage.value = 1
  loadRecords()
}

const resetFilters = () => {
  dateRange.value = []
  selectedPoints.value = []
  selectedMetrics.value = []
  selectedStatus.value = ''
  selectedTags.value = []
  tableSearch.value = ''
  currentPage.value = 1
  loadRecords()
}

const viewRecordDetail = (record) => {
  selectedRecord.value = record
  showDetailModal.value = true
}

const handleSelectionChange = (selection) => {
  selectedRecords.value = selection
}

const handleSortChange = ({ prop, order }) => {
  tableSort.value = { prop, order }
  loadRecords()
}

const handleTableSearch = () => {
  currentPage.value = 1
  loadRecords()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadRecords()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadRecords()
}

const handleAdd = () => {
  router.push('/batch-input')
}

const handleBatchUpload = () => {
  router.push('/batch-input')
}

const handleBatchDelete = async () => {
  if (!selectedRecords.value.length) {
    ElMessage.warning('请选择要删除的记录')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRecords.value.length} 条记录吗？`,
      '批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const recordIds = selectedRecords.value.map(record => record.id)
    await waterQualityApi.batchDeleteRecords(recordIds)
    
    ElMessage.success('批量删除成功')
    loadRecords()
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败: ' + (error.response?.data?.message || error.message))
    }
  }
}

const handleExport = async (format) => {
  try {
    loading.value = true
    
    // 构建导出参数
    const params = {
      format: format,
      ...buildFilterParams()
    }
    
    const response = await waterQualityApi.exportRecords(params)
    
    // 创建下载链接
    const blob = new Blob([response], { 
      type: format === 'pdf' ? 'application/pdf' : 
            format === 'excel' ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' :
            'text/csv'
    })
    
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `water_quality_records.${format}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success(`导出${format.toUpperCase()}格式成功`)
    
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

const editRecord = (record) => {
  router.push(`/batch-input/${record.id}`)
}

const deleteRecord = async (record) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条记录吗？',
      '删除记录',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await waterQualityApi.deleteRecord(record.id)
    ElMessage.success('删除成功')
    loadRecords()
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败: ' + (error.response?.data?.message || error.message))
    }
  }
}

const addRecordTag = (record) => {
  selectedRecord.value = record
  showTagDialog.value = true
}

const saveTag = async () => {
  if (!tagForm.type) {
    ElMessage.warning('请选择标签类型')
    return
  }
  
  try {
    const updatedRecord = {
      ...selectedRecord.value,
      tags: [...(selectedRecord.value.tags || []), tagForm.type]
    }
    
    await waterQualityApi.updateRecord(selectedRecord.value.id, updatedRecord)
    ElMessage.success('标签保存成功')
    showTagDialog.value = false
    tagForm.type = ''
    tagForm.note = ''
    loadRecords()
    
  } catch (error) {
    console.error('保存标签失败:', error)
    ElMessage.error('保存标签失败: ' + (error.response?.data?.message || error.message))
  }
}

const addNote = async () => {
  if (!newNote.value.trim()) {
    ElMessage.warning('请输入备注内容')
    return
  }
  
  try {
    const note = {
      content: newNote.value,
      author: 'current_user', // 应该从用户信息获取
      createdAt: new Date().toISOString()
    }
    
    const updatedRecord = {
      ...selectedRecord.value,
      notes: [...(selectedRecord.value.notes || []), note]
    }
    
    await waterQualityApi.updateRecord(selectedRecord.value.id, updatedRecord)
    ElMessage.success('备注添加成功')
    newNote.value = ''
    selectedRecord.value = updatedRecord
    
  } catch (error) {
    console.error('添加备注失败:', error)
    ElMessage.error('添加备注失败: ' + (error.response?.data?.message || error.message))
  }
}

const saveSubscribe = () => {
  // 保存订阅逻辑
  ElMessage.success('订阅设置保存成功')
  showSubscribeDialog.value = false
}

// 工具方法
const buildFilterParams = () => {
  const params = {}
  
  if (dateRange.value && dateRange.value.length === 2) {
    params.date_after = dateRange.value[0].toISOString().split('T')[0]
    params.date_before = dateRange.value[1].toISOString().split('T')[0]
  }
  
  if (selectedPoints.value.length > 0) {
    params.point_id = selectedPoints.value.join(',')
  }
  
  if (selectedStatus.value) {
    params.status = selectedStatus.value
  }
  
  if (tableSearch.value) {
    params.search = tableSearch.value
  }
  
  return params
}

// 工具方法
const getStatusText = (status) => {
  const statusMap = {
    normal: '正常',
    warning: '警告',
    danger: '超标'
  }
  return statusMap[status] || status
}

const getStatusTagType = (status) => {
  const typeMap = {
    normal: 'success',
    warning: 'warning',
    danger: 'danger'
  }
  return typeMap[status] || 'info'
}

const getMetricClass = (value, metric) => {
  // 根据指标值和类型返回样式类
  return 'metric-normal'
}

const getTagType = (tag) => {
  const typeMap = {
    suspicious: 'danger',
    verified: 'success',
    pending: 'warning',
    anomaly: 'danger'
  }
  return typeMap[tag] || 'info'
}

const getTagText = (tag) => {
  const textMap = {
    suspicious: '可疑数据',
    verified: '已核实',
    pending: '待处理',
    anomaly: '异常'
  }
  return textMap[tag] || tag
}

const formatTime = (time) => {
  return new Date(time).toLocaleString()
}

const formatRecordTime = (time) => {
  return time
}

const getRecordClass = (record) => {
  return `record-${record.status}`
}

const getAbnormalMetrics = (record) => {
  // 返回异常指标
  return []
}

const selectTimelineDate = (date) => {
  selectedDate.value = date
  // 加载该日期的记录
}

const loadMoreDates = () => {
  // 加载更多日期
}

const previousMonth = () => {
  if (currentMonth.value === 1) {
    currentMonth.value = 12
    currentYear.value--
  } else {
    currentMonth.value--
  }
  generateCalendarDays()
}

const nextMonth = () => {
  if (currentMonth.value === 12) {
    currentMonth.value = 1
    currentYear.value++
  } else {
    currentMonth.value++
  }
  generateCalendarDays()
}

const selectCalendarDate = (date) => {
  selectedDate.value = date
  // 加载该日期的记录
}

const loadTimelineDates = () => {
  // 生成时间轴日期
  const dates = []
  const today = new Date()
  
  for (let i = 0; i < 7; i++) {
    const date = new Date(today)
    date.setDate(today.getDate() - i)
    
    const dateStr = date.toISOString().split('T')[0]
    const dayRecords = waterQualityRecords.value.filter(record => record.date === dateStr)
    
    let status = 'normal'
    if (dayRecords.some(record => record.status === 'danger')) {
      status = 'danger'
    } else if (dayRecords.some(record => record.status === 'warning')) {
      status = 'warning'
    }
    
    dates.push({
      value: dateStr,
      label: `${date.getMonth() + 1}/${date.getDate()}`,
      status: status,
      count: dayRecords.length
    })
  }
  
  timelineDates.value = dates
}

const generateCalendarDays = () => {
  // 生成日历天数
  const days = []
  const firstDay = new Date(currentYear.value, currentMonth.value - 1, 1)
  const lastDay = new Date(currentYear.value, currentMonth.value, 0)
  const startDate = new Date(firstDay)
  startDate.setDate(startDate.getDate() - firstDay.getDay())
  
  for (let i = 0; i < 42; i++) {
    const date = new Date(startDate)
    date.setDate(startDate.getDate() + i)
    const dateStr = date.toISOString().split('T')[0]
    const dayRecords = waterQualityRecords.value.filter(record => record.date === dateStr)
    
    let status = 'normal'
    if (dayRecords.some(record => record.status === 'danger')) {
      status = 'danger'
    } else if (dayRecords.some(record => record.status === 'warning')) {
      status = 'warning'
    }
    
    days.push({
      date: dateStr,
      day: date.getDate(),
      otherMonth: date.getMonth() !== currentMonth.value - 1,
      hasData: dayRecords.length > 0,
      status: status,
      records: dayRecords
    })
  }
  
  calendarDays.value = days
}

const initWaveChart = () => {
  if (!waveChartRef.value) return
  
  const chart = echarts.init(waveChartRef.value)
  const option = {
    title: {
      text: `${waveMetric.value} 波形图`
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00']
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: [7.2, 7.3, 7.1, 7.4, 7.5, 9.2, 7.8, 7.6, 7.4, 7.3],
      type: 'line',
      smooth: true,
      markPoint: {
        data: [{
          name: '异常点',
          value: 9.2,
          xAxis: 5,
          yAxis: 9.2
        }]
      }
    }]
  }
  
  chart.setOption(option)
  
  chart.on('click', (params) => {
    selectedWavePoint.value = {
      point_id: 'P-042',
      time: params.name,
      value: params.value,
      status: params.value > 8.5 ? 'danger' : 'normal'
    }
  })
}

const updateWaveChart = () => {
  initWaveChart()
}

const initQualityCharts = () => {
  // 初始化质量看板图表
}

const getProgressColor = (percentage) => {
  if (percentage >= 95) return '#67c23a'
  if (percentage >= 85) return '#e6a23c'
  return '#f56c6c'
}

const getDifferenceClass = (value) => {
  if (Math.abs(value) < 0.1) return 'difference-small'
  if (Math.abs(value) < 0.5) return 'difference-medium'
  return 'difference-large'
}

const calculateDifference = (metric) => {
  const records = selectedCompareRecords.value
  if (records.length < 2) return 0
  
  const values = records.map(r => r[metric])
  return Math.max(...values) - Math.min(...values)
}

const updateCompareSelection = () => {
  // 更新对比选择
}

const removeCompareRecord = (index) => {
  compareRecords.value.splice(index, 1)
}

const generateCompareReport = () => {
  ElMessage.success('对比报告生成中...')
}

const exportCompareResult = () => {
  ElMessage.success('导出对比结果...')
}

const viewMissingRecords = () => {
  ElMessage.info('查看缺失记录')
}

const viewAnomalyRecords = () => {
  ElMessage.info('查看异常记录')
}

const navigateRecord = (direction) => {
  // 导航到上一条/下一条记录
}

const hasPrevRecord = computed(() => {
  // 检查是否有上一条记录
  return false
})

const hasNextRecord = computed(() => {
  // 检查是否有下一条记录
  return false
})

const clearSnapshot = () => {
  currentSnapshot.value = null
  resetFilters()
}

// 生命周期
onMounted(() => {
  loadRecords()
  generateCalendarDays()
  loadTimelineDates()
})
</script>

<style scoped>
.data-viewer-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.page-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.subtitle {
  font-size: 14px;
  color: #909399;
  font-weight: normal;
}

.view-switcher {
  display: flex;
  gap: 5px;
}

.snapshot-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.snapshot-left {
  display: flex;
  gap: 10px;
  align-items: center;
}

.snapshot-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.snapshot-name {
  font-weight: 500;
}

.snapshot-time {
  font-size: 12px;
  color: #909399;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.filter-group {
  display: flex;
  gap: 10px;
  align-items: center;
}

.filter-actions {
  display: flex;
  gap: 10px;
}

.main-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 20px;
  min-height: 600px;
}

/* 时间轴视图样式 */
.timeline-view {
  padding: 20px 0;
}

.timeline-header h3 {
  margin-bottom: 15px;
  color: #303133;
}

.timeline-dates {
  display: flex;
  gap: 10px;
  align-items: center;
  overflow-x: auto;
  padding: 10px 0;
}

.timeline-date {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  cursor: pointer;
  min-width: 80px;
  transition: all 0.3s;
}

.timeline-date:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.timeline-date.active {
  border-color: #409eff;
  background: #409eff;
  color: white;
}

.date-label {
  font-size: 12px;
  font-weight: 500;
}

.date-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 5px;
}

.date-indicator.normal {
  background: #67c23a;
}

.date-indicator.warning {
  background: #e6a23c;
}

.date-indicator.danger {
  background: #f56c6c;
}

.timeline-content {
  margin-top: 20px;
}

.timeline-records {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.timeline-record {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.timeline-record:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.record-time {
  font-size: 12px;
  color: #909399;
  min-width: 50px;
}

.record-point {
  font-weight: 500;
  min-width: 80px;
}

.record-metrics {
  display: flex;
  gap: 5px;
  flex: 1;
}

.metric-tag {
  padding: 2px 6px;
  background: #f56c6c;
  color: white;
  border-radius: 4px;
  font-size: 12px;
}

.record-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.record-status.normal {
  background: #f0f9ff;
  color: #409eff;
}

.record-status.warning {
  background: #fdf6ec;
  color: #e6a23c;
}

.record-status.danger {
  background: #fef0f0;
  color: #f56c6c;
}

/* 日历视图样式 */
.calendar-view {
  padding: 20px 0;
}

.calendar-header {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.calendar-grid {
  max-width: 600px;
  margin: 0 auto;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background: #dcdfe6;
  margin-bottom: 1px;
}

.weekday {
  padding: 10px;
  text-align: center;
  background: #f5f7fa;
  font-weight: 500;
  color: #606266;
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background: #dcdfe6;
}

.calendar-day {
  padding: 15px 5px;
  text-align: center;
  background: white;
  cursor: pointer;
  position: relative;
  min-height: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.calendar-day:hover {
  background: #f5f7fa;
}

.calendar-day.other-month {
  color: #c0c4cc;
}

.calendar-day.selected {
  background: #409eff;
  color: white;
}

.day-number {
  font-size: 14px;
  font-weight: 500;
}

.day-indicator {
  position: absolute;
  top: 5px;
  right: 5px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.day-indicator.normal {
  background: #67c23a;
}

.day-indicator.warning {
  background: #e6a23c;
}

.day-indicator.danger {
  background: #f56c6c;
}

.calendar-records {
  margin-top: 30px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 6px;
}

.day-records {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.day-record {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.day-record:hover {
  background: #f0f9ff;
}

/* 波形视图样式 */
.wave-view {
  padding: 20px 0;
}

.wave-controls {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.wave-chart-container {
  height: 400px;
  margin-bottom: 20px;
}

.wave-point-info {
  margin-top: 20px;
}

/* 表格视图样式 */
.table-view {
  padding: 20px 0;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.toolbar-left {
  display: flex;
  gap: 10px;
}

.toolbar-right {
  display: flex;
  gap: 10px;
}

.table-container {
  background: white;
  border-radius: 6px;
  overflow: hidden;
}

.table-pagination {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.metric-normal {
  color: #67c23a;
}

.metric-warning {
  color: #e6a23c;
}

.metric-danger {
  color: #f56c6c;
}

.record-tag {
  margin-right: 5px;
}

/* 对比视图样式 */
.compare-view {
  padding: 20px 0;
}

.compare-selector h4 {
  margin-bottom: 15px;
  color: #303133;
}

.compare-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.compare-card {
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  padding: 15px;
  transition: all 0.3s;
}

.compare-card.selected {
  border-color: #409eff;
  background: #f0f9ff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.record-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.compare-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.comparison-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 6px;
  overflow: hidden;
}

.comparison-table th,
.comparison-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #dcdfe6;
}

.comparison-table th {
  background: #f5f7fa;
  font-weight: 500;
  color: #606266;
}

.difference-small {
  color: #67c23a;
}

.difference-medium {
  color: #e6a23c;
}

.difference-large {
  color: #f56c6c;
}

/* 质量看板样式 */
.quality-view {
  padding: 20px 0;
}

.quality-overview {
  margin-bottom: 30px;
}

.quality-card {
  height: 120px;
}

.quality-item {
  text-align: center;
}

.quality-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
}

.quality-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 15px;
}

.online-status {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.status-item {
  font-size: 12px;
}

.quality-charts {
  margin-top: 30px;
}

.chart-header {
  margin-bottom: 20px;
}

.chart-container {
  height: 300px;
}

/* 记录详情样式 */
.record-detail {
  padding: 20px 0;
}

.record-notes {
  margin-top: 30px;
}

.record-notes h4 {
  margin-bottom: 15px;
  color: #303133;
}

.notes-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.note-item {
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.note-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 12px;
  color: #909399;
}

.note-content {
  color: #606266;
}

.record-actions {
  display: flex;
  gap: 10px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #dcdfe6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .viewer-header {
    flex-direction: column;
    gap: 15px;
  }
  
  .filter-bar {
    flex-direction: column;
    gap: 15px;
  }
  
  .filter-group {
    flex-wrap: wrap;
  }
  
  .timeline-dates {
    flex-wrap: nowrap;
    overflow-x: auto;
  }
  
  .compare-cards {
    grid-template-columns: 1fr;
  }
}
</style>
