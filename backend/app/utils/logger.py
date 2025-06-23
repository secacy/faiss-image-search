"""
日志工具模块
提供统一的日志配置和记录功能
"""

import os
import logging
import logging.handlers
from loguru import logger
import sys

from ..core.config import get_settings

settings = get_settings()


def setup_logging():
    """设置日志配置"""
    
    # 创建日志目录
    log_dir = os.path.dirname(settings.logging.file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # 移除默认的loguru处理器
    logger.remove()
    
    # 添加控制台处理器
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.logging.level,
        colorize=True
    )
    
    # 添加文件处理器
    if settings.logging.file:
        logger.add(
            settings.logging.file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=settings.logging.level,
            rotation="10 MB",  # 使用标准的时间或大小格式
            retention=settings.logging.backup_count,
            compression="zip",
            encoding="utf-8"
        )
    
    # 设置其他库的日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    
    logger.info("日志系统初始化完成")


def get_logger(name: str = None):
    """获取日志记录器"""
    if name:
        return logger.bind(name=name)
    return logger


class LoggerMixin:
    """日志混入类"""
    
    @property
    def logger(self):
        """获取当前类的日志记录器"""
        return get_logger(self.__class__.__name__)


# 创建应用日志记录器
app_logger = get_logger("app")
api_logger = get_logger("api")
service_logger = get_logger("service")
model_logger = get_logger("model")
faiss_logger = get_logger("faiss") 