"""
系统配置数据模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
import json

from ..core.database import Base


class SystemConfig(Base):
    """系统配置模型"""
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    config_key = Column(String(100), unique=True, nullable=False, index=True)
    config_value = Column(Text, nullable=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<SystemConfig(key='{self.config_key}', value='{self.config_value[:50]}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "config_key": self.config_key,
            "config_value": self.config_value,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_value_as_json(self):
        """获取JSON格式的值"""
        try:
            return json.loads(self.config_value) if self.config_value else None
        except (json.JSONDecodeError, TypeError):
            return self.config_value
    
    def get_value_as_int(self, default: int = 0) -> int:
        """获取整数格式的值"""
        try:
            return int(self.config_value) if self.config_value else default
        except (ValueError, TypeError):
            return default
    
    def get_value_as_bool(self, default: bool = False) -> bool:
        """获取布尔格式的值"""
        if not self.config_value:
            return default
        return str(self.config_value).lower() in ('true', '1', 'yes', 'on')
    
    def set_value_from_json(self, value):
        """设置JSON格式的值"""
        if value is None:
            self.config_value = None
        else:
            self.config_value = json.dumps(value, ensure_ascii=False) 