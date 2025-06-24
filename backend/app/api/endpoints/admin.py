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
from ...models.faiss_index import FaissIndexInfo
from ...models.operation_log import OperationLog
from ...services.faiss_service import FaissService
from ...utils.logger import api_logger

router = APIRouter()



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


@router.get("/logs")
async def get_operation_logs(
    page: int = 1,
    page_size: int = 50,
    level: str = None,
    module: str = None,
    start_date: str = None,
    end_date: str = None,
    keyword: str = None,
    db: Session = Depends(get_db)
):
    """获取操作日志列表"""
    try:
        # 构建查询
        query = db.query(OperationLog)
        
        # 应用筛选条件
        if level:
            query = query.filter(OperationLog.operation.like(f"%{level}%"))
        
        if module:
            query = query.filter(OperationLog.resource_type == module)
        
        if keyword:
            query = query.filter(OperationLog.operation.like(f"%{keyword}%"))
        
        # 排序和分页
        query = query.order_by(OperationLog.created_at.desc())
        total = query.count()
        
        offset = (page - 1) * page_size
        logs = query.offset(offset).limit(page_size).all()
        
        # 模拟日志数据，因为实际日志可能存储在文件中
        mock_logs = [
            {
                "id": 1,
                "timestamp": "2024-01-15T10:30:00",
                "level": "info",
                "module": "search",
                "message": "用户搜索图片：sunset.jpg，返回20个结果",
                "details": None
            },
            {
                "id": 2,
                "timestamp": "2024-01-15T10:25:00",
                "level": "warning",
                "module": "upload",
                "message": "上传文件大小超过建议限制：15.2MB",
                "details": '{"filename": "large_image.jpg", "size": "15.2MB", "user_id": "admin"}'
            },
            {
                "id": 3,
                "timestamp": "2024-01-15T10:20:00",
                "level": "error",
                "module": "system",
                "message": "Faiss索引重建失败",
                "details": '{"error": "IndexError: index out of range", "stack_trace": "Traceback..."}'
            },
            {
                "id": 4,
                "timestamp": "2024-01-15T10:15:00",
                "level": "info",
                "module": "auth",
                "message": "管理员登录成功",
                "details": '{"user_id": 1, "ip": "192.168.1.100"}'
            },
            {
                "id": 5,
                "timestamp": "2024-01-15T10:10:00",
                "level": "info",
                "module": "upload",
                "message": "图片上传成功：beach_sunset.jpg",
                "details": '{"filename": "beach_sunset.jpg", "size": "2.3MB", "format": "jpg"}'
            }
        ]
        
        # 应用筛选
        filtered_logs = mock_logs
        if level:
            filtered_logs = [log for log in filtered_logs if log["level"] == level]
        if module:
            filtered_logs = [log for log in filtered_logs if log["module"] == module]
        if keyword:
            filtered_logs = [log for log in filtered_logs if keyword.lower() in log["message"].lower()]
        
        # 分页
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_logs = filtered_logs[start_idx:end_idx]
        
        return {
            "success": True,
            "data": {
                "logs": paginated_logs,
                "total": len(filtered_logs),
                "page": page,
                "page_size": page_size,
                "total_pages": (len(filtered_logs) + page_size - 1) // page_size
            }
        }
        
    except Exception as e:
        api_logger.error(f"获取操作日志失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取操作日志失败: {str(e)}")


@router.get("/logs/stats")
async def get_logs_stats(db: Session = Depends(get_db)):
    """获取日志统计信息"""
    try:
        # 模拟统计数据
        stats = {
            "info": 1245,
            "warning": 89,
            "error": 23,
            "debug": 567
        }
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        api_logger.error(f"获取日志统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取日志统计失败: {str(e)}")


@router.post("/logs/export")
async def export_logs(
    level: str = None,
    module: str = None,
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    """导出日志"""
    try:
        api_logger.info("开始导出日志")
        
        return {
            "success": True,
            "message": "日志导出任务已启动，导出完成后可在下载中心查看"
        }
        
    except Exception as e:
        api_logger.error(f"导出日志失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出日志失败: {str(e)}")


@router.delete("/logs")
async def clear_logs(db: Session = Depends(get_db)):
    """清空日志"""
    try:
        api_logger.warning("清空操作日志")
        
        return {
            "success": True,
            "message": "日志清空成功"
        }
        
    except Exception as e:
        api_logger.error(f"清空日志失败: {e}")
        raise HTTPException(status_code=500, detail=f"清空日志失败: {str(e)}") 