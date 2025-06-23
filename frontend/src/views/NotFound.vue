<template>
  <div class="not-found">
    <div class="not-found-container">
      <div class="error-image">
        <div class="error-number">404</div>
        <div class="error-illustration">
          <div class="magnifying-glass">
            <div class="handle"></div>
            <div class="lens"></div>
          </div>
        </div>
      </div>
      
      <div class="error-content">
        <h1>页面未找到</h1>
        <p>抱歉，您访问的页面不存在或已被移动。</p>
        <p>请检查URL是否正确，或返回首页重新开始。</p>
        
        <div class="action-buttons">
          <el-button type="primary" size="large" @click="goHome">
            <el-icon><HomeFilled /></el-icon>
            返回首页
          </el-button>
          <el-button size="large" @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回上页
          </el-button>
        </div>
        
        <div class="suggestions">
          <h3>您可能在寻找：</h3>
          <ul>
            <li><router-link to="/">图片搜索首页</router-link></li>
            <li><router-link to="/gallery">图片画廊</router-link></li>
            <li><router-link to="/admin/login">管理员登录</router-link></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { HomeFilled, ArrowLeft } from '@element-plus/icons-vue'

const router = useRouter()

// 返回首页
const goHome = () => {
  router.push('/')
}

// 返回上一页
const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/')
  }
}
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.not-found-container {
  max-width: 800px;
  text-align: center;
  background: white;
  border-radius: 20px;
  padding: 60px 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  animation: fadeIn 0.8s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.error-image {
  position: relative;
  margin-bottom: 40px;
}

.error-number {
  font-size: 8rem;
  font-weight: 900;
  color: #e74c3c;
  margin-bottom: 20px;
  text-shadow: 0 4px 8px rgba(231, 76, 60, 0.3);
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

.error-illustration {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.magnifying-glass {
  position: relative;
  width: 80px;
  height: 80px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-10px) rotate(5deg);
  }
}

.lens {
  width: 60px;
  height: 60px;
  border: 4px solid #3498db;
  border-radius: 50%;
  background: rgba(52, 152, 219, 0.1);
}

.handle {
  position: absolute;
  bottom: -10px;
  right: -10px;
  width: 6px;
  height: 25px;
  background: #3498db;
  border-radius: 3px;
  transform: rotate(45deg);
}

.error-content h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 20px;
  font-weight: 700;
}

.error-content p {
  font-size: 1.1rem;
  color: #7f8c8d;
  margin-bottom: 15px;
  line-height: 1.6;
}

.action-buttons {
  margin: 40px 0;
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.suggestions {
  margin-top: 40px;
  padding-top: 30px;
  border-top: 1px solid #ecf0f1;
}

.suggestions h3 {
  font-size: 1.3rem;
  color: #2c3e50;
  margin-bottom: 20px;
}

.suggestions ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.suggestions li {
  margin: 10px 0;
}

.suggestions a {
  color: #3498db;
  text-decoration: none;
  font-size: 1.1rem;
  transition: color 0.3s ease;
}

.suggestions a:hover {
  color: #2980b9;
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .not-found-container {
    padding: 40px 20px;
    margin: 10px;
  }
  
  .error-number {
    font-size: 6rem;
  }
  
  .error-content h1 {
    font-size: 2rem;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .action-buttons .el-button {
    width: 200px;
  }
}

@media (max-width: 480px) {
  .error-number {
    font-size: 4.5rem;
  }
  
  .error-content h1 {
    font-size: 1.8rem;
  }
  
  .error-content p {
    font-size: 1rem;
  }
  
  .magnifying-glass {
    width: 60px;
    height: 60px;
  }
  
  .lens {
    width: 45px;
    height: 45px;
  }
}
</style> 