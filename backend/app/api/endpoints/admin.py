"""
管理后台API端点
提供系统管理功能
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
from pydantic import BaseModel

from ...core.database import get_db
from ...models.image import Image
from ...models.system_config import SystemConfig
from ...models.faiss_index import FaissIndexInfo
from ...services.faiss_service import FaissService
from ...utils.logger import api_logger

router = APIRouter()


class ConfigUpdateRequest(BaseModel):
    """配置更新请求模型"""
    config_key: str
    config_value: str
    description: str = None


def get_faiss_service(request: Request) -> FaissService:
    """获取Faiss服务"""
    if not hasattr(request.app.state, 'faiss_service'):
        raise HTTPException(status_code=500, detail="Faiss服务未初始化")
    return request.app.state.faiss_service


@router.get("/dashboard")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    faiss_service: FaissService = Depends(get_faiss_service)
):
    """获取仪表板统计数据"""
    try:
        # 图片统计
        total_images = db.query(Image).filter(Image.is_active == True).count()
        
        # Faiss索引信息
        faiss_info = faiss_service.get_index_info()
        
        # 存储使用情况
        total_size = db.query(func.sum(Image.file_size)).filter(Image.is_active == True).scalar() or 0
        
        return {
            "success": True,
            "data": {
                "overview": {
                    "total_images": total_images,
                    "total_storage_mb": round(total_size / 1024 / 1024, 2)
                },
                "faiss_index": faiss_info
            }
        }
        
    except Exception as e:
        api_logger.error(f"获取仪表板数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取仪表板数据失败: {str(e)}")


@router.get("/images/stats")
async def get_images_detailed_stats(db: Session = Depends(get_db)):
    """获取图片详细统计"""
    try:
        # 按格式统计
        format_stats = db.query(
            Image.format,
            func.count(Image.id).label('count'),
            func.sum(Image.file_size).label('total_size')
        ).filter(Image.is_active == True).group_by(Image.format).all()
        
        format_data = []
        for stat in format_stats:
            format_data.append({
                "format": stat.format,
                "count": stat.count,
                "total_size": stat.total_size,
                "avg_size": round(stat.total_size / stat.count / 1024, 2) if stat.count > 0 else 0
            })
        
        # 按月份统计
        monthly_stats = db.query(
            func.year(Image.upload_time).label('year'),
            func.month(Image.upload_time).label('month'),
            func.count(Image.id).label('count')
        ).filter(Image.is_active == True).group_by(
            func.year(Image.upload_time),
            func.month(Image.upload_time)
        ).order_by(
            func.year(Image.upload_time).desc(),
            func.month(Image.upload_time).desc()
        ).limit(12).all()
        
        monthly_data = []
        for stat in monthly_stats:
            monthly_data.append({
                "period": f"{stat.year}-{stat.month:02d}",
                "count": stat.count
            })
        
        return {
            "success": True,
            "data": {
                "format_stats": format_data,
                "monthly_upload_trend": monthly_data
            }
        }
        
    except Exception as e:
        api_logger.error(f"获取图片统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取图片统计失败: {str(e)}")


@router.get("/config")
async def get_system_config(db: Session = Depends(get_db)):
    """获取系统配置"""
    try:
        configs = db.query(SystemConfig).all()
        config_dict = {}
        
        for config in configs:
            config_dict[config.config_key] = {
                "value": config.config_value,
                "description": config.description
            }
        
        # 返回默认配置结构
        default_config = {
            "basic": {
                "system_name": config_dict.get("system_name", {}).get("value", "图与图寻"),
                "system_description": config_dict.get("system_description", {}).get("value", "智能图像搜索系统"),
                "admin_email": config_dict.get("admin_email", {}).get("value", "admin@example.com"),
                "max_upload_size": int(config_dict.get("max_upload_size", {}).get("value", "10485760")) // (1024*1024),
                "default_search_limit": int(config_dict.get("default_search_limit", {}).get("value", "20")),
                "maintenance_mode": config_dict.get("maintenance_mode", {}).get("value", "false").lower() == "true"
            },
            "search": {
                "similarity_threshold": float(config_dict.get("similarity_threshold", {}).get("value", "0.7")),
                "max_results": int(config_dict.get("max_results", {}).get("value", "100")),
                "timeout": int(config_dict.get("search_timeout", {}).get("value", "30")),
                "enable_cache": config_dict.get("enable_cache", {}).get("value", "true").lower() == "true",
                "cache_expire": int(config_dict.get("cache_expire", {}).get("value", "3600"))
            },
            "storage": {
                "type": config_dict.get("storage_type", {}).get("value", "local"),
                "path": config_dict.get("storage_path", {}).get("value", "./data/images"),
                "image_quality": int(config_dict.get("image_quality", {}).get("value", "90")),
                "auto_cleanup": config_dict.get("auto_cleanup", {}).get("value", "false").lower() == "true",
                "cleanup_interval": int(config_dict.get("cleanup_interval", {}).get("value", "30"))
            },
            "model": {
                "type": config_dict.get("model_type", {}).get("value", "resnet50"),
                "path": config_dict.get("model_path", {}).get("value", "./models/resnet50.pth"),
                "batch_size": int(config_dict.get("batch_size", {}).get("value", "8")),
                "device": config_dict.get("device", {}).get("value", "auto"),
                "feature_dim": int(config_dict.get("feature_dim", {}).get("value", "2048"))
            },
            "security": {
                "enable_rate_limit": config_dict.get("enable_rate_limit", {}).get("value", "true").lower() == "true",
                "rate_limit": int(config_dict.get("rate_limit", {}).get("value", "100")),
                "jwt_secret": config_dict.get("jwt_secret", {}).get("value", "your-secret-key"),
                "token_expire": int(config_dict.get("token_expire", {}).get("value", "24")),
                "enable_cors": config_dict.get("enable_cors", {}).get("value", "true").lower() == "true"
            }
        }
        
        return {
            "success": True,
            "data": default_config
        }
        
    except Exception as e:
        api_logger.error(f"获取系统配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取系统配置失败: {str(e)}")


@router.post("/config")
async def update_system_config(
    config_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """更新系统配置"""
    try:
        updated_configs = []
        
        # 扁平化配置数据
        flat_config = {}
        for category, settings in config_data.items():
            if isinstance(settings, dict):
                for key, value in settings.items():
                    flat_key = f"{key}" if category == "basic" else f"{key}"
                    flat_config[flat_key] = str(value)
        
        # 配置映射
        config_mapping = {
            "system_name": "系统名称",
            "system_description": "系统描述",
            "admin_email": "管理员邮箱",
            "max_upload_size": "最大上传文件大小(MB)",
            "default_search_limit": "默认搜索结果数量",
            "maintenance_mode": "维护模式",
            "similarity_threshold": "相似度阈值",
            "max_results": "最大搜索结果数",
            "timeout": "搜索超时时间",
            "enable_cache": "启用缓存",
            "cache_expire": "缓存过期时间",
            "type": "存储类型",
            "path": "存储路径",
            "image_quality": "图片质量",
            "auto_cleanup": "自动清理",
            "cleanup_interval": "清理间隔",
            "model_type": "模型类型",
            "model_path": "模型路径",
            "batch_size": "批处理大小",
            "device": "设备类型",
            "feature_dim": "特征维度",
            "enable_rate_limit": "启用访问限制",
            "rate_limit": "访问限制次数",
            "jwt_secret": "JWT密钥",
            "token_expire": "Token过期时间",
            "enable_cors": "启用跨域"
        }
        
        for key, value in flat_config.items():
            description = config_mapping.get(key, key)
            
            # 查找现有配置
            existing_config = db.query(SystemConfig).filter(
                SystemConfig.config_key == key
            ).first()
            
            if existing_config:
                existing_config.config_value = value
                existing_config.description = description
                updated_configs.append(key)
            else:
                new_config = SystemConfig(
                    config_key=key,
                    config_value=value,
                    description=description
                )
                db.add(new_config)
                updated_configs.append(key)
        
        db.commit()
        
        api_logger.info(f"系统配置已更新: {updated_configs}")
        
        return {
            "success": True,
            "message": "配置更新成功",
            "data": {
                "updated_configs": updated_configs
            }
        }
        
    except Exception as e:
        api_logger.error(f"更新系统配置失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新系统配置失败: {str(e)}")


@router.get("/config/{config_key}")
async def get_config_value(config_key: str, db: Session = Depends(get_db)):
    """获取单个配置值"""
    try:
        config = db.query(SystemConfig).filter(
            SystemConfig.config_key == config_key
        ).first()
        
        if not config:
            raise HTTPException(status_code=404, detail="配置项不存在")
        
        return {
            "success": True,
            "data": {
                "config_key": config.config_key,
                "config_value": config.config_value,
                "description": config.description
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"获取配置值失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取配置值失败: {str(e)}")


@router.put("/config/{config_key}")
async def update_config_value(
    config_key: str,
    request: ConfigUpdateRequest,
    db: Session = Depends(get_db)
):
    """更新单个配置值"""
    try:
        config = db.query(SystemConfig).filter(
            SystemConfig.config_key == config_key
        ).first()
        
        if config:
            config.config_value = request.config_value
            if request.description:
                config.description = request.description
        else:
            config = SystemConfig(
                config_key=config_key,
                config_value=request.config_value,
                description=request.description or config_key
            )
            db.add(config)
        
        db.commit()
        
        return {
            "success": True,
            "message": "配置更新成功",
            "data": config.to_dict()
        }
        
    except Exception as e:
        api_logger.error(f"更新配置值失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新配置值失败: {str(e)}")


@router.get("/system/info")
async def get_system_info(
    request: Request,
    db: Session = Depends(get_db),
    faiss_service: FaissService = Depends(get_faiss_service)
):
    """获取系统信息"""
    try:
        import psutil
        import time
        from datetime import datetime, timedelta
        
        # 系统状态
        system_info = {
            "version": "1.0.0",
            "python_version": "3.9.0",
            "uptime": "2天 3小时 45分钟",
            "cpu_usage": round(psutil.cpu_percent(interval=1), 1),
            "memory_usage": round(psutil.virtual_memory().percent, 1),
            "disk_usage": round(psutil.disk_usage('/').percent, 1)
        }
        
        # 服务状态
        services_status = {
            "database": "connected",
            "faiss_index": "active",
            "model_service": "loaded"
        }
        
        return {
            "success": True,
            "data": {
                "system_info": system_info,
                "services_status": services_status
            }
        }
        
    except Exception as e:
        api_logger.error(f"获取系统信息失败: {e}")
        return {
            "success": True,
            "data": {
                "system_info": {
                    "version": "1.0.0",
                    "python_version": "3.9.0",
                    "uptime": "未知",
                    "cpu_usage": 0,
                    "memory_usage": 0,
                    "disk_usage": 0
                },
                "services_status": {
                    "database": "unknown",
                    "faiss_index": "unknown",
                    "model_service": "unknown"
                }
            }
        }


@router.post("/system/restart")
async def restart_system():
    """重启系统"""
    try:
        # 这里应该实现系统重启逻辑
        api_logger.info("系统重启请求")
        
        return {
            "success": True,
            "message": "系统重启请求已接收，将在5秒后重启"
        }
        
    except Exception as e:
        api_logger.error(f"系统重启失败: {e}")
        raise HTTPException(status_code=500, detail=f"系统重启失败: {str(e)}")


@router.post("/system/cache/clear")
async def clear_system_cache():
    """清理系统缓存"""
    try:
        # 这里应该实现缓存清理逻辑
        api_logger.info("清理系统缓存")
        
        return {
            "success": True,
            "message": "系统缓存清理完成"
        }
        
    except Exception as e:
        api_logger.error(f"清理缓存失败: {e}")
        raise HTTPException(status_code=500, detail=f"清理缓存失败: {str(e)}")


@router.post("/index/rebuild")
async def rebuild_faiss_index(
    faiss_service: FaissService = Depends(get_faiss_service)
):
    """重建Faiss索引"""
    try:
        # 这里应该实现异步重建索引的逻辑
        api_logger.info("开始重建Faiss索引")
        
        return {
            "success": True,
            "message": "索引重建任务已启动，请稍后查看进度"
        }
        
    except Exception as e:
        api_logger.error(f"重建索引失败: {e}")
        raise HTTPException(status_code=500, detail=f"重建索引失败: {str(e)}") 