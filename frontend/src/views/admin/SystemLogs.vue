<template>
  <div class="system-logs">
    <div class="page-header">
      <h1>操作日志</h1>
      <div class="page-actions">
        <el-button type="primary" @click="exportLogs">
          导出日志
        </el-button>
        <el-button type="danger" @click="clearLogs">
          清空日志
        </el-button>
      </div>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="6">
          <el-select v-model="filter.level" placeholder="日志级别" clearable @change="loadLogs">
            <el-option label="全部" value="" />
            <el-option label="信息" value="info" />
            <el-option label="警告" value="warning" />
            <el-option label="错误" value="error" />
            <el-option label="调试" value="debug" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="6">
          <el-select v-model="filter.module" placeholder="模块" clearable @change="loadLogs">
            <el-option label="全部" value="" />
            <el-option label="搜索" value="search" />
            <el-option label="上传" value="upload" />
            <el-option label="认证" value="auth" />
            <el-option label="系统" value="system" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="6">
          <el-date-picker
            v-model="filter.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="loadLogs"
          />
        </el-col>
        <el-col :xs="24" :sm="6">
          <el-input
            v-model="filter.keyword"
            placeholder="搜索关键词..."
            @input="handleSearch"
            clearable
          />
        </el-col>
      </el-row>
    </el-card>

    <!-- 日志统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="6" :sm="3">
        <div class="stat-item info">
          <div class="stat-value">{{ stats.info }}</div>
          <div class="stat-label">信息</div>
        </div>
      </el-col>
      <el-col :xs="6" :sm="3">
        <div class="stat-item warning">
          <div class="stat-value">{{ stats.warning }}</div>
          <div class="stat-label">警告</div>
        </div>
      </el-col>
      <el-col :xs="6" :sm="3">
        <div class="stat-item error">
          <div class="stat-value">{{ stats.error }}</div>
          <div class="stat-label">错误</div>
        </div>
      </el-col>
      <el-col :xs="6" :sm="3">
        <div class="stat-item debug">
          <div class="stat-value">{{ stats.debug }}</div>
          <div class="stat-label">调试</div>
        </div>
      </el-col>
    </el-row>

    <!-- 日志列表 -->
    <el-card class="logs-card">
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="8" animated />
      </div>

      <div v-else-if="logs.length > 0" class="logs-list">
        <div
          v-for="log in logs"
          :key="log.id"
          class="log-item"
          :class="log.level"
        >
          <div class="log-header">
            <div class="log-level">
              <el-tag :type="getLevelTagType(log.level)" size="small">
                {{ log.level.toUpperCase() }}
              </el-tag>
            </div>
            <div class="log-time">{{ formatTime(log.timestamp) }}</div>
            <div class="log-module">{{ log.module }}</div>
          </div>
          <div class="log-message">{{ log.message }}</div>
          <div v-if="log.details" class="log-details">
            <el-collapse>
              <el-collapse-item title="详细信息" :name="log.id">
                <pre>{{ log.details }}</pre>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>
      </div>

      <el-empty v-else description="暂无日志数据" :image-size="200" />
    </el-card>

    <!-- 分页 -->
    <div v-if="total > 0" class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[20, 50, 100, 200]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handlePageSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 响应式数据
const loading = ref(false)
const logs = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(50)

const filter = ref({
  level: '',
  module: '',
  dateRange: [],
  keyword: ''
})

const stats = ref({
  info: 0,
  warning: 0,
  error: 0,
  debug: 0
})

// 模拟日志数据
const mockLogs = [
  {
    id: 1,
    timestamp: new Date(Date.now() - 1000 * 60 * 5),
    level: 'info',
    module: 'search',
    message: '用户搜索图片：sunset.jpg，返回20个结果',
    details: null
  },
  {
    id: 2,
    timestamp: new Date(Date.now() - 1000 * 60 * 10),
    level: 'warning',
    module: 'upload',
    message: '上传文件大小超过建议限制：15.2MB',
    details: JSON.stringify({
      filename: 'large_image.jpg',
      size: '15.2MB',
      user_id: 'admin'
    }, null, 2)
  },
  {
    id: 3,
    timestamp: new Date(Date.now() - 1000 * 60 * 15),
    level: 'error',
    module: 'system',
    message: 'Faiss索引重建失败',
    details: JSON.stringify({
      error: 'IndexError: index out of range',
      stack_trace: 'Traceback (most recent call last):\n  File "faiss_service.py", line 156, in rebuild_index\n    ...'
    }, null, 2)
  },
  {
    id: 4,
    timestamp: new Date(Date.now() - 1000 * 60 * 20),
    level: 'info',
    module: 'auth',
    message: '管理员登录成功',
    details: JSON.stringify({
      username: 'admin',
      ip: '192.168.1.100',
      user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }, null, 2)
  },
  {
    id: 5,
    timestamp: new Date(Date.now() - 1000 * 60 * 25),
    level: 'debug',
    module: 'search',
    message: '特征提取完成，耗时：1.23秒',
    details: null
  }
]

// 加载日志数据
const loadLogs = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 这里应该调用实际的API
    let filteredLogs = [...mockLogs]
    
    // 应用筛选条件
    if (filter.value.level) {
      filteredLogs = filteredLogs.filter(log => log.level === filter.value.level)
    }
    
    if (filter.value.module) {
      filteredLogs = filteredLogs.filter(log => log.module === filter.value.module)
    }
    
    if (filter.value.keyword) {
      filteredLogs = filteredLogs.filter(log => 
        log.message.toLowerCase().includes(filter.value.keyword.toLowerCase())
      )
    }
    
    // 模拟分页
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    logs.value = filteredLogs.slice(start, end)
    total.value = filteredLogs.length
    
    // 计算统计数据
    stats.value = {
      info: mockLogs.filter(log => log.level === 'info').length,
      warning: mockLogs.filter(log => log.level === 'warning').length,
      error: mockLogs.filter(log => log.level === 'error').length,
      debug: mockLogs.filter(log => log.level === 'debug').length
    }
    
  } catch (error) {
    console.error('加载日志失败:', error)
    ElMessage.error('加载日志失败')
  } finally {
    loading.value = false
  }
}

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1
  loadLogs()
}

// 处理分页大小变化
const handlePageSizeChange = () => {
  currentPage.value = 1
  loadLogs()
}

// 处理页码变化
const handlePageChange = () => {
  loadLogs()
}

// 导出日志
const exportLogs = () => {
  // 创建CSV内容
  const headers = ['时间', '级别', '模块', '消息', '详情']
  const csvContent = [
    headers.join(','),
    ...logs.value.map(log => [
      formatTime(log.timestamp),
      log.level,
      log.module,
      `"${log.message}"`,
      log.details ? `"${log.details.replace(/"/g, '""')}"` : ''
    ].join(','))
  ].join('\n')
  
  // 创建下载链接
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `system_logs_${new Date().toISOString().split('T')[0]}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  ElMessage.success('日志导出完成')
}

// 清空日志
const clearLogs = () => {
  ElMessageBox.confirm('确定要清空所有日志吗？此操作不可恢复。', '清空确认', {
    type: 'warning'
  }).then(() => {
    logs.value = []
    total.value = 0
    stats.value = { info: 0, warning: 0, error: 0, debug: 0 }
    ElMessage.success('日志已清空')
  }).catch(() => {})
}

// 工具方法
const getLevelTagType = (level) => {
  const types = {
    info: '',
    warning: 'warning',
    error: 'danger',
    debug: 'info'
  }
  return types[level] || ''
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString('zh-CN')
}

// 组件挂载时加载数据
onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.system-logs {
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

.filter-card {
  margin-bottom: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #3498db;
}

.stat-item.info {
  border-left-color: #3498db;
}

.stat-item.warning {
  border-left-color: #f39c12;
}

.stat-item.error {
  border-left-color: #e74c3c;
}

.stat-item.debug {
  border-left-color: #95a5a6;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #2c3e50;
}

.stat-label {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-top: 5px;
}

.logs-card {
  margin-bottom: 20px;
}

.loading-container {
  padding: 20px;
}

.logs-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.log-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  border-left: 4px solid #dee2e6;
  transition: all 0.3s ease;
}

.log-item:hover {
  background: #e9ecef;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.log-item.info {
  border-left-color: #3498db;
}

.log-item.warning {
  border-left-color: #f39c12;
}

.log-item.error {
  border-left-color: #e74c3c;
}

.log-item.debug {
  border-left-color: #95a5a6;
}

.log-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 8px;
}

.log-level {
  flex-shrink: 0;
}

.log-time {
  color: #7f8c8d;
  font-size: 0.9rem;
  flex-shrink: 0;
}

.log-module {
  background: #ecf0f1;
  color: #2c3e50;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  flex-shrink: 0;
}

.log-message {
  color: #2c3e50;
  line-height: 1.5;
  margin-bottom: 8px;
}

.log-details {
  margin-top: 10px;
}

.log-details pre {
  background: #2c3e50;
  color: #ecf0f1;
  padding: 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  overflow-x: auto;
  margin: 0;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .log-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .stats-row .el-col {
    margin-bottom: 10px;
  }
}
</style> 