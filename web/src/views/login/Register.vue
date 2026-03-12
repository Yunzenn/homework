<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-header">
        <div class="logo">
          <el-icon size="40" color="#409EFF">
            <HotWater />
          </el-icon>
          <h1>水质监控系统</h1>
        </div>
        <p class="subtitle">创建您的账户，开始水质监控之旅</p>
      </div>

      <div class="register-form">
        <h2 class="form-title">用户注册</h2>
        <p class="form-subtitle">请填写以下信息完成注册</p>

        <el-form
          ref="registerFormRef"
          :model="registerForm"
          :rules="registerRules"
          @submit.prevent="handleRegister"
        >
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item prop="username">
                <el-input
                  v-model="registerForm.username"
                  placeholder="用户名"
                  size="large"
                  :prefix-icon="User"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="nickname">
                <el-input
                  v-model="registerForm.nickname"
                  placeholder="昵称（可选）"
                  size="large"
                  :prefix-icon="Avatar"
                  clearable
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item prop="email">
            <el-input
              v-model="registerForm.email"
              placeholder="邮箱地址"
              size="large"
              :prefix-icon="Message"
              clearable
            />
          </el-form-item>

          <el-form-item prop="phone">
            <el-input
              v-model="registerForm.phone"
              placeholder="手机号码（可选）"
              size="large"
              :prefix-icon="Phone"
              clearable
            />
          </el-form-item>

          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item prop="password">
                <el-input
                  v-model="registerForm.password"
                  type="password"
                  placeholder="密码"
                  size="large"
                  :prefix-icon="Lock"
                  show-password
                  @input="checkPasswordStrength"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="confirmPassword">
                <el-input
                  v-model="registerForm.confirmPassword"
                  type="password"
                  placeholder="确认密码"
                  size="large"
                  :prefix-icon="Lock"
                  show-password
                />
              </el-form-item>
            </el-col>
          </el-row>

          <!-- 密码强度指示器 -->
          <div class="password-strength" v-if="registerForm.password">
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
            <div class="agreement">
              <el-checkbox v-model="agreeToTerms">
                我已阅读并同意
                <a href="#" @click.prevent="showTerms" class="terms-link">《用户协议》</a>
                和
                <a href="#" @click.prevent="showPrivacy" class="terms-link">《隐私政策》</a>
              </el-checkbox>
            </div>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="authStore.loading"
              :disabled="!agreeToTerms"
              @click="handleRegister"
              class="register-button"
            >
              {{ authStore.loading ? '注册中...' : '立即注册' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="form-footer">
          <p>
            已有账号？
            <router-link to="/login" class="login-link">
              立即登录
            </router-link>
          </p>
        </div>
      </div>
    </div>

    <div class="register-footer">
      <p>&copy; 2026 水质监控系统. 保留所有权利.</p>
    </div>

    <!-- 用户协议对话框 -->
    <el-dialog
      v-model="termsDialogVisible"
      title="用户协议"
      width="600px"
      class="terms-dialog"
    >
      <div class="terms-content">
        <h3>1. 服务条款</h3>
        <p>欢迎使用水质监控系统。通过注册和使用本服务，您同意遵守以下条款...</p>
        
        <h3>2. 用户责任</h3>
        <p>用户应当保证提供的信息真实有效，不得利用系统进行违法活动...</p>
        
        <h3>3. 隐私保护</h3>
        <p>我们重视用户隐私，将按照相关法律法规保护您的个人信息...</p>
        
        <h3>4. 知识产权</h3>
        <p>本系统的所有内容均受知识产权法保护...</p>
      </div>
      <template #footer>
        <el-button @click="termsDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 隐私政策对话框 -->
    <el-dialog
      v-model="privacyDialogVisible"
      title="隐私政策"
      width="600px"
      class="privacy-dialog"
    >
      <div class="privacy-content">
        <h3>1. 信息收集</h3>
        <p>我们收集的信息类型包括：账户信息、使用数据、设备信息等...</p>
        
        <h3>2. 信息使用</h3>
        <p>收集的信息将用于：提供服务、改善用户体验、安全保障等...</p>
        
        <h3>3. 信息保护</h3>
        <p>我们采用行业标准的安全措施保护您的个人信息...</p>
        
        <h3>4. 信息共享</h3>
        <p>除法律要求外，我们不会向第三方分享您的个人信息...</p>
      </div>
      <template #footer>
        <el-button @click="privacyDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  User, Lock, Message, Phone, Avatar, HotWater 
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 表单引用
const registerFormRef = ref()

// 表单数据
const registerForm = reactive({
  username: '',
  nickname: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: ''
})

// 密码强度
const passwordStrength = reactive({
  score: 0,
  width: '0%',
  text: '弱',
  class: 'weak'
})

// 状态
const agreeToTerms = ref(false)
const termsDialogVisible = ref(false)
const privacyDialogVisible = ref(false)

// 表单验证规则
const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3-20个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  nickname: [
    { max: 50, message: '昵称长度不能超过50个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号码', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
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
  
  // 长度检查
  if (value.length >= 8) score += 1
  if (value.length >= 12) score += 1
  
  // 字符类型检查
  if (/[a-z]/.test(value)) score += 1
  if (/[A-Z]/.test(value)) score += 1
  if (/\d/.test(value)) score += 1
  if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(value)) score += 1

  // 更新密码强度显示
  updatePasswordStrength(score)
  
  if (score < 3) {
    callback(new Error('密码强度太弱，请包含大小写字母、数字和特殊字符'))
  } else {
    callback()
  }
}

// 密码匹配验证
function validatePasswordMatch(rule, value, callback) {
  if (!value) {
    callback(new Error('请确认密码'))
  } else if (value !== registerForm.password) {
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
  if (!registerForm.password) return
  
  let score = 0
  
  if (registerForm.password.length >= 8) score += 1
  if (registerForm.password.length >= 12) score += 1
  if (/[a-z]/.test(registerForm.password)) score += 1
  if (/[A-Z]/.test(registerForm.password)) score += 1
  if (/\d/.test(registerForm.password)) score += 1
  if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(registerForm.password)) score += 1

  updatePasswordStrength(score)
}

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return

  try {
    const valid = await registerFormRef.value.validate()
    if (!valid) return

    if (!agreeToTerms.value) {
      ElMessage.warning('请先阅读并同意用户协议和隐私政策')
      return
    }

    const result = await authStore.register(registerForm)
    
    if (result.success) {
      ElMessage.success('注册成功！请登录您的账户')
      router.push('/login')
    } else {
      ElMessage.error(result.error)
    }
  } catch (error) {
    console.error('注册失败:', error)
    ElMessage.error('注册失败，请重试')
  }
}

// 显示用户协议
const showTerms = () => {
  termsDialogVisible.value = true
}

// 显示隐私政策
const showPrivacy = () => {
  privacyDialogVisible.value = true
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
  position: relative;
}

.register-page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
  opacity: 0.3;
}

.register-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px;
  width: 100%;
  max-width: 520px;
  position: relative;
  z-index: 1;
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 8px;
}

.logo h1 {
  font-size: 28px;
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

.register-form {
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

.agreement {
  font-size: 14px;
  color: #64748b;
  line-height: 1.5;
}

.terms-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.3s ease;
}

.terms-link:hover {
  color: #764ba2;
  text-decoration: underline;
}

.register-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  transition: all 0.3s ease;
}

.register-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.register-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.register-button:active:not(:disabled) {
  transform: translateY(0);
}

.form-footer {
  text-align: center;
  margin-top: 24px;
}

.form-footer p {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.login-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.3s ease;
}

.login-link:hover {
  color: #764ba2;
}

.register-footer {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
}

.register-footer p {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

/* 对话框样式 */
:deep(.terms-dialog .el-dialog__body),
:deep(.privacy-dialog .el-dialog__body) {
  padding: 20px;
  max-height: 400px;
  overflow-y: auto;
}

.terms-content h3,
.privacy-content h3 {
  color: #1f2937;
  font-size: 16px;
  margin: 16px 0 8px 0;
}

.terms-content p,
.privacy-content p {
  color: #64748b;
  line-height: 1.6;
  margin: 0 0 16px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .register-page {
    padding: 16px;
  }
  
  .register-container {
    padding: 30px 24px;
    border-radius: 16px;
    max-width: 100%;
  }
  
  .logo h1 {
    font-size: 24px;
  }
  
  .form-title {
    font-size: 20px;
  }
  
  .register-button {
    height: 44px;
    font-size: 15px;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .register-container {
    background: rgba(31, 41, 55, 0.95);
    color: #f9fafb;
  }
  
  .logo h1,
  .form-title {
    color: #f9fafb;
  }
  
  .form-subtitle,
  .form-footer p,
  .agreement {
    color: #9ca3af;
  }
  
  .terms-content h3,
  .privacy-content h3 {
    color: #f9fafb;
  }
  
  .terms-content p,
  .privacy-content p {
    color: #9ca3af;
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

.register-container {
  animation: fadeInUp 0.6s ease-out;
}
</style>
