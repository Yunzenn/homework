<template>
  <div ref="chartRef" :style="{ width: '100%', height: height }"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { useAppStore } from '@/stores/app'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({})
  },
  height: {
    type: String,
    default: '400px'
  },
  title: {
    type: String,
    default: ''
  }
})

const chartRef = ref(null)
let chartInstance = null
const appStore = useAppStore()

// 水质指标配置
const indicators = [
  { name: 'pH值', min: 0, max: 14, unit: '', key: 'ph', color: '#5470c6' },
  { name: '余氯', min: 0, max: 5, unit: 'mg/L', key: 'chlorine', color: '#91cc75' },
  { name: '浊度', min: 0, max: 10, unit: 'NTU', key: 'turbidity', color: '#fac858' },
  { name: '电导率', min: 0, max: 1500, unit: 'µS/cm', key: 'conductivity', color: '#ee6666' },
  { name: '氧化还原电位', min: 0, max: 1000, unit: 'mV', key: 'orp', color: '#73c0de' }
]

// 图表配置
const getChartOption = () => {
  const isDark = appStore.theme === 'dark'
  
  const series = indicators.map((indicator, index) => ({
    name: indicator.name,
    type: 'gauge',
    center: [
      (index % 3) * 33 + 16.5 + '%',
      Math.floor(index / 3) * 50 + 25 + '%'
    ],
    radius: index < 3 ? '25%' : '20%',
    min: indicator.min,
    max: indicator.max,
    splitNumber: 5,
    axisLine: {
      lineStyle: {
        width: 8,
        color: [
          [0.3, '#ff4757'],
          [0.7, '#ffa502'],
          [1, '#26de81']
        ]
      }
    },
    pointer: {
      itemStyle: {
        color: indicator.color
      }
    },
    axisTick: {
      distance: -30,
      length: 8,
      lineStyle: {
        color: isDark ? '#4C4D4F' : '#E4E7ED',
        width: 2
      }
    },
    splitLine: {
      distance: -30,
      length: 30,
      lineStyle: {
        color: isDark ? '#4C4D4F' : '#E4E7ED',
        width: 4
      }
    },
    axisLabel: {
      color: isDark ? '#A3A6AD' : '#909399',
      distance: 40,
      fontSize: 12
    },
    detail: {
      valueAnimation: true,
      formatter: function (value) {
        return `{value|${value}}{unit|${indicator.unit}}`
      },
      rich: {
        value: {
          fontSize: 16,
          fontWeight: 'bolder',
          color: isDark ? '#E5EAF3' : '#303133'
        },
        unit: {
          fontSize: 12,
          color: isDark ? '#A3A6AD' : '#909399',
          padding: [0, 0, 0, 4]
        }
      }
    },
    data: [
      {
        value: props.data[indicator.key] || 0,
        name: indicator.name
      }
    ]
  }))

  return {
    title: {
      text: props.title,
      left: 'center',
      top: 0,
      textStyle: {
        color: isDark ? '#E5EAF3' : '#303133',
        fontSize: 16,
        fontWeight: 600
      }
    },
    tooltip: {
      trigger: 'item',
      backgroundColor: isDark ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.9)',
      borderColor: isDark ? '#4C4D4F' : '#E4E7ED',
      textStyle: {
        color: isDark ? '#E5EAF3' : '#303133'
      }
    },
    series: series
  }
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return
  
  chartInstance = echarts.init(chartRef.value)
  chartInstance.setOption(getChartOption())
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
}

// 更新图表
const updateChart = () => {
  if (!chartInstance) return
  
  chartInstance.setOption(getChartOption(), true)
}

// 处理窗口大小变化
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// 监听数据变化
watch(() => props.data, () => {
  nextTick(() => {
    updateChart()
  })
}, { deep: true })

// 监听主题变化
watch(() => appStore.theme, () => {
  nextTick(() => {
    updateChart()
  })
})

onMounted(() => {
  nextTick(() => {
    initChart()
  })
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style lang="scss" scoped>
// 图表容器样式
</style>
