<template>
  <div class="reset-password-page">
    <div class="reset-password-container">
      <div class="reset-password-header">
        <div class="logo">
          <el-icon size="40" color="#409EFF">
            <HotWater />
          </el-icon>
          <h1>水质监控系统</h1>
        </div>
        <p class="subtitle">设置新密码，保护您的账户安全</p>
      </div>

      <div class="reset-password-form">
        <h2 class="form-title">重置密码</h2>
        <p class="form-subtitle">请设置您的新密码</p>

        <el-form
          ref="resetFormRef"
          :model="resetForm"
          :rules="resetRules"
          @submit.prevent="handleSubmit"
        >
          <el-form-item prop="newPassword">
            <el-input
              v-model="resetForm.newPassword"
              type="password"
              placeholder="新密码"
              size="large"
              :prefix-icon="Lock"
              show-password
              @input="checkPasswordStrength"
            />
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <el-input
              v-model="resetForm.confirmPassword"
              type="password"
              placeholder="确认新密码"
              size="large"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>

          <!-- 密码强度指示器 -->
          <div class="password-strength" v-if="resetForm.newPassword">
            <div class="strength-label">密码强度：</div>
            <div class="strength-bar">
              <div 
                class="strength-fill" 
                :class="passwordStrength.class"
                :style="{ width: passwordStrength.width }"
              ></div>
            </div>
            <div class="strength-text" :class="passwordStrength.class">
              {{ passwordStrength.text }}
            </div>
          </div>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="authStore.loading"
              @click="handleSubmit"
              class="submit-button"
            >
              {{ authStore.loading ? '重置中...' : '确认重置' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="form-footer">
          <router-link to="/login" class="back-link">
            <el-icon><ArrowLeft /></el-icon>
            返回登录
          </router-link>
        </div>

        <!-- 密码要求提示 -->
        <div class="password-requirements">
          <h4 class="requirements-title">
            <el-icon><Lock /></el-icon>
            密码要求
          </h4>
          <ul class="requirements-list">
            <li :class="{ 'met': requirements.length }">
              <el-icon><Check v-if="requirements.length" /><Close v-else /></el-icon>
              至少8个字符
            </li>
            <li :class="{ 'met': requirements.uppercase }">
              <el-icon><Check v-if="requirements.uppercase" /><Close v-else /></el-icon>
              包含大写字母
            </li>
            <li :class="{ 'met': requirements.lowercase }">
              <el-icon><Check v-if="requirements.lowercase" /><Close v-else /></el-icon>
              包含小写字母
            </li>
            <li :class="{ 'met': requirements.number }">
              <el-icon><Check v-if="requirements.number" /><Close v-else /></el-icon>
              包含数字
            </li>
            <li :class="{ 'met': requirements.special }">
              <el-icon><Check v-if="requirements.special" /><Close v-else /></el-icon>
              包含特殊字符
            </li>
          </ul>
        </div>
      </div>
    </div>

    <div class="reset-password-footer">
      <p>&copy; 2026 水质监控系统. 保留所有权利.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  HotWater, Lock, ArrowLeft, Check, Close 
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 表单引用
const resetFormRef = ref()

// 表单数据
const resetForm = reactive({
  newPassword: '',
  confirmPassword: ''
})

// 密码强度
const passwordStrength = reactive({
  score: 0,
  width: '0%',
  text: '弱',
  class: 'weak'
})

// 密码要求检查
const requirements = reactive({
  length: false,
  uppercase: false,
  lowercase: false,
  number: false,
  special: false
})

// 重置token
const resetToken = ref('')

// 表单验证规则
const resetRules = {
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, max: 128, message: '密码长度在8-128个字符', trigger: 'blur' },
    { validator: validatePasswordStrength, trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validatePasswordMatch, trigger: 'blur' }
  ]
}

// 密码强度验证
function validatePasswordStrength(rule, value, callback) {
  if (!value) {
    callback()
    return
  }

  let score = 0
  
  // 更新密码要求检查
  requirements.length = value.length >= 8
  requirements.uppercase = /[A-Z]/.test(value)
  requirements.lowercase = /[a-z]/.test(value)
  requirements.number = /\d/.test(value)
  requirements.special = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(value)

  // 计算分数
  if (requirements.length) score += 1
  if (value.length >= 12) score += 1
  if (requirements.uppercase) score += 1
  if (requirements.lowercase) score += 1
  if (requirements.number) score += 1
  if (requirements.special) score += 1

  // 更新密码强度显示
  updatePasswordStrength(score)
  
  if (score < 3) {
    callback(new Error('密码强度太弱，请满足更多要求'))
  } else {
    callback()
  }
}

// 密码匹配验证
function validatePasswordMatch(rule, value, callback) {
  if (!value) {
    callback(new Error('请确认密码'))
  } else if (value !== resetForm.newPassword) {
    callback(new Error('两次密码输入不一致'))
  } else {
    callback()
  }
}

// 更新密码强度显示
function updatePasswordStrength(score) {
  passwordStrength.score = score
  
  if (score <= 2) {
    passwordStrength.width = '33%'
    passwordStrength.text = '弱'
    passwordStrength.class = 'weak'
  } else if (score <= 4) {
    passwordStrength.width = '66%'
    passwordStrength.text = '中'
    passwordStrength.class = 'medium'
  } else {
    passwordStrength.width = '100%'
    passwordStrength.text = '强'
    passwordStrength.class = 'strong'
  }
}

// 检查密码强度
const checkPasswordStrength = () => {
  if (!resetForm.newPassword) return

  // 更新密码要求检查
  requirements.length = resetForm.newPassword.length >= 8
  requirements.uppercase = /[A-Z]/.test(resetForm.newPassword)
  requirements.lowercase = /[a-z]/.test(resetForm.newPassword)
  requirements.number = /\d/.test(resetForm.newPassword)
  requirements.special = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(resetForm.newPassword)

  // 计算分数
  let score = 0
  if (requirements.length) score += 1
  if (resetForm.newPassword.length >= 12) score += 1
  if (requirements.uppercase) score += 1
  if (requirements.lowercase) score += 1
  if (requirements.number) score += 1
  if (requirements.special) score += 1

  updatePasswordStrength(score)
}

// 处理提交
const handleSubmit = async () => {
  if (!resetFormRef.value) return

  try {
    const valid = await resetFormRef.value.validate()
    if (!valid) return

    const result = await authStore.resetPassword(resetToken.value, resetForm.newPassword)
    
    if (result.success) {
      ElMessage.success('密码重置成功！请使用新密码登录')
      
      // 延迟跳转到登录页面
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    } else {
      ElMessage.error(result.error)
    }
  } catch (error) {
    console.error('重置密码失败:', error)
    ElMessage.error('重置失败，请重试')
  }
}

// 组件挂载时获取token
onMounted(() => {
  const token = route.query.token
  if (!token) {
    ElMessage.error('无效的重置链接')
    router.push('/forgot-password')
    return
  }
  
  resetToken.value = token
})
</script>

<style scoped>
.reset-password-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
  position: relative;
}

.reset-password-page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
  opacity: 0.3;
}

.reset-password-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px;
  width: 100%;
  max-width: 480px;
  position: relative;
  z-index: 1;
}

.reset-password-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 12px;
  margin-bottom: 8px;
  margin-left: -20px;
}

.logo h1 {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
  opacity: 0.8;
}

.reset-password-form {
  margin-bottom: 30px;
}

.form-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  text-align: center;
  margin: 0 0 8px 0;
}

.form-subtitle {
  font-size: 14px;
  color: #64748b;
  text-align: center;
  margin: 0 0 24px 0;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
  border-color: #667eea;
}

.password-strength {
  margin-top: -12px;
  margin-bottom: 16px;
  padding: 0 4px;
}

.strength-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.strength-bar {
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.strength-fill.weak {
  background: #ef4444;
  width: 33%;
}

.strength-fill.medium {
  background: #f59e0b;
  width: 66%;
}

.strength-fill.strong {
  background: #10b981;
  width: 100%;
}

.strength-text {
  font-size: 12px;
  margin-top: 4px;
  font-weight: 600;
}

.strength-text.weak {
  color: #ef4444;
}

.strength-text.medium {
  color: #f59e0b;
}

.strength-text.strong {
  color: #10b981;
}

.submit-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  transition: all 0.3s ease;
}

.submit-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.submit-button:active {
  transform: translateY(0);
}

.form-footer {
  text-align: center;
  margin-top: 24px;
}

.back-link {
  color: #667eea;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: color 0.3s ease;
}

.back-link:hover {
  color: #764ba2;
}

.password-requirements {
  margin-top: 30px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.requirements-title {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.requirements-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.requirements-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 6px;
  transition: color 0.3s ease;
}

.requirements-list li.met {
  color: #10b981;
}

.requirements-list .el-icon {
  font-size: 14px;
}

.requirements-list li:not(.met) .el-icon {
  color: #ef4444;
}

.requirements-list li.met .el-icon {
  color: #10b981;
}

.reset-password-footer {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
}

.reset-password-footer p {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .reset-password-page {
    padding: 16px;
  }
  
  .reset-password-container {
    padding: 30px 24px;
    border-radius: 16px;
  }
  
  .logo h1 {
    font-size: 24px;
  }
  
  .form-title {
    font-size: 20px;
  }
  
  .submit-button {
    height: 44px;
    font-size: 15px;
  }
  
  .password-requirements {
    padding: 16px;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .reset-password-container {
    background: rgba(31, 41, 55, 0.95);
    color: #f9fafb;
  }
  
  .logo h1,
  .form-title,
  .requirements-title {
    color: #f9fafb;
  }
  
  .form-subtitle {
    color: #9ca3af;
  }
  
  .password-requirements {
    background: rgba(55, 65, 81, 0.5);
    border-color: #374151;
  }
  
  .requirements-list li {
    color: #9ca3af;
  }
  
  .requirements-list li.met {
    color: #10b981;
  }
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.reset-password-container {
  animation: fadeInUp 0.6s ease-out;
}
</style>
