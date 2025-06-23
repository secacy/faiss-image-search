<template>
  <div class="admin-login">
    <div class="login-container">
      <!-- Logo和标题 -->
      <div class="login-header">
        <el-icon size="48" color="#409eff">
          <Picture />
        </el-icon>
        <div class="header-text">
          <h1>图与图寻 - 管理后台</h1>
        </div>
      </div>

      <!-- 登录表单 -->
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            :prefix-icon="User"
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            :prefix-icon="Lock"
            show-password
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="loginForm.remember">
            记住我
          </el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 底部信息 -->
      <div class="login-footer">
        <p class="footer-links">
          <router-link to="/">← 返回首页</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Picture, User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const loading = ref(false)
const loginFormRef = ref(null)

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: '',
  remember: false
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 100, message: '密码长度在 6 到 100 个字符', trigger: 'blur' }
  ]
}

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    const valid = await loginFormRef.value.validate()
    if (!valid) return

    loading.value = true
    
    // 调用登录接口
    await authStore.login({
      username: loginForm.username,
      password: loginForm.password
    })

    ElMessage.success('登录成功')
    router.push('/admin/dashboard')
    
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error(error.message || '登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}

// 组件挂载时检查是否已登录
onMounted(() => {
  if (authStore.isAuthenticated) {
    router.push('/admin/dashboard')
  }
  
  // 开发模式下自动填充账号
  if (import.meta.env.DEV) {
    loginForm.username = 'admin'
    loginForm.password = 'admin123'
  }
})
</script>

<style scoped>
.admin-login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  padding: 20px;
}

.login-container {
  background: white;
  border: 1px solid #e4e7ed;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.login-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.header-text {
  flex: 1;
}

.header-text h1 {
  font-size: 1.5rem;
  color: #303133;
  margin: 0 0 4px 0;
  font-weight: 600;
}

.header-text p {
  font-size: 0.9rem;
  color: #909399;
  margin: 0;
}

.login-form {
  margin-bottom: 24px;
}

.login-form .el-form-item {
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
  height: 42px;
}

.login-footer {
  text-align: center;
  border-top: 1px solid #e4e7ed;
  padding-top: 16px;
}

.footer-text {
  color: #909399;
  font-size: 0.85rem;
  margin: 0 0 8px 0;
}

.footer-links {
  margin: 0;
}

.footer-links a {
  color: #409eff;
  text-decoration: none;
  font-size: 0.85rem;
}

.footer-links a:hover {
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    padding: 30px 24px;
    margin: 0 16px;
  }
  
  .header-text h1 {
    font-size: 1.3rem;
  }
  
  .login-header {
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .admin-login {
    padding: 16px;
  }
  
  .login-container {
    padding: 24px 20px;
    margin: 0;
  }
  
  .header-text h1 {
    font-size: 1.2rem;
  }
  
  .login-header {
    flex-direction: column;
    text-align: center;
    gap: 8px;
  }
  
  .header-text {
    text-align: center;
  }
}
</style> 