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
  showLegend: {
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
      trigger: 'item',
      backgroundColor: isDark ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.9)',
      borderColor: isDark ? '#4C4D4F' : '#E4E7ED',
      textStyle: {
        color: isDark ? '#E5EAF3' : '#303133'
      },
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: props.showLegend ? {
      orient: 'vertical',
      left: 'left',
      textStyle: {
        color: isDark ? '#CFD3DC' : '#606266'
      }
    } : undefined,
    series: [
      {
        name: '报警统计',
        type: 'pie',
        radius: ['40%', '70%'],
        center: props.showLegend ? ['60%', '50%'] : ['50%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: isDark ? '#141414' : '#ffffff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold',
            color: isDark ? '#E5EAF3' : '#303133'
          }
        },
        labelLine: {
          show: false
        },
        data: props.data.length > 0 ? props.data : [
          { value: 0, name: '无报警' }
        ]
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
