#!/usr/bin/env python3
"""
FAISS 索引诊断脚本
"""

import os
import sys
import asyncio

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.models.image import Image
from app.services.faiss_service import FaissService
from app.utils.logger import setup_logging

setup_logging()


async def diagnose_index():
    """诊断索引问题"""
    print("🔍 开始诊断 FAISS 索引问题...")
    
    # 检查数据库
    db = next(get_db())
    total_images = db.query(Image).count()
    active_images = db.query(Image).filter(Image.is_active == True).count()
    images_with_faiss_id = db.query(Image).filter(Image.faiss_id.isnot(None)).count()
    
    print(f"📊 数据库统计:")
    print(f"  - 总图片数: {total_images}")
    print(f"  - 活跃图片数: {active_images}")
    print(f"  - 有 faiss_id 的图片数: {images_with_faiss_id}")
    
    # 检查 FAISS 索引
    faiss_service = FaissService()
    await faiss_service.initialize()
    
    print(f"🗂️  FAISS 索引统计:")
    print(f"  - 索引中的向量数量: {faiss_service.index.ntotal}")
    print(f"  - 下一个 faiss_id: {faiss_service.next_faiss_id}")
    
    # 检查映射关系
    print(f"🔗 映射关系统计:")
    print(f"  - id_mapping 映射数量: {len(faiss_service.id_mapping)}")
    print(f"  - reverse_mapping 映射数量: {len(faiss_service.reverse_mapping)}")
    
    # 列出有 faiss_id 的图片
    images_with_id = db.query(Image).filter(Image.faiss_id.isnot(None)).all()
    print(f"\n📝 有 faiss_id 的图片列表:")
    for img in images_with_id[:10]:  # 只显示前10个
        print(f"  - ID: {img.id}, faiss_id: {img.faiss_id}, file: {img.file_path}")
    
    if len(images_with_id) > 10:
        print(f"  ... 还有 {len(images_with_id) - 10} 张图片")
    
    # 检查文件是否存在
    missing_files = []
    for img in images_with_id:
        image_path = os.path.join("data", "images", img.file_path)
        if not os.path.exists(image_path):
            missing_files.append(img.file_path)
    
    if missing_files:
        print(f"\n⚠️  缺失的图片文件 ({len(missing_files)} 个):")
        for file_path in missing_files[:5]:
            print(f"  - {file_path}")
        if len(missing_files) > 5:
            print(f"  ... 还有 {len(missing_files) - 5} 个文件缺失")
    else:
        print("\n✅ 所有图片文件都存在")
    
    # 检查映射一致性
    print(f"\n🔍 映射一致性检查:")
    db_faiss_ids = {img.faiss_id for img in images_with_id}
    mapping_faiss_ids = set(faiss_service.id_mapping.keys())
    
    missing_in_mapping = db_faiss_ids - mapping_faiss_ids
    extra_in_mapping = mapping_faiss_ids - db_faiss_ids
    
    if missing_in_mapping:
        print(f"  - 数据库中有但映射中缺失的 faiss_id: {missing_in_mapping}")
    if extra_in_mapping:
        print(f"  - 映射中有但数据库中缺失的 faiss_id: {extra_in_mapping}")
    
    if not missing_in_mapping and not extra_in_mapping:
        print("  - ✅ 映射关系一致")
    
    await faiss_service.cleanup()
    db.close()


if __name__ == "__main__":
    asyncio.run(diagnose_index()) 