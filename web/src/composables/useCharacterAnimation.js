import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'

/**
 * 角色动画管理 Hook
 * 提供角色状态管理、眼睛跟随、表情变化等功能
 */
export function useCharacterAnimation() {
  // 角色状态
  const characterState = ref('idle')
  const isAnimating = ref(false)
  
  // 眼睛位置
  const eyePosition = reactive({ x: 0, y: 0 })
  const pupilPosition = reactive({ 
    left: { x: 0, y: 0 }, 
    right: { x: 0, y: 0 } 
  })
  
  // 鼠标位置
  const mousePosition = reactive({ x: 0, y: 0 })
  
  // 动画定时器
  let idleTimer = null
  let blinkTimer = null
  let animationFrame = null
  
  // 状态配置
  const stateConfig = {
    idle: {
      duration: 3000,
      nextStates: ['focusing', 'typing', 'surprised', 'sleepy'],
      animations: ['breathe', 'blink']
    },
    focusing: {
      duration: 0,
      nextStates: ['idle', 'typing', 'surprised'],
      animations: ['focus']
    },
    typing: {
      duration: 0,
      nextStates: ['idle', 'focusing', 'surprised'],
      animations: ['typing-bounce']
    },
    surprised: {
      duration: 800,
      nextStates: ['idle', 'focusing'],
      animations: ['surprise']
    },
    success: {
      duration: 1500,
      nextStates: ['idle'],
      animations: ['success-bounce', 'hearts']
    },
    error: {
      duration: 2000,
      nextStates: ['idle'],
      animations: ['shake']
    },
    sleepy: {
      duration: 0,
      nextStates: ['idle', 'focusing'],
      animations: ['sleepy-sway', 'yawn']
    }
  }
  
  // 设置角色状态
  const setCharacterState = (newState) => {
    if (characterState.value === newState) return
    
    const currentState = characterState.value
    const currentConfig = stateConfig[currentState]
    const newConfig = stateConfig[newState]
    
    // 检查状态转换是否合法
    if (!newConfig.nextStates.includes(currentState) && currentState !== 'idle') {
      console.warn(`Invalid state transition: ${currentState} -> ${newState}`)
      return
    }
    
    characterState.value = newState
    isAnimating.value = true
    
    // 触发状态变化动画
    triggerStateAnimation(newState)
    
    // 自动状态恢复
    if (newConfig.duration > 0) {
      setTimeout(() => {
        if (characterState.value === newState) {
          setCharacterState('idle')
        }
      }, newConfig.duration)
    }
  }
  
  // 触发状态动画
  const triggerStateAnimation = (state) => {
    const character = document.querySelector('.water-drop-character')
    if (!character) return
    
    // 移除所有状态类
    Object.keys(stateConfig).forEach(stateName => {
      character.classList.remove(stateName)
    })
    
    // 添加新状态类
    nextTick(() => {
      character.classList.add(state)
    })
  }
  
  // 更新眼睛位置
  const updateEyePosition = (containerRef) => {
    if (!containerRef || characterState.value === 'sleepy') return
    
    const rect = containerRef.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2
    
    // 计算鼠标相对于角色中心的位置
    const deltaX = mousePosition.x - centerX
    const deltaY = mousePosition.y - centerY
    
    // 限制瞳孔移动范围
    const maxPupilOffset = 4
    const maxEyeOffset = 3
    
    // 瞳孔位置（更精确的跟随）
    pupilPosition.left.x = Math.max(-maxPupilOffset, Math.min(maxPupilOffset, deltaX / 20))
    pupilPosition.left.y = Math.max(-maxPupilOffset, Math.min(maxPupilOffset, deltaY / 20))
    pupilPosition.right.x = Math.max(-maxPupilOffset, Math.min(maxPupilOffset, deltaX / 20))
    pupilPosition.right.y = Math.max(-maxPupilOffset, Math.min(maxPupilOffset, deltaY / 20))
    
    // 眼睛容器位置（更轻微的跟随）
    eyePosition.x = Math.max(-maxEyeOffset, Math.min(maxEyeOffset, deltaX / 30))
    eyePosition.y = Math.max(-maxEyeOffset, Math.min(maxEyeOffset, deltaY / 30))
  }
  
  // 处理鼠标移动
  const handleMouseMove = (e) => {
    mousePosition.x = e.clientX
    mousePosition.y = e.clientY
  }
  
  // 眨眼动画
  const blink = () => {
    const eyelids = document.querySelectorAll('.eyelid')
    if (!eyelids.length) return
    
    eyelids.forEach(eyelid => {
      eyelid.style.transition = 'opacity 0.15s ease-in-out'
      eyelid.style.opacity = '1'
      
      setTimeout(() => {
        eyelid.style.opacity = '0'
      }, 150)
    })
  }
  
  // 开始眨眼定时器
  const startBlinking = () => {
    const scheduleNextBlink = () => {
      const interval = Math.random() * 3000 + 2000 // 2-5秒
      blinkTimer = setTimeout(scheduleNextBlink, interval)
    }
    
    // 立即眨眼一次
    blink()
    scheduleNextBlink()
  }
  
  // 重置空闲定时器
  const resetIdleTimer = () => {
    if (idleTimer) {
      clearTimeout(idleTimer)
      idleTimer = null
    }
  }
  
  // 开始空闲定时器
  const startIdleTimer = () => {
    resetIdleTimer()
    idleTimer = setTimeout(() => {
      setCharacterState('sleepy')
    }, 30000) // 30秒无操作
  }
  
  // 处理输入框聚焦
  const handleInputFocus = (field) => {
    setCharacterState('focusing')
    resetIdleTimer()
  }
  
  // 处理输入框失焦
  const handleInputBlur = () => {
    setCharacterState('idle')
    startIdleTimer()
  }
  
  // 处理输入
  const handleInputChange = () => {
    setCharacterState('typing')
    resetIdleTimer()
  }
  
  // 处理密码可见性切换
  const handlePasswordToggle = () => {
    setCharacterState('surprised')
  }
  
  // 处理登录成功
  const handleLoginSuccess = () => {
    setCharacterState('success')
  }
  
  // 处理登录失败
  const handleLoginError = () => {
    setCharacterState('error')
  }
  
  // 获取状态文字
  const getStateText = (state) => {
    const stateTexts = {
      idle: '😊 我在这里等你',
      focusing: '👀 专注中...',
      typing: '⌨️ 正在输入...',
      surprised: '😳 哇！',
      success: '🎉 太棒了！',
      error: '😢 呜呜...',
      sleepy: '😴 好困...'
    }
    return stateTexts[state] || stateTexts.idle
  }
  
  // 获取当前状态文字
  const getCurrentStateText = () => {
    return getStateText(characterState.value)
  }
  
  // 初始化
  const initialize = (containerRef) => {
    // 监听鼠标移动
    document.addEventListener('mousemove', handleMouseMove)
    
    // 开始眨眼动画
    startBlinking()
    
    // 开始空闲定时器
    startIdleTimer()
    
    // 开始眼睛跟随动画循环
    const animate = () => {
      updateEyePosition(containerRef)
      animationFrame = requestAnimationFrame(animate)
    }
    animate()
  }
  
  // 清理
  const cleanup = () => {
    document.removeEventListener('mousemove', handleMouseMove)
    
    if (idleTimer) {
      clearTimeout(idleTimer)
    }
    
    if (blinkTimer) {
      clearTimeout(blinkTimer)
    }
    
    if (animationFrame) {
      cancelAnimationFrame(animationFrame)
    }
  }
  
  // 生命周期管理
  onMounted(() => {
    // 组件挂载时的初始化逻辑
  })
  
  onUnmounted(() => {
    cleanup()
  })
  
  return {
    // 状态
    characterState,
    isAnimating,
    eyePosition,
    pupilPosition,
    mousePosition,
    
    // 方法
    setCharacterState,
    triggerStateAnimation,
    updateEyePosition,
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
    getStateText,
    getCurrentStateText,
    initialize,
    cleanup
  }
}

/**
 * 眼睛跟随 Hook
 * 专门处理眼睛跟随鼠标的逻辑
 */
export function useEyeTracking() {
  const eyePosition = reactive({ x: 0, y: 0 })
  const pupilPosition = reactive({ 
    left: { x: 0, y: 0 }, 
    right: { x: 0, y: 0 } 
  })
  
  const mousePosition = reactive({ x: 0, y: 0 })
  
  // 计算眼睛跟随位置
  const calculateEyeFollow = (containerRef, mouseX, mouseY) => {
    if (!containerRef) return { left: { x: 0, y: 0 }, right: { x: 0, y: 0 } }
    
    const rect = containerRef.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2
    
    // 计算角度和距离
    const deltaX = mouseX - centerX
    const deltaY = mouseY - centerY
    const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY)
    
    // 限制瞳孔移动范围
    const maxOffset = 4
    const factor = Math.min(1, maxOffset / (distance / 10))
    
    return {
      left: {
        x: Math.max(-maxOffset, Math.min(maxOffset, deltaX * factor / 20)),
        y: Math.max(-maxOffset, Math.min(maxOffset, deltaY * factor / 20))
      },
      right: {
        x: Math.max(-maxOffset, Math.min(maxOffset, deltaX * factor / 20)),
        y: Math.max(-maxOffset, Math.min(maxOffset, deltaY * factor / 20))
      }
    }
  }
  
  // 更新眼睛位置
  const updateEyes = (containerRef) => {
    const positions = calculateEyeFollow(containerRef, mousePosition.x, mousePosition.y)
    
    pupilPosition.left = positions.left
    pupilPosition.right = positions.right
    
    // 眼睛容器轻微移动
    eyePosition.x = Math.max(-3, Math.min(3, (mousePosition.x - containerRef.getBoundingClientRect().left - containerRef.offsetWidth / 2) / 30))
    eyePosition.y = Math.max(-2, Math.min(2, (mousePosition.y - containerRef.getBoundingClientRect().top - containerRef.offsetHeight / 2) / 30))
  }
  
  return {
    eyePosition,
    pupilPosition,
    mousePosition,
    calculateEyeFollow,
    updateEyes
  }
}

/**
 * 表单动画 Hook
 * 处理表单相关的动画效果
 */
export function useFormAnimation() {
  const formState = ref('idle')
  const isFormAnimating = ref(false)
  
  // 表单状态配置
  const formStates = {
    idle: { animations: ['form-idle'] },
    focusing: { animations: ['form-focus'] },
    error: { animations: ['form-error', 'shake'] },
    success: { animations: ['form-success', 'pulse'] }
  }
  
  // 设置表单状态
  const setFormState = (newState) => {
    if (formState.value === newState) return
    
    formState.value = newState
    isFormAnimating.value = true
    
    triggerFormAnimation(newState)
  }
  
  // 触发表单动画
  const triggerFormAnimation = (state) => {
    const form = document.querySelector('.login-form')
    if (!form) return
    
    // 移除所有状态类
    Object.keys(formStates).forEach(stateName => {
      form.classList.remove(`form-${stateName}`)
    })
    
    // 添加新状态类
    nextTick(() => {
      form.classList.add(`form-${state}`)
    })
  }
  
  // 处理表单聚焦
  const handleFormFocus = () => {
    setFormState('focusing')
  }
  
  // 处理表单失焦
  const handleFormBlur = () => {
    setFormState('idle')
  }
  
  // 处理表单错误
  const handleFormError = () => {
    setFormState('error')
    setTimeout(() => {
      setFormState('idle')
    }, 500)
  }
  
  // 处理表单成功
  const handleFormSuccess = () => {
    setFormState('success')
  }
  
  return {
    formState,
    isFormAnimating,
    setFormState,
    triggerFormAnimation,
    handleFormFocus,
    handleFormBlur,
    handleFormError,
    handleFormSuccess
  }
}
