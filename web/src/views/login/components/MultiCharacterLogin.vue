<template>
  <div class="multi-character-container">
    <!-- 多个卡通角色 -->
    <div class="characters-scene" ref="sceneRef">
      <!-- 紫色角色 - 后层 -->
      <div 
        class="character purple-character" 
        :class="getCharacterClass('purple')"
        :style="getCharacterStyle('purple')"
      >
        <div class="character-body">
          <!-- 眼睛 -->
          <div class="eyes">
            <div class="eye" :class="{ 'blinking': purpleBlinking }">
              <div class="pupil" :style="getPupilStyle('purple')"></div>
            </div>
            <div class="eye" :class="{ 'blinking': purpleBlinking }">
              <div class="pupil" :style="getPupilStyle('purple')"></div>
            </div>
          </div>
          <!-- 嘴巴（简单线条） -->
          <div class="mouth" :class="getMouthClass('purple')"></div>
        </div>
      </div>

      <!-- 黑色角色 - 中层 -->
      <div 
        class="character black-character" 
        :class="getCharacterClass('black')"
        :style="getCharacterStyle('black')"
      >
        <div class="character-body">
          <!-- 眼睛 -->
          <div class="eyes">
            <div class="eye" :class="{ 'blinking': blackBlinking }">
              <div class="pupil" :style="getPupilStyle('black')"></div>
            </div>
            <div class="eye" :class="{ 'blinking': blackBlinking }">
              <div class="pupil" :style="getPupilStyle('black')"></div>
            </div>
          </div>
          <!-- 嘴巴 -->
          <div class="mouth" :class="getMouthClass('black')"></div>
        </div>
      </div>

      <!-- 橙色角色 - 前层 -->
      <div 
        class="character orange-character" 
        :class="getCharacterClass('orange')"
        :style="getCharacterStyle('orange')"
      >
        <div class="character-body">
          <!-- 眼睛 -->
          <div class="eyes">
            <div class="eye" :class="{ 'blinking': orangeBlinking }">
              <div class="pupil" :style="getPupilStyle('orange')"></div>
            </div>
            <div class="eye" :class="{ 'blinking': orangeBlinking }">
              <div class="pupil" :style="getPupilStyle('orange')"></div>
            </div>
          </div>
          <!-- 嘴巴 -->
          <div class="mouth" :class="getMouthClass('orange')"></div>
        </div>
      </div>

      <!-- 黄色角色 - 前层右侧 -->
      <div 
        class="character yellow-character" 
        :class="getCharacterClass('yellow')"
        :style="getCharacterStyle('yellow')"
      >
        <div class="character-body">
          <!-- 眼睛 -->
          <div class="eyes">
            <div class="eye" :class="{ 'blinking': yellowBlinking }">
              <div class="pupil" :style="getPupilStyle('yellow')"></div>
            </div>
            <div class="eye" :class="{ 'blinking': yellowBlinking }">
              <div class="pupil" :style="getPupilStyle('yellow')"></div>
            </div>
          </div>
          <!-- 嘴巴（水平线表示） -->
          <div class="mouth" :class="getMouthClass('yellow')"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'

// 鼠标位置
const mousePosition = reactive({ x: 0, y: 0 })

// 角色状态
const purpleBlinking = ref(false)
const blackBlinking = ref(false)
const orangeBlinking = ref(false)
const yellowBlinking = ref(false)

// 角色位置配置
const characterPositions = {
  purple: { left: '70px', bottom: '0px', width: '180px', height: '440px' },
  black: { left: '240px', bottom: '0px', width: '120px', height: '310px' },
  orange: { left: '0px', bottom: '0px', width: '240px', height: '200px' },
  yellow: { left: '310px', bottom: '0px', width: '140px', height: '230px' }
}

// 角色颜色配置
const characterColors = {
  purple: { bg: '#6C3FF5', eye: 'white', pupil: '#2D2D2D' },
  black: { bg: '#2D2D2D', eye: 'white', pupil: '#000000' },
  orange: { bg: '#FF9B6B', eye: 'white', pupil: '#2D2D2D' },
  yellow: { bg: '#E8D754', eye: 'white', pupil: '#2D2D2D' }
}

// 定时器
let blinkTimers = {}

// 处理鼠标移动
const handleMouseMove = (e) => {
  mousePosition.x = e.clientX
  mousePosition.y = e.clientY
}

// 获取角色样式
const getCharacterStyle = (character) => {
  const baseStyle = { ...characterPositions[character] }
  
  // 根据输入状态调整样式
  if (isTyping.value) {
    if (character === 'purple') {
      baseStyle.height = passwordVisible.value ? '440px' : '400px'
    } else if (character === 'black') {
      baseStyle.transform = passwordVisible.value 
        ? 'skewX(0deg) translateX(20px)' 
        : `skewX(${getSkewAngle()}deg) translateX(20px)`
    }
  } else if (passwordVisible.value && character === 'purple') {
    baseStyle.transform = 'skewX(0deg)'
  }
  
  return baseStyle
}

// 获取角色类名
const getCharacterClass = (character) => {
  const classes = []
  
  if (isTyping.value) {
    classes.push('typing')
  }
  
  if (passwordVisible.value && character === 'purple') {
    classes.push('peeking')
  }
  
  if (isLookingAtEachOther.value) {
    classes.push('looking-at-each-other')
  }
  
  return classes.join(' ')
}

// 获取瞳孔样式
const getPupilStyle = (character) => {
  const sceneRef = document.querySelector('.characters-scene')
  if (!sceneRef) return {}
  
  const characterEl = sceneRef.querySelector(`.${character}-character`)
  if (!characterEl) return {}
  
  const rect = characterEl.getBoundingClientRect()
  const centerX = rect.left + rect.width / 2
  const centerY = rect.top + rect.height / 3 // 眼睛大概在1/3高度
  
  const deltaX = mousePosition.x - centerX
  const deltaY = mousePosition.y - centerY
  
  // 计算瞳孔位置
  let x = 0, y = 0
  
  if (isTyping.value && passwordVisible.value && character === 'purple') {
    // 紫色角色偷看时看向特定方向
    x = character === 'purple' ? -4 : 0
    y = character === 'purple' ? -4 : 0
  } else if (isLookingAtEachOther.value) {
    // 互相看时
    if (character === 'purple' || character === 'black') {
      x = 3 // 向右看
    } else {
      x = -3 // 向左看
    }
    y = 4 // 稍微向上
  } else {
    // 正常跟随鼠标
    const distance = Math.min(Math.sqrt(deltaX * deltaX + deltaY * deltaY), 5)
    const angle = Math.atan2(deltaY, deltaX)
    x = Math.cos(angle) * distance
    y = Math.sin(angle) * distance
  }
  
  return {
    transform: `translate(${x}px, ${y}px)`,
    transition: 'transform 0.1s ease-out'
  }
}

// 获取嘴巴类名
const getMouthClass = (character) => {
  const classes = []
  
  if (isTyping.value) {
    classes.push('typing-mouth')
  }
  
  if (isLookingAtEachOther.value) {
    classes.push('happy-mouth')
  }
  
  return classes.join(' ')
}

// 状态变量
const isTyping = ref(false)
const passwordVisible = ref(false)
const isLookingAtEachOther = ref(false)

// 计算倾斜角度
const getSkewAngle = () => {
  return isLookingAtEachOther.value ? 15 : 0
}

// 开始眨眼动画
const startBlinking = (character) => {
  const scheduleBlink = () => {
    const interval = Math.random() * 4000 + 3000 // 3-7秒
    
    const blinkTimeout = setTimeout(() => {
      if (character === 'purple') purpleBlinking.value = true
      if (character === 'black') blackBlinking.value = true
      if (character === 'orange') orangeBlinking.value = true
      if (character === 'yellow') yellowBlinking.value = true
      
      setTimeout(() => {
        if (character === 'purple') purpleBlinking.value = false
        if (character === 'black') blackBlinking.value = false
        if (character === 'orange') orangeBlinking.value = false
        if (character === 'yellow') yellowBlinking.value = false
        
        scheduleBlink()
      }, 150)
    }, interval)
    
    blinkTimers[character] = blinkTimeout
  }
  
  scheduleBlink()
}

// 停止眨眼动画
const stopBlinking = (character) => {
  if (blinkTimers[character]) {
    clearTimeout(blinkTimers[character])
    delete blinkTimers[character]
  }
  
  if (character === 'purple') purpleBlinking.value = false
  if (character === 'black') blackBlinking.value = false
  if (character === 'orange') orangeBlinking.value = false
  if (character === 'yellow') yellowBlinking.value = false
}

// 暴露方法给父组件
const setTyping = (typing) => {
  isTyping.value = typing
}

const setPasswordVisible = (visible) => {
  passwordVisible.value = visible
}

const setLookingAtEachOther = (looking) => {
  isLookingAtEachOther.value = looking
}

// 组件挂载
onMounted(() => {
  document.addEventListener('mousemove', handleMouseMove)
  
  // 开始所有角色的眨眼动画
  startBlinking('purple')
  startBlinking('black')
  startBlinking('orange')
  startBlinking('yellow')
})

// 组件卸载
onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove)
  
  // 清理所有定时器
  Object.keys(blinkTimers).forEach(character => {
    stopBlinking(character)
  })
})

// 暴露方法
defineExpose({
  setTyping,
  setPasswordVisible,
  setLookingAtEachOther
})
</script>

<style scoped>
.multi-character-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.characters-scene {
  position: relative;
  width: 550px;
  height: 400px;
  margin: 0 auto;
}

/* 角色基础样式 */
.character {
  position: absolute;
  transition: all 0.7s ease-in-out;
  transform-origin: bottom center;
}

.character-body {
  width: 100%;
  height: 100%;
  position: relative;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* 紫色角色 */
.purple-character {
  background: #6C3FF5;
  border-radius: 10px 10px 0 0;
}

.purple-character.typing {
  height: 400px;
}

.purple-character.peeking {
  transform: skewX(0deg);
}

.purple-character.looking-at-each-other {
  transform: skewX(-12deg) translateX(40px);
}

/* 黑色角色 */
.black-character {
  background: #2D2D2D;
  border-radius: 8px 8px 0 0;
}

.black-character.typing {
  transform: skewX(15deg) translateX(20px);
}

.black-character.looking-at-each-other {
  transform: skewX(22.5deg) translateX(20px);
}

/* 橙色角色 */
.orange-character {
  background: #FF9B6B;
  border-radius: 120px 120px 0 0;
}

.orange-character.typing {
  transform: skewX(0deg);
}

.orange-character.looking-at-each-other {
  transform: skewX(-15deg);
}

/* 黄色角色 */
.yellow-character {
  background: #E8D754;
  border-radius: 70px 70px 0 0;
}

.yellow-character.typing {
  transform: skewX(0deg);
}

.yellow-character.looking-at-each-other {
  transform: skewX(15deg);
}

/* 眼睛样式 */
.eyes {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.eye {
  width: 16px;
  height: 16px;
  background: white;
  border-radius: 50%;
  position: relative;
  overflow: hidden;
}

.pupil {
  width: 8px;
  height: 8px;
  background: #2D2D2D;
  border-radius: 50%;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.eye.blinking {
  height: 2px;
}

.eye.blinking .pupil {
  display: none;
}

/* 嘴巴样式 */
.mouth {
  width: 20px;
  height: 4px;
  background: #2D2D2D;
  border-radius: 2px;
  transition: all 0.2s ease;
}

.mouth.typing-mouth {
  width: 16px;
  height: 4px;
}

.mouth.happy-mouth {
  width: 24px;
  height: 12px;
  border-radius: 0 0 12px 12px;
  background: transparent;
  border: 2px solid #2D2D2D;
  border-top: none;
}

/* 特殊效果 */
.character.typing .eyes {
  transform: translateY(-2px);
}

.character.looking-at-each-other .eyes {
  transform: translateY(-1px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .characters-scene {
    width: 100%;
    max-width: 400px;
    height: 300px;
  }
  
  .character {
    transform: scale(0.8);
  }
  
  .eyes {
    gap: 6px;
  }
  
  .eye {
    width: 14px;
    height: 14px;
  }
  
  .pupil {
    width: 6px;
    height: 6px;
  }
  
  .mouth {
    width: 16px;
    height: 3px;
  }
}

/* 动画优化 */
.character {
  will-change: transform;
}

.pupil {
  will-change: transform;
}

/* 无障碍支持 */
@media (prefers-reduced-motion: reduce) {
  .character {
    transition: none;
  }
  
  .pupil {
    transition: none;
  }
}
</style>
