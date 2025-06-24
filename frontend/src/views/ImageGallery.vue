<template>
  <div class="image-gallery">
    <div class="gallery-header">
      <h1>图片画廊</h1>
      <p>浏览系统中的所有图片</p>
    </div>

    <!-- 搜索和筛选栏 -->
    <div class="gallery-filters">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索图片名称..."
            @input="handleSearch"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :xs="12" :sm="6" :md="4">
          <el-select v-model="sortOrder" @change="handleSort" placeholder="排序方式">
            <el-option label="最新上传" value="newest" />
            <el-option label="最早上传" value="oldest" />
            <el-option label="文件大小" value="size" />
            <el-option label="文件名" value="name" />
          </el-select>
        </el-col>
        <el-col :xs="12" :sm="6" :md="4">
          <el-select v-model="pageSize" @change="handlePageSizeChange" placeholder="每页显示">
            <el-option label="12张" :value="12" />
            <el-option label="24张" :value="24" />
            <el-option label="48张" :value="48" />
            <el-option label="96张" :value="96" />
          </el-select>
        </el-col>
      </el-row>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="6" animated />
    </div>

    <!-- 图片网格 -->
    <div v-else class="image-grid">
      <div 
        v-for="image in images" 
        :key="image.id" 
        class="image-card"
        @click="openImageDetail(image)"
      >
        <div class="image-container">
          <img 
            :src="getImageUrl(image)" 
            :alt="image.filename"
            @error="handleImageError"
            loading="lazy"
          />
          <div class="image-overlay">
            <div class="image-actions">
              <el-button 
                type="primary" 
                size="small" 
                @click.stop="searchSimilar(image)"
                :icon="Search"
              >
                相似搜索
              </el-button>
              <el-button 
                type="info" 
                size="small" 
                @click.stop="downloadImage(image)"
                :icon="Download"
              >
                下载
              </el-button>
            </div>
          </div>
        </div>
        <div class="image-info">
          <h3 class="image-title">{{ image.filename }}</h3>
          <p class="image-meta">
            <span>{{ formatFileSize(image.file_size) }}</span>
            <span>{{ formatDate(image.upload_time) }}</span>
          </p>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty 
      v-if="!loading && images.length === 0" 
      description="暂无图片数据" 
      :image-size="200"
    />

    <!-- 分页 -->
    <div v-if="total > 0" class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[12, 24, 48, 96]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handlePageSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 图片详情对话框 -->
    <el-dialog 
      v-model="showImageDetail" 
      :title="currentImage?.filename"
      width="80%"
      top="5vh"
    >
      <div v-if="currentImage" class="image-detail">
        <div class="detail-image">
          <img :src="getImageUrl(currentImage)" :alt="currentImage.filename" />
        </div>
        <div class="detail-info">
          <el-descriptions title="图片信息" :column="2" border>
            <el-descriptions-item label="文件名">{{ currentImage.filename }}</el-descriptions-item>
            <el-descriptions-item label="文件大小">{{ formatFileSize(currentImage.file_size) }}</el-descriptions-item>
            <el-descriptions-item label="图片尺寸">{{ currentImage.width }} × {{ currentImage.height }}</el-descriptions-item>
            <el-descriptions-item label="上传时间">{{ formatDate(currentImage.upload_time) }}</el-descriptions-item>
            <el-descriptions-item label="文件路径" :span="2">{{ currentImage.file_path }}</el-descriptions-item>
            <el-descriptions-item label="哈希值" :span="2">{{ currentImage.hash }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showImageDetail = false">关闭</el-button>
          <el-button type="primary" @click="searchSimilar(currentImage)">相似搜索</el-button>
          <el-button type="success" @click="downloadImage(currentImage)">下载图片</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getImages } from '@/api/search'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const images = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(24)
const searchKeyword = ref('')
const sortOrder = ref('newest')
const showImageDetail = ref(false)
const currentImage = ref(null)

// 加载图片列表
const loadImages = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchKeyword.value,
      sort: sortOrder.value
    }
    
    const response = await getImages(params)
    images.value = response.data.items || []
    total.value = response.data.total || 0
  } catch (error) {
    console.error('加载图片失败:', error)
    ElMessage.error('加载图片失败')
  } finally {
    loading.value = false
  }
}

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1
  loadImages()
}

// 处理排序
const handleSort = () => {
  currentPage.value = 1
  loadImages()
}

// 处理分页大小变化
const handlePageSizeChange = () => {
  currentPage.value = 1
  loadImages()
}

// 处理页码变化
const handlePageChange = () => {
  loadImages()
}

// 获取图片URL
const getImageUrl = (imageOrPath) => {
  // 如果是图片对象且有url属性，优先使用
  if (typeof imageOrPath === 'object' && imageOrPath.url) {
    return imageOrPath.url
  }
  
  // 兼容字符串路径的情况
  const path = typeof imageOrPath === 'string' ? imageOrPath : imageOrPath?.file_path
  if (!path) return '/placeholder.svg'
  if (path.startsWith('http')) return path
  
  // 从完整路径中提取文件名
  const filename = path.split(/[/\\]/).pop()
  return `/static/images/${filename}`
}

// 处理图片加载错误
const handleImageError = (event) => {
  event.target.src = '/placeholder.svg'
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

// 打开图片详情
const openImageDetail = (image) => {
  currentImage.value = image
  showImageDetail.value = true
}

// 相似搜索
const searchSimilar = (image) => {
  router.push({
    name: 'SearchResults',
    query: { 
      type: 'image_id',
      image_id: image.id,
      filename: image.filename
    }
  })
}

// 下载图片
const downloadImage = (image) => {
  const link = document.createElement('a')
      link.href = getImageUrl(image)
  link.download = image.filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  ElMessage.success('开始下载图片')
}

// 组件挂载时加载数据
onMounted(() => {
  loadImages()
})
</script>

<style scoped>
.image-gallery {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.gallery-header {
  text-align: center;
  margin-bottom: 30px;
}

.gallery-header h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 10px;
}

.gallery-header p {
  font-size: 1.1rem;
  color: #7f8c8d;
}

.gallery-filters {
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.loading-container {
  padding: 20px;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.image-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}

.image-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.image-container {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.image-card:hover .image-container img {
  transform: scale(1.05);
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-card:hover .image-overlay {
  opacity: 1;
}

.image-actions {
  display: flex;
  gap: 10px;
}

.image-info {
  padding: 15px;
}

.image-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.image-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: #7f8c8d;
  margin: 0;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

.image-detail {
  display: flex;
  gap: 30px;
}

.detail-image {
  flex: 1;
  text-align: center;
}

.detail-image img {
  max-width: 100%;
  max-height: 500px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.detail-info {
  flex: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .image-gallery {
    padding: 15px;
  }
  
  .gallery-header h1 {
    font-size: 2rem;
  }
  
  .image-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
  }
  
  .image-detail {
    flex-direction: column;
    gap: 20px;
  }
}

@media (max-width: 480px) {
  .image-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 15px;
  }
  
  .gallery-filters {
    padding: 15px;
  }
  
  .image-actions {
    flex-direction: column;
    gap: 8px;
  }
}
</style> 