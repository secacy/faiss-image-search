#!/usr/bin/env python3
"""
重建 FAISS 索引脚本
用于修复搜索功能失效的问题
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加项目路径到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db, Base, engine
from app.models.image import Image
from app.services.model_service import ModelService
from app.services.faiss_service import FaissService
from app.utils.logger import setup_logging

# 设置日志
setup_logging()


async def rebuild_faiss_index():
    """重建 FAISS 索引"""
    print("🔄 开始重建 FAISS 索引...")
    
    # 初始化服务
    model_service = ModelService()
    faiss_service = FaissService()
    
    try:
        # 初始化模型服务
        await model_service.initialize()
        print("✅ 模型服务初始化完成")
        
        # 初始化 FAISS 服务（会创建新的索引）
        await faiss_service.initialize()
        print("✅ FAISS 服务初始化完成")
        
        # 获取数据库中的所有图片
        db = next(get_db())
        images = db.query(Image).filter(Image.is_active == True).all()
        print(f"📊 找到 {len(images)} 张活跃图片")
        
        if not images:
            print("⚠️  数据库中没有活跃的图片记录")
            return
        
        # 重建索引
        rebuilt_count = 0
        for image in images:
            try:
                # 检查图片文件是否存在
                image_path = os.path.join("data", "images", image.file_path)
                if not os.path.exists(image_path):
                    print(f"⚠️  图片文件不存在，跳过: {image.file_path}")
                    continue
                
                # 提取特征
                features = await model_service.extract_features(image_path)
                
                # 添加到索引
                faiss_id = await faiss_service.add_vector(features, image.id)
                
                # 更新数据库中的 faiss_id
                image.faiss_id = faiss_id
                db.commit()
                
                rebuilt_count += 1
                print(f"✅ 重建索引: {image.file_path} (faiss_id: {faiss_id})")
                
            except Exception as e:
                print(f"❌ 处理图片失败 {image.file_path}: {e}")
                continue
        
        print(f"🎉 索引重建完成! 成功重建 {rebuilt_count} 张图片的索引")
        
        # 保存索引
        await faiss_service.save_index()
        print("💾 索引已保存到磁盘")
        
    except Exception as e:
        print(f"❌ 重建索引失败: {e}")
        raise
    finally:
        # 清理资源
        await model_service.cleanup()
        await faiss_service.cleanup()
        db.close()


if __name__ == "__main__":
    asyncio.run(rebuild_faiss_index()) 