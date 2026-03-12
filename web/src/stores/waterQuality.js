import { defineStore } from 'pinia'
import { waterQualityApi } from '@/api/waterQuality'

export const useWaterQualityStore = defineStore('waterQuality', {
  state: () => ({
    analysisData: [],
    pointAnalysis: [],
    overview: {
      totalRecords: 0,
      totalPoints: 0,
      alertCount: 0,
      recordsChange: 0,
      pointsChange: 0,
      alertsChange: 0,
      completenessRate: 0,
      completenessChange: 0
    },
    loading: false
  }),

  getters: {
    getAnalysisData: (state) => state.analysisData,
    getPointAnalysis: (state) => state.pointAnalysis,
    getOverview: (state) => state.overview,
    isLoading: (state) => state.loading
  },

  actions: {
    async fetchAnalysisData(dateRange) {
      try {
        this.loading = true
        
        // 获取时间范围内的数据
        const params = {}
        if (dateRange && dateRange.length === 2) {
          params.date_after = dateRange[0].toISOString().split('T')[0]
          params.date_before = dateRange[1].toISOString().split('T')[0]
        }
        
        const response = await waterQualityApi.getRecords(params)
        const records = response.results || response
        
        this.analysisData = records
        
        // 计算概览数据
        this.calculateOverview(records)
        
        // 计算监测点分析
        this.calculatePointAnalysis(records)
        
      } catch (error) {
        console.error('获取分析数据失败:', error)
        
        // 使用模拟数据
        const mockRecords = this.generateMockData()
        this.analysisData = mockRecords
        this.calculateOverview(mockRecords)
        this.calculatePointAnalysis(mockRecords)
        
      } finally {
        this.loading = false
      }
    },

    calculateOverview(records) {
      const totalRecords = records.length
      const totalPoints = [...new Set(records.map(r => r.point_id))].length
      
      // 预警阈值
      const alertThresholds = {
        chlorine: { min: 0.5, max: 4.0 },
        conductivity: { max: 1000 },
        ph: { min: 6.5, max: 8.5 },
        orp: { min: 400 },
        turbidity: { max: 5.0 }
      }
      
      const alertRecords = records.filter(r => {
        return r.chlorine < alertThresholds.chlorine.min || r.chlorine > alertThresholds.chlorine.max ||
               r.conductivity > alertThresholds.conductivity.max ||
               r.ph < alertThresholds.ph.min || r.ph > alertThresholds.ph.max ||
               r.orp < alertThresholds.orp.min ||
               r.turbidity > alertThresholds.turbidity.max
      })
      
      const alertCount = alertRecords.length
      const completenessRate = totalRecords > 0 ? Math.round((totalRecords - alertRecords.length) / totalRecords * 100) : 100
      
      // 模拟历史数据对比
      const previousData = this.getPreviousPeriodData()
      
      this.overview = {
        totalRecords,
        totalPoints,
        alertCount,
        recordsChange: totalRecords - previousData.records,
        pointsChange: totalPoints - previousData.points,
        alertsChange: alertCount - previousData.alerts,
        completenessRate,
        completenessChange: completenessRate - previousData.completeness
      }
    },

    calculatePointAnalysis(records) {
      const pointGroups = {}
      
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
          }
        }
        
        const group = pointGroups[record.point_id]
        group.records.push(record)
        group.chlorine.push(record.chlorine)
        group.conductivity.push(record.conductivity)
        group.ph.push(record.ph)
        group.orp.push(record.orp)
        group.turbidity.push(record.turbidity)
      })
      
      // 预警阈值
      const alertThresholds = {
        chlorine: { min: 0.5, max: 4.0 },
        conductivity: { max: 1000 },
        ph: { min: 6.5, max: 8.5 },
        orp: { min: 400 },
        turbidity: { max: 5.0 }
      }
      
      // 计算每个监测点的统计数据
      const analysis = Object.values(pointGroups).map(group => {
        const alertRecords = group.records.filter(r => {
          return r.chlorine < alertThresholds.chlorine.min || r.chlorine > alertThresholds.chlorine.max ||
                 r.conductivity > alertThresholds.conductivity.max ||
                 r.ph < alertThresholds.ph.min || r.ph > alertThresholds.ph.max ||
                 r.orp < alertThresholds.orp.min ||
                 r.turbidity > alertThresholds.turbidity.max
        })
        
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
        }
      })
      
      this.pointAnalysis = analysis
    },

    getPreviousPeriodData() {
      // 模拟历史数据
      return {
        records: Math.floor(Math.random() * 20) + 10,
        points: Math.floor(Math.random() * 3) + 2,
        alerts: Math.floor(Math.random() * 5) + 1,
        completeness: Math.floor(Math.random() * 10) + 80
      }
    },

    generateMockData() {
      const points = ['监测点001', '监测点002', '监测点003', '监测点004', '监测点005']
      const records = []
      const now = new Date()
      
      // 生成最近7天的数据
      for (let i = 0; i < 7; i++) {
        const date = new Date(now)
        date.setDate(date.getDate() - i)
        const dateStr = date.toISOString().split('T')[0]
        
        points.forEach(point => {
          // 每天生成3-5条记录
          const recordCount = Math.floor(Math.random() * 3) + 3
          for (let j = 0; j < recordCount; j++) {
            const hour = Math.floor(Math.random() * 24)
            const minute = Math.floor(Math.random() * 60)
            const time = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
            
            records.push({
              record_id: records.length + 1,
              point_id: point,
              date: dateStr,
              time: time,
              chlorine: Number((Math.random() * 4 + 0.5).toFixed(2)),
              conductivity: Number((Math.random() * 800 + 200).toFixed(2)),
              ph: Number((Math.random() * 2 + 6.5).toFixed(2)),
              orp: Number((Math.random() * 400 + 400).toFixed(2)),
              turbidity: Number((Math.random() * 4 + 0.5).toFixed(2))
            })
          }
        })
      }
      
      return records
    },

    clearData() {
      this.analysisData = []
      this.pointAnalysis = []
      this.overview = {
        totalRecords: 0,
        totalPoints: 0,
        alertCount: 0,
        recordsChange: 0,
        pointsChange: 0,
        alertsChange: 0,
        completenessRate: 0,
        completenessChange: 0
      }
    }
  }
})
