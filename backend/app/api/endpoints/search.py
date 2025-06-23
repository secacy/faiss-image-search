"""
图片搜索API端点
提供以图搜图功能
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import time
import httpx
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


@router.post("/by-upload")
async def search_by_upload(
    file: UploadFile = File(...),
    k: int = Form(default=10),
    db: Session = Depends(get_db),
    model_service: ModelService = Depends(get_model_service),
    faiss_service: FaissService = Depends(get_faiss_service)
):
    """通过上传文件进行图片搜索"""
    start_time = time.time()
    
    try:
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必须是图片格式")
        
        # 验证K值
        k = max(1, min(k, settings.search.max_k))
        
        # 读取文件内容
        file_content = await file.read()
        
        # 提取特征
        api_logger.info(f"开始提取查询图片特征: {file.filename}")
        query_features = await model_service.extract_features(file_content)
        
        # 执行搜索
        api_logger.info(f"开始搜索相似图片，K={k}")
        similarities, image_ids = await faiss_service.search(query_features, k)
        
        # 获取图片详情
        results = []
        if image_ids:
            images = db.query(Image).filter(
                Image.id.in_(image_ids),
                Image.is_active == True
            ).all()
            
            # 按搜索结果顺序排列
            image_dict = {img.id: img for img in images}
            for i, (image_id, similarity) in enumerate(zip(image_ids, similarities)):
                if image_id in image_dict:
                    img = image_dict[image_id]
                    results.append({
                        "rank": i + 1,
                        "similarity": similarity,
                        "image": {
                            "id": img.id,
                            "filename": img.filename,
                            "original_name": img.original_name,
                            "url": img.url,
                            "thumbnail_url": img.thumbnail_url,
                            "width": img.width,
                            "height": img.height,
                            "file_size": img.file_size,
                            "upload_time": img.upload_time.isoformat() if img.upload_time else None
                        }
                    })
        
        # 计算搜索时间
        search_duration = time.time() - start_time
        

        
        api_logger.info(f"搜索完成，返回{len(results)}个结果，耗时{search_duration:.3f}秒")
        
        return {
            "success": True,
            "data": {
                "query_info": {
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "size": len(file_content)
                },
                "search_params": {
                    "k": k,
                    "duration": round(search_duration, 3)
                },
                "results": results,
                "total_found": len(results)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.post("/by-url")
async def search_by_url(
    image_url: str = Form(...),
    k: int = Form(default=10),
    db: Session = Depends(get_db),
    model_service: ModelService = Depends(get_model_service),
    faiss_service: FaissService = Depends(get_faiss_service)
):
    """通过图片URL进行搜索"""
    start_time = time.time()
    
    try:
        # 验证K值
        k = max(1, min(k, settings.search.max_k))
        
        # 下载图片
        api_logger.info(f"开始下载图片: {image_url}")
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(image_url)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="无法下载图片")
            
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="URL必须指向图片文件")
            
            image_content = response.content
        
        # 提取特征
        api_logger.info("开始提取查询图片特征")
        query_features = await model_service.extract_features(image_content)
        
        # 执行搜索
        api_logger.info(f"开始搜索相似图片，K={k}")
        similarities, image_ids = await faiss_service.search(query_features, k)
        
        # 获取图片详情
        results = []
        if image_ids:
            images = db.query(Image).filter(
                Image.id.in_(image_ids),
                Image.is_active == True
            ).all()
            
            # 按搜索结果顺序排列
            image_dict = {img.id: img for img in images}
            for i, (image_id, similarity) in enumerate(zip(image_ids, similarities)):
                if image_id in image_dict:
                    img = image_dict[image_id]
                    results.append({
                        "rank": i + 1,
                        "similarity": similarity,
                        "image": {
                            "id": img.id,
                            "filename": img.filename,
                            "original_name": img.original_name,
                            "url": img.url,
                            "thumbnail_url": img.thumbnail_url,
                            "width": img.width,
                            "height": img.height,
                            "file_size": img.file_size,
                            "upload_time": img.upload_time.isoformat() if img.upload_time else None
                        }
                    })
        
        # 计算搜索时间
        search_duration = time.time() - start_time
        

        
        api_logger.info(f"搜索完成，返回{len(results)}个结果，耗时{search_duration:.3f}秒")
        
        return {
            "success": True,
            "data": {
                "query_info": {
                    "url": image_url,
                    "content_type": content_type,
                    "size": len(image_content)
                },
                "search_params": {
                    "k": k,
                    "duration": round(search_duration, 3)
                },
                "results": results,
                "total_found": len(results)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"URL搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.post("/by-image-id/{image_id}")
async def search_by_image_id(
    image_id: int,
    k: int = Form(default=10),
    db: Session = Depends(get_db),
    model_service: ModelService = Depends(get_model_service),
    faiss_service: FaissService = Depends(get_faiss_service)
):
    """通过数据库中的图片ID进行搜索"""
    start_time = time.time()
    
    try:
        # 验证K值
        k = max(1, min(k, settings.search.max_k))
        
        # 获取查询图片
        query_image = db.query(Image).filter(
            Image.id == image_id,
            Image.is_active == True
        ).first()
        
        if not query_image:
            raise HTTPException(status_code=404, detail="图片不存在")
        
        # 提取特征
        api_logger.info(f"开始提取查询图片特征: {query_image.filename}")
        query_features = await model_service.extract_features(query_image.file_path)
        
        # 执行搜索
        api_logger.info(f"开始搜索相似图片，K={k}")
        similarities, image_ids = await faiss_service.search(query_features, k + 1)  # +1 排除自身
        
        # 过滤掉查询图片本身
        filtered_results = []
        for img_id, similarity in zip(image_ids, similarities):
            if img_id != image_id:
                filtered_results.append((img_id, similarity))
        
        # 限制结果数量
        filtered_results = filtered_results[:k]
        
        # 获取图片详情
        results = []
        if filtered_results:
            result_image_ids = [r[0] for r in filtered_results]
            images = db.query(Image).filter(
                Image.id.in_(result_image_ids),
                Image.is_active == True
            ).all()
            
            # 按搜索结果顺序排列
            image_dict = {img.id: img for img in images}
            for i, (img_id, similarity) in enumerate(filtered_results):
                if img_id in image_dict:
                    img = image_dict[img_id]
                    results.append({
                        "rank": i + 1,
                        "similarity": similarity,
                        "image": {
                            "id": img.id,
                            "filename": img.filename,
                            "original_name": img.original_name,
                            "url": img.url,
                            "thumbnail_url": img.thumbnail_url,
                            "width": img.width,
                            "height": img.height,
                            "file_size": img.file_size,
                            "upload_time": img.upload_time.isoformat() if img.upload_time else None
                        }
                    })
        
        # 计算搜索时间
        search_duration = time.time() - start_time
        

        
        api_logger.info(f"搜索完成，返回{len(results)}个结果，耗时{search_duration:.3f}秒")
        
        return {
            "success": True,
            "data": {
                "query_info": {
                    "image_id": query_image.id,
                    "filename": query_image.filename,
                    "original_name": query_image.original_name,
                    "url": query_image.url
                },
                "search_params": {
                    "k": k,
                    "duration": round(search_duration, 3)
                },
                "results": results,
                "total_found": len(results)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"图片ID搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


