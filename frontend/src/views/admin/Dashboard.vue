<template>
  <div class="admin-dashboard">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <el-row :gutter="20">
        <el-col :xs="24" :md="16">
          <h1>欢迎回来，{{ userStore.user?.username || 'Admin' }}！</h1>
          <p>系统运行状态良好，今天是 {{ getCurrentDate() }}</p>
        </el-col>
        <el-col :xs="24" :md="8" class="banner-actions">
          <el-button type="primary" :icon="Refresh" @click="refreshData">
            刷新数据
          </el-button>
          <el-button type="success" :icon="Upload" @click="goToUpload">
            上传图片
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #e3f2fd;">
            <el-icon size="32" color="#2196f3"><Picture /></el-icon>
          </div>
          <div class="stat-content">
            <h3>{{ stats.totalImages || 0 }}</h3>
            <p>总图片数</p>
          </div>
        </div>
      </el-col>
      

      
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #fff3e0;">
            <el-icon size="32" color="#ff9800"><User /></el-icon>
          </div>
          <div class="stat-content">
            <h3>{{ stats.totalUsers || 0 }}</h3>
            <p>用户数量</p>
          </div>
        </div>
      </el-col>
      
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #fce4ec;">
            <el-icon size="32" color="#e91e63"><DataBoard /></el-icon>
          </div>
          <div class="stat-content">
            <h3>{{ formatFileSize(stats.totalStorage || 0) }}</h3>
            <p>存储使用</p>
          </div>
        </div>
      </el-col>
    </el-row>



    <!-- 系统信息 -->
    <el-row :gutter="20" class="system-row">
      <el-col :xs="24" :lg="8">
        <el-card header="系统状态">
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

      <el-col :xs="24" :lg="8">
        <el-card header="快速操作">
          <div class="quick-actions">
            <el-button type="primary" :icon="Upload" @click="goToUpload" block>
              批量上传图片
            </el-button>
            <el-button type="info" :icon="View" @click="goToGallery" block>
              查看图片库
            </el-button>
            <el-button type="warning" :icon="Setting" @click="goToSettings" block>
              系统设置
            </el-button>
            <el-button type="danger" :icon="Delete" @click="showCleanupDialog" block>
              清理数据
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card header="存储分析">
          <div class="storage-info">
            <div class="storage-item">
              <span class="label">图片总数:</span>
              <span class="value">{{ stats.totalImages || 0 }}</span>
            </div>
            <div class="storage-item">
              <span class="label">总存储:</span>
              <span class="value">{{ formatFileSize(stats.totalStorage || 0) }}</span>
            </div>
            <div class="storage-item">
              <span class="label">平均文件大小:</span>
              <span class="value">{{ formatFileSize(stats.avgFileSize || 0) }}</span>
            </div>
            <div class="storage-item">
              <span class="label">最大文件:</span>
              <span class="value">{{ formatFileSize(stats.maxFileSize || 0) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>



    <!-- 清理数据确认对话框 -->
    <el-dialog v-model="showCleanup" title="数据清理" width="400px">
      <el-alert 
        title="警告" 
        type="warning" 
        description="此操作将清理系统缓存和临时文件，不会删除图片数据。" 
        show-icon 
        :closable="false"
      />
      <template #footer>
        <el-button @click="showCleanup = false">取消</el-button>
        <el-button type="primary" @click="performCleanup">确认清理</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Picture, Search, User, DataBoard, Refresh, Upload, 
  View, Setting, Delete 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const userStore = useAuthStore()

// 响应式数据
const stats = reactive({
  totalImages: 0,
  totalUsers: 0,
  totalStorage: 0,
  avgFileSize: 0,
  maxFileSize: 0
})

const systemInfo = reactive({
  faissStatus: 'active',
  dbStatus: 'connected',
  modelStatus: 'loaded'
})


const showCleanup = ref(false)

// 获取当前日期
const getCurrentDate = () => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

// 获取图片URL
const getImageUrl = (path) => {
  if (!path) return '/placeholder.svg'
  return path.startsWith('http') ? path : `${import.meta.env.VITE_API_BASE_URL}/static/${path}`
}

// 处理图片加载错误
const handleImageError = (event) => {
  event.target.src = '/placeholder.svg'
}



// 显示清理对话框
const showCleanupDialog = () => {
  showCleanup.value = true
}

// 执行清理
const performCleanup = async () => {
  try {
    // 这里应该调用后端清理接口
    ElMessage.success('系统清理完成')
    showCleanup.value = false
  } catch (error) {
    ElMessage.error('清理失败：' + error.message)
  }
}

// 导航到上传页面
const goToUpload = () => {
  router.push('/admin/upload')
}

// 导航到图片库
const goToGallery = () => {
  router.push('/gallery')
}

// 导航到设置页面
const goToSettings = () => {
  router.push('/admin/config')
}

// 刷新数据
const refreshData = async () => {
  await loadDashboardData()
  ElMessage.success('数据已刷新')
}

// 加载仪表板数据
const loadDashboardData = async () => {
  try {
    // 模拟数据，实际应该从API获取
    stats.totalImages = 1234
    stats.totalUsers = 12
    stats.totalStorage = 2.5 * 1024 * 1024 * 1024 // 2.5GB
    stats.avgFileSize = 2.1 * 1024 * 1024 // 2.1MB
    stats.maxFileSize = 15.6 * 1024 * 1024 // 15.6MB



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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 12px;
  margin-bottom: 30px;
}

.welcome-banner h1 {
  font-size: 2rem;
  margin: 0 0 10px 0;
  font-weight: 600;
}

.welcome-banner p {
  font-size: 1.1rem;
  margin: 0;
  opacity: 0.9;
}

.banner-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  justify-content: flex-end;
}

.stats-row {
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-content h3 {
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.stat-content p {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.charts-row {
  margin-bottom: 30px;
}

.chart-card {
  height: 300px;
}

.search-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.search-item:last-child {
  border-bottom: none;
}

.search-info h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 1rem;
}

.search-info p {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.85rem;
}

.search-results {
  color: #3498db;
  font-weight: 600;
  font-size: 0.9rem;
}



.system-row {
  margin-bottom: 30px;
}

.system-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-item .label {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.storage-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.storage-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.storage-item .label {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.storage-item .value {
  color: #2c3e50;
  font-weight: 600;
  font-size: 0.9rem;
}

.image-detail {
  text-align: center;
}

.image-detail img {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .welcome-banner {
    padding: 20px;
  }
  
  .welcome-banner h1 {
    font-size: 1.6rem;
  }
  
  .banner-actions {
    justify-content: flex-start;
    margin-top: 15px;
  }
  
  .stat-card {
    padding: 15px;
  }
  
  .stat-content h3 {
    font-size: 1.5rem;
  }
  
  .chart-card {
    height: auto;
    min-height: 250px;
  }
  
  .recent-images {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .stats-row .el-col {
    margin-bottom: 15px;
  }
  
  .charts-row .el-col,
  .system-row .el-col {
    margin-bottom: 20px;
  }
  
  .quick-actions .el-button {
    font-size: 0.9rem;
  }
}
</style> 