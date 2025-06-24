#!/bin/bash

echo "🚀 图与图寻 - 快速安装脚本"
echo "================================="

# 检查Python版本
echo "🐍 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python 3.8或更高版本"
    exit 1
fi

python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python版本: $python_version"

# 检查Node.js版本
echo "📦 检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo "❌ 未找到Node.js，请先安装Node.js 16或更高版本"
    exit 1
fi

node_version=$(node -v)
echo "✅ Node.js版本: $node_version"

# 创建虚拟环境（可选）
read -p "🤔 是否激活Python虚拟环境？(y/n): " create_venv
if [ "$create_venv" = "y" ] || [ "$create_venv" = "Y" ]; then
    echo "📦 激活虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
fi

# 安装后端依赖
echo "📦 安装后端依赖..."
cd backend
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ 后端依赖安装完成"
else
    echo "❌ 后端依赖安装失败"
    exit 1
fi
cd ..

# 安装前端依赖
echo "📦 安装前端依赖..."
cd frontend
npm install
if [ $? -eq 0 ]; then
    echo "✅ 前端依赖安装完成"
else
    echo "❌ 前端依赖安装失败"
    exit 1
fi
cd ..

# 创建必要的目录
echo "📁 创建项目目录..."
mkdir -p data/images
mkdir -p data/index
mkdir -p logs
echo "✅ 目录创建完成"

# 检查数据库配置
echo "🗄️  数据库配置..."
echo "请确保已安装并配置MySQL数据库"
echo "数据库初始化SQL文件位于: config/database.sql"
echo "配置文件位于: config/app.yaml"

echo ""
echo "🎉 安装完成！"
echo "================================="
echo "📚 启动指南:"
echo ""
echo "1. 配置数据库:"
echo "   mysql -u root -p < config/database.sql"
echo ""
echo "2. 修改配置文件:"
echo "   编辑 config/app.yaml 中的数据库连接信息"
echo ""
echo "3. 启动后端服务:"
echo "   cd backend && python main.py"
echo ""
echo "4. 启动前端服务:"
echo "   cd frontend && npm run dev"
echo ""
echo "5. 访问应用:"
echo "   前端: http://localhost:3000"
echo "   后端API: http://localhost:8000/docs"
echo ""
echo "🔧 注意事项:"
echo "- 首次运行会下载PyTorch模型，可能需要较长时间"
echo "- 确保有足够的磁盘空间存储图片和索引文件"
echo "- GPU支持需要安装对应的PyTorch版本"
echo ""
echo "✨ 开始你的智能图像搜索之旅吧！" 