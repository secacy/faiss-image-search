#!/usr/bin/env python3
"""
图与图寻 - 简化版后端启动文件
只包含基本的FastAPI功能，用于测试
"""

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    import os
    import yaml
    from pathlib import Path
except ImportError as e:
    print(f"❌ 缺少依赖包: {e}")
    print("请运行以下命令安装依赖:")
    print("pip install fastapi uvicorn pyyaml")
    exit(1)

# 创建FastAPI应用
app = FastAPI(
    title="图与图寻 API (简化版)",
    description="基于Faiss的以图搜图API服务 - 简化测试版本",
    version="1.0.0-simple",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "message": "图与图寻 API 服务运行中 (简化版)",
        "status": "healthy",
        "version": "1.0.0-simple"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "mode": "simplified",
        "available_endpoints": ["/", "/health", "/docs", "/redoc"]
    }

@app.get("/api/v1/test")
async def test_api():
    """测试API接口"""
    return {
        "message": "API测试成功",
        "timestamp": "2024-06-08",
        "status": "ok"
    }

def check_dependencies():
    """检查依赖和环境"""
    print("🔍 检查运行环境...")
    
    # 检查目录
    dirs_to_check = ["../config", "../data", "../logs"]
    for dir_path in dirs_to_check:
        if not os.path.exists(dir_path):
            print(f"📁 创建目录: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
    
    # 检查配置文件
    config_path = "../config/config.yaml"
    if os.path.exists(config_path):
        print(f"✅ 配置文件存在: {config_path}")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                print(f"✅ 配置文件解析成功，包含 {len(config)} 个配置段")
        except Exception as e:
            print(f"⚠️ 配置文件解析失败: {e}")
    else:
        print(f"⚠️ 配置文件不存在: {config_path}")
    
    print("✅ 环境检查完成")

if __name__ == "__main__":
    print("🚀 启动图与图寻简化版服务...")
    
    # 检查环境
    check_dependencies()
    
    # 启动服务
    print("🌐 启动Web服务...")
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 