<template>
  <div class="enhanced-animated-login-page">
    <!-- 动态背景效果 -->
    <div class="background-effect">
      <div class="water-bubble" v-for="i in 10" :key="i" :style="getBubbleStyle(i)"></div>
      <div class="wave-effect"></div>
      <div class="grid-pattern"></div>
    </div>

    <div class="login-container">
      <!-- 左侧多角色区域 -->
      <div class="character-section">
        <div class="brand-header">
          <div class="logo">
            <div class="logo-icon">💧</div>
            <h1 class="brand-name">水质监控系统</h1>
          </div>
          <p class="brand-subtitle">Professional Water Quality Monitoring</p>
        </div>

        <!-- 多角色场景 -->
        <div class="characters-scene" ref="sceneRef">
          <!-- 紫色角色 - 后层 -->
          <div 
            class="character purple-character" 
            :class="getCharacterClass('purple')"
            :style="getCharacterStyle('purple')"
          >
            <div class="character-body">
              <div class="eyes">
                <div class="eye" :class="{ 'blinking': purpleBlinking }">
                  <div class="pupil" :style="getPupilStyle('purple')"></div>
                </div>
                <div class="eye" :class="{ 'blinking': purpleBlinking }">
                  <div class="pupil" :style="getPupilStyle('purple')"></div>
                </div>
              </div>
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
              <div class="eyes">
                <div class="eye" :class="{ 'blinking': blackBlinking }">
                  <div class="pupil" :style="getPupilStyle('black')"></div>
                </div>
                <div class="eye" :class="{ 'blinking': blackBlinking }">
                  <div class="pupil" :style="getPupilStyle('black')"></div>
                </div>
              </div>
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
              <div class="eyes">
                <div class="eye" :class="{ 'blinking': orangeBlinking }">
                  <div class="pupil" :style="getPupilStyle('orange')"></div>
                </div>
                <div class="eye" :class="{ 'blinking': orangeBlinking }">
                  <div class="pupil" :style="getPupilStyle('orange')"></div>
                </div>
              </div>
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
              <div class="eyes">
                <div class="eye" :class="{ 'blinking': yellowBlinking }">
                  <div class="pupil" :style="getPupilStyle('yellow')"></div>
                </div>
                <div class="eye" :class="{ 'blinking': yellowBlinking }">
                  <div class="pupil" :style="getPupilStyle('yellow')"></div>
                </div>
              </div>
              <div class="mouth" :class="getMouthClass('yellow')"></div>
            </div>
          </div>
        </div>

        <!-- 互动提示 -->
        <div class="interaction-hint" v-if="showHint" :class="hintType">
          {{ hintMessage }}
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <div class="form-section">
        <div class="form-header">
          <h1 class="welcome-title">欢迎回来</h1>
          <p class="welcome-subtitle">智能水质监控 · 专业分析 · 决策支持</p>
        </div>

        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          @submit.prevent="handleLogin"
          class="login-form"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="用户名 / 邮箱 / 手机号"
              size="large"
              :prefix-icon="User"
              clearable
              @focus="handleInputFocus('username')"
              @blur="handleInputBlur"
              @input="handleInputChange"
              class="custom-input"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="密码"
              size="large"
              :prefix-icon="Lock"
              :suffix-icon="showPassword ? View : Hide"
              show-password
              @focus="handleInputFocus('password')"
              @blur="handleInputBlur"
              @input="handleInputChange"
              @click-suffix="togglePasswordVisibility"
              class="custom-input"
            />
          </el-form-item>

          <el-form-item>
            <div class="form-options">
              <el-checkbox v-model="loginForm.remember" class="custom-checkbox">
                记住密码（7天）
              </el-checkbox>
              <router-link to="/forgot-password" class="forgot-link">
                忘记密码？
              </router-link>
            </div>
          </el-form-item>

          <!-- 测试账号提示 -->
          <div class="test-account-hint">
            <el-alert
              title="测试账号"
              type="info"
              :closable="false"
              show-icon
            >
              <div class="test-account-info">
                <p><strong>用户名：</strong>admin</p>
                <p><strong>密码：</strong>admin123</p>
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="fillTestAccount"
                  style="margin-top: 8px;"
                >
                  一键填入
                </el-button>
              </div>
            </el-alert>
          </div>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="authStore.loading"
              @click="handleLogin"
              class="login-button"
            >
              <template v-if="!authStore.loading">
                <span class="button-text">立即登录</span>
                <el-icon class="button-icon"><Right /></el-icon>
              </template>
              <template v-else>
                <span>登录中...</span>
              </template>
            </el-button>
          </el-form-item>
        </el-form>

        <div class="form-footer">
          <p class="register-prompt">
            还没有账号？
            <router-link to="/register" class="register-link">
              立即注册
            </router-link>
          </p>
          
          <div class="social-login">
            <p class="social-title">其他登录方式</p>
            <div class="social-buttons">
              <el-button
                type="success"
                size="large"
                :icon="ChatLineRound"
                circle
                @click="handleWechatLogin"
                class="social-btn wechat-btn"
              />
              <el-button
                type="info"
                size="large"
                :icon="Monitor"
                circle
                @click="handleDingTalkLogin"
                class="social-btn dingtalk-btn"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 页面底部 -->
    <div class="page-footer">
      <div class="footer-links">
        <a href="#" class="footer-link">隐私政策</a>
        <span class="separator">|</span>
        <a href="#" class="footer-link">服务条款</a>
        <span class="separator">|</span>
        <a href="#" class="footer-link">联系我们</a>
      </div>
      <p class="copyright">&copy; 2026 水质监控系统. 保留所有权利.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  User, Lock, View, Hide, ChatLineRound, Monitor, Right 
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 引用
const loginFormRef = ref()
const sceneRef = ref()

// 表单数据
const loginForm = reactive({
  username: '',
  password: '',
  remember: false
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名/邮箱/手机号', trigger: 'blur' },
    { min: 3, message: '用户名长度至少3位', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
}

// 角色状态
const purpleBlinking = ref(false)
const blackBlinking = ref(false)
const orangeBlinking = ref(false)
const yellowBlinking = ref(false)

// 交互状态
const showPassword = ref(false)
const showHint = ref(false)
const hintMessage = ref('')
const hintType = ref('')

// 鼠标位置
const mousePosition = reactive({ x: 0, y: 0 })

// 角色位置配置
const characterPositions = {
  purple: { left: '60px', bottom: '0px', width: '160px', height: '380px' },
  black: { left: '200px', bottom: '0px', width: '100px', height: '280px' },
  orange: { left: '0px', bottom: '0px', width: '200px', height: '180px' },
  yellow: { left: '280px', bottom: '0px', width: '120px', height: '200px' }
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
let hintTimer = null
let idleTimer = null

// 当前输入字段
const currentInputField = ref('')

// 处理鼠标移动
const handleMouseMove = (e) => {
  mousePosition.x = e.clientX
  mousePosition.y = e.clientY
}

// 获取角色样式
const getCharacterStyle = (character) => {
  const baseStyle = { ...characterPositions[character] }
  
  // 根据输入状态调整样式
  if (currentInputField.value) {
    if (character === 'purple') {
      baseStyle.height = showPassword.value ? '440px' : '400px'
    } else if (character === 'black') {
      baseStyle.transform = showPassword.value 
        ? 'skewX(0deg) translateX(20px)' 
        : `skewX(${getSkewAngle()}deg) translateX(20px)`
    }
  } else if (showPassword.value && character === 'purple') {
    baseStyle.transform = 'skewX(0deg)'
  }
  
  return baseStyle
}

// 获取角色类名
const getCharacterClass = (character) => {
  const classes = []
  
  if (currentInputField.value) {
    classes.push('typing')
  }
  
  if (showPassword.value && character === 'purple') {
    classes.push('peeking')
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
  const centerY = rect.top + rect.height / 3
  
  const deltaX = mousePosition.x - centerX
  const deltaY = mousePosition.y - centerY
  
  // 计算瞳孔位置
  let x = 0, y = 0
  
  if (showPassword.value && character === 'purple') {
    // 紫色角色偷看时看向特定方向
    x = -4
    y = -4
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
  
  if (currentInputField.value) {
    classes.push('typing-mouth')
  }
  
  return classes.join(' ')
}

// 计算倾斜角度
const getSkewAngle = () => {
  return Math.random() * 10 - 5 // -5 到 5 度
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

// 显示提示消息
const showHintMessage = (message, type = 'info', duration = 2000) => {
  hintMessage.value = message
  hintType.value = type
  showHint.value = true
  
  if (hintTimer) {
    clearTimeout(hintTimer)
  }
  
  hintTimer = setTimeout(() => {
    showHint.value = false
  }, duration)
}

// 检查是否为开发环境
const isDevelopment = computed(() => {
  return import.meta.env.DEV
})

// 填入测试账号
const fillTestAccount = () => {
  loginForm.username = 'admin'
  loginForm.password = 'admin123'
  loginForm.remember = true
  showHintMessage('已填入测试账号，点击登录即可', 'success')
}

// 处理输入框聚焦
const handleInputFocus = (field) => {
  currentInputField.value = field
  showHintMessage('角色正在关注你的输入~', 'info')
  resetIdleTimer()
  startIdleTimer()
}

// 处理输入框失焦
const handleInputBlur = () => {
  currentInputField.value = ''
  showHintMessage('角色在休息中...', 'info')
  startIdleTimer()
}

// 处理输入
const handleInputChange = () => {
  if (currentInputField.value) {
    showHintMessage('角色在认真听你输入~', 'typing')
  }
  resetIdleTimer()
}

// 切换密码可见性
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
  showHintMessage(showPassword.value ? '哇！密码可见了！' : '密码已隐藏', 'surprised')
  
  setTimeout(() => {
    if (currentInputField.value) {
      showHintMessage('角色在关注你的输入~', 'info')
    } else {
      showHintMessage('角色在休息中...', 'info')
    }
  }, 1000)
}

// 重置空闲定时器
const resetIdleTimer = () => {
  if (idleTimer) {
    clearTimeout(idleTimer)
  }
}

// 开始空闲定时器
const startIdleTimer = () => {
  resetIdleTimer()
  idleTimer = setTimeout(() => {
    showHintMessage('角色在打哈欠...好困~', 'sleepy')
  }, 30000) // 30秒无操作
}

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    const valid = await loginFormRef.value.validate()
    if (!valid) return

    showHintMessage('角色在为你加油！', 'success')

    const result = await authStore.login(loginForm)
    
    if (result.success) {
      showHintMessage('太棒了！登录成功！', 'success')
      
      // 检查是否为测试账号
      if (result.data?.is_test_account) {
        ElMessage({
          message: '登录成功！（测试账号）',
          type: 'success',
          duration: 3000
        })
      } else {
        ElMessage.success('登录成功！')
      }
      
      // 获取重定向路径，默认跳转到主界面
      const redirectPath = router.currentRoute.value.query.redirect || '/dashboard'
      
      setTimeout(() => {
        router.push(redirectPath)
      }, 1500)
    } else {
      showHintMessage('呜呜...登录失败，再试一次吧', 'error')
      ElMessage.error(result.error || '用户名或密码错误')
      
      setTimeout(() => {
        showHintMessage('角色在休息中...', 'info')
      }, 2000)
    }
  } catch (error) {
    showHintMessage('哎呀！网络错误，请重试', 'error')
    ElMessage.error('登录失败，请重试')
    
    setTimeout(() => {
      showHintMessage('角色在休息中...', 'info')
    }, 2000)
  }
}

// 处理社交登录
const handleWechatLogin = () => {
  showHintMessage('角色对微信登录很感兴趣！', 'info')
  ElMessage.info('微信登录功能开发中...')
  setTimeout(() => {
    showHintMessage('角色在休息中...', 'info')
  }, 1500)
}

const handleDingTalkLogin = () => {
  showHintMessage('角色对钉钉登录很好奇！', 'info')
  ElMessage.info('钉钉登录功能开发中...')
  setTimeout(() => {
    showHintMessage('角色在休息中...', 'info')
  }, 1500)
}

// 获取气泡样式
const getBubbleStyle = (index) => {
  const size = Math.random() * 40 + 20
  const duration = Math.random() * 15 + 10
  const delay = Math.random() * 5
  
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${Math.random() * 100}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`,
    opacity: Math.random() * 0.3 + 0.1
  }
}

// 组件挂载
onMounted(() => {
  // 如果已经登录，直接跳转
  if (authStore.isAuthenticated) {
    router.push('/dashboard')
    return
  }

  // 监听鼠标移动
  document.addEventListener('mousemove', handleMouseMove)
  
  // 开始所有角色的眨眼动画
  startBlinking('purple')
  startBlinking('black')
  startBlinking('orange')
  startBlinking('yellow')
  
  // 开始空闲定时器
  startIdleTimer()
  
  // 显示欢迎提示
  setTimeout(() => {
    showHintMessage('欢迎回来！角色们在等你~', 'welcome')
  }, 1000)
})

// 组件卸载
onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove)
  
  // 清理所有定时器
  Object.keys(blinkTimers).forEach(character => {
    stopBlinking(character)
  })
  
  if (hintTimer) {
    clearTimeout(hintTimer)
  }
  
  if (idleTimer) {
    clearTimeout(idleTimer)
  }
})
</script>

<style scoped>
.enhanced-animated-login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #1890ff 0%, #6ab7ff 100%);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* 动态背景效果 */
.background-effect {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 1;
}

.water-bubble {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  animation: float-up linear infinite;
  backdrop-filter: blur(2px);
}

@keyframes float-up {
  0% {
    transform: translateY(100vh) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 0.4;
  }
  90% {
    opacity: 0.4;
  }
  100% {
    transform: translateY(-100px) rotate(360deg);
    opacity: 0;
  }
}

.wave-effect {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100px;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M0,50 Q25,30 50,50 T100,50 L100,100 L0,100 Z" fill="rgba(255,255,255,0.05)"/></svg>');
  background-size: 200px 100px;
  animation: wave 10s linear infinite;
}

@keyframes wave {
  0% { background-position-x: 0; }
  100% { background-position-x: 200px; }
}

.grid-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
  opacity: 0.3;
}

/* 主容器 */
.login-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  position: relative;
  z-index: 2;
}

/* 左侧角色区域 */
.character-section {
  flex: 0 0 45%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  min-height: 500px;
  max-height: 600px;
  position: relative;
  padding-top: 20px;
}

.brand-header {
  text-align: center;
  margin-bottom: 20px;
  margin-top: 0;
  position: relative;
  z-index: 10;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 15px;
  margin-bottom: 8px;
  margin-left: -40px;
  margin-top: 10px;
}

.logo-icon {
  font-size: 48px;
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.brand-name {
  font-size: 32px;
  font-weight: 700;
  color: white;
  margin: 0;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.brand-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  font-style: italic;
}

.characters-scene {
  position: relative;
  width: 500px;
  height: 350px;
  margin: 10px auto 20px auto;
  overflow: hidden;
}

/* 角色基础样式 */
.character {
  position: absolute;
  transition: all 0.7s ease-in-out;
  transform-origin: bottom center;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
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

/* 黑色角色 */
.black-character {
  background: #2D2D2D;
  border-radius: 8px 8px 0 0;
}

.black-character.typing {
  transform: skewX(15deg) translateX(20px);
}

/* 橙色角色 */
.orange-character {
  background: #FF9B6B;
  border-radius: 120px 120px 0 0;
}

.orange-character.typing {
  transform: skewX(0deg);
}

/* 黄色角色 */
.yellow-character {
  background: #E8D754;
  border-radius: 70px 70px 0 0;
}

.yellow-character.typing {
  transform: skewX(0deg);
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
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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

/* 互动提示 */
.interaction-hint {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 255, 255, 0.95);
  color: #1890ff;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  animation: hint-bounce 0.5s ease-out;
  white-space: nowrap;
  border: 2px solid transparent;
  z-index: 100;
}

.interaction-hint.info {
  border-color: #1890ff;
  color: #1890ff;
}

.interaction-hint.success {
  border-color: #10b981;
  color: #10b981;
}

.interaction-hint.error {
  border-color: #ef4444;
  color: #ef4444;
}

.interaction-hint.surprised {
  border-color: #f59e0b;
  color: #f59e0b;
}

.interaction-hint.sleepy {
  border-color: #6b7280;
  color: #6b7280;
}

.interaction-hint.welcome {
  border-color: #8b5cf6;
  color: #8b5cf6;
}

/* 测试账号提示 */
.test-account-hint {
  margin-bottom: 20px;
}

.test-account-info p {
  margin: 8px 0;
  font-size: 14px;
}

.test-account-info strong {
  color: #409EFF;
  font-family: 'Courier New', monospace;
}

@keyframes hint-bounce {
  0% { transform: translateY(20px); opacity: 0; }
  100% { transform: translateY(0); opacity: 1; }
}

/* 右侧表单区域 */
.form-section {
  flex: 0 0 55%;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 50px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 500px;
  margin-left: 40px;
  position: relative;
  overflow: hidden;
}

.form-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #1890ff, #6ab7ff);
}

.form-header {
  text-align: center;
  margin-bottom: 40px;
}

.welcome-title {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 12px 0;
  background: linear-gradient(135deg, #1890ff, #6ab7ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
  opacity: 0.8;
}

.login-form {
  margin-bottom: 30px;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
}

:deep(.custom-input .el-input__wrapper) {
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.8);
}

:deep(.custom-input .el-input__wrapper:hover) {
  box-shadow: 0 8px 25px rgba(24, 144, 255, 0.15);
  transform: translateY(-2px);
}

:deep(.custom-input .el-input__wrapper.is-focus) {
  box-shadow: 0 8px 30px rgba(24, 144, 255, 0.25);
  border-color: #1890ff;
  transform: translateY(-2px);
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

:deep(.custom-checkbox .el-checkbox__label) {
  color: #64748b;
  font-weight: 500;
}

.forgot-link {
  color: #1890ff;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.3s ease;
}

.forgot-link:hover {
  color: #40a9ff;
}

.login-button {
  width: 100%;
  height: 52px;
  font-size: 18px;
  font-weight: 600;
  border-radius: 16px;
  background: linear-gradient(135deg, #1890ff, #6ab7ff);
  border: none;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.login-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.login-button:hover::before {
  left: 100%;
}

.login-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(24, 144, 255, 0.4);
}

.login-button:active {
  transform: translateY(-1px);
}

.button-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.button-icon {
  transition: transform 0.3s ease;
}

.login-button:hover .button-icon {
  transform: translateX(4px);
}

.form-footer {
  text-align: center;
}

.register-prompt {
  font-size: 14px;
  color: #64748b;
  margin: 0 0 24px 0;
}

.register-link {
  color: #1890ff;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.3s ease;
}

.register-link:hover {
  color: #40a9ff;
}

.social-login {
  border-top: 1px solid #e5e7eb;
  padding-top: 24px;
}

.social-title {
  font-size: 13px;
  color: #9ca3af;
  margin: 0 0 16px 0;
  text-align: center;
}

.social-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.social-btn {
  width: 48px;
  height: 48px;
  transition: all 0.3s ease;
  position: relative;
}

.social-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: all 0.3s ease;
}

.social-btn:hover::before {
  width: 100%;
  height: 100%;
}

.social-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

/* 页面底部 */
.page-footer {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
  z-index: 2;
}

.footer-links {
  margin-bottom: 8px;
}

.footer-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-size: 12px;
  transition: color 0.3s ease;
  margin: 0 8px;
}

.footer-link:hover {
  color: white;
}

.separator {
  color: rgba(255, 255, 255, 0.6);
  margin: 0 4px;
}

.copyright {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .login-container {
    flex-direction: column;
    padding: 20px;
  }
  
  .character-section {
    flex: none;
    margin-bottom: 15px;
    min-height: 250px;
    max-height: 300px;
  }
  
  .brand-header {
    margin-top: 0;
    margin-bottom: 15px;
  }
  
  .characters-scene {
    width: 100%;
    max-width: 350px;
    height: 250px;
    margin: 0 auto 10px auto;
  }
}

@media (max-width: 768px) {
  .login-container {
    padding: 16px;
  }
  
  .form-section {
    padding: 30px 20px;
    border-radius: 20px;
  }
  
  .welcome-title {
    font-size: 28px;
  }
  
  .login-button {
    height: 48px;
    font-size: 16px;
  }
  
  .social-buttons {
    gap: 12px;
  }
  
  .social-btn {
    width: 44px;
    height: 44px;
  }
  
  .characters-scene {
    transform: scale(0.7);
  }
}

@media (max-width: 480px) {
  .form-section {
    padding: 24px 16px;
  }
  
  .welcome-title {
    font-size: 24px;
  }
  
  .login-button {
    height: 44px;
    font-size: 15px;
  }
  
  .form-options {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .interaction-hint {
    bottom: 5px;
    font-size: 11px;
    padding: 6px 12px;
  }
}

/* 测试账号提示样式 */
.test-account-hint {
  margin: 16px 0;
}

.test-account-info p {
  margin: 4px 0;
  font-size: 14px;
}

.test-account-info .el-button {
  width: 100%;
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .form-section {
    background: rgba(31, 41, 55, 0.95);
    color: #f9fafb;
  }
  
  .welcome-title {
    color: #f9fafb;
  }
  
  .welcome-subtitle,
  .register-prompt {
    color: #9ca3af;
  }
  
  :deep(.custom-input .el-input__wrapper) {
    background: rgba(55, 65, 81, 0.8);
    color: #f9fafb;
  }
  
  .social-title {
    color: #6b7280;
  }
}

/* 性能优化 */
.login-button,
.social-btn,
.water-bubble {
  will-change: transform;
}

.character {
  will-change: transform;
}

.pupil {
  will-change: transform;
}

/* 无障碍支持 */
@media (prefers-reduced-motion: reduce) {
  .water-bubble,
  .wave-effect,
  .login-button::before,
  .social-btn::before {
    animation: none;
  }
  
  .login-button:hover,
  .social-btn:hover {
    transform: none;
  }
  
  .character {
    transition: none;
  }
  
  .pupil {
    transition: none;
  }
}
</style>
