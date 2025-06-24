"""
图片管理API端点
提供图片上传、查看、删除等功能
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import hashlib
from PIL import Image as PILImage
import io

from ...core.database import get_db
from ...models.image import Image
from ...services.model_service import ModelService
from ...services.faiss_service import FaissService
from ...core.config import get_settings
from ...utils.logger import api_logger

router = APIRouter()
settings = get_settings()


def get_model_service(request: Request) -> ModelService:
    """获取模型服务"""
    if not hasattr(request.app.state, 'model_service'):
        raise HTTPException(status_code=500, detail="模型服务未初始化")
    return request.app.state.model_service


def get_faiss_service(request: Request) -> FaissService:
    """获取Faiss服务"""
    if not hasattr(request.app.state, 'faiss_service'):
        raise HTTPException(status_code=500, detail="Faiss服务未初始化")
    return request.app.state.faiss_service


def calculate_file_hash(file_content: bytes) -> str:
    """计算文件MD5哈希值"""
    return hashlib.md5(file_content).hexdigest()


def save_uploaded_file(file_content: bytes, filename: str) -> str:
    """保存上传的文件"""
    # 确保上传目录存在
    upload_dir = settings.storage.upload_dir
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
    
    # 生成唯一文件名
    file_ext = os.path.splitext(filename)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # 保存文件
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    return file_path, unique_filename


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    model_service: ModelService = Depends(get_model_service),
    faiss_service: FaissService = Depends(get_faiss_service)
):
    """上传图片"""
    try:
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必须是图片格式")
        
        # 读取文件内容
        file_content = await file.read()
        
        # 验证文件大小
        if len(file_content) > settings.storage.max_file_size:
            raise HTTPException(status_code=400, detail="文件大小超过限制")
        
        # 计算文件哈希
        file_hash = calculate_file_hash(file_content)
        
        # 检查是否已存在相同文件
        existing_image = db.query(Image).filter(Image.hash_value == file_hash).first()
        if existing_image and existing_image.is_active:
            return {
                "success": True,
                "message": "图片已存在",
                "data": existing_image.to_dict()
            }
        
        # 获取图片信息
        try:
            with PILImage.open(io.BytesIO(file_content)) as img:
                width, height = img.size
                format_name = img.format.lower() if img.format else 'unknown'
        except Exception as e:
            api_logger.warning(f"获取图片信息失败: {e}")
            width = height = None
            format_name = 'unknown'
        
        # 保存文件
        file_path, unique_filename = save_uploaded_file(file_content, file.filename)
        
        # 提取特征
        api_logger.info(f"开始提取图片特征: {file.filename}")
        features = await model_service.extract_features(file_content)
        
        # 创建数据库记录
        image_record = Image(
            filename=unique_filename,
            original_name=file.filename,
            file_path=file_path,
            file_size=len(file_content),
            width=width,
            height=height,
            format=format_name,
            hash_value=file_hash,
            description=description,
            tags=tags.split(',') if tags else None
        )
        
        db.add(image_record)
        db.flush()  # 获取ID但不提交
        
        # 添加到Faiss索引
        faiss_id = await faiss_service.add_vector(features, image_record.id)
        image_record.faiss_id = faiss_id
        
        # 提交事务
        db.commit()
        
        api_logger.info(f"图片上传成功: {file.filename} -> {unique_filename}")
        
        return {
            "success": True,
            "message": "图片上传成功",
            "data": image_record.to_dict()
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        api_logger.error(f"图片上传失败: {e}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/list")
async def list_images(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取图片列表"""
    try:
        # 分页查询
        offset = (page - 1) * page_size
        
        # 查询图片
        images_query = db.query(Image).filter(Image.is_active == True).order_by(Image.upload_time.desc())
        
        total = images_query.count()
        images = images_query.offset(offset).limit(page_size).all()
        
        # 转换为响应格式
        image_list = [img.to_dict() for img in images]
        
        return {
            "success": True,
            "data": {
                "images": image_list,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": (total + page_size - 1) // page_size
                }
            }
        }
        
    except Exception as e:
        api_logger.error(f"获取图片列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取图片列表失败: {str(e)}")


@router.get("/{image_id}")
async def get_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    """获取图片详情"""
    try:
        image = db.query(Image).filter(
            Image.id == image_id,
            Image.is_active == True
        ).first()
        
        if not image:
            raise HTTPException(status_code=404, detail="图片不存在")
        
        return {
            "success": True,
            "data": image.to_dict(include_path=True)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"获取图片详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取图片详情失败: {str(e)}")


@router.delete("/{image_id}")
async def delete_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    """删除图片"""
    try:
        image = db.query(Image).filter(
            Image.id == image_id,
            Image.is_active == True
        ).first()
        
        if not image:
            raise HTTPException(status_code=404, detail="图片不存在")
        
        # 标记为删除（软删除）
        image.is_active = False
        db.commit()
        
        # 从Faiss索引中移除图片特征
        try:
            faiss_service.remove_image(image_id)
        except Exception as e:
            logger.warning(f"从索引中移除图片失败: {e}")
        # await faiss_service.remove_vector(image_id)
        
        api_logger.info(f"图片删除成功: {image.filename}")
        
        return {
            "success": True,
            "message": "图片删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        api_logger.error(f"删除图片失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除图片失败: {str(e)}")


@router.put("/{image_id}")
async def update_image(
    image_id: int,
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """更新图片信息"""
    try:
        image = db.query(Image).filter(
            Image.id == image_id,
            Image.is_active == True
        ).first()
        
        if not image:
            raise HTTPException(status_code=404, detail="图片不存在")
        
        # 更新信息
        if description is not None:
            image.description = description
        
        if tags is not None:
            image.tags = tags.split(',') if tags else None
        
        db.commit()
        
        return {
            "success": True,
            "message": "图片信息更新成功",
            "data": image.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        api_logger.error(f"更新图片信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新图片信息失败: {str(e)}")


@router.get("/stats/summary")
async def get_images_stats(db: Session = Depends(get_db)):
    """获取图片统计信息"""
    try:
        # 总图片数
        total_images = db.query(Image).filter(Image.is_active == True).count()
        
        # 总文件大小
        from sqlalchemy import func
        total_size_result = db.query(func.sum(Image.file_size)).filter(Image.is_active == True).scalar()
        total_size = total_size_result or 0
        
        # 按格式统计
        format_stats = db.query(
            Image.format,
            func.count(Image.id).label('count')
        ).filter(Image.is_active == True).group_by(Image.format).all()
        
        format_dict = {stat.format: stat.count for stat in format_stats}
        
        return {
            "success": True,
            "data": {
                "total_images": total_images,
                "total_size": total_size,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "format_stats": format_dict
            }
        }
        
    except Exception as e:
        api_logger.error(f"获取图片统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取图片统计失败: {str(e)}") 