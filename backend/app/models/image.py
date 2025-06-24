"""
图片数据模型
"""

from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..core.database import Base


class Image(Base):
    """图片模型"""
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False)  # 存储的文件名
    original_name = Column(String(255), nullable=False)  # 原始文件名
    file_path = Column(String(500), nullable=False)  # 文件路径
    file_size = Column(BigInteger, nullable=False)  # 文件大小（字节）
    width = Column(Integer, nullable=True)  # 图片宽度
    height = Column(Integer, nullable=True)  # 图片高度
    format = Column(String(10), nullable=True)  # 图片格式（jpg, png等）
    hash_value = Column(String(64), unique=True, nullable=True, index=True)  # 文件哈希值
    faiss_id = Column(Integer, unique=True, nullable=True, index=True)  # Faiss索引中的ID
    upload_time = Column(DateTime, default=func.now(), nullable=False)
    upload_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    tags = Column(JSON, nullable=True)  # 标签信息
    description = Column(Text, nullable=True)  # 图片描述
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 关系
    uploader = relationship("User", backref="uploaded_images", foreign_keys=[upload_by])
    
    def __repr__(self):
        return f"<Image(id={self.id}, filename='{self.filename}', faiss_id={self.faiss_id})>"
    
    def to_dict(self, include_path: bool = False):
        """转换为字典"""
        result = {
            "id": self.id,
            "filename": self.filename,
            "original_name": self.original_name,
            "file_size": self.file_size,
            "width": self.width,
            "height": self.height,
            "format": self.format,
            "hash_value": self.hash_value,
            "faiss_id": self.faiss_id,
            "upload_time": self.upload_time.isoformat() if self.upload_time else None,
            "upload_by": self.upload_by,
            "tags": self.tags,
            "description": self.description,
            "is_active": self.is_active,
            "url": self.url,
            "thumbnail_url": self.thumbnail_url
        }
        
        if include_path:
            result["file_path"] = self.file_path
            
        return result
    
    @property
    def url(self) -> str:
        """获取图片访问URL"""
        return f"/static/images/{self.filename}"
    
    @property
    def thumbnail_url(self) -> str:
        """获取缩略图URL"""
        name, ext = self.filename.rsplit('.', 1)
        return f"/static/images/thumbnails/{name}_thumb.{ext}"
    
    def get_dimensions(self) -> tuple:
        """获取图片尺寸"""
        return (self.width, self.height) if self.width and self.height else (0, 0)
    
    def get_aspect_ratio(self) -> float:
        """获取宽高比"""
        if self.width and self.height and self.height > 0:
            return self.width / self.height
        return 1.0 