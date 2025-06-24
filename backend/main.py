#!/usr/bin/env python3
"""
图与图寻 - 后端主应用入口
基于FastAPI的以图搜图Web服务
"""

import os
# 解决OpenMP库冲突问题
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.database import create_tables
from app.api.routes import api_router
from app.services.faiss_service import FaissService
from app.services.model_service import ModelService
from app.utils.logger import setup_logging

# 设置日志
setup_logging()

# 获取配置
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    print("🚀 正在启动图与图寻服务...")
    
    # 初始化数据库表
    await create_tables()
    
    # 初始化模型服务
    model_service = ModelService()
    await model_service.initialize()
    app.state.model_service = model_service
    
    # 初始化Faiss服务
    faiss_service = FaissService()
    await faiss_service.initialize()
    app.state.faiss_service = faiss_service
    
    print("✅ 服务启动完成!")
    
    yield
    
    # 关闭时清理
    print("🛑 正在关闭服务...")
    if hasattr(app.state, 'model_service'):
        await app.state.model_service.cleanup()
    if hasattr(app.state, 'faiss_service'):
        await app.state.faiss_service.cleanup()
    print("✅ 服务已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="图与图寻 API",
    description="基于Faiss的以图搜图API服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.server.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
import os
static_dir = os.path.join(os.path.dirname(__file__), "data")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 注册API路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "message": "图与图寻 API 服务运行中",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """详细健康检查"""
    return {
        "status": "healthy",
        "database": "connected",
        "faiss_service": "initialized",
        "model_service": "initialized"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.debug,
        log_level="info"
    ) 