<template>
  <div class="forgot-password-page">
    <div class="forgot-password-container">
      <div class="forgot-password-header">
        <div class="logo">
          <el-icon size="40" color="#409EFF">
            <HotWater />
          </el-icon>
          <h1>水质监控系统</h1>
        </div>
        <p class="subtitle">重置您的密码，重新获得账户访问权限</p>
      </div>

      <div class="forgot-password-form">
        <h2 class="form-title">忘记密码</h2>
        <p class="form-subtitle">请输入您的邮箱地址，我们将发送重置链接给您</p>

        <el-form
          ref="forgotFormRef"
          :model="forgotForm"
          :rules="forgotRules"
          @submit.prevent="handleSubmit"
        >
          <el-form-item prop="email">
            <el-input
              v-model="forgotForm.email"
              placeholder="请输入注册时使用的邮箱地址"
              size="large"
              :prefix-icon="Message"
              clearable
              @keyup.enter="handleSubmit"
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="authStore.loading"
              @click="handleSubmit"
              class="submit-button"
            >
              {{ authStore.loading ? '发送中...' : '发送重置链接' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="form-footer">
          <router-link to="/login" class="back-link">
            <el-icon><ArrowLeft /></el-icon>
            返回登录
          </router-link>
        </div>

        <!-- 帮助信息 -->
        <div class="help-section">
          <h3 class="help-title">
            <el-icon><QuestionFilled /></el-icon>
            需要帮助？
          </h3>
          <div class="help-content">
            <div class="help-item">
              <h4>📧 没有收到邮件？</h4>
              <ul>
                <li>请检查垃圾邮件文件夹</li>
                <li>确认邮箱地址是否正确</li>
                <li>等待几分钟后重试</li>
              </ul>
            </div>
            <div class="help-item">
              <h4>🔒 邮件链接过期？</h4>
              <p>重置链接有效期为24小时，过期后需要重新申请。</p>
            </div>
            <div class="help-item">
              <h4>📞 联系管理员</h4>
              <p>如果遇到问题，请联系系统管理员获取帮助。</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="forgot-password-footer">
      <p>&copy; 2026 水质监控系统. 保留所有权利.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  HotWater, Message, ArrowLeft, QuestionFilled 
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 表单引用
const forgotFormRef = ref()

// 表单数据
const forgotForm = reactive({
  email: ''
})

// 表单验证规则
const forgotRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ]
}

// 处理提交
const handleSubmit = async () => {
  if (!forgotFormRef.value) return

  try {
    const valid = await forgotFormRef.value.validate()
    if (!valid) return

    const result = await authStore.forgotPassword(forgotForm.email)
    
    if (result.success) {
      ElMessage.success({
        message: '重置链接已发送到您的邮箱，请查收',
        duration: 5000
      })
      
      // 延迟跳转到登录页面
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    } else {
      ElMessage.error(result.error)
    }
  } catch (error) {
    console.error('发送重置邮件失败:', error)
    ElMessage.error('发送失败，请重试')
  }
}
</script>

<style scoped>
.forgot-password-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
  position: relative;
}

.forgot-password-page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
  opacity: 0.3;
}

.forgot-password-container {
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

.forgot-password-header {
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

.forgot-password-form {
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
  margin: 0 0 30px 0;
  line-height: 1.5;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
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

.help-section {
  margin-top: 40px;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
}

.help-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.help-content {
  display: grid;
  gap: 20px;
}

.help-item {
  background: #f8fafc;
  padding: 16px;
  border-radius: 12px;
  border-left: 4px solid #667eea;
}

.help-item h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.help-item p {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin: 0;
}

.help-item ul {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin: 0;
  padding-left: 16px;
}

.help-item li {
  margin-bottom: 4px;
}

.forgot-password-footer {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
}

.forgot-password-footer p {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .forgot-password-page {
    padding: 16px;
  }
  
  .forgot-password-container {
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
  
  .help-content {
    grid-template-columns: 1fr;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .forgot-password-container {
    background: rgba(31, 41, 55, 0.95);
    color: #f9fafb;
  }
  
  .logo h1,
  .form-title,
  .help-title {
    color: #f9fafb;
  }
  
  .form-subtitle {
    color: #9ca3af;
  }
  
  .help-item {
    background: rgba(55, 65, 81, 0.5);
    border-left-color: #667eea;
  }
  
  .help-item h4 {
    color: #f9fafb;
  }
  
  .help-item p,
  .help-item ul {
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

.forgot-password-container {
  animation: fadeInUp 0.6s ease-out;
}

/* 成功状态动画 */
@keyframes successPulse {
  0% {
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  }
  50% {
    box-shadow: 0 20px 60px rgba(16, 185, 129, 0.3);
  }
  100% {
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  }
}

.success-animation {
  animation: successPulse 2s ease-in-out;
}
</style>
