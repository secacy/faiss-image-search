<template>
  <div class="home-page">

    <!-- 搜图区域 -->
    <div class="search-section">
      <div class="search-container">
        <!-- 左侧：上传和搜索区域 -->
        <div class="upload-search-area">
          <el-card class="search-card card" shadow="never">

            <!-- 上传搜索区域 -->
            <div class="upload-section">
              <el-upload
                ref="uploadRef"
                class="upload-demo"
                drag
                :auto-upload="false"
                :on-change="handleFileChange"
                :show-file-list="false"
                accept="image/*"
              >

                  <el-icon class="el-icon--upload" size="48">
                    <UploadFilled />
                  </el-icon>
                  <div class="el-upload__text">
                    将图片拖到此处，或<em>点击上传</em>
                  </div>

              </el-upload>
                <!-- OR 分隔线 -->
                <div class="separator">
                  <span class="separator-text">OR</span>
                </div>

                <!-- URL输入区域 -->
                <div class="url-section">
                  <el-input
                    v-model="imageUrl"
                    placeholder="输入图片地址"
                    size="large"
                    clearable
                    class="url-input"
                  >
                    <template #prepend>
                      <el-icon><Link /></el-icon>
                    </template>
                  </el-input>
                </div>
              

              <!-- 预览上传的图片 -->
              <div v-if="uploadedFile" class="preview-section fade-in">
                <el-divider content-position="left">图片预览</el-divider>
                <div class="preview-container">
                  <img :src="previewUrl" class="preview-image" alt="预览图片" />
                  <div class="preview-info">
                    <p><strong>文件名：</strong>{{ uploadedFile.name }}</p>
                    <p><strong>大小：</strong>{{ formatFileSize(uploadedFile.size) }}</p>
                    <p><strong>类型：</strong>{{ uploadedFile.type }}</p>
                  </div>
                </div>
              </div>
              
            </div>

            

            <!-- 搜索按钮 -->
            <div class="search-actions">
              <el-button
                type="primary"
                size="large"
                :loading="searching"
                :disabled="!canSearch"
                @click="performSearch"
                class="btn-primary search-btn"
              >
                <el-icon><Search /></el-icon>
                开始搜索
              </el-button>
            </div>
          </el-card>
        </div>

        <!-- 右侧：看板娘区域 -->
        <div class="mascot-section">
          <div class="mascot-area">
            <div class="mascot-character">
              <el-icon><Picture /></el-icon>
            </div>
            <div class="mascot-text">
              <p>🌟 欢迎使用图与图寻！</p>
              <p>我将为您寻找相似图像</p>
              <p>数据库中最相似的图像</p>
              <p>带您探索视觉世界的奇妙~ ✨</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜索结果展示（如果有结果才显示，并跳转到结果页） -->

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElLoading } from 'element-plus'
import { UploadFilled, Search, Link, Picture } from '@element-plus/icons-vue'
import { searchApi } from '@/api/search'

const router = useRouter()

// 响应式数据
const uploadedFile = ref(null)
const previewUrl = ref('')
const imageUrl = ref('')
const searching = ref(false)

// 搜索参数
const searchParams = ref({
  k: 10
})

// 计算属性
const canSearch = computed(() => {
  return uploadedFile.value !== null || imageUrl.value.trim() !== ''
})

// 处理文件上传
const handleFileChange = (file) => {
  const { raw } = file
  
  // 检查文件类型
  if (!raw.type.startsWith('image/')) {
    ElMessage.error('请选择图片文件')
    return
  }
  
  // 检查文件大小（10MB）
  if (raw.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 10MB')
    return
  }
  
  uploadedFile.value = raw
  
  // 创建预览URL
  const reader = new FileReader()
  reader.onload = (e) => {
    previewUrl.value = e.target.result
  }
  reader.readAsDataURL(raw)
}

// 执行搜索
const performSearch = async () => {
  if (!canSearch.value) return
  
  searching.value = true
  
  try {
    let response
    let queryType = ''
    let queryImage = ''
    
    if (uploadedFile.value) {
      // 文件上传搜索
      const formData = new FormData()
      formData.append('file', uploadedFile.value)
      formData.append('k', searchParams.value.k)
      
      response = await searchApi.searchByUpload(formData)
      queryType = 'upload'
      queryImage = previewUrl.value
    } else if (imageUrl.value.trim()) {
      // URL搜索
      const formData = new FormData()
      formData.append('image_url', imageUrl.value)
      formData.append('k', searchParams.value.k)
      
      response = await searchApi.searchByUrl(formData)
      queryType = 'url'
      queryImage = imageUrl.value
    }
    
    if (response.success) {
      // 跳转到搜索结果页面，传递数据
      router.push({
        name: 'SearchResults',
        state: {
          results: response.data.results,
          searchParams: response.data.search_params,
          queryImage: queryImage,
          queryType: queryType
        }
      })
    } else {
      ElMessage.error('搜索失败，请重试')
    }
  } catch (error) {
    console.error('搜索错误：', error)
    ElMessage.error('搜索失败：' + (error.message || '网络错误'))
  } finally {
    searching.value = false
  }
}


// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

onMounted(() => {
  // 页面加载完成后的初始化逻辑
})
</script>

<style scoped>
.home-page {
  height: 100vh;
  background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-light) 100%);
  padding-bottom: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
}


/* 搜图区域 */
.search-section {
  padding: 20px;
  flex: 1;
  display: flex;
  align-items: center;
}

.search-container {
  max-width: 900px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 30px;
  align-items: center;
  width: 100%;
}

@media (max-width: 1024px) {
  .search-container {
    grid-template-columns: 1fr;
    gap: 20px;
    max-width: 500px;
  }
}

.upload-search-area {
  width: 100%;
}

.search-card {
  border: none;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-light);
}


.upload-section {
  margin: 20px 0;
}

.upload-content {
  border-color: var(--border-color);
  background: var(--bg-secondary);
  transition: all 0.3s ease;
  padding: 25px 20px;
}

.upload-content:hover {
  border-color: var(--primary-color);
  background: var(--bg-light);
  transform: translateY(-2px);
}

.preview-section {
  margin-top: 20px;
}

.preview-container {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.preview-image {
  max-width: 160px;
  max-height: 160px;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-light);
}

.preview-info {
  flex: 1;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: var(--border-radius);
  border: 1px solid var(--border-color);
}

.preview-info p {
  margin: 6px 0;
  font-size: 13px;
  color: var(--text-primary);
}

/* OR 分隔线 */
.separator {
  text-align: center;
  margin: 20px 0;
  position: relative;
}

.separator::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--border-color);
}

.separator-text {
  background: var(--bg-primary);
  padding: 0 16px;
  color: var(--text-secondary);
  font-size: 14px;
  position: relative;
  z-index: 1;
}

.url-section {
  margin: 0px 0;
}

.url-input {
  border-radius: 24px;
}

.url-tip {
  margin-top: 12px;
}

.search-params {
  margin: 20px 0;
}

.params-row {
  display: flex;
  gap: 20px;
  align-items: center;
}

.param-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.param-item label {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
  white-space: nowrap;
}

.search-actions {
  text-align: center;
  margin-top: 20px;
}

.search-btn {
  background: linear-gradient(45deg, var(--primary-color), var(--primary-light));
  border: none;
  font-weight: 600;
  padding: 12px 30px;
  box-shadow: var(--shadow-light);
  transition: all 0.3s ease;
}

.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-medium);
  background: linear-gradient(45deg, var(--primary-dark), var(--primary-color));
}

/* 看板娘区域 */
.mascot-section {
  display: flex;
  align-items: center;
}

/* Element Plus 输入框圆角样式覆盖 */
:deep(.el-input__wrapper) {
  border-radius: 24px;
  padding: 0 18px;
  border: 2px solid var(--border-color);
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.1);
}

:deep(.el-input__wrapper.is-focus) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

:deep(.el-input-group__prepend) {
  border-radius: 24px 0 0 24px;
  border: 2px solid var(--border-color);
  border-right: none;
  background: var(--bg-secondary);
}

:deep(.el-input-group .el-input__wrapper) {
  border-radius: 0 24px 24px 0;
}

:deep(.el-input-group:hover .el-input-group__prepend) {
  border-color: var(--primary-color);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .home-page {
    height: 100vh;
    height: 100dvh; /* 移动端精确视口高度 */
  }
  
  .search-section {
    padding: 15px;
  }
  
  .search-container {
    max-width: 95%;
  }
  
  .upload-content {
    padding: 20px 15px;
  }
  
  .preview-image {
    max-width: 120px;
    max-height: 120px;
  }
  
  .search-params {
    margin: 15px 0;
  }
  
  .separator {
    margin: 15px 0;
  }
}


</style> 