"""
操作日志数据模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..core.database import Base


class OperationLog(Base):
    """操作日志模型"""
    __tablename__ = "operation_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    operation = Column(String(50), nullable=False, index=True)  # 操作类型
    resource_type = Column(String(50), nullable=True)  # 资源类型
    resource_id = Column(Integer, nullable=True)  # 资源ID
    details = Column(JSON, nullable=True)  # 操作详情
    ip_address = Column(String(45), nullable=True)  # IP地址
    user_agent = Column(Text, nullable=True)  # 用户代理
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # 关系
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<OperationLog(id={self.id}, operation='{self.operation}', user_id={self.user_id})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "operation": self.operation,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def create_log(cls, operation: str, user_id: int = None, resource_type: str = None, 
                   resource_id: int = None, details: dict = None, ip_address: str = None, 
                   user_agent: str = None):
        """创建操作日志"""
        return cls(
            user_id=user_id,
            operation=operation,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        ) 