<template>
  <div class="image-upload">
    <div class="page-header">
      <h1>图片上传</h1>
      <el-button @click="goBack">返回列表</el-button>
    </div>

    <el-row :gutter="30">
      <!-- 左侧上传区域 -->
      <el-col :xs="24" :lg="14">
        <el-card class="upload-card">
          <template #header>
            <div class="card-header">
              <span>选择文件</span>
              <el-button v-if="selectedFiles.length > 0" type="text" @click="clearFiles">
                清空
              </el-button>
            </div>
          </template>

          <!-- 拖拽上传区域 -->
          <div
            class="upload-area"
            :class="{ 'drag-over': isDragOver }"
            @drop="handleDrop"
            @dragover="handleDragOver"
            @dragleave="handleDragLeave"
            @click="selectFiles"
          >
            <div v-if="selectedFiles.length === 0" class="upload-placeholder">
              <el-icon class="upload-icon"><UploadFilled /></el-icon>
              <p class="upload-text">拖拽图片到此处，或点击选择文件</p>
              <p class="upload-hint">支持 JPG、PNG、GIF、WEBP 格式，单文件最大 10MB</p>
            </div>

            <!-- 文件预览 -->
            <div v-else class="files-preview">
              <div
                v-for="(file, index) in selectedFiles"
                :key="index"
                class="file-preview-item"
              >
                <div class="preview-image">
                  <img :src="file.preview" :alt="file.name" />
                  <div class="preview-overlay">
                    <el-button
                      type="danger"
                      :icon="Delete"
                      size="small"
                      @click.stop="removeFile(index)"
                    >
                      删除
                    </el-button>
                  </div>
                </div>
                <div class="file-info">
                  <div class="file-name">{{ file.name }}</div>
                  <div class="file-size">{{ formatFileSize(file.size) }}</div>
                  <el-progress
                    v-if="file.uploading"
                    :percentage="file.progress"
                    :status="file.status"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- 隐藏的文件选择器 -->
          <input
            ref="fileInput"
            type="file"
            multiple
            accept="image/*"
            style="display: none"
            @change="handleFileSelect"
          />

          <!-- 批量操作 -->
          <div v-if="selectedFiles.length > 0" class="batch-actions">
            <el-row justify="space-between" align="middle">
              <el-col :span="12">
                <span>已选择 {{ selectedFiles.length }} 个文件</span>
              </el-col>
              <el-col :span="12" class="text-right">
                <el-button
                  v-if="!uploading"
                  type="primary"
                  :loading="uploading"
                  @click="startUpload"
                >
                  开始上传
                </el-button>
                <el-button v-else type="warning" @click="cancelUpload">
                  取消上传
                </el-button>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧表单区域 -->
      <el-col :xs="24" :lg="10">
        <el-card class="form-card">
          <template #header>
            <span>图片信息</span>
          </template>

          <el-form :model="uploadForm" label-width="80px">
            <el-form-item label="描述">
              <el-input
                v-model="uploadForm.description"
                type="textarea"
                :rows="3"
                placeholder="为图片添加描述..."
              />
            </el-form-item>

            <el-form-item label="标签">
              <el-input
                v-model="uploadForm.tags"
                placeholder="用逗号分隔多个标签，如：风景,自然,山水"
              />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 上传统计 -->
        <el-card class="stats-card" style="margin-top: 20px;">
          <template #header>
            <span>上传统计</span>
          </template>

          <div class="upload-stats">
            <div class="stat-item">
              <div class="stat-label">成功</div>
              <div class="stat-value success">{{ uploadStats.success }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">失败</div>
              <div class="stat-value error">{{ uploadStats.failed }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">总数</div>
              <div class="stat-value">{{ uploadStats.total }}</div>
            </div>
          </div>

          <el-progress
            v-if="uploading"
            :percentage="uploadProgress"
            :stroke-width="6"
            class="overall-progress"
          />
        </el-card>

        <!-- 最近上传 -->
        <el-card v-if="recentUploads.length > 0" class="recent-card" style="margin-top: 20px;">
          <template #header>
            <span>最近上传</span>
          </template>

          <div class="recent-uploads">
            <div
              v-for="upload in recentUploads"
              :key="upload.id"
              class="recent-item"
            >
              <img :src="getImageUrl(upload)" :alt="upload.filename" />
              <div class="recent-info">
                <div class="recent-name">{{ upload.original_name }}</div>
                <div class="recent-time">{{ formatDate(upload.upload_time) }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { UploadFilled, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElNotification } from 'element-plus'
import { imageApi } from '@/api/search'

const router = useRouter()

// 响应式数据
const fileInput = ref(null)
const selectedFiles = ref([])
const isDragOver = ref(false)
const uploading = ref(false)
const uploadStats = ref({ success: 0, failed: 0, total: 0 })
const recentUploads = ref([])

const uploadForm = ref({
  description: '',
  tags: ''
})

// 计算属性
const uploadProgress = computed(() => {
  if (uploadStats.value.total === 0) return 0
  return Math.round(((uploadStats.value.success + uploadStats.value.failed) / uploadStats.value.total) * 100)
})

// 文件处理方法
const selectFiles = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  addFiles(files)
  event.target.value = '' // 清空input
}

const handleDrop = (event) => {
  event.preventDefault()
  isDragOver.value = false
  
  const files = Array.from(event.dataTransfer.files)
  const imageFiles = files.filter(file => file.type.startsWith('image/'))
  
  if (imageFiles.length !== files.length) {
    ElMessage.warning('只能上传图片文件')
  }
  
  if (imageFiles.length > 0) {
    addFiles(imageFiles)
  }
}

const handleDragOver = (event) => {
  event.preventDefault()
  isDragOver.value = true
}

const handleDragLeave = (event) => {
  event.preventDefault()
  isDragOver.value = false
}

const addFiles = (files) => {
  files.forEach(file => {
    // 检查文件大小
    if (file.size > 10 * 1024 * 1024) {
      ElMessage.error(`文件 ${file.name} 超过 10MB 大小限制`)
      return
    }

    // 检查是否已存在
    const exists = selectedFiles.value.some(f => f.name === file.name && f.size === file.size)
    if (exists) {
      ElMessage.warning(`文件 ${file.name} 已存在`)
      return
    }

    // 创建预览
    const reader = new FileReader()
    reader.onload = (e) => {
      selectedFiles.value.push({
        file,
        name: file.name,
        size: file.size,
        preview: e.target.result,
        uploading: false,
        progress: 0,
        status: ''
      })
    }
    reader.readAsDataURL(file)
  })
}

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
}

const clearFiles = () => {
  selectedFiles.value = []
}

// 上传方法
const startUpload = async () => {
  if (selectedFiles.value.length === 0) {
    ElMessage.warning('请先选择文件')
    return
  }

  uploading.value = true
  uploadStats.value = { success: 0, failed: 0, total: selectedFiles.value.length }

  for (let i = 0; i < selectedFiles.value.length; i++) {
    const fileItem = selectedFiles.value[i]
    try {
      fileItem.uploading = true
      fileItem.progress = 0
      
      await uploadSingleFile(fileItem)
      
      fileItem.progress = 100
      fileItem.status = 'success'
      uploadStats.value.success++
      
    } catch (error) {
      console.error('上传失败:', error)
      fileItem.progress = 100
      fileItem.status = 'exception'
      uploadStats.value.failed++
    } finally {
      fileItem.uploading = false
    }
  }

  uploading.value = false

  // 显示结果通知
  if (uploadStats.value.success > 0) {
    ElNotification({
      title: '上传完成',
      message: `成功上传 ${uploadStats.value.success} 张图片${uploadStats.value.failed > 0 ? `，失败 ${uploadStats.value.failed} 张` : ''}`,
      type: 'success',
      duration: 3000
    })
  }

  // 刷新最近上传
  loadRecentUploads()
}

const uploadSingleFile = async (fileItem) => {
  const formData = new FormData()
  formData.append('file', fileItem.file)
  formData.append('description', uploadForm.value.description)
  formData.append('tags', uploadForm.value.tags)

  // 模拟上传进度
  const progressInterval = setInterval(() => {
    if (fileItem.progress < 90) {
      fileItem.progress += 10
    }
  }, 200)

  try {
    const response = await imageApi.uploadImage(formData)
    clearInterval(progressInterval)
    
    if (response.success) {
      fileItem.progress = 100
      return response.data
    } else {
      throw new Error(response.message || '上传失败')
    }
  } catch (error) {
    clearInterval(progressInterval)
    throw error
  }
}

const cancelUpload = () => {
  uploading.value = false
  selectedFiles.value.forEach(file => {
    file.uploading = false
    file.progress = 0
    file.status = ''
  })
}

// 工具方法
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

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

const goBack = () => {
  router.push('/admin/images')
}

// 加载最近上传
const loadRecentUploads = async () => {
  try {
    const response = await imageApi.getImages({ page: 1, page_size: 5 })
    if (response.success) {
      recentUploads.value = response.data.images || []
    }
  } catch (error) {
    console.error('加载最近上传失败:', error)
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadRecentUploads()
})
</script>

<style scoped>
.image-upload {
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

.upload-card {
  min-height: 500px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-area {
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover,
.upload-area.drag-over {
  border-color: #409eff;
  background-color: rgba(64, 158, 255, 0.05);
}

.upload-placeholder {
  color: #909399;
}

.upload-icon {
  font-size: 4rem;
  color: #c0c4cc;
  margin-bottom: 20px;
}

.upload-text {
  font-size: 1.1rem;
  margin: 10px 0;
}

.upload-hint {
  font-size: 0.9rem;
  color: #c0c4cc;
}

.files-preview {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
  width: 100%;
}

.file-preview-item {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.file-preview-item:hover {
  transform: translateY(-2px);
}

.preview-image {
  position: relative;
  width: 100%;
  height: 100px;
  overflow: hidden;
}

.preview-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-overlay {
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

.file-preview-item:hover .preview-overlay {
  opacity: 1;
}

.file-info {
  padding: 10px;
}

.file-name {
  font-size: 0.85rem;
  color: #2c3e50;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 5px;
}

.file-size {
  font-size: 0.8rem;
  color: #7f8c8d;
  margin-bottom: 8px;
}

.batch-actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.text-right {
  text-align: right;
}

.form-card .el-form-item {
  margin-bottom: 20px;
}

.upload-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
}

.stat-value.success {
  color: #67c23a;
}

.stat-value.error {
  color: #f56c6c;
}

.overall-progress {
  margin-top: 10px;
}

.recent-uploads {
  max-height: 200px;
  overflow-y: auto;
}

.recent-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.recent-item:last-child {
  border-bottom: none;
}

.recent-item img {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 4px;
  margin-right: 10px;
}

.recent-info {
  flex: 1;
}

.recent-name {
  font-size: 0.9rem;
  color: #2c3e50;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recent-time {
  font-size: 0.8rem;
  color: #7f8c8d;
  margin-top: 2px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .upload-area {
    padding: 20px;
    min-height: 200px;
  }
  
  .upload-icon {
    font-size: 3rem;
  }
  
  .files-preview {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 10px;
  }
  
  .upload-stats {
    flex-direction: column;
    gap: 10px;
  }
}
</style> 