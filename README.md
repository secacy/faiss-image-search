# 图与图寻 (Pic Search)

基于 Faiss 的以图搜图工具，支持图像数据集管理和高效的相似图像检索。

## 功能特性

### 🖼️ 图像数据集导入和管理
- 支持单张/批量图片上传
- 数据库图片浏览与分页展示
- 图片删除功能

### 🔍 基于内容的图像检索
- 多种图片输入方式：拖拽、文件选择、URL输入
- 基于深度学习的特征提取（ResNet预训练模型）
- Faiss高效相似度匹配

### 📊 检索结果TOP-K展示
- 可自定义K值（返回最相似的前K张图片）
- 图片墙展示界面
- 相似度评分显示
- 图片预览与大图查看

## 技术栈

### 前端
- **框架**: Vue 3
- **UI组件**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP客户端**: Axios

### 后端
- **框架**: FastAPI
- **图像处理**: PyTorch + torchvision
- **特征提取**: 预训练ResNet模型
- **相似度检索**: Faiss
- **数据库**: MySQL
- **文件存储**: 本地文件系统

### 基础设施
- **配置管理**: YAML
- **认证**: JWT Token
- **日志**: Python logging

## 项目结构

```
faiss-image-search-v3/
├── backend/                # 后端服务
│   ├── app/               # FastAPI应用
│   ├── models/            # 数据模型
│   ├── services/          # 业务逻辑
│   ├── utils/             # 工具函数
│   └── requirements.txt   # Python依赖
├── frontend/              # 前端应用
│   ├── src/               # Vue源码
│   ├── public/            # 静态资源
│   └── package.json       # Node依赖
├── data/                  # 数据目录
│   ├── images/            # 图片存储
│   └── index/             # Faiss索引文件
├── config/                # 配置文件
└── docs/                  # 文档
```

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- 推荐：CUDA支持的GPU（可选，用于加速）

### 一键安装
```bash
# 运行安装脚本
chmod +x install.sh
./install.sh
```

### 手动安装

#### 1. 克隆项目
```bash
git clone <repository-url>
cd faiss-image-search-v3
```

#### 2. 后端设置
```bash
cd backend
pip install -r requirements.txt
```

#### 3. 前端设置
```bash
cd frontend
npm install
```

#### 4. 数据库初始化
```bash
# 创建数据库和表结构
mysql -u root -p < config/database.sql
```

#### 5. 配置文件
编辑 `config/app.yaml`，修改数据库连接信息：
```yaml
database:
  host: "localhost"
  port: 3306
  username: "your_username"
  password: "your_password"
  database: "pic_search"
```

### 启动服务

#### 方式一：使用启动脚本
```bash
# 启动后端（开发模式）
python scripts/start.py --reload

# 启动前端
cd frontend && npm run dev
```

#### 方式二：手动启动
```bash
# 启动后端
cd backend
python main.py

# 启动前端（新终端）
cd frontend
npm run dev
```

## 访问地址

- 前端应用: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- 管理后台: http://localhost:3000/admin

## 开发指南

详细的开发文档请参考 [docs/](./docs/) 目录。

## 许可证

MIT License 


## 管理后台说明
默认账号：admin / admin123