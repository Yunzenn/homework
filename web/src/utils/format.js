import dayjs from 'dayjs'

/**
 * 格式化日期时间
 * @param {string|Date} datetime 日期时间
 * @param {string} format 格式化模板
 * @returns {string} 格式化后的日期时间
 */
export const formatDateTime = (datetime, format = 'YYYY-MM-DD HH:mm:ss') => {
  if (!datetime) return '-'
  return dayjs(datetime).format(format)
}

/**
 * 格式化日期
 * @param {string|Date} date 日期
 * @returns {string} 格式化后的日期
 */
export const formatDate = (date) => {
  return formatDateTime(date, 'YYYY-MM-DD')
}

/**
 * 格式化时间
 * @param {string|Date} time 时间
 * @returns {string} 格式化后的时间
 */
export const formatTime = (time) => {
  return formatDateTime(time, 'HH:mm:ss')
}

/**
 * 格式化数值，保留指定小数位数
 * @param {number} value 数值
 * @param {number} decimals 小数位数
 * @returns {string} 格式化后的数值
 */
export const formatNumber = (value, decimals = 2) => {
  if (value === null || value === undefined) return '-'
  return Number(value).toFixed(decimals)
}

/**
 * 格式化百分比
 * @param {number} value 数值
 * @param {number} decimals 小数位数
 * @returns {string} 格式化后的百分比
 */
export const formatPercent = (value, decimals = 1) => {
  if (value === null || value === undefined) return '-'
  return `${Number(value).toFixed(decimals)}%`
}

/**
 * 格式化文件大小
 * @param {number} bytes 字节数
 * @returns {string} 格式化后的文件大小
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 获取相对时间
 * @param {string|Date} datetime 日期时间
 * @returns {string} 相对时间描述
 */
export const getRelativeTime = (datetime) => {
  if (!datetime) return '-'
  
  const now = dayjs()
  const target = dayjs(datetime)
  const diff = now.diff(target, 'second')
  
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  if (diff < 2592000) return `${Math.floor(diff / 86400)}天前`
  
  return formatDate(datetime)
}

/**
 * 格式化水质指标值
 * @param {number} value 数值
 * @param {string} unit 单位
 * @param {number} decimals 小数位数
 * @returns {string} 格式化后的值
 */
export const formatWaterQualityValue = (value, unit = '', decimals = 2) => {
  if (value === null || value === undefined) return '-'
  const formattedValue = formatNumber(value, decimals)
  return unit ? `${formattedValue} ${unit}` : formattedValue
}

/**
 * 获取报警级别颜色
 * @param {string} level 报警级别
 * @returns {string} 颜色类名
 */
export const getAlertLevelColor = (level) => {
  const colorMap = {
    '正常': 'success',
    '警告': 'warning',
    '严重': 'danger'
  }
  return colorMap[level] || 'info'
}

/**
 * 获取水质状态颜色
 * @param {string} field 字段名
 * @param {number} value 数值
 * @param {object} thresholds 阈值配置
 * @returns {string} 颜色类名
 */
export const getWaterQualityStatusColor = (field, value, thresholds = {}) => {
  if (!thresholds[field]) return 'info'
  
  const threshold = thresholds[field]
  
  if (threshold.min !== undefined && value < threshold.min) {
    return 'danger'
  }
  if (threshold.max !== undefined && value > threshold.max) {
    const severity = value > threshold.max * 1.5 ? 'danger' : 'warning'
    return severity
  }
  
  return 'success'
}

/**
 * 格式化监测点ID
 * @param {string} pointId 监测点ID
 * @returns {string} 格式化后的监测点ID
 */
export const formatPointId = (pointId) => {
  if (!pointId) return '-'
  return pointId.replace('监测点', 'Point ')
}

/**
 * 生成随机颜色
 * @returns {string} 随机颜色
 */
export const getRandomColor = () => {
  const colors = [
    '#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399',
    '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
    '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#8dd3c7'
  ]
  return colors[Math.floor(Math.random() * colors.length)]
}
