<template>
  <div class="search-results-page">
    <!-- 顶部区域：原始图片展示 + 返回按钮 -->
    <div class="result-header">
      <div class="header-container">
        <!-- 返回按钮 -->
        <div class="back-section">
          <el-button 
            type="primary" 
            @click="goBack" 
            class="btn-primary back-btn"
            size="large"
          >
            <el-icon><ArrowLeft /></el-icon>
            返回搜索
          </el-button>
        </div>

        <!-- 原始图片缩略图 -->
        <div class="query-image-section">
          <div class="query-image-container">
            <img 
              v-if="queryImage" 
              :src="queryImage" 
              class="query-image" 
              alt="搜索的原始图片"
            />
            <div class="query-info">
              <h2 class="query-title">搜索结果</h2>
              <p class="query-desc">
                <span v-if="queryType === 'upload'">上传图片搜索</span>
                <span v-else-if="queryType === 'url'">URL图片搜索</span>
              </p>
              <div class="search-stats">
                <el-tag v-if="results.length > 0" type="success" size="large">
                  找到 {{ results.length }} 个相似图片
                </el-tag>
                <el-tag v-if="searchDuration" type="info" size="large">
                  耗时 {{ searchDuration }}s
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜索结果区域 -->
    <div class="results-section">
      <div class="results-container">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <div class="loading-content">
            <div class="loading-spinner"></div>
            <p>正在搜索相似图片...</p>
          </div>
        </div>

        <!-- 结果网格 - 每行3个卡片 -->
        <div v-else-if="results.length > 0" class="image-grid fade-in">
          <div
            v-for="(result, index) in results"
            :key="result.image?.id || index"
            class="image-card"
            @click="openImageDetail(result.image)"
          >
            <!-- 排名标识 -->
            <div class="rank-badge">
              <span>#{{ index + 1 }}</span>
            </div>

            <!-- 图片容器 -->
            <div class="image-container">
              <img
                :src="getImageUrl(result.image)"
                :alt="result.image?.original_name || result.image?.filename"
                @error="handleImageError"
                loading="lazy"
              />
              
              <!-- 相似度分数覆盖层 -->
              <div class="similarity-overlay">
                <div class="similarity-badge">
                  {{ (result.similarity * 100).toFixed(1) }}%
                </div>
              </div>

              <!-- 悬停操作 -->
              <div class="image-overlay">
                <div class="image-actions">
                  <el-button
                    type="info"
                    size="small"
                    @click.stop="downloadImage(result.image)"
                    class="action-btn"
                  >
                    <el-icon><Download /></el-icon>
                    下载
                  </el-button>
                </div>
              </div>
            </div>

            <!-- 图片信息 -->
            <div class="info">
              <div class="filename">
                {{ result.image?.original_name || result.image?.filename || '未知文件' }}
              </div>
              <div class="meta">
                <span>{{ formatFileSize(result.image?.file_size) }}</span>
                <span>{{ result.image?.width }}×{{ result.image?.height }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 空结果状态 -->
        <div v-else-if="!loading && hasSearched" class="empty-state">
          <div class="empty-icon">🔍</div>
          <div class="empty-text">没有找到相似的图片</div>
          <div class="empty-description">
            尝试使用其他图片进行搜索，或者检查图片是否清晰
          </div>
          <el-button type="primary" @click="goBack" class="btn-primary">
            重新搜索
          </el-button>
        </div>
      </div>
    </div>

    <!-- 图片详情对话框 -->
    <el-dialog
      v-model="showImageDetail"
      :title="currentImage?.original_name || currentImage?.filename"
      width="80%"
      top="5vh"
      class="image-detail-dialog"
    >
      <div v-if="currentImage" class="image-detail">
        <div class="detail-image">
          <img :src="getImageUrl(currentImage)" :alt="currentImage.original_name" />
        </div>
        <div class="detail-info">
          <el-descriptions title="图片信息" :column="2" border>
            <el-descriptions-item label="文件名">
              {{ currentImage.original_name || currentImage.filename }}
            </el-descriptions-item>
            <el-descriptions-item label="文件大小">
              {{ formatFileSize(currentImage.file_size) }}
            </el-descriptions-item>
            <el-descriptions-item label="图片尺寸">
              {{ currentImage.width }} × {{ currentImage.height }}
            </el-descriptions-item>
            <el-descriptions-item label="上传时间">
              {{ formatDate(currentImage.upload_time) }}
            </el-descriptions-item>
            <el-descriptions-item label="文件路径" :span="2">
              {{ currentImage.file_path }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showImageDetail = false">关闭</el-button>
          <el-button type="success" @click="downloadImage(currentImage)" class="btn-accent">
            下载图片
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Search, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { searchByFile, searchByUrl, searchByImageId } from '@/api/search'

const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(false)
const results = ref([])
const totalResults = ref(0)
const hasSearched = ref(false)
const showImageDetail = ref(false)
const currentImage = ref(null)

// 搜索参数
const topK = ref(10)
const threshold = ref(0.5)
const searchType = ref('')
const searchUrl = ref('')
const queryFilename = ref('')

// 搜索相关数据
const queryImage = ref('')
const queryType = ref('')
const searchDuration = ref(0)

// 从路由参数获取搜索信息
const initSearchFromRoute = () => {
  const query = route.query
  searchType.value = query.type || ''
  searchUrl.value = query.url || ''
  queryFilename.ref = query.filename || ''
  topK.value = Number(query.top_k) || 10
  threshold.value = Number(query.threshold) || 0.5

  // 立即执行搜索
  if (searchType.value) {
    performSearch()
  }
}

// 执行搜索
const performSearch = async () => {
  loading.value = true
  hasSearched.value = true
  
  try {
    let response
    const params = {
      top_k: topK.value,
      threshold: threshold.value
    }

    switch (searchType.value) {
      case 'file':
        // 文件搜索需要从前一个页面传递的文件数据
        ElMessage.error('文件搜索需要重新上传文件')
        router.push('/')
        return
        
      case 'url':
        response = await searchByUrl(searchUrl.value, params)
        break
        
      case 'image_id':
        response = await searchByImageId(route.query.image_id, params)
        break
        
      default:
        ElMessage.error('无效的搜索类型')
        router.push('/')
        return
    }

    results.value = response.data.results || []
    totalResults.value = results.value.length
    
    // 更新搜索相关数据
    queryImage.value = response.data.queryImage || ''
    queryType.value = response.data.queryType || ''
    searchDuration.value = response.data.searchParams?.duration || 0
  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败，请重试')
  } finally {
    loading.value = false
  }
}

// 处理参数变化
const handleParamsChange = () => {
  // 更新URL参数
  router.replace({
    query: {
      ...route.query,
      top_k: topK.value,
      threshold: threshold.value
    }
  })
}

// 获取图片URL
const getImageUrl = (image) => {
  if (!image) return '/placeholder.svg'
  
  // 如果有url字段直接使用
  if (image.url) {
    return image.url
  }
  
  // 否则构建URL
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  if (image.thumbnail_path) {
    return `${baseUrl}/static/thumbnails/${image.thumbnail_path.split('/').pop()}`
  } else if (image.file_path) {
    return `${baseUrl}/static/images/${image.file_path.split('/').pop()}`
  }
  
  return '/placeholder.svg'
}

// 处理图片加载错误
const handleImageError = (event) => {
  event.target.src = '/placeholder.svg'
}

// 获取相似度百分比
const getScorePercentage = (similarity) => {
  return Math.round(similarity * 100)
}

// 获取分数样式
const getScoreStyle = (similarity) => {
  const percentage = similarity * 100
  let color = '#e74c3c' // 红色 (低相似度)
  
  if (percentage >= 80) {
    color = '#27ae60' // 绿色 (高相似度)
  } else if (percentage >= 60) {
    color = '#f39c12' // 橙色 (中等相似度)
  }
  
  return {
    background: `conic-gradient(${color} ${percentage}%, #ecf0f1 ${percentage}%)`
  }
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleString('zh-CN')
}

// 打开图片详情
const openImageDetail = (image) => {
  currentImage.value = image
  showImageDetail.value = true
}


// 下载图片
const downloadImage = (image) => {
  if (!image) return
  
  const url = getImageUrl(image)
  const link = document.createElement('a')
  link.href = url
  link.download = image.original_name || image.filename || 'image'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  ElMessage.success('开始下载图片')
}

// 返回搜索页面
const goBack = () => {
  router.push({ name: 'Home' })
}

// 页面加载时获取搜索结果数据
onMounted(() => {
  // 从路由状态获取搜索结果数据
  const state = history.state
  if (state && state.results) {
    results.value = state.results
    queryImage.value = state.queryImage
    queryType.value = state.queryType
    searchDuration.value = state.searchParams?.duration || 0
    hasSearched.value = true
  } else {
    // 如果没有搜索结果数据，返回首页
    goBack()
  }
})
</script>

<style scoped>
.search-results-page {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-light) 100%);
}

/* 顶部区域 */
.result-header {
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  padding: 30px 20px;
  box-shadow: var(--shadow-light);
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 30px;
}

.back-section {
  flex-shrink: 0;
}

.back-btn {
  background: linear-gradient(45deg, var(--primary-color), var(--primary-light));
  border: none;
  font-weight: 600;
  padding: 12px 24px;
  box-shadow: var(--shadow-light);
  transition: all 0.3s ease;
}

.back-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-medium);
  background: linear-gradient(45deg, var(--primary-dark), var(--primary-color));
}

.query-image-section {
  flex: 1;
}

.query-image-container {
  display: flex;
  align-items: center;
  gap: 24px;
}

.query-image {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-light);
  border: 2px solid var(--border-color);
}

.query-info {
  flex: 1;
}

.query-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.query-desc {
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.search-stats {
  display: flex;
  gap: 12px;
}

/* 搜索结果区域 */
.results-section {
  padding: 40px 20px;
}

.results-container {
  max-width: 1200px;
  margin: 0 auto;
}

/* 加载状态 */
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.loading-content {
  text-align: center;
  color: var(--text-secondary);
}

.loading-content p {
  margin-top: 20px;
  font-size: 16px;
}

/* 图片卡片增强 */
.image-card {
  position: relative;
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-light);
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid var(--border-color);
}

.image-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-heavy);
}

.rank-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 2;
  background: linear-gradient(45deg, var(--accent-color), var(--accent-light));
  color: white;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: bold;
  box-shadow: var(--shadow-light);
}

.image-container {
  position: relative;
  overflow: hidden;
}

.image-container img {
  width: 100%;
  height: 240px;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.image-card:hover .image-container img {
  transform: scale(1.05);
}

.similarity-overlay {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 2;
}

.similarity-badge {
  background: linear-gradient(45deg, var(--primary-color), var(--primary-light));
  color: white;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: bold;
  box-shadow: var(--shadow-light);
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.3s ease;
}

.image-card:hover .image-overlay {
  opacity: 1;
}

.image-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  font-size: 12px;
  padding: 8px 16px;
  border-radius: var(--border-radius);
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .header-container {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
  }
  
  .query-image-container {
    flex-direction: column;
    text-align: center;
  }
}

@media (max-width: 640px) {
  .result-header {
    padding: 20px 16px;
  }
  
  .results-section {
    padding: 20px 16px;
  }
  
  .query-image {
    width: 100px;
    height: 100px;
  }
  
  .query-title {
    font-size: 20px;
  }
  
  .search-stats {
    flex-direction: column;
    gap: 8px;
  }
}

/* 图片详情对话框 */
.image-detail {
  display: flex;
  gap: 30px;
  align-items: flex-start;
}

.detail-image {
  flex-shrink: 0;
  max-width: 400px;
}

.detail-image img {
  width: 100%;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-light);
}

.detail-info {
  flex: 1;
}

@media (max-width: 768px) {
  .image-detail {
    flex-direction: column;
  }
  
  .detail-image {
    max-width: 100%;
  }
}
</style> 