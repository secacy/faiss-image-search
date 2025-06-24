<template>
  <el-container class="user-layout">
    <el-header class="header">
      <div class="header-content">
        <div class="logo">
          <el-icon class="logo-icon"><Search /></el-icon>
          <span class="logo-text">图与图寻</span>
        </div>
        <el-menu
          :default-active="currentRoute"
          class="nav-menu"
          mode="horizontal"
          router
        >
        </el-menu>
        <div class="header-actions">
          <el-button text @click="goToAdmin" class="admin-btn">
            <el-icon><Setting /></el-icon>
            管理后台
          </el-button>
        </div>
      </div>
    </el-header>
    <el-main class="main-content">
      <router-view />
    </el-main>
    <el-footer class="footer">
      <div class="footer-content">
        <p>&copy; 2024 图与图寻. 基于 Faiss 的智能图像搜索系统.</p>
      </div>
    </el-footer>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Camera, Search, Picture, Setting } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const currentRoute = computed(() => route.path)

const goToAdmin = () => {
  router.push('/admin/login')
}
</script>

<style scoped>
.user-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-light) 100%);
}

.header {
  background: var(--bg-primary);
  box-shadow: var(--shadow-light);
  padding: 0;
  border-bottom: 1px solid var(--border-color);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 100%;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(45deg, var(--primary-color), var(--accent-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  transition: all 0.3s ease;
}

.logo:hover {
  transform: scale(1.05);
}

.logo-icon {
  font-size: 28px;
  color: var(--primary-color);
}

.nav-menu {
  flex: 1;
  border-bottom: none;
  margin-left: 40px;
  background: transparent;
}

.nav-menu .el-menu-item {
  border-bottom: 2px solid transparent;
  color: var(--text-secondary);
  font-weight: 500;
  transition: all 0.3s ease;
}

.nav-menu .el-menu-item:hover {
  background: var(--bg-light);
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.nav-menu .el-menu-item.is-active {
  background: var(--bg-light);
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.admin-btn {
  color: var(--text-secondary);
  font-weight: 500;
  padding: 8px 16px;
  border-radius: var(--border-radius);
  transition: all 0.3s ease;
}

.admin-btn:hover {
  background: var(--bg-light);
  color: var(--accent-color);
  transform: translateY(-1px);
}

.main-content {
  background: transparent;
  padding: 0;
  min-height: calc(100vh - 120px);
}

.footer {
  background: transparent;
  color: var(--text-secondary);
  text-align: center;
  padding: 20px 0;
  margin-top: auto;
  border-top: 1px solid var(--border-color);
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  font-size: 14px;
  opacity: 0.9;
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
  }
  
  .nav-menu {
    margin-left: 20px;
  }
  
  .logo-text {
    display: none;
  }
  
  .nav-menu .el-menu-item span {
    display: none;
  }
  
  .admin-btn span {
    display: none;
  }
}

@media (max-width: 480px) {
  .logo {
    font-size: 16px;
  }
  
  .logo-icon {
    font-size: 24px;
  }
  
  .nav-menu {
    margin-left: 16px;
  }
}
</style> 