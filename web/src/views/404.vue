<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <div class="error-message">页面不存在</div>
      <div class="error-description">
        抱歉，您访问的页面不存在或已被移除
      </div>
      <div class="error-actions">
        <el-button type="primary" @click="goHome">
          <el-icon><House /></el-icon>
          返回首页
        </el-button>
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回上页
        </el-button>
      </div>
    </div>
    
    <div class="illustration">
      <el-icon size="200" color="#c0c4cc">
        <DocumentDelete />
      </el-icon>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { House, ArrowLeft, DocumentDelete } from '@element-plus/icons-vue'

const router = useRouter()

const goHome = () => {
  router.push('/')
}

const goBack = () => {
  router.go(-1)
}
</script>

<style lang="scss" scoped>
.not-found-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--el-bg-color-page);
  padding: $spacing-lg;
  
  .not-found-content {
    text-align: center;
    margin-right: $spacing-xl;
    
    .error-code {
      font-size: 120px;
      font-weight: 700;
      color: var(--el-color-primary);
      line-height: 1;
      margin-bottom: $spacing-lg;
      text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .error-message {
      font-size: $font-size-extra-large;
      font-weight: 600;
      color: var(--el-text-color-primary);
      margin-bottom: $spacing-md;
    }
    
    .error-description {
      font-size: $font-size-base;
      color: var(--el-text-color-regular);
      margin-bottom: $spacing-xl;
      max-width: 400px;
    }
    
    .error-actions {
      display: flex;
      gap: $spacing-md;
      justify-content: center;
    }
  }
  
  .illustration {
    opacity: 0.3;
  }
}

// 响应式设计
@include respond-to(md) {
  .not-found-container {
    flex-direction: column;
    text-align: center;
    
    .not-found-content {
      margin-right: 0;
      margin-bottom: $spacing-lg;
    }
  }
}
</style>
