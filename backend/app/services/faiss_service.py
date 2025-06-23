"""
Faiss服务
负责构建和维护图像特征向量索引，以及执行相似度搜索
"""

import faiss
import numpy as np
import os
from typing import List, Tuple, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import pickle

from ..core.config import get_settings
from ..core.database import get_db
from ..models.image import Image
from ..models.faiss_index import FaissIndexInfo
from ..utils.logger import LoggerMixin

settings = get_settings()


class FaissService(LoggerMixin):
    """Faiss索引服务类"""
    
    def __init__(self):
        self.index = None
        self.index_path = settings.faiss.index_path
        self.feature_dim = settings.faiss.feature_dim
        self.index_type = settings.faiss.index_type
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.id_mapping = {}  # faiss_id -> image_id 的映射
        self.reverse_mapping = {}  # image_id -> faiss_id 的映射
        self.next_faiss_id = 0
        
    async def initialize(self):
        """初始化Faiss索引"""
        try:
            self.logger.info("正在初始化Faiss索引服务...")
            
            # 创建索引目录
            index_dir = os.path.dirname(self.index_path)
            if not os.path.exists(index_dir):
                os.makedirs(index_dir, exist_ok=True)
            
            # 在线程池中加载或创建索引
            await asyncio.get_event_loop().run_in_executor(
                self.executor, self._load_or_create_index
            )
            
            self.logger.info(f"Faiss索引初始化完成，当前向量数量: {self.index.ntotal}, 下一个faiss_id: {self.next_faiss_id}")
            
        except Exception as e:
            self.logger.error(f"Faiss索引初始化失败: {e}")
            raise
    
    def _load_or_create_index(self):
        """加载或创建索引（在线程池中执行）"""
        if os.path.exists(self.index_path):
            # 加载现有索引
            self.logger.info(f"加载现有索引: {self.index_path}")
            self.index = faiss.read_index(self.index_path)
            
            # 加载ID映射
            mapping_path = self.index_path.replace('.index', '_mapping.pkl')
            if os.path.exists(mapping_path):
                with open(mapping_path, 'rb') as f:
                    mapping_data = pickle.load(f)
                    self.id_mapping = mapping_data.get('id_mapping', {})
                    self.reverse_mapping = mapping_data.get('reverse_mapping', {})
                    self.next_faiss_id = mapping_data.get('next_faiss_id', 0)
            else:
                # 如果没有映射文件，从数据库重建映射
                self._rebuild_mapping_from_db()
        else:
            # 创建新索引
            self.logger.info(f"创建新索引: {self.index_type}")
            if self.index_type == "IndexFlatIP":
                # 内积索引（适合归一化后的向量）
                self.index = faiss.IndexFlatIP(self.feature_dim)
            elif self.index_type == "IndexFlatL2":
                # L2距离索引
                self.index = faiss.IndexFlatL2(self.feature_dim)
            elif self.index_type == "IndexIVFFlat":
                # IVF索引（倒排文件索引）
                quantizer = faiss.IndexFlatIP(self.feature_dim)
                self.index = faiss.IndexIVFFlat(quantizer, self.feature_dim, 100)
            else:
                # 默认使用内积索引
                self.index = faiss.IndexFlatIP(self.feature_dim)
            
            # 为新索引从数据库重建映射
            self._rebuild_mapping_from_db()
    
    def _rebuild_mapping_from_db(self):
        """从数据库重建ID映射"""
        try:
            from sqlalchemy.orm import sessionmaker
            from sqlalchemy import create_engine
            
            # 创建数据库连接
            engine = create_engine(settings.database.url)
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()
            
            try:
                # 查询所有有效的图片记录
                images = db.query(Image).filter(
                    Image.is_active == True,
                    Image.faiss_id.isnot(None)
                ).order_by(Image.faiss_id).all()
                
                # 重建映射
                for image in images:
                    self.id_mapping[image.faiss_id] = image.id
                    self.reverse_mapping[image.id] = image.faiss_id
                
                # 设置下一个可用的faiss_id
                if images:
                    max_faiss_id = max(image.faiss_id for image in images)
                    self.next_faiss_id = max_faiss_id + 1
                else:
                    self.next_faiss_id = 0
                
                self.logger.info(f"从数据库重建映射完成，下一个可用faiss_id: {self.next_faiss_id}")
                
            finally:
                db.close()
                
        except Exception as e:
            self.logger.error(f"重建映射失败: {e}")
            # 如果重建失败，至少确保不会从0开始
            self.next_faiss_id = 1000
    
    async def add_vector(self, feature_vector: np.ndarray, image_id: int) -> int:
        """
        添加特征向量到索引
        
        Args:
            feature_vector: 特征向量
            image_id: 图像ID
            
        Returns:
            Faiss索引中的ID
        """
        try:
            faiss_id = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._add_vector_sync, feature_vector, image_id
            )
            
            # 保存索引
            await self._save_index()
            
            return faiss_id
        except Exception as e:
            self.logger.error(f"添加向量失败: {e}")
            raise
    
    def _add_vector_sync(self, feature_vector: np.ndarray, image_id: int) -> int:
        """同步添加向量（在线程池中执行）"""
        # 确保向量是二维的
        if feature_vector.ndim == 1:
            feature_vector = feature_vector.reshape(1, -1)
        
        # 检查向量维度
        if feature_vector.shape[1] != self.feature_dim:
            raise ValueError(f"特征向量维度不匹配: 期望{self.feature_dim}, 实际{feature_vector.shape[1]}")
        
        # 分配Faiss ID
        faiss_id = self.next_faiss_id
        self.next_faiss_id += 1
        
        # 更新映射
        self.id_mapping[faiss_id] = image_id
        self.reverse_mapping[image_id] = faiss_id
        
        # 添加到索引
        self.index.add(feature_vector.astype(np.float32))
        
        return faiss_id
    
    async def search(self, query_vector: np.ndarray, k: int = 10) -> Tuple[List[float], List[int]]:
        """
        搜索最相似的向量
        
        Args:
            query_vector: 查询向量
            k: 返回的结果数量
            
        Returns:
            (相似度得分列表, 图像ID列表)
        """
        try:
            similarities, image_ids = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._search_sync, query_vector, k
            )
            return similarities, image_ids
        except Exception as e:
            self.logger.error(f"搜索失败: {e}")
            raise
    
    def _search_sync(self, query_vector: np.ndarray, k: int) -> Tuple[List[float], List[int]]:
        """同步搜索（在线程池中执行）"""
        if self.index.ntotal == 0:
            return [], []
        
        # 确保查询向量是二维的
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        
        # 检查向量维度
        if query_vector.shape[1] != self.feature_dim:
            raise ValueError(f"查询向量维度不匹配: 期望{self.feature_dim}, 实际{query_vector.shape[1]}")
        
        # 限制k值
        k = min(k, self.index.ntotal)
        
        # 执行搜索
        scores, faiss_indices = self.index.search(query_vector.astype(np.float32), k)
        
        # 转换Faiss索引为图像ID
        similarities = []
        image_ids = []
        
        for i, (score, faiss_idx) in enumerate(zip(scores[0], faiss_indices[0])):
            if faiss_idx in self.id_mapping:
                image_id = self.id_mapping[faiss_idx]
                similarities.append(float(score))
                image_ids.append(image_id)
        
        return similarities, image_ids
    
    async def _save_index(self):
        """保存索引到文件"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                self.executor, self._save_index_sync
            )
        except Exception as e:
            self.logger.error(f"保存索引失败: {e}")
    
    def _save_index_sync(self):
        """同步保存索引（在线程池中执行）"""
        # 保存Faiss索引
        faiss.write_index(self.index, self.index_path)
        
        # 保存ID映射
        mapping_path = self.index_path.replace('.index', '_mapping.pkl')
        mapping_data = {
            'id_mapping': self.id_mapping,
            'reverse_mapping': self.reverse_mapping,
            'next_faiss_id': self.next_faiss_id
        }
        with open(mapping_path, 'wb') as f:
            pickle.dump(mapping_data, f)
    
    def get_index_info(self) -> dict:
        """获取索引信息"""
        return {
            "total_vectors": self.index.ntotal if self.index else 0,
            "feature_dim": self.feature_dim,
            "index_type": self.index_type,
            "index_path": self.index_path,
            "is_trained": self.index.is_trained if self.index else False
        }
    
    def is_initialized(self) -> bool:
        """检查索引是否已初始化"""
        return self.index is not None
    
    async def cleanup(self):
        """清理资源"""
        try:
            self.logger.info("正在清理Faiss服务资源...")
            
            # 保存索引
            if self.index is not None:
                await self._save_index()
            
            # 关闭线程池
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True)
            
            self.logger.info("Faiss服务资源清理完成")
        except Exception as e:
            self.logger.error(f"Faiss服务清理失败: {e}") 