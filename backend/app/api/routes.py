"""
API路由主入口
组织所有的路由模块
"""

from fastapi import APIRouter

from .endpoints import auth, images, search, admin

# 创建主路由器
api_router = APIRouter()

# 注册各个路由模块
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(images.router, prefix="/images", tags=["图片管理"])
api_router.include_router(search.router, prefix="/search", tags=["图片搜索"])
api_router.include_router(admin.router, prefix="/admin", tags=["管理后台"]) 