<template>
  <div class="system-config">
    <div class="page-header">
      <h1>系统配置</h1>
      <div class="page-actions">
        <el-button type="primary" @click="saveConfig" :loading="saving">
          保存配置
        </el-button>
        <el-button @click="resetConfig">
          重置
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :xs="24" :lg="16">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- 基础设置 -->
          <el-tab-pane label="基础设置" name="basic">
            <el-form :model="config.basic" label-width="120px">
              <el-form-item label="系统名称">
                <el-input v-model="config.basic.system_name" placeholder="图与图寻" />
              </el-form-item>
              
              <el-form-item label="系统描述">
                <el-input 
                  v-model="config.basic.system_description" 
                  type="textarea" 
                  :rows="3"
                  placeholder="智能图像搜索系统"
                />
              </el-form-item>

              <el-form-item label="管理员邮箱">
                <el-input v-model="config.basic.admin_email" placeholder="admin@example.com" />
              </el-form-item>

              <el-form-item label="最大上传大小">
                <el-input-number 
                  v-model="config.basic.max_upload_size" 
                  :min="1" 
                  :max="100"
                  placeholder="10"
                />
                <span style="margin-left: 10px;">MB</span>
              </el-form-item>

              <el-form-item label="默认搜索数量">
                <el-input-number 
                  v-model="config.basic.default_search_limit" 
                  :min="5" 
                  :max="100"
                  placeholder="20"
                />
              </el-form-item>

              <el-form-item label="维护模式">
                <el-switch 
                  v-model="config.basic.maintenance_mode"
                  active-text="开启"
                  inactive-text="关闭"
                />
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <!-- 搜索设置 -->
          <el-tab-pane label="搜索设置" name="search">
            <el-form :model="config.search" label-width="120px">
              <el-form-item label="相似度阈值">
                <el-slider 
                  v-model="config.search.similarity_threshold" 
                  :min="0.1" 
                  :max="1.0" 
                  :step="0.05"
                  show-input
                />
              </el-form-item>

              <el-form-item label="最大结果数">
                <el-input-number 
                  v-model="config.search.max_results" 
                  :min="10" 
                  :max="1000"
                />
              </el-form-item>

              <el-form-item label="搜索超时">
                <el-input-number 
                  v-model="config.search.timeout" 
                  :min="5" 
                  :max="300"
                />
                <span style="margin-left: 10px;">秒</span>
              </el-form-item>

              <el-form-item label="启用缓存">
                <el-switch 
                  v-model="config.search.enable_cache"
                  active-text="开启"
                  inactive-text="关闭"
                />
              </el-form-item>

              <el-form-item label="缓存过期时间">
                <el-input-number 
                  v-model="config.search.cache_expire" 
                  :min="60" 
                  :max="86400"
                  :disabled="!config.search.enable_cache"
                />
                <span style="margin-left: 10px;">秒</span>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <!-- 存储设置 -->
          <el-tab-pane label="存储设置" name="storage">
            <el-form :model="config.storage" label-width="120px">
              <el-form-item label="存储类型">
                <el-radio-group v-model="config.storage.type">
                  <el-radio label="local">本地存储</el-radio>
                  <el-radio label="oss" disabled>阿里云OSS</el-radio>
                  <el-radio label="s3" disabled>AWS S3</el-radio>
                </el-radio-group>
              </el-form-item>

              <el-form-item label="存储路径">
                <el-input v-model="config.storage.path" placeholder="./data/images" />
              </el-form-item>

              <el-form-item label="图片质量">
                <el-slider 
                  v-model="config.storage.image_quality" 
                  :min="50" 
                  :max="100" 
                  :step="5"
                  show-input
                />
              </el-form-item>

              <el-form-item label="自动清理">
                <el-switch 
                  v-model="config.storage.auto_cleanup"
                  active-text="开启"
                  inactive-text="关闭"
                />
              </el-form-item>

              <el-form-item label="清理间隔">
                <el-input-number 
                  v-model="config.storage.cleanup_interval" 
                  :min="1" 
                  :max="365"
                  :disabled="!config.storage.auto_cleanup"
                />
                <span style="margin-left: 10px;">天</span>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <!-- 模型设置 -->
          <el-tab-pane label="AI模型" name="model">
            <el-form :model="config.model" label-width="120px">
              <el-form-item label="模型类型">
                <el-select v-model="config.model.type" placeholder="选择模型">
                  <el-option label="ResNet50" value="resnet50" />
                  <el-option label="EfficientNet" value="efficientnet" />
                  <el-option label="CLIP" value="clip" />
                </el-select>
              </el-form-item>

              <el-form-item label="模型路径">
                <el-input v-model="config.model.path" placeholder="./models/resnet50.pth" />
              </el-form-item>

              <el-form-item label="批处理大小">
                <el-input-number 
                  v-model="config.model.batch_size" 
                  :min="1" 
                  :max="32"
                />
              </el-form-item>

              <el-form-item label="设备类型">
                <el-radio-group v-model="config.model.device">
                  <el-radio label="cpu">CPU</el-radio>
                  <el-radio label="cuda">CUDA (GPU)</el-radio>
                  <el-radio label="auto">自动检测</el-radio>
                </el-radio-group>
              </el-form-item>

              <el-form-item label="特征维度">
                <el-input-number 
                  v-model="config.model.feature_dim" 
                  :min="128" 
                  :max="4096"
                  :step="64"
                />
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <!-- 安全设置 -->
          <el-tab-pane label="安全设置" name="security">
            <el-form :model="config.security" label-width="120px">
              <el-form-item label="API访问限制">
                <el-switch 
                  v-model="config.security.enable_rate_limit"
                  active-text="开启"
                  inactive-text="关闭"
                />
              </el-form-item>

              <el-form-item label="每分钟请求数">
                <el-input-number 
                  v-model="config.security.rate_limit" 
                  :min="10" 
                  :max="1000"
                  :disabled="!config.security.enable_rate_limit"
                />
              </el-form-item>

              <el-form-item label="JWT密钥">
                <el-input 
                  v-model="config.security.jwt_secret" 
                  type="password" 
                  show-password
                  placeholder="请输入JWT密钥"
                />
              </el-form-item>

              <el-form-item label="Token过期时间">
                <el-input-number 
                  v-model="config.security.token_expire" 
                  :min="1" 
                  :max="168"
                />
                <span style="margin-left: 10px;">小时</span>
              </el-form-item>

              <el-form-item label="允许跨域">
                <el-switch 
                  v-model="config.security.enable_cors"
                  active-text="开启"
                  inactive-text="关闭"
                />
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </el-col>

      <!-- 右侧信息面板 -->
      <el-col :xs="24" :lg="8">
        <el-card class="info-card">
          <template #header>
            <span>系统信息</span>
          </template>
          
          <div class="system-info">
            <div class="info-item">
              <span class="info-label">系统版本:</span>
              <span class="info-value">v{{ systemInfo.version }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Python版本:</span>
              <span class="info-value">{{ systemInfo.python_version }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">运行时间:</span>
              <span class="info-value">{{ systemInfo.uptime }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">CPU使用率:</span>
              <el-progress 
                :percentage="systemInfo.cpu_usage" 
                :color="getCpuColor(systemInfo.cpu_usage)"
                :stroke-width="8"
              />
            </div>
            <div class="info-item">
              <span class="info-label">内存使用率:</span>
              <el-progress 
                :percentage="systemInfo.memory_usage" 
                :color="getMemoryColor(systemInfo.memory_usage)"
                :stroke-width="8"
              />
            </div>
            <div class="info-item">
              <span class="info-label">磁盘使用率:</span>
              <el-progress 
                :percentage="systemInfo.disk_usage" 
                :color="getDiskColor(systemInfo.disk_usage)"
                :stroke-width="8"
              />
            </div>
          </div>
        </el-card>

        <el-card class="actions-card" style="margin-top: 20px;">
          <template #header>
            <span>系统操作</span>
          </template>
          
          <div class="system-actions">
            <el-button type="warning" @click="restartSystem" :loading="restarting">
              重启系统
            </el-button>
            <el-button type="info" @click="clearCache">
              清除缓存
            </el-button>
            <el-button type="success" @click="backupData">
              备份数据
            </el-button>
            <el-button type="danger" @click="resetToDefault">
              恢复默认
            </el-button>
          </div>
        </el-card>

        <el-card class="logs-card" style="margin-top: 20px;">
          <template #header>
            <span>最近操作日志</span>
          </template>
          
          <div class="recent-logs">
            <div 
              v-for="log in recentLogs" 
              :key="log.id" 
              class="log-item"
              :class="log.level"
            >
              <div class="log-time">{{ formatTime(log.timestamp) }}</div>
              <div class="log-message">{{ log.message }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import searchAPI from '@/api/search.js'

// 响应式数据
const activeTab = ref('basic')
const saving = ref(false)
const restarting = ref(false)

const config = ref({
  basic: {
    system_name: '图与图寻',
    system_description: '智能图像搜索系统',
    admin_email: 'admin@example.com',
    max_upload_size: 10,
    default_search_limit: 20,
    maintenance_mode: false
  },
  search: {
    similarity_threshold: 0.7,
    max_results: 100,
    timeout: 30,
    enable_cache: true,
    cache_expire: 3600
  },
  storage: {
    type: 'local',
    path: './data/images',
    image_quality: 90,
    auto_cleanup: false,
    cleanup_interval: 30
  },
  model: {
    type: 'resnet50',
    path: './models/resnet50.pth',
    batch_size: 8,
    device: 'auto',
    feature_dim: 2048
  },
  security: {
    enable_rate_limit: true,
    rate_limit: 100,
    jwt_secret: 'your-secret-key',
    token_expire: 24,
    enable_cors: true
  }
})

const systemInfo = ref({
  version: '1.0.0',
  python_version: '3.9.0',
  uptime: '2天 3小时 45分钟',
  cpu_usage: 25,
  memory_usage: 68,
  disk_usage: 45
})

const recentLogs = ref([
  {
    id: 1,
    timestamp: new Date(),
    level: 'info',
    message: '系统配置已更新'
  },
  {
    id: 2,
    timestamp: new Date(Date.now() - 300000),
    level: 'warning',
    message: 'CPU使用率较高'
  },
  {
    id: 3,
    timestamp: new Date(Date.now() - 600000),
    level: 'success',
    message: '数据备份完成'
  }
])

// 加载系统配置
const loadConfig = async () => {
  try {
    const response = await searchAPI.admin.config.getAll()
    if (response.data.success) {
      config.value = response.data.data
    }
  } catch (error) {
    console.error('加载配置失败:', error)
    ElMessage.error('加载系统配置失败')
  }
}

// 保存配置
const saveConfig = async () => {
  saving.value = true
  try {
    const response = await searchAPI.admin.config.update(config.value)
    if (response.data.success) {
      ElMessage.success('配置保存成功')
    } else {
      throw new Error(response.data.message || '保存失败')
    }
  } catch (error) {
    console.error('保存配置失败:', error)
    ElMessage.error('保存配置失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

// 重置配置
const resetConfig = () => {
  ElMessageBox.confirm('确定要重置当前配置吗？', '重置确认', {
    type: 'warning'
  }).then(() => {
    // 重置到默认值
    loadDefaultConfig()
    ElMessage.success('配置已重置')
  }).catch(() => {})
}

// 重启系统
const restartSystem = async () => {
  try {
    await ElMessageBox.confirm('确定要重启系统吗？这将会中断当前所有连接。', '重启确认', {
      type: 'warning'
    })
    
    restarting.value = true
    const response = await searchAPI.admin.system.restart()
    if (response.data.success) {
      ElMessage.success(response.data.message || '系统正在重启...')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重启系统失败:', error)
      ElMessage.error('重启系统失败: ' + (error.response?.data?.detail || error.message))
    }
  } finally {
    restarting.value = false
  }
}

// 清除缓存
const clearCache = async () => {
  try {
    const response = await searchAPI.admin.system.clearCache()
    if (response.data.success) {
      ElMessage.success(response.data.message || '缓存清除成功')
    }
  } catch (error) {
    console.error('清理缓存失败:', error)
    ElMessage.error('清理缓存失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 备份数据
const backupData = () => {
  ElMessage.success('数据备份已开始')
}

// 恢复默认设置
const resetToDefault = () => {
  ElMessageBox.confirm('确定要恢复所有默认设置吗？', '恢复默认', {
    type: 'warning'
  }).then(() => {
    loadDefaultConfig()
    ElMessage.success('已恢复默认设置')
  }).catch(() => {})
}

// 加载默认配置
const loadDefaultConfig = () => {
  // 这里重新设置默认值
  config.value = {
    basic: {
      system_name: '图与图寻',
      system_description: '智能图像搜索系统',
      admin_email: 'admin@example.com',
      max_upload_size: 10,
      default_search_limit: 20,
      maintenance_mode: false
    },
    search: {
      similarity_threshold: 0.7,
      max_results: 100,
      timeout: 30,
      enable_cache: true,
      cache_expire: 3600
    },
    storage: {
      type: 'local',
      path: './data/images',
      image_quality: 90,
      auto_cleanup: false,
      cleanup_interval: 30
    },
    model: {
      type: 'resnet50',
      path: './models/resnet50.pth',
      batch_size: 8,
      device: 'auto',
      feature_dim: 2048
    },
    security: {
      enable_rate_limit: true,
      rate_limit: 100,
      jwt_secret: 'your-secret-key',
      token_expire: 24,
      enable_cors: true
    }
  }
}

// 工具方法
const getCpuColor = (usage) => {
  if (usage < 50) return '#67c23a'
  if (usage < 80) return '#e6a23c'
  return '#f56c6c'
}

const getMemoryColor = (usage) => {
  if (usage < 60) return '#67c23a'
  if (usage < 85) return '#e6a23c'
  return '#f56c6c'
}

const getDiskColor = (usage) => {
  if (usage < 70) return '#67c23a'
  if (usage < 90) return '#e6a23c'
  return '#f56c6c'
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString('zh-CN')
}

// 组件挂载时加载配置
onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.system-config {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  color: #2c3e50;
}

.page-actions {
  display: flex;
  gap: 10px;
}

.el-tabs {
  height: calc(100vh - 200px);
  overflow-y: auto;
}

.el-form {
  padding: 20px;
}

.info-card,
.actions-card,
.logs-card {
  height: fit-content;
}

.system-info {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.info-label {
  font-size: 0.9rem;
  color: #7f8c8d;
}

.info-value {
  font-weight: bold;
  color: #2c3e50;
}

.system-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.system-actions .el-button {
  width: 100%;
}

.recent-logs {
  max-height: 200px;
  overflow-y: auto;
}

.log-item {
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.log-item:last-child {
  border-bottom: none;
}

.log-time {
  font-size: 0.8rem;
  color: #95a5a6;
  margin-bottom: 2px;
}

.log-message {
  font-size: 0.9rem;
  color: #2c3e50;
}

.log-item.info .log-message {
  color: #409eff;
}

.log-item.warning .log-message {
  color: #e6a23c;
}

.log-item.success .log-message {
  color: #67c23a;
}

.log-item.error .log-message {
  color: #f56c6c;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .el-tabs {
    height: auto;
  }
  
  .system-actions {
    flex-direction: row;
    flex-wrap: wrap;
  }
  
  .system-actions .el-button {
    width: calc(50% - 5px);
  }
}
</style>