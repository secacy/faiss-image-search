"""
Faiss索引信息数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func

from ..core.database import Base


class FaissIndexInfo(Base):
    """Faiss索引信息模型"""
    __tablename__ = "faiss_index_info"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    index_path = Column(String(500), nullable=False)  # 索引文件路径
    total_vectors = Column(Integer, default=0, nullable=False)  # 向量总数
    feature_dim = Column(Integer, default=2048, nullable=False)  # 特征维度
    index_type = Column(String(50), default="IndexFlatIP", nullable=False)  # 索引类型
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    is_current = Column(Boolean, default=True, nullable=False)  # 是否为当前使用的索引
    
    def __repr__(self):
        return f"<FaissIndexInfo(id={self.id}, vectors={self.total_vectors}, type='{self.index_type}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "index_path": self.index_path,
            "total_vectors": self.total_vectors,
            "feature_dim": self.feature_dim,
            "index_type": self.index_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_current": self.is_current
        }
    
    def get_size_info(self) -> dict:
        """获取索引大小信息"""
        return {
            "total_vectors": self.total_vectors,
            "feature_dim": self.feature_dim,
            "estimated_memory": self.total_vectors * self.feature_dim * 4,  # 假设float32
            "index_type": self.index_type
        } 