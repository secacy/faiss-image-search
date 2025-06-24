<template>
  <div class="admin-layout">
    <!-- 顶部导航栏 -->
    <div class="admin-header">
      <div class="header-left">
        <h1 class="admin-title">图与图寻 - 管理后台</h1>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-icon><User /></el-icon>
            {{ userStore.user?.username || 'Admin' }}
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 侧边栏和主要内容 -->
    <div class="admin-container">
      <!-- 侧边栏 -->
      <div class="admin-sidebar">
        <el-menu
          :default-active="$route.path"
          class="admin-menu"
          router
          background-color="#f8f9fa"
          text-color="#495057"
          active-text-color="#007bff"
        >
          <el-menu-item index="/admin/dashboard">
            <el-icon><DataBoard /></el-icon>
            <span>仪表板</span>
          </el-menu-item>
          
          <el-menu-item index="/admin/images">
            <el-icon><List /></el-icon>
            <span>图片列表</span>
          </el-menu-item>
          
          <el-menu-item index="/admin/upload">
            <el-icon><Upload /></el-icon>
            <span>上传图片</span>
          </el-menu-item>

          <el-menu-item index="/admin/logs">
            <el-icon><Document /></el-icon>
            <span>操作日志</span>
          </el-menu-item>

          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>返回前台</span>
          </el-menu-item>
        </el-menu>
      </div>

      <!-- 主要内容区域 -->
      <div class="admin-main">
        <div class="admin-content">
          <router-view />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { 
  User, ArrowDown, SwitchButton, DataBoard, 
  List, Upload, Document, HomeFilled 
} from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useAuthStore()

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/admin/login')
  }
}
</script>

<style scoped>
.admin-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.admin-header {
  height: 60px;
  background: #f5f6f7;
  color: #495057;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border-bottom: 1px solid #e9ecef;
}

.admin-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #343a40;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.3s;
  color: #495057;
}

.user-info:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.admin-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.admin-sidebar {
  width: 250px;
  background: #f8f9fa;
  overflow-y: hidden;
  border-right: 1px solid #e9ecef;
  flex-shrink: 0;
}

.admin-menu {
  border: none;
  height: 100%;
  overflow: visible;
}

.admin-menu :deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
  border-radius: 8px;
  margin: 4px 8px;
  color: #495057;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.admin-menu :deep(.el-menu-item .el-icon) {
  margin-right: 8px;
}

.admin-menu :deep(.el-menu-item span) {
  font-weight: 500;
}

.admin-menu :deep(.el-menu-item:hover) {
  background-color: #e9ecef;
  color: #007bff;
}

.admin-menu :deep(.el-menu-item.is-active) {
  background-color: #e7f3ff;
  color: #007bff;
}

.admin-main {
  flex: 1;
  background: #ffffff;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.admin-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: #fafbfc;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-sidebar {
    width: 200px;
  }
  
  .admin-content {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .admin-header {
    padding: 0 15px;
  }
  
  .admin-title {
    font-size: 16px;
  }
  
  .admin-sidebar {
    width: 180px;
  }
  
  .admin-content {
    padding: 16px;
  }
}
</style> 