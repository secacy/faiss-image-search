<template>
  <div class="admin-dashboard">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <el-row :gutter="20">
        <el-col :xs="24" :md="16">
          <h1>欢迎回来，{{ userStore.user?.username || 'Admin' }}！</h1>
          <p>系统运行状态良好，今天是 {{ getCurrentDate() }}</p>
        </el-col>
      </el-row>
    </div>

    <!-- 系统信息 -->
    <el-row :gutter="24" class="system-row">
      <el-col :xs="24">
        <el-card header="系统状态" class="system-card">
          <div class="system-info">
            <div class="info-item">
              <span class="label">Faiss 索引状态:</span>
              <el-tag :type="systemInfo.faissStatus === 'active' ? 'success' : 'danger'">
                {{ systemInfo.faissStatus === 'active' ? '正常' : '异常' }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="label">数据库连接:</span>
              <el-tag :type="systemInfo.dbStatus === 'connected' ? 'success' : 'danger'">
                {{ systemInfo.dbStatus === 'connected' ? '已连接' : '断开' }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="label">模型状态:</span>
              <el-tag :type="systemInfo.modelStatus === 'loaded' ? 'success' : 'warning'">
                {{ systemInfo.modelStatus === 'loaded' ? '已加载' : '未加载' }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const userStore = useAuthStore()

const systemInfo = reactive({
  faissStatus: 'active',
  dbStatus: 'connected',
  modelStatus: 'loaded'
})

// 获取当前日期
const getCurrentDate = () => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
}

// 加载仪表板数据
const loadDashboardData = async () => {
  try {
    // 这里可以加载系统状态数据
    console.log('仪表板加载完成')
  } catch (error) {
    console.error('加载仪表板数据失败:', error)
    ElMessage.error('加载数据失败')
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.admin-dashboard {
  padding: 0;
}

.welcome-banner {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  color: #1565c0;
  padding: 32px;
  border-radius: 16px;
  margin-bottom: 32px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e3f2fd;
}

.welcome-banner h1 {
  font-size: 2rem;
  margin: 0 0 12px 0;
  font-weight: 600;
  color: #0d47a1;
}

.welcome-banner p {
  font-size: 1.1rem;
  margin: 0;
  opacity: 0.8;
  color: #1976d2;
}

.system-row {
  margin-bottom: 32px;
}

.system-card {
  border-radius: 16px;
  border: 1px solid #f0f0f0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.system-card :deep(.el-card__header) {
  background: #fafbfc;
  border-bottom: 1px solid #f0f0f0;
  padding: 20px 24px;
  font-weight: 600;
  color: #2c3e50;
}

.system-card :deep(.el-card__body) {
  padding: 24px;
}

.system-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f8f9fa;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  color: #6c757d;
  font-size: 0.95rem;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .welcome-banner {
    padding: 24px;
    margin-bottom: 24px;
  }
  
  .welcome-banner h1 {
    font-size: 1.6rem;
  }
  
  .system-row {
    margin-bottom: 24px;
  }
}

@media (max-width: 480px) {
  .welcome-banner {
    padding: 20px;
  }
  
  .welcome-banner h1 {
    font-size: 1.4rem;
  }
}
</style> 