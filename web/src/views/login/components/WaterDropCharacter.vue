<template>
  <div class="character-wrapper" ref="characterWrapper">
    <svg
      class="water-drop-character"
      :class="[characterState, { 'is-animating': isAnimating }]"
      width="200"
      height="200"
      viewBox="0 0 200 200"
    >
      <!-- 定义渐变和滤镜 -->
      <defs>
        <!-- 水滴渐变 -->
        <linearGradient id="waterGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#1890ff;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#6ab7ff;stop-opacity:1" />
        </linearGradient>
        
        <!-- 高光渐变 -->
        <radialGradient id="highlightGradient">
          <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0.8" />
          <stop offset="100%" style="stop-color:#ffffff;stop-opacity:0" />
        </radialGradient>
        
        <!-- 发光效果 -->
        <filter id="glow">
          <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
        
        <!-- 阴影滤镜 -->
        <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
          <feDropShadow dx="0" dy="4" stdDeviation="6" flood-opacity="0.2"/>
        </filter>
      </defs>
      
      <!-- 水滴主体 -->
      <g class="water-drop-body">
        <path
          d="M100,30 C100,30 120,60 120,90 C120,120 100,150 100,180 C100,150 80,120 80,90 C80,60 100,30 100,30 Z"
          fill="url(#waterGradient)"
          filter="url(#glow)"
          class="drop-shape"
        />
        
        <!-- 高光效果 -->
        <ellipse
          cx="85"
          cy="70"
          rx="15"
          ry="20"
          fill="url(#highlightGradient)"
          opacity="0.6"
          class="highlight"
        />
      </g>
      
      <!-- 眼睛容器 -->
      <g 
        class="eyes-container" 
        :transform="`translate(${eyePosition.x}, ${eyePosition.y})`"
      >
        <!-- 左眼 -->
        <g class="eye left-eye">
          <!-- 眼白 -->
          <ellipse 
            cx="75" 
            cy="85" 
            rx="12" 
            ry="15" 
            fill="white" 
            class="eye-white"
          />
          
          <!-- 瞳孔 -->
          <g class="pupil-group">
            <ellipse 
              cx="75" 
              cy="85" 
              rx="6" 
              ry="8" 
              fill="#333" 
              class="pupil"
              :transform="`translate(${pupilPosition.left.x}, ${pupilPosition.left.y})`"
            />
            
            <!-- 瞳孔高光 -->
            <ellipse
              cx="77"
              cy="83"
              rx="2"
              ry="3"
              fill="white"
              opacity="0.8"
              class="pupil-highlight"
            />
          </g>
          
          <!-- 眨眼覆盖 -->
          <ellipse 
            cx="75" 
            cy="85" 
            rx="12" 
            ry="15" 
            fill="url(#waterGradient)" 
            class="eyelid"
            opacity="0"
          />
        </g>
        
        <!-- 右眼 -->
        <g class="eye right-eye">
          <!-- 眼白 -->
          <ellipse 
            cx="125" 
            cy="85" 
            rx="12" 
            ry="15" 
            fill="white" 
            class="eye-white"
          />
          
          <!-- 瞳孔 -->
          <g class="pupil-group">
            <ellipse 
              cx="125" 
              cy="85" 
              rx="6" 
              ry="8" 
              fill="#333" 
              class="pupil"
              :transform="`translate(${pupilPosition.right.x}, ${pupilPosition.right.y})`"
            />
            
            <!-- 瞳孔高光 -->
            <ellipse
              cx="127"
              cy="83"
              rx="2"
              ry="3"
              fill="white"
              opacity="0.8"
              class="pupil-highlight"
            />
          </g>
          
          <!-- 眨眼覆盖 -->
          <ellipse 
            cx="125" 
            cy="85" 
            rx="12" 
            ry="15" 
            fill="url(#waterGradient)" 
            class="eyelid"
            opacity="0"
          />
        </g>
      </g>
      
      <!-- 嘴巴 -->
      <path 
        :d="mouthPath" 
        stroke="#333" 
        stroke-width="2" 
        fill="none"
        stroke-linecap="round"
        class="mouth"
      />
      
      <!-- 腮红（害羞/惊讶时） -->
      <g class="blushes">
        <ellipse 
          cx="60" 
          cy="110" 
          rx="15" 
          ry="10" 
          fill="#ffb3ba" 
          opacity="0" 
          class="blush left-blush" 
        />
        <ellipse 
          cx="140" 
          cy="110" 
          rx="15" 
          ry="10" 
          fill="#ffb3ba" 
          opacity="0" 
          class="blush right-blush" 
        />
      </g>
      
      <!-- 爱心动画（成功时） -->
      <g class="hearts" opacity="0">
        <path 
          d="M85,140 C85,140 80,135 75,135 C70,135 65,140 65,140 C65,140 70,145 75,145 C80,145 85,140 85,140 Z" 
          fill="#ff6b6b" 
          class="heart left-heart"
        />
        <path 
          d="M135,140 C135,140 130,135 125,135 C120,135 115,140 115,140 C115,140 120,145 125,145 C130,145 135,140 135,140 Z" 
          fill="#ff6b6b" 
          class="heart right-heart"
        />
      </g>
      
      <!-- 汗滴（失败时） -->
      <g class="sweat" opacity="0">
        <ellipse
          cx="145"
          cy="75"
          rx="3"
          ry="5"
          fill="#87ceeb"
          class="sweat-drop"
        />
      </g>
    </svg>
    
    <!-- 状态文字 -->
    <div class="character-status" :class="characterState">
      {{ statusText }}
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useCharacterAnimation } from '@/composables/useCharacterAnimation'

const props = defineProps({
  state: {
    type: String,
    default: 'idle'
  },
  autoBlink: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['stateChange', 'blink', 'click'])

// 引用
const characterWrapper = ref()

// 使用角色动画 Hook
const {
  characterState,
  isAnimating,
  eyePosition,
  pupilPosition,
  mousePosition,
  setCharacterState,
  blink,
  startBlinking,
  resetIdleTimer,
  startIdleTimer,
  handleInputFocus,
  handleInputBlur,
  handleInputChange,
  handlePasswordToggle,
  handleLoginSuccess,
  handleLoginError,
  getCurrentStateText,
  initialize,
  cleanup
} = useCharacterAnimation()

// 嘴巴路径
const mouthPath = computed(() => {
  const paths = {
    idle: 'M85,130 Q100,140 115,130',
    focusing: 'M80,130 Q100,135 120,130',
    typing: 'M85,125 Q100,130 115,125',
    surprised: 'M85,130 Q100,145 115,130',
    success: 'M85,135 Q100,145 115,135',
    error: 'M85,135 Q100,125 115,135',
    sleepy: 'M90,135 Q100,140 110,135'
  }
  return paths[characterState.value] || paths.idle
})

// 状态文字
const statusText = computed(() => {
  return getCurrentStateText()
})

// 监听外部状态变化
watch(() => props.state, (newState) => {
  if (newState && newState !== characterState.value) {
    setCharacterState(newState)
  }
}, { immediate: true })

// 监听状态变化，发送事件
watch(characterState, (newState) => {
  emit('stateChange', newState)
  
  // 根据状态触发相应的视觉效果
  triggerStateEffects(newState)
})

// 触发状态特效
const triggerStateEffects = (state) => {
  const character = characterWrapper.value?.querySelector('.water-drop-character')
  if (!character) return
  
  switch (state) {
    case 'success':
      triggerSuccessEffect()
      break
    case 'error':
      triggerErrorEffect()
      break
    case 'surprised':
      triggerSurprisedEffect()
      break
    case 'sleepy':
      triggerSleepyEffect()
      break
  }
}

// 成功特效
const triggerSuccessEffect = () => {
  const hearts = document.querySelectorAll('.heart')
  hearts.forEach((heart, index) => {
    setTimeout(() => {
      heart.style.animation = 'heart-float 1s ease-out forwards'
    }, index * 100)
  })
}

// 错误特效
const triggerErrorEffect = () => {
  const sweat = document.querySelector('.sweat')
  if (sweat) {
    sweat.style.opacity = '1'
    sweat.style.animation = 'sweat-drop 1s ease-in-out infinite'
  }
}

// 惊讶特效
const triggerSurprisedEffect = () => {
  const blushes = document.querySelectorAll('.blush')
  blushes.forEach(blush => {
    blush.style.opacity = '0.6'
    blush.style.transition = 'opacity 0.3s ease-in-out'
  })
  
  setTimeout(() => {
    blushes.forEach(blush => {
      blush.style.opacity = '0'
    })
  }, 800)
}

// 困倦特效
const triggerSleepyEffect = () => {
  const character = document.querySelector('.water-drop-character')
  if (character) {
    character.style.animation = 'sleepy-sway 2s ease-in-out infinite alternate'
  }
}

// 处理点击
const handleClick = () => {
  emit('click')
  // 点击时触发惊讶表情
  setCharacterState('surprised')
  setTimeout(() => {
    setCharacterState('idle')
  }, 800)
}

// 组件挂载
onMounted(() => {
  if (characterWrapper.value) {
    initialize(characterWrapper.value)
    
    // 添加点击事件
    characterWrapper.value.addEventListener('click', handleClick)
    
    // 开始自动眨眼
    if (props.autoBlink) {
      startBlinking()
    }
  }
})

// 组件卸载
onUnmounted(() => {
  cleanup()
  
  if (characterWrapper.value) {
    characterWrapper.value.removeEventListener('click', handleClick)
  }
})

// 暴露方法给父组件
defineExpose({
  setCharacterState,
  blink,
  handleInputFocus,
  handleInputBlur,
  handleInputChange,
  handlePasswordToggle,
  handleLoginSuccess,
  handleLoginError
})
</script>

<style scoped>
.character-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  cursor: pointer;
  user-select: none;
}

.water-drop-character {
  filter: drop-shadow(0 10px 30px rgba(0, 0, 0, 0.2));
  transition: all 0.3s ease;
  will-change: transform;
}

/* 角色状态样式 */
.water-drop-character.idle {
  animation: breathe 3s ease-in-out infinite;
}

.water-drop-character.focusing {
  transform: scale(1.05);
}

.water-drop-character.typing {
  animation: typing-bounce 0.5s ease-in-out infinite alternate;
}

.water-drop-character.surprised {
  transform: scale(1.1);
}

.water-drop-character.success {
  animation: success-bounce 1s ease-in-out;
}

.water-drop-character.error {
  animation: shake 0.5s ease-in-out;
}

.water-drop-character.sleepy {
  animation: sleepy-sway 2s ease-in-out infinite alternate;
}

/* 基础动画 */
@keyframes breathe {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}

@keyframes typing-bounce {
  0% { transform: translateY(0); }
  100% { transform: translateY(-3px); }
}

@keyframes success-bounce {
  0%, 100% { transform: scale(1) rotate(0deg); }
  25% { transform: scale(1.1) rotate(-5deg); }
  75% { transform: scale(1.1) rotate(5deg); }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

@keyframes sleepy-sway {
  0% { transform: rotate(-2deg); }
  100% { transform: rotate(2deg); }
}

/* 眼睛样式 */
.eyes-container {
  transition: transform 0.2s ease-out;
  will-change: transform;
}

.eye-white {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.pupil {
  transition: transform 0.15s ease-out;
  will-change: transform;
}

.eyelid {
  transition: opacity 0.15s ease-in-out;
}

/* 嘴巴样式 */
.mouth {
  transition: d 0.3s ease-in-out;
}

/* 特效样式 */
.blush {
  transition: opacity 0.3s ease-in-out;
}

.hearts {
  transition: opacity 0.3s ease-in-out;
}

.heart {
  transform-origin: center;
}

@keyframes heart-float {
  0% { 
    transform: translateY(0) scale(0); 
    opacity: 0; 
  }
  50% { 
    transform: translateY(-15px) scale(1); 
    opacity: 1; 
  }
  100% { 
    transform: translateY(-30px) scale(0.8); 
    opacity: 0; 
  }
}

.sweat {
  transition: opacity 0.3s ease-in-out;
}

@keyframes sweat-drop {
  0% { 
    transform: translateY(0); 
    opacity: 0.6; 
  }
  100% { 
    transform: translateY(10px); 
    opacity: 0; 
  }
}

/* 高光效果 */
.highlight {
  animation: shimmer 3s ease-in-out infinite;
}

@keyframes shimmer {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 0.8; }
}

/* 状态文字 */
.character-status {
  text-align: center;
  font-size: 16px;
  font-weight: 600;
  color: white;
  background: rgba(255, 255, 255, 0.2);
  padding: 8px 16px;
  border-radius: 20px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  margin-top: 20px;
  min-width: 120px;
}

.character-status.idle {
  background: rgba(24, 144, 255, 0.2);
}

.character-status.focusing {
  background: rgba(106, 183, 255, 0.3);
}

.character-status.typing {
  background: rgba(24, 144, 255, 0.25);
}

.character-status.surprised {
  background: rgba(255, 179, 186, 0.3);
}

.character-status.success {
  background: rgba(16, 185, 129, 0.3);
}

.character-status.error {
  background: rgba(239, 68, 68, 0.3);
}

.character-status.sleepy {
  background: rgba(156, 163, 175, 0.3);
}

/* 悬停效果 */
.character-wrapper:hover .water-drop-character {
  transform: scale(1.05);
  filter: drop-shadow(0 15px 40px rgba(0, 0, 0, 0.25));
}

/* 点击效果 */
.character-wrapper:active .water-drop-character {
  transform: scale(0.95);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .water-drop-character {
    width: 160px;
    height: 160px;
  }
  
  .character-status {
    font-size: 14px;
    padding: 6px 12px;
    min-width: 100px;
  }
}

/* 性能优化 */
.water-drop-character {
  will-change: transform;
}

.eyes-container {
  will-change: transform;
}

.pupil {
  will-change: transform;
}

/* 无障碍支持 */
@media (prefers-reduced-motion: reduce) {
  .water-drop-character,
  .eyes-container,
  .pupil,
  .mouth,
  .character-status {
    animation: none;
    transition: none;
  }
}
</style>
