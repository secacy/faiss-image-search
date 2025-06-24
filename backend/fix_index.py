#!/usr/bin/env python3
"""
FAISS 索引修复脚本
完全重建 FAISS 索引和映射关系
"""

import os
import sys
import asyncio
import shutil

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.models.image import Image
from app.services.model_service import ModelService
from app.services.faiss_service import FaissService
from app.utils.logger import setup_logging

setup_logging()


async def fix_faiss_index():
    """完全修复 FAISS 索引"""
    print("🔧 开始修复 FAISS 索引...")
    
    # 1. 删除现有的索引文件
    index_path = "data/index/image_features.index"
    mapping_path = "data/index/image_features_mapping.pkl"
    
    if os.path.exists(index_path):
        os.remove(index_path)
        print(f"✅ 删除旧索引文件: {index_path}")
    
    if os.path.exists(mapping_path):
        os.remove(mapping_path)
        print(f"✅ 删除旧映射文件: {mapping_path}")
    
    # 2. 重置数据库中的 faiss_id
    db = next(get_db())
    try:
        images = db.query(Image).all()
        for image in images:
            image.faiss_id = None
        db.commit()
        print(f"✅ 重置数据库中的 faiss_id ({len(images)} 张图片)")
    finally:
        db.close()
    
    # 3. 初始化服务
    model_service = ModelService()
    faiss_service = FaissService()
    
    try:
        # 初始化模型服务
        await model_service.initialize()
        print("✅ 模型服务初始化完成")
        
        # 初始化 FAISS 服务（会创建新的索引）
        await faiss_service.initialize()
        print("✅ FAISS 服务初始化完成（新索引）")
        
        # 4. 重新处理所有活跃图片
        db = next(get_db())
        try:
            active_images = db.query(Image).filter(Image.is_active == True).all()
            print(f"📊 找到 {len(active_images)} 张活跃图片")
            
            rebuilt_count = 0
            skipped_count = 0
            
            for i, image in enumerate(active_images, 1):
                try:
                    # 构建图片路径 - 检查多种可能的路径格式
                    possible_paths = [
                        image.file_path,  # 完整路径
                        os.path.join("data", "images", image.file_path),  # 相对路径
                        os.path.join("data", "images", os.path.basename(image.file_path))  # 只用文件名
                    ]
                    
                    image_path = None
                    for path in possible_paths:
                        if os.path.exists(path):
                            image_path = path
                            break
                    
                    if image_path is None:
                        print(f"⚠️  [{i}/{len(active_images)}] 图片文件不存在，跳过: {image.file_path}")
                        print(f"    尝试的路径: {possible_paths}")
                        skipped_count += 1
                        continue
                    
                    print(f"🔄 [{i}/{len(active_images)}] 处理: {os.path.basename(image.file_path)}")
                    
                    # 提取特征
                    features = await model_service.extract_features(image_path)
                    
                    # 添加到索引
                    faiss_id = await faiss_service.add_vector(features, image.id)
                    
                    # 更新数据库中的 faiss_id
                    image.faiss_id = faiss_id
                    db.commit()
                    
                    rebuilt_count += 1
                    print(f"✅ [{i}/{len(active_images)}] 成功重建: {os.path.basename(image.file_path)} (faiss_id: {faiss_id})")
                    
                except Exception as e:
                    print(f"❌ [{i}/{len(active_images)}] 处理失败 {image.file_path}: {e}")
                    skipped_count += 1
                    continue
            
            print(f"\n🎉 索引修复完成!")
            print(f"  - 成功重建: {rebuilt_count} 张图片")
            print(f"  - 跳过/失败: {skipped_count} 张图片")
            
            # 5. 保存索引
            await faiss_service._save_index()
            print("💾 索引已保存到磁盘")
            
            # 6. 验证结果
            print(f"\n🔍 验证结果:")
            print(f"  - FAISS 索引向量数量: {faiss_service.index.ntotal}")
            print(f"  - 映射关系数量: {len(faiss_service.id_mapping)}")
            print(f"  - 下一个 faiss_id: {faiss_service.next_faiss_id}")
            
        finally:
            db.close()
        
    except Exception as e:
        print(f"❌ 修复索引失败: {e}")
        raise
    finally:
        # 清理资源
        await model_service.cleanup()
        await faiss_service.cleanup()


if __name__ == "__main__":
    asyncio.run(fix_faiss_index()) 