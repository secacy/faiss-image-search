<template>
  <div class="image-management">
    <div class="page-header">
      <h1>图片管理</h1>
      <div class="page-actions">
        <el-button type="primary" :icon="Plus" @click="goToUpload">
          上传图片
        </el-button>
        <el-button :icon="Refresh" @click="refreshData">
          刷新
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="8">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索图片名称..."
            :prefix-icon="Search"
            @input="handleSearch"
            clearable
          />
        </el-col>
        <el-col :xs="12" :sm="4">
          <el-select v-model="pageSize" @change="handlePageSizeChange" placeholder="每页显示">
            <el-option label="20张" :value="20" />
            <el-option label="50张" :value="50" />
            <el-option label="100张" :value="100" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <!-- 批量操作 -->
    <div v-if="selectedImages.length > 0" class="batch-actions">
      <el-alert
        :title="`已选择 ${selectedImages.length} 张图片`"
        type="info"
        :closable="false"
      >
        <template #default>
          <div class="batch-buttons">
            <el-button type="danger" size="small" @click="batchDelete">
              删除选中
            </el-button>
            <el-button size="small" @click="clearSelection">
              清除选择
            </el-button>
          </div>
        </template>
      </el-alert>
    </div>

    <!-- 图片列表 -->
    <el-card class="images-card">
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="6" animated />
      </div>

      <div v-else-if="images.length > 0" class="images-grid">
        <div
          v-for="image in images"
          :key="image.id"
          class="image-item"
          :class="{ selected: selectedImages.includes(image.id) }"
        >
          <!-- 选择框 -->
          <el-checkbox
            v-model="selectedImages"
            :label="image.id"
            class="image-checkbox"
          />

          <!-- 图片容器 -->
          <div class="image-container" @click="openImageDetail(image)">
            <img
              :src="getImageUrl(image)"
              :alt="image.filename"
              @error="handleImageError"
              loading="lazy"
            />
            
            <!-- 悬停操作 -->
            <div class="image-overlay">
              <div class="image-actions">
                <el-button type="primary" size="small" :icon="View" @click.stop="openImageDetail(image)">
                  查看
                </el-button>
                <el-button type="danger" size="small" :icon="Delete" @click.stop="deleteImage(image)">
                  删除
                </el-button>
              </div>
            </div>
          </div>

          <!-- 图片信息 -->
          <div class="image-info">
            <h4 class="image-title">{{ image.original_name || image.filename }}</h4>
            <div class="image-meta">
              <span>{{ formatFileSize(image.file_size) }}</span>
              <span>{{ image.width }}×{{ image.height }}</span>
            </div>
            <div class="image-date">
              {{ formatDate(image.upload_time) }}
            </div>
          </div>
        </div>
      </div>

      <el-empty v-else description="暂无图片数据" :image-size="200" />
    </el-card>

    <!-- 分页 -->
    <div v-if="total > 0" class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handlePageSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 图片详情对话框 -->
    <el-dialog v-model="showImageDetail" :title="currentImage?.original_name" width="80%">
      <div v-if="currentImage" class="image-detail">
        <div class="detail-image">
          <img :src="getImageUrl(currentImage)" :alt="currentImage.filename" />
        </div>
        <div class="detail-info">
          <el-descriptions title="图片信息" :column="2" border>
            <el-descriptions-item label="原始文件名">{{ currentImage.original_name }}</el-descriptions-item>
            <el-descriptions-item label="存储文件名">{{ currentImage.filename }}</el-descriptions-item>
            <el-descriptions-item label="文件大小">{{ formatFileSize(currentImage.file_size) }}</el-descriptions-item>
            <el-descriptions-item label="图片尺寸">{{ currentImage.width }} × {{ currentImage.height }}</el-descriptions-item>
            <el-descriptions-item label="格式">{{ currentImage.format?.toUpperCase() }}</el-descriptions-item>
            <el-descriptions-item label="上传时间">{{ formatDate(currentImage.upload_time) }}</el-descriptions-item>
            <el-descriptions-item label="文件路径" :span="2">{{ currentImage.file_path }}</el-descriptions-item>
            <el-descriptions-item label="MD5哈希" :span="2">{{ currentImage.hash_value }}</el-descriptions-item>
            <el-descriptions-item label="描述" :span="2">{{ currentImage.description || '无' }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showImageDetail = false">关闭</el-button>
          <el-button type="danger" @click="deleteImage(currentImage)">删除图片</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Refresh, Search, View, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { imageApi } from '@/api/search'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const images = ref([])
const total = ref(0)
const totalSize = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchKeyword = ref('')
const selectedImages = ref([])
const showImageDetail = ref(false)
const currentImage = ref(null)

// 加载图片列表
const loadImages = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchKeyword.value
    }
    
    const response = await imageApi.getImages(params)
    if (response.success) {
      images.value = response.data.images || []
      total.value = response.data.pagination?.total || 0
      
      // 计算总大小
      totalSize.value = images.value.reduce((sum, img) => sum + (img.file_size || 0), 0)
    } else {
      ElMessage.error(response.message || '加载图片失败')
    }
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

// 删除图片
const deleteImage = async (image) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除图片 "${image.original_name || image.filename}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await imageApi.deleteImage(image.id)
    if (response.success) {
      ElMessage.success('删除成功')
      showImageDetail.value = false
      loadImages()
    } else {
      ElMessage.error(response.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除图片失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 批量删除
const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedImages.value.length} 张图片吗？`,
      '批量删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里需要后端支持批量删除接口
    for (const imageId of selectedImages.value) {
      await imageApi.deleteImage(imageId)
    }
    
    ElMessage.success('批量删除成功')
    selectedImages.value = []
    loadImages()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

// 清除选择
const clearSelection = () => {
  selectedImages.value = []
}

// 刷新数据
const refreshData = () => {
  loadImages()
}

// 跳转到上传页面
const goToUpload = () => {
  router.push('/admin/upload')
}

// 组件挂载时加载数据
onMounted(() => {
  loadImages()
})
</script>

<style scoped>
.image-management {
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



.batch-actions {
  margin-bottom: 20px;
}

.batch-buttons {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.images-card {
  margin-bottom: 20px;
}

.loading-container {
  padding: 20px;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.image-item {
  position: relative;
  border: 2px solid transparent;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.image-item.selected {
  border-color: #409eff;
  background-color: rgba(64, 158, 255, 0.1);
}

.image-checkbox {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 2;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
  padding: 2px;
}

.image-container {
  position: relative;
  width: 100%;
  height: 150px;
  overflow: hidden;
  border-radius: 8px;
  cursor: pointer;
}

.image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.image-item:hover .image-container img {
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

.image-item:hover .image-overlay {
  opacity: 1;
}

.image-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.image-info {
  padding: 10px;
  background: white;
}

.image-title {
  font-size: 0.9rem;
  margin: 0 0 5px 0;
  color: #2c3e50;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.image-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #7f8c8d;
  margin-bottom: 5px;
}

.image-date {
  font-size: 0.8rem;
  color: #95a5a6;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
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
  max-height: 400px;
  border-radius: 8px;
}

.detail-info {
  flex: 1;
}

.dialog-footer {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .images-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
  }
  
  .image-detail {
    flex-direction: column;
    gap: 20px;
  }
  
  .image-actions {
    flex-direction: row;
    gap: 5px;
  }
}
</style>