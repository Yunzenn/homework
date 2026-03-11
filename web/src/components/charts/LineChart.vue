<template>
  <div ref="chartRef" :style="{ width: '100%', height: height }"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { useAppStore } from '@/stores/app'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  height: {
    type: String,
    default: '400px'
  },
  title: {
    type: String,
    default: ''
  },
  smooth: {
    type: Boolean,
    default: true
  }
})

const chartRef = ref(null)
let chartInstance = null
const appStore = useAppStore()

// 图表配置
const getChartOption = () => {
  const isDark = appStore.theme === 'dark'
  
  return {
    title: {
      text: props.title,
      left: 'center',
      textStyle: {
        color: isDark ? '#E5EAF3' : '#303133',
        fontSize: 16,
        fontWeight: 600
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: isDark ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.9)',
      borderColor: isDark ? '#4C4D4F' : '#E4E7ED',
      textStyle: {
        color: isDark ? '#E5EAF3' : '#303133'
      },
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    legend: {
      data: ['余氯', '电导率', 'pH值', '氧化还原电位', '浊度'],
      top: 30,
      textStyle: {
        color: isDark ? '#CFD3DC' : '#606266'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: props.data.map(item => item.date || ''),
      axisLine: {
        lineStyle: {
          color: isDark ? '#4C4D4F' : '#E4E7ED'
        }
      },
      axisLabel: {
        color: isDark ? '#A3A6AD' : '#909399'
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '数值',
        position: 'left',
        axisLine: {
          lineStyle: {
            color: isDark ? '#4C4D4F' : '#E4E7ED'
          }
        },
        axisLabel: {
          color: isDark ? '#A3A6AD' : '#909399'
        },
        splitLine: {
          lineStyle: {
            color: isDark ? '#363637' : '#F2F6FC'
          }
        }
      }
    ],
    series: [
      {
        name: '余氯',
        type: 'line',
        smooth: props.smooth,
        data: props.data.map(item => item.chlorine || 0),
        itemStyle: { color: '#5470c6' },
        areaStyle: {
          opacity: 0.1
        }
      },
      {
        name: '电导率',
        type: 'line',
        smooth: props.smooth,
        data: props.data.map(item => (item.conductivity || 0) / 100), // 缩放显示
        itemStyle: { color: '#91cc75' },
        areaStyle: {
          opacity: 0.1
        }
      },
      {
        name: 'pH值',
        type: 'line',
        smooth: props.smooth,
        data: props.data.map(item => item.ph || 0),
        itemStyle: { color: '#fac858' },
        areaStyle: {
          opacity: 0.1
        }
      },
      {
        name: '氧化还原电位',
        type: 'line',
        smooth: props.smooth,
        data: props.data.map(item => (item.orp || 0) / 100), // 缩放显示
        itemStyle: { color: '#ee6666' },
        areaStyle: {
          opacity: 0.1
        }
      },
      {
        name: '浊度',
        type: 'line',
        smooth: props.smooth,
        data: props.data.map(item => item.turbidity || 0),
        itemStyle: { color: '#73c0de' },
        areaStyle: {
          opacity: 0.1
        }
      }
    ]
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
