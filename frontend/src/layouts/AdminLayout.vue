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
          background-color="#2c3e50"
          text-color="#ecf0f1"
          active-text-color="#3498db"
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
  background: #34495e;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.admin-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.admin-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.admin-sidebar {
  width: 250px;
  background: #2c3e50;
  overflow-y: auto;
}

.admin-menu {
  border: none;
  height: 100%;
}

.admin-menu .el-menu-item,
.admin-menu .el-sub-menu__title {
  height: 50px;
  line-height: 50px;
}

.admin-main {
  flex: 1;
  background: #f5f7fa;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.admin-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-sidebar {
    width: 200px;
  }
  
  .admin-content {
    padding: 15px;
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
    padding: 10px;
  }
}
</style> 